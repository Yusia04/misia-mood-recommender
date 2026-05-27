# MISIA Mood Recommender

今の気分に寄り添う MISIA の楽曲を推薦する Streamlit Web アプリです。
Anthropic API (Claude) を利用して、入力された気分を分析し、MISIA 公式全曲リスト由来の曲データベースから 1〜3 曲を提案します。

## 主な機能

- API キーなしでも動くデモモード
- すぐ試せる入力例ボタン
- 履歴クリアボタン
- 公式全曲リスト由来の 408 曲データベース
- 推薦カードから公式ページへ移動できるリンク
- 感情ラベル候補を曲データベースから自動生成
- 入力文と Claude 出力の HTML エスケープ

## セットアップ

Python 3.9 以上が必要です。

```bash
cd misia-mood-recommender

mkdir -p ~/.venvs
python3.9 -m venv ~/.venvs/misia-mood-recommender
source ~/.venvs/misia-mood-recommender/bin/activate

python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

## 起動

```bash
cd misia-mood-recommender
source ~/.venvs/misia-mood-recommender/bin/activate
python -m streamlit run app.py
```

ブラウザで `http://localhost:8501` を開きます。

## 使い方

Claude API を使う場合は、左サイドバーに Anthropic API Key を入力します。
API キーなしで見せたい場合は、左サイドバーの「API を使わないデモモード」をオンにします。

入力例:

- `まじで萎えてる`
- `研究発表前で緊張してる`
- `今日は前向きに頑張りたい`

## ファイル構成

```text
misia-mood-recommender/
├── app.py            # Streamlit UI と推薦処理
├── song_database.py  # 曲名・感情ラベル・説明文・公式ページURL
├── requirements.txt  # 依存パッケージ
└── README.md
```

曲データは MISIA 公式サイトの全曲リストをもとに作成しています。
公式ページ: https://www.misia.jp/allsongs
