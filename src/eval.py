import json
from dotenv import load_dotenv
from pathlib import Path
load_dotenv()

from langfuse import get_client
from langfuse.openai import openai
from dataclasses import dataclass

class ObsExtractor():
  def __init__(self, dataset_name: str="simulated-conversations"):
    self.dataset_name = dataset_name
    self.langfuse = get_client()

  def fetch_latest_run(self):
    runs = self.langfuse.get_dataset_runs(dataset_name=self.dataset_name, page=1, limit=1)
    if runs.data:
      latest_run = self.langfuse.get_dataset_run(dataset_name=self.dataset_name, run_name=runs.data[0].name)
      return latest_run
    return None

  def get_observations_for_eval(self):
    observations = []
    latest_run = self.fetch_latest_run()
    dataset_run_items = latest_run.dataset_run_items

    for run_item in dataset_run_items:
      trace_id = run_item.trace_id
      related_trace = self.langfuse.api.trace.get(trace_id=trace_id)
      observation = related_trace.observations[0]
      observations.append({
        "trace_id": observation.trace_id,
        "input": observation.input,
        "output": observation.output
      })

    return observations

  def submit_score(
    self,
    trace_id: str,
    name: str,
    score: int,
    comment: str | None = None
  ):
    """
    評価結果をLangfuseにスコアとして登録する

    Args:
      trace_id: 評価対象のtrace ID
      name: スコア名（例: "adaptability", "actionability"）
      score: スコア値（1-5）
      comment: コメント（評価理由など）
    """
    self.langfuse.create_score(
      trace_id=trace_id,
      name=name,
      value=score,
      comment=comment
    )

@dataclass
class EvalData:
  persona: str
  scenario: str
  trajectory: list[dict]

  def format_trajectory(self) -> str:
    formatted = []
    for msg in self.trajectory:
      role = msg.get("role", "unknown")
      content = msg.get("content", "")
      formatted.append(f"[{role}]: {content}")
    return "\n\n".join(formatted)


def eval_llm_as_a_judge(
  system_prompt: str,
  user_prompt_template: str,
  eval_data: EvalData,
  model: str = "gpt-5.1"
) -> dict:
  """
  LLM-as-a-judgeによる評価を実行する

  Args:
    system_prompt: 評価基準・ルーブリックを含むsystemプロンプト
    user_prompt_template: 入力データフォーマットのテンプレート（{{persona}}, {{scenario}}, {{trajectory}}を含む）
    eval_data: 評価対象のデータ（EvalData型）
    model: 使用するモデル名

  Returns:
    評価結果のdict（score, reasoning, その他評価項目固有のフィールド）
  """
  user_prompt = user_prompt_template.replace("{{persona}}", eval_data.persona)
  user_prompt = user_prompt.replace("{{scenario}}", eval_data.scenario)
  user_prompt = user_prompt.replace("{{trajectory}}", eval_data.format_trajectory())

  response = openai.chat.completions.create(
    model=model,
    messages=[
      {"role": "system", "content": system_prompt},
      {"role": "user", "content": user_prompt}
    ],
    temperature=0.0,
    response_format={"type": "json_object"}
  )

  result_text = response.choices[0].message.content

  try:
    result = json.loads(result_text)
    # scoreをintに変換（文字列やfloatで返される可能性があるため）
    if result.get("score") is not None:
      result["score"] = int(result["score"])
  except json.JSONDecodeError:
    result = {
      "score": None,
      "reasoning": "Failed to parse JSON response",
      "raw_response": result_text
    }
  except (ValueError, TypeError):
    # int変換に失敗した場合
    result["score"] = None

  return result


def load_prompt(prompt_path: str) -> str:
  with open(prompt_path, "r", encoding="utf-8") as f:
    return f.read()


def observation_to_eval_data(observation: dict) -> EvalData:
  """
  ObsExtractorから取得したobservationをEvalDataに変換する

  Args:
    observation: ObsExtractor.get_observations_for_eval()で取得したデータ
      - input: {"persona": str, "scenario": str}
      - output: {"trajectory": list[dict], "num_turns": int}

  Returns:
    EvalData
  """
  input_data = observation.get("input", {})
  output_data = observation.get("output", {})

  return EvalData(
    persona=input_data.get("persona", ""),
    scenario=input_data.get("scenario", ""),
    trajectory=output_data.get("trajectory", [])
  )


if __name__ == "__main__":
  prompt_dir = Path(__file__).parent.parent / "prompt"

  # システムプロンプト（評価基準・ルーブリック）
  system_prompts = {
    "adaptability": load_prompt(prompt_dir / "eval_adaptability.md"),
    "actionability": load_prompt(prompt_dir / "eval_actionability.md"),
    "coherence_naturalness": load_prompt(prompt_dir / "eval_coherence_naturalness.md"),
  }

  # 共通のユーザープロンプト（入力データフォーマット）
  user_prompt_template = load_prompt(prompt_dir / "eval_input_format.md")

  extractor = ObsExtractor()
  observations = extractor.get_observations_for_eval()

  print(f"取得したデータ数: {len(observations)}")

  for i, obs in enumerate(observations):
    trace_id = obs["trace_id"]
    print(f"\n{'='*60}")
    print(f"対話 {i + 1} (trace_id: {trace_id})")
    print('='*60)

    eval_data = observation_to_eval_data(obs)
    print(f"ペルソナ: {eval_data.persona[:50]}...")
    print(f"ターン数: {len(eval_data.trajectory) / 2}")

    for eval_name, system_prompt in system_prompts.items():
      print(f"\n--- {eval_name} ---")
      result = eval_llm_as_a_judge(
        system_prompt=system_prompt,
        user_prompt_template=user_prompt_template,
        eval_data=eval_data
      )

      score = result.get("score")
      reasoning = result.get("reasoning", "")

      print(f"スコア: {score}")
      print(f"理由: {reasoning[:100]}...")

      # Langfuseにスコアを登録
      if score is not None:
        extractor.submit_score(
          trace_id=trace_id,
          name=eval_name,
          score=score,
          comment=reasoning
        )
        print(f"✓ Langfuseに登録完了")

  print(f"\n{'='*60}")
  print("すべての評価が完了しました")
