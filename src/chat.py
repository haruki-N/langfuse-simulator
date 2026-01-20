from dataclasses import dataclass, asdict
from dotenv import load_dotenv

load_dotenv()

from langfuse.openai import openai
from langfuse import get_client, observe


@dataclass
class GenerationConfig:
  model: str = "gpt-4o-mini"
  max_tokens: int = 1000
  temperature: float = 0.7
  top_p: float = 1.0
  frequency_penalty: float = 0.0
  presence_penalty: float = 0.0


class SimpleChat:
  def __init__(self, config: GenerationConfig | None = None):
    self.conversation_history = [
      {
        "role": "system",
        "content": "You are a helpful cooking assistant that answers questions about recipes and cooking."
      }
    ]
    self.config = config or GenerationConfig()

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
        metadata=asdict(self.config)
      )
      return assistant_message

    except Exception as e:
      print(f"Error adding message: {e}")
      return None

  def print_history(self):
    import json
    print("Conversation history: ")
    print(json.dumps(self.conversation_history, indent=2, ensure_ascii=False))
    print("-" * 50)

  def clear_history(self):
    self.conversation_history = [
      {
        "role": "system",
        "content": "You are a helpful cooking assistant that answers questions about recipes and cooking."
      }
    ]
    print("Conversation history cleared.")
