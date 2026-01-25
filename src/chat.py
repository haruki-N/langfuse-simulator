from dataclasses import dataclass, asdict, field
from dotenv import load_dotenv

load_dotenv()

from langfuse.openai import openai
from langfuse import get_client, observe
from logger import get_logger

logger = get_logger(__name__)


DEFAULT_SYSTEM_PROMPT = "You are a helpful cooking assistant that answers questions about recipes and cooking."


REASONING_MODEL_PREFIXES = ("o1", "o3", "gpt-5", "gpt-5.1")


@dataclass
class GenerationConfig:
  model: str = "gpt-4o-mini"
  max_tokens: int | None = None
  max_completion_tokens: int | None = None
  temperature: float | None = None
  top_p: float = 1.0
  frequency_penalty: float = 0.0
  presence_penalty: float = 0.0
  # Langfuse Prompt Management 用設定
  prompt_name: str | None = None
  prompt_variables: dict = field(default_factory=dict)

  def __post_init__(self):
    if self._is_reasoning_model():
      self._normalize_for_reasoning_model()

  def _is_reasoning_model(self) -> bool:
    return self.model.startswith(REASONING_MODEL_PREFIXES)

  def _normalize_for_reasoning_model(self):
    if self.max_tokens is not None and self.max_completion_tokens is None:
      self.max_completion_tokens = self.max_tokens
      self.max_tokens = None
      logger.info(f"Reasoning model detected: converted max_tokens to max_completion_tokens={self.max_completion_tokens}")

    # 推論モデルは reasoning_tokens + output_tokens で消費するため、小さすぎる場合は拡大
    if self.max_completion_tokens is not None and self.max_completion_tokens < 3000:
      logger.warning(f"Reasoning model detected: max_completion_tokens={self.max_completion_tokens} is too small, expanding to 10000")
      self.max_completion_tokens = 10000

    if self.temperature is not None:
      logger.warning(f"Reasoning model detected: temperature={self.temperature} is not supported, setting to None")
      self.temperature = None


def get_system_prompt(config: "GenerationConfig") -> str:
  """
  Langfuse Prompt Management から system prompt を取得する。
  prompt_name が設定されていない場合はデフォルトのプロンプトを返す。
  """
  if config.prompt_name is None:
    logger.info("No Prompt Name at Langfuse provided: use default prompt at config")
    return DEFAULT_SYSTEM_PROMPT

  try:
    langfuse = get_client()
    prompt = langfuse.get_prompt(config.prompt_name)
    return prompt.compile(**config.prompt_variables)
  except Exception as e:
    raise ValueError(f"Failed to fetch prompt '{config.prompt_name}' from Langfuse: {e}")


class SimpleChat:
  def __init__(self, config: GenerationConfig | None = None):
    self.config = config or GenerationConfig()
    self._system_prompt = get_system_prompt(self.config)
    self.conversation_history = [
      {
        "role": "system",
        "content": self._system_prompt
      }
    ]

  def _build_request_params(self) -> dict:
    is_reasoning = self.config._is_reasoning_model()

    if is_reasoning:
      messages = [
        {"role": "developer" if m["role"] == "system" else m["role"], "content": m["content"]}
        for m in self.conversation_history
      ]
    else:
      messages = self.conversation_history

    params = {
      "model": self.config.model,
      "messages": messages,
    }

    # 推論モデルの場合は max_completion_tokens を使用
    if self.config.max_completion_tokens is not None:
      params["max_completion_tokens"] = self.config.max_completion_tokens
    elif self.config.max_tokens is not None:
      params["max_tokens"] = self.config.max_tokens

    if self.config.temperature is not None:
      params["temperature"] = self.config.temperature

    if not is_reasoning:
      params["top_p"] = self.config.top_p
      params["frequency_penalty"] = self.config.frequency_penalty
      params["presence_penalty"] = self.config.presence_penalty

    return params

  @observe
  def add_message(self, messages: list[dict] | str):
    try:
      if isinstance(messages, str):
        messages = [{"role": "user", "content": messages}]
        self.conversation_history.extend(messages)

      params = self._build_request_params()
      logger.debug(f"Request params: {params}")

      response = openai.chat.completions.create(**params)
      logger.debug(f"Response: {response}")

      assistant_message = response.choices[0].message.content
      self.conversation_history.append({
        "role": "assistant",
        "content": assistant_message
      })
      get_client().update_current_trace(
        input=messages,
        output=assistant_message,
        tags=['simulator_experiment'],
      )
      return assistant_message

    except Exception as e:
      logger.error(f"Error adding message: {e}")
      return None

  def print_history(self):
    import json
    logger.info("Conversation history: ")
    logger.info(json.dumps(self.conversation_history, indent=2, ensure_ascii=False))
    logger.debug("-" * 50)

  def clear_history(self):
    self.conversation_history = [
      {
        "role": "system",
        "content": self._system_prompt
      }
    ]
    logger.info("Conversation history cleared.")
