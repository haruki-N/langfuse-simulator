from dotenv import load_dotenv
load_dotenv()

from langfuse import get_client
from setup_dataset import create_dataset

langfuse = get_client()


def main():
    # setup dataset
    try:
        dataset = langfuse.get_dataset(name="simulated-conversations")
        print(f"Dataset '{dataset.name}' already exists, skipping creation")
    except Exception:
        print("Dataset not found, creating...")
        create_dataset()

if __name__ == "__main__":
    main()
