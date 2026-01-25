from openevals.simulators import run_multiturn_simulation, create_llm_simulated_user
from chat import SimpleChat, GenerationConfig


def create_app_wrapper(config: GenerationConfig | None = None):
  """
  OpenEvalsのマルチターンシミュレーションを使ったアプリケーション関数
  スレッドid単位で対話履歴を管理

  OpenEvals expects:
  - Input: ChatCompletionMessage (dict-like with role and content)
  - Output: same as input
  """
  chat_instances = {}

  def app(inputs, *, thread_id: str, **kwargs):
    if thread_id not in chat_instances:
      chat_instances[thread_id] = SimpleChat(config=config)
    chat = chat_instances[thread_id]
    content = inputs.get("content") if isinstance(inputs, dict) else inputs.content
    response_text = chat.add_message(content)

    return {
      "role": "assistant",
      "content": response_text
    }

  return app


def generate_synthetic_conversation(
    persona: str,
    scenario: str,
    max_turns: int=3,
    config: GenerationConfig | None = None
  ):
  """
  ペルソナ、シナリオ設定を利用して会話データを合成

  Args:
    persona: 仮想ユーザーのペルソナ
    scenario: 会話シチュエーション
    max_turns: 最大会話ターン数
  Returns:
    評価スコアと合わせた会話履歴
  """
  app = create_app_wrapper(config=config)

  # 仮想ユーザー
  system_prompt_simulated = f"""あなたは以下のシチュエーションにいます:
  {scenario}

  あなたの性格は以下の通りです:
  {persona}

  自然に状況を説明し、助けを求めてください。心理状態に基づきながら自然に会話を進めてください。必要に応じてフォローアップの質問をしてください。
  課題が解決されたら、感謝を述べて対話を終了してください。"""

  user = create_llm_simulated_user(
    system=system_prompt_simulated,
    model="openai:gpt-4o-mini",
  )

  result = run_multiturn_simulation(
    app=app,
    user=user,
    max_turns=max_turns,
  )

  return result
