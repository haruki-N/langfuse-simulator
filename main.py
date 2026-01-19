from dotenv import load_dotenv
load_dotenv()

from langfuse import get_client
from setup_dataset import create_dataset
from exp_runner import run_dataset_experiment

langfuse = get_client()


def main():
    DATASET = "simulated-conversations"
    EXP = "シミュレーション実験-v0"
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
        experiment_name=EXP
    )

if __name__ == "__main__":
    main()
