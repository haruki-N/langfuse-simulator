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

    langfuse.create_dataset_item(
      dataset_name="simulated-conversations",
      input={
        "persona": "パン作りに初挑戦する好奇心旺盛な大学生。科学的な理由を知りたがり、なぜその手順が必要なのか質問が多い。失敗を恐れつつも学ぶ意欲が高い。",
        "scenario": "初めて手ごねパンを作ろうとしている。生地をこねて1時間発酵させたが、全く膨らんでいない。室温は約18度。イーストは開封後3ヶ月経過したもの。原因を知りたいし、今からリカバリーできるか知りたい。"
      }
    )

    langfuse.create_dataset_item(
      dataset_name="simulated-conversations",
      input={
        "persona": "健康を気にする50代の主婦。家族に糖尿病の人がいるため、糖質を抑えたいが味は妥協したくない。代替食材についての知識を求めている。",
        "scenario": "娘の誕生日にチーズケーキを作りたいが、糖質を抑えたレシピを探している。通常のレシピでは砂糖150g、小麦粉大さじ2を使う。ラカントとアーモンドプードルは持っている。味や食感がどう変わるか、分量の調整が必要か知りたい。"
      }
    )

    langfuse.create_dataset_item(
      dataset_name="simulated-conversations",
      input={
        "persona": "一人暮らしを始めたばかりの新社会人。料理経験はほぼゼロで、基本的な調理用語も分からないことがある。節約しながら自炊を続けたいと思っている。",
        "scenario": "スーパーで鶏むね肉が安かったので1kg買ったが、どう保存・調理すればいいか分からない。冷蔵庫は小さく冷凍スペースも限られている。今週中に使い切りたいが、毎日同じ味だと飽きそう。簡単で飽きない調理法のバリエーションを知りたい。"
      }
    )

    print(f"Dataset items created successfully")

  except Exception as e:
    print(f"Error creating dataset item: {e}")
    return None

  return dataset
