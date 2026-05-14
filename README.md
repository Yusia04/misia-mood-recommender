# 🎵 MISIA Mood Recommender

今の気分に寄り添う MISIA の楽曲を推薦する Streamlit Web アプリです。  
Anthropic API (Claude) を利用して、入力された気分を分析し 1〜3 曲をカード形式で提案します。

---

## セットアップ方法

### 1. リポジトリをクローン／ディレクトリへ移動

```bash
cd my-app
```

### 2. 依存パッケージをインストール

**uv を使う場合（推奨）**

```bash
uv add streamlit anthropic python-dotenv
```

**pip を使う場合**

```bash
pip install -r requirements.txt
```

---

## API キー設定方法

1. `.env.example` をコピーして `.env` を作成します。

```bash
cp .env.example .env
```

2. `.env` を開き、`ANTHROPIC_API_KEY` に取得したキーを貼り付けます。

```dotenv
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

> API キーは [Anthropic Console](https://console.anthropic.com/settings/keys) で取得できます。

---

## 起動方法

```bash
streamlit run app.py
```

ブラウザで `http://localhost:8501` が自動的に開きます。

---

## 使い方

1. 画面下部の入力欄に「今の気分」を日本語で入力します  
   例：`疲れた`、`前向きになりたい`、`夜に浸りたい`
2. Enter を押すと MISIA の楽曲を 1〜3 曲推薦します
3. 会話履歴は画面上に残ります（ブラウザをリロードするとリセットされます）

---

## ファイル構成

```
my-app/
├── app.py            # メインアプリ
├── requirements.txt  # 依存パッケージ一覧
├── .env.example      # 環境変数サンプル
└── README.md         # このファイル
```

---

## 注意事項

- `.env` ファイルは Git にコミットしないでください（`.gitignore` に追加推奨）
- 使用モデルは `claude-haiku-4-5`（低コスト・高速）です。変更する場合は `app.py` の `model=` を編集してください
