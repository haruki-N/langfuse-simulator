# langfuse-simulator

LLMのマルチターン対話性能を評価するためのシミュレーション・評価パイプライン。
OpenEvalsを使用して合成対話を生成し、LLM-as-a-judgeで品質を評価、結果をLangfuseに記録します。

## ディレクトリ構成

```
langfuse-simulator/
├── src/
│   ├── main.py           # エントリーポイント（データセット作成〜実験実行）
│   ├── setup_dataset.py  # Langfuseデータセットの作成
│   ├── simulator.py      # OpenEvalsを使った対話シミュレーション
│   ├── exp_runner.py     # データセットに対する実験実行
│   ├── eval.py           # LLM-as-a-judgeによる評価
│   ├── chat.py           # シンプルなチャットクラス（評価対象のアプリ）
│   └── debug.py          # デバッグ用
├── prompt/
│   ├── eval_adaptability.md        # 適応性評価のルーブリック
│   ├── eval_actionability.md       # 実行可能性評価のルーブリック
│   ├── eval_coherence_naturalness.md # 一貫性・自然さ評価のルーブリック
│   └── eval_input_format.md        # 共通の入力フォーマット
├── .env                  # 環境変数（OPENAI_API_KEY, LANGFUSE_*）
├── pyproject.toml
└── README.md
```

## セットアップ

```bash
# 依存関係のインストール
uv sync

# 環境変数の設定
cp .env.example .env
# .env に以下を設定:
# OPENAI_API_KEY=sk-...
# LANGFUSE_PUBLIC_KEY=pk-...
# LANGFUSE_SECRET_KEY=sk-...
# LANGFUSE_HOST=https://cloud.langfuse.com (optional)
```

## 使い方

### 1. データセット作成〜対話シミュレーション実行

```bash
uv run python src/main.py
```

これにより以下が実行されます：
1. Langfuseにデータセット `simulated-conversations` を作成（存在しない場合）
2. データセットの各アイテム（ペルソナ・シナリオ）に対して対話をシミュレーション
3. 結果をLangfuseに記録

### 2. LLM-as-a-judgeによる評価

```bash
uv run python src/eval.py
```

最新の実験結果に対して以下の3項目で評価を実行し、スコアをLangfuseに登録します：

| 評価項目 | 説明 |
|----------|------|
| **Adaptability** | ユーザーの感情・理解度・緊急度に応じた応答調整 |
| **Actionability** | 提案の具体性・実行可能性 |
| **Coherence & Naturalness** | 対話の一貫性・自然さ |

## 処理フロー

```
[データセット作成] → [対話シミュレーション] → [LLM-as-a-judge評価] → [Langfuse記録]
   setup_dataset.py      simulator.py              eval.py
                         exp_runner.py
```

## 評価プロンプトのカスタマイズ

`prompt/` ディレクトリ内のMarkdownファイルを編集することで、評価基準をカスタマイズできます。

- **システムプロンプト**（`eval_*.md`）: 評価観点・ルーブリック・出力形式を定義
- **ユーザープロンプト**（`eval_input_format.md`）: 評価対象データの入力フォーマット

新しい評価項目を追加する場合：
1. `prompt/eval_<新項目>.md` を作成
2. `eval.py` の `system_prompts` に追加

## 主要クラス・関数

### `eval.py`

```python
# 評価データ構造
@dataclass
class EvalData:
    persona: str
    scenario: str
    trajectory: list[dict]

# LLM-as-a-judge評価の実行
def eval_llm_as_a_judge(
    system_prompt: str,
    user_prompt_template: str,
    eval_data: EvalData,
    model: str = "gpt-5.1"
) -> dict:
    # Returns: {"score": int, "reasoning": str, ...}

# Langfuseからの観測データ取得・スコア登録
class ObsExtractor:
    def get_observations_for_eval() -> list[dict]
    def submit_score(trace_id, name, score, comment)
```

### `simulator.py`

```python
# 合成対話の生成
def generate_synthetic_conversation(
    persona: str,
    scenario: str,
    max_turns: int = 3
) -> dict:
    # Returns: {"trajectory": [...], "num_turns": int}
```

## 依存関係

- `langfuse`: トレーシング・データセット管理
- `openai`: LLM API
- `openevals`: マルチターンシミュレーション
- `python-dotenv`: 環境変数管理
