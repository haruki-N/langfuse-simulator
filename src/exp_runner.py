from dataclasses import asdict
from dotenv import load_dotenv
load_dotenv()

from langfuse import get_client
from simulator import generate_synthetic_conversation
from chat import GenerationConfig
from logger import get_logger

logger = get_logger(__name__)

def run_dataset_experiment(dataset_name: str, experiment_name: str, config: GenerationConfig | None = None):
  langfuse = get_client()
  dataset = langfuse.get_dataset(dataset_name)
  config = config or GenerationConfig()

  logger.info(f"データセット: {dataset_name} (インスタンス件数: {len(dataset.items)})")

  def run_task(*, item, **kwargs):
    persona = item.input.get("persona")
    scenario = item.input.get("scenario")

    if not persona or not scenario:
      raise ValueError(f"Dataset item must have 'persona' and 'scenario' fields. Got: {item.input}")

    logger.info(f"Generating conversation for scenario: {scenario[:30]}...")

    result = generate_synthetic_conversation(
      persona=persona,
      scenario=scenario,
      config=config,
    )

    return {
      "trajectory": result["trajectory"],
      "num_turns": len([m for m in result["trajectory"] if m.get("role") == "user"])
    }

  result = dataset.run_experiment(
    name=experiment_name,
    description="ペルソナ・シナリオを利用したユーザーシミュレーション実験",
    task=run_task,
    metadata=asdict(config),
  )

  get_client().flush()
  logger.info("Experiment complete!")
