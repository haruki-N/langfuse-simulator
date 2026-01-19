from dotenv import load_dotenv

load_dotenv()

from langfuse.openai import openai
from langfuse import get_client, observe


class SimpleChat:
  def __init__(self, model: str = "gpt-4o-mini"):
    self.conversation_history = [
      {
        "role": "system",
        "content": "You are a helpful cooking assistant that answers questions about recipes and cooking."
      }
    ]
    self.model = model

  @observe
  def add_message(self, messages: list[dict] | str):
    try:
      if isinstance(messages, str):
        messages = [{"role": "user", "content": messages}]
        self.conversation_history.extend(messages)

      response = openai.chat.completions.create(
        model=self.model,
        messages=self.conversation_history,
        max_tokens=1000,
        temperature=0.7,
      )

      assistant_message = response.choices[0].message.content
      self.conversation_history.append({
        "role": "assistant",
        "content": assistant_message
      })
      get_client().update_current_trace(
        input=messages,
        output=assistant_message,
        tags=['simulator_experiment']
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
