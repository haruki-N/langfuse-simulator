from dataclasses import dataclass, asdict, field
from dotenv import load_dotenv

load_dotenv()

from langfuse.openai import openai
from langfuse import get_client, observe
from logger import get_logger

logger = get_logger(__name__)


DEFAULT_SYSTEM_PROMPT = "You are a helpful cooking assistant that answers questions about recipes and cooking."


@dataclass
class GenerationConfig:
  model: str = "gpt-4o-mini"
  max_tokens: int | None = None
  temperature: float | None = None
  top_p: float = 1.0
  frequency_penalty: float = 0.0
  presence_penalty: float = 0.0
  # Langfuse Prompt Management 用設定
  prompt_name: str | None = None
  prompt_variables: dict = field(default_factory=dict)


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

  @observe
  def add_message(self, messages: list[dict] | str):
    try:
      if isinstance(messages, str):
        messages = [{"role": "user", "content": messages}]
        self.conversation_history.extend(messages)

      response = openai.chat.completions.create(
        model=self.config.model,
        messages=self.conversation_history,
        max_tokens=self.config.max_tokens,
        temperature=self.config.temperature,
        top_p=self.config.top_p,
        frequency_penalty=self.config.frequency_penalty,
        presence_penalty=self.config.presence_penalty,
      )

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
