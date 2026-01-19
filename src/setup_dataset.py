from langfuse import get_client

langfuse = get_client()

def create_dataset():
  try:
    dataset = langfuse.create_dataset(
    name='simulated-conversations',
    description='ペルソナとシナリオを設定した合成データ'
  )
    print(f"Dataset created successfully: {dataset}")

  except Exception as e:
    print(f"Error creating dataset: {e}")
    return None

  try:
    langfuse.create_dataset_item(
      dataset_name="simulated-conversations",
      input={
        "persona": "初めてのディナーパーティーを18時30分に開く緊張気味の主催者。複数の料理を同時に作ることに不安を感じており、段取りに不慣れで、安心感を求めて何度も確認の質問をする。",
        "scenario": "現在16時30分。調理が必要なのは：ローストチキン（1時間半）、ローストした野菜（45分）、マッシュポテト（30分）、グレイビーソース。オーブンは1台しかなく、すべてが時間通りに仕上がるか心配している。"
      }
    )

    langfuse.create_dataset_item(
      dataset_name="simulated-conversations",
      input={
        "persona": "ビーフストロガノフのソースにサワークリームを加えたら分離してしまった、ストレスを抱えた料理人。お客さんが20分後に到着する。焦っていて、すぐに実行できる現実的な解決策を求めている。",
        "scenario": "熱いフライパンにサワークリームを入れたら分離してしまい、ソースがざらざらで分離した状態になった。手元には生クリーム、バター、小麦粉、ビーフブイヨン、追加のサワークリームがある。修復できるのか、それとも別のプランが必要なのかを知りたい。"
      }
    )
    print(f"Dataset items created successfully")

  except Exception as e:
    print(f"Error creating dataset item: {e}")
    return None

  return dataset
