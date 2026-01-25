from dotenv import load_dotenv
load_dotenv()

from langfuse import get_client
from setup_dataset import create_dataset
from exp_runner import run_dataset_experiment
from chat import GenerationConfig
from logger import get_logger

logger = get_logger(__name__)

langfuse = get_client()


def main():
    DATASET = "simulated-conversations"

    # agent config (not simulated user)
    config = GenerationConfig(
        model="gpt-5",
        max_tokens=1000,
        temperature=0.7,
        prompt_name="system prompt for simulated-user experiment"
    )
    EXP = f"{config.model} with {config.prompt_name}"

    # setup dataset
    try:
        dataset = langfuse.get_dataset(name=DATASET)
        logger.info(f"Dataset '{dataset.name}' already exists, skipping creation")
    except Exception:
        logger.info("Dataset not found, creating...")
        create_dataset()

    # run exp
    run_dataset_experiment(
        dataset_name=DATASET,
        experiment_name=EXP,
        config=config
    )
    logger.info("Experiments done successfully! Eval results with eval.py if you needed")

if __name__ == "__main__":
    main()
