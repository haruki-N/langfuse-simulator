from dotenv import load_dotenv
load_dotenv()

from langfuse import get_client
from setup_dataset import create_dataset
from exp_runner import run_dataset_experiment
from chat import GenerationConfig

langfuse = get_client()


def main():
    DATASET = "simulated-conversations"
    EXP = "simulated-exp-v0"

    # agent config (not simulated user)
    config = GenerationConfig(
        model="gpt-4o-mini",
        max_tokens=1000,
        temperature=0.7,
    )

    # setup dataset
    try:
        dataset = langfuse.get_dataset(name=DATASET)
        print(f"Dataset '{dataset.name}' already exists, skipping creation")
    except Exception:
        print("Dataset not found, creating...")
        create_dataset()

    # run exp
    run_dataset_experiment(
        dataset_name=DATASET,
        experiment_name=EXP,
        config=config
    )
    print("Experiments done successfully! Eval results with eval.py if you needed")

if __name__ == "__main__":
    main()
