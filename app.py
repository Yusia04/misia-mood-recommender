"""
MISIA Mood Recommender
今の気分に合った MISIA の楽曲を推薦する Streamlit アプリ
"""

from __future__ import annotations

import html

import streamlit as st

from song_database import SONG_DATABASE

try:
    import anthropic
except ImportError:
    anthropic = None


class _MissingAnthropicAuthenticationError(Exception):
    pass


class _MissingAnthropicAPIError(Exception):
    pass


ANTHROPIC_AUTHENTICATION_ERROR = getattr(
    anthropic, "AuthenticationError", _MissingAnthropicAuthenticationError
)
ANTHROPIC_API_ERROR = getattr(anthropic, "APIError", _MissingAnthropicAPIError)

MODEL_NAME = "claude-haiku-4-5-20251001"
EXAMPLE_MOODS = [
    "まじで萎えてる",
    "研究発表前で緊張してる",
    "今日は前向きに頑張りたい",
]

# ─────────────────────────────────────────
# ページ設定（必ず最初に呼び出す）
# ─────────────────────────────────────────
st.set_page_config(
    page_title="MISIA Mood Recommender",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "history" not in st.session_state:
    # history は {"mood": str, "html": str} のリスト
    st.session_state.history = []

# ─────────────────────────────────────────
# カスタム CSS：ダークテーマ・音楽アプリ風
# ─────────────────────────────────────────
st.markdown(
    """
<style>
/* ===== 全体背景 ===== */
.stApp {
    background:
        radial-gradient(circle at 18% 12%, rgba(125, 211, 252, 0.12), transparent 28%),
        radial-gradient(circle at 82% 4%, rgba(248, 212, 117, 0.10), transparent 24%),
        linear-gradient(135deg, #071014 0%, #111827 42%, #1c1a2e 72%, #0f172a 100%);
    color: #edf2f7;
}

/* ===== メインコンテナの横幅を広めに ===== */
.block-container {
    max-width: 900px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}

/* ===== タイトルエリア ===== */
.title-area {
    text-align: center;
    padding: 2.4rem 1rem 1.8rem;
    background: linear-gradient(180deg, rgba(125, 211, 252, 0.10) 0%, transparent 100%);
    border-bottom: 1px solid rgba(125, 211, 252, 0.18);
    margin-bottom: 2rem;
    border-radius: 0 0 8px 8px;
}

.app-title {
    font-size: 2.6rem;
    font-weight: 700;
    background: linear-gradient(90deg, #f8d475, #7dd3fc, #f0abfc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: 0;
    margin-bottom: 0.4rem;
}

.app-subtitle {
    font-size: 1.05rem;
    color: #b7c4d8;
    letter-spacing: 0;
}

.status-strip {
    display: flex;
    flex-wrap: wrap;
    gap: 0.65rem;
    justify-content: center;
    margin-top: 1.1rem;
}

.status-pill {
    background: rgba(15, 23, 42, 0.58);
    border: 1px solid rgba(148, 163, 184, 0.28);
    border-radius: 999px;
    color: #dbeafe;
    font-size: 0.82rem;
    padding: 0.32rem 0.82rem;
}

/* ===== 会話バブル ===== */
.user-bubble {
    background: linear-gradient(135deg, rgba(20, 83, 45, 0.45), rgba(15, 23, 42, 0.86));
    border: 1px solid rgba(45, 212, 191, 0.35);
    border-radius: 8px 8px 2px 8px;
    padding: 1rem 1.4rem;
    margin: 1rem 0 0.5rem auto;
    max-width: 75%;
    color: #e6fffb;
    box-shadow: 0 4px 15px rgba(20, 184, 166, 0.12);
}

.user-label {
    font-size: 0.75rem;
    color: #7dd3fc;
    margin-bottom: 0.3rem;
    font-weight: 600;
    letter-spacing: 0;
}

/* ===== 推薦カードコンテナ ===== */
.rec-container {
    margin: 1rem 0 1.5rem;
}

.emotion-tag {
    display: inline-block;
    background: rgba(248, 212, 117, 0.13);
    border: 1px solid rgba(248, 212, 117, 0.38);
    border-radius: 999px;
    padding: 0.3rem 1rem;
    font-size: 0.9rem;
    color: #fde68a;
    margin-bottom: 1.2rem;
}

.examples-label {
    color: #dbeafe;
    font-size: 0.92rem;
    font-weight: 700;
    margin: 0.4rem 0 0.6rem;
}

div[data-testid="stHorizontalBlock"] .stButton > button {
    background: rgba(15, 23, 42, 0.86) !important;
    border: 1px solid rgba(125, 211, 252, 0.48) !important;
    border-radius: 8px !important;
    color: #f8fafc !important;
    min-height: 3rem;
    box-shadow: 0 8px 18px rgba(0, 0, 0, 0.22);
}

div[data-testid="stHorizontalBlock"] .stButton > button p {
    color: #f8fafc !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
}

div[data-testid="stHorizontalBlock"] .stButton > button:hover {
    background: rgba(30, 41, 59, 0.98) !important;
    border-color: rgba(253, 230, 138, 0.75) !important;
}

div[data-testid="stHorizontalBlock"] .stButton > button:hover p {
    color: #fde68a !important;
}

/* ===== 楽曲カード ===== */
.song-card {
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.88), rgba(29, 78, 116, 0.40));
    border: 1px solid rgba(125, 211, 252, 0.24);
    border-radius: 8px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255,255,255,0.05);
    transition: border-color 0.2s;
}

.song-card:hover {
    border-color: rgba(248, 212, 117, 0.48);
}

.song-title {
    font-size: 1.3rem;
    font-weight: 700;
    color: #f8fafc;
    margin-bottom: 0.6rem;
}

.song-reason {
    font-size: 0.95rem;
    color: #c7d2fe;
    line-height: 1.65;
    margin-bottom: 0.8rem;
    padding-left: 0.5rem;
    border-left: 2px solid rgba(45, 212, 191, 0.55);
}

.song-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    align-items: center;
    color: #94a3b8;
    font-size: 0.82rem;
}

.song-link {
    color: #7dd3fc;
    text-decoration: none;
    border-bottom: 1px solid rgba(125, 211, 252, 0.45);
}

.song-link:hover {
    color: #fde68a;
    border-bottom-color: rgba(253, 230, 138, 0.65);
}

.closing-message {
    font-size: 0.92rem;
    color: #fde68a;
    font-style: italic;
    text-align: right;
    margin-top: 0.4rem;
}

/* ===== 区切り線 ===== */
.divider {
    border: none;
    border-top: 1px solid rgba(148, 163, 184, 0.18);
    margin: 2rem 0;
}

/* ===== チャット入力欄のオーバーライド ===== */
.stChatInput textarea {
    background-color: rgba(15, 23, 42, 0.95) !important;
    border: 1px solid rgba(45, 212, 191, 0.35) !important;
    color: #eff6ff !important;
    border-radius: 8px !important;
    caret-color: #fde68a !important;
}

.stChatInput textarea::placeholder {
    color: #dbeafe !important;
    opacity: 0.9 !important;
}

.stChatInput textarea:focus {
    border-color: rgba(125, 211, 252, 0.78) !important;
    box-shadow: 0 0 0 2px rgba(125, 211, 252, 0.16) !important;
}

/* ===== スピナー文字色 ===== */
.stSpinner > div {
    color: #7dd3fc !important;
}

/* ===== エラーメッセージ ===== */
.error-box {
    background: rgba(220, 38, 38, 0.1);
    border: 1px solid rgba(220, 38, 38, 0.4);
    border-radius: 8px;
    padding: 1rem 1.4rem;
    color: #fca5a5;
    margin: 1rem 0;
}

/* ===== フッター ===== */
.footer {
    text-align: center;
    color: rgba(203, 213, 225, 0.45);
    font-size: 0.78rem;
    margin-top: 3rem;
    letter-spacing: 0;
}

@media (max-width: 640px) {
    .app-title {
        font-size: 2rem;
    }

    .user-bubble {
        max-width: 100%;
    }

    .song-card {
        padding: 1.1rem 1rem;
    }
}
</style>
""",
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────
# サイドバー: API Key 設定
# ─────────────────────────────────────────
st.sidebar.header("API Key 設定")
st.sidebar.markdown(
    "このアプリは Anthropic API を使って楽曲推薦文を生成します。  \n"
    "利用するには、ご自身の Anthropic API Key を入力してください。  \n"
    "入力されたキーは保存されません。"
)
api_key = st.sidebar.text_input(
    "Anthropic API Key",
    type="password",
    placeholder="sk-ant-...",
)
demo_mode = st.sidebar.toggle(
    "API を使わないデモモード",
    value=False,
    help="発表時に API キーや通信が使えない場合でも、ローカルの曲データだけで推薦を表示します。",
)

if anthropic is None:
    demo_mode = True
    st.sidebar.warning("anthropic パッケージが未導入のため、デモモードで動作します。")

if st.sidebar.button("履歴をクリア", use_container_width=True):
    st.session_state.history = []
    st.rerun()

# ─────────────────────────────────────────
# タイトルエリア
# ─────────────────────────────────────────
st.markdown(
    f"""
<div class="title-area">
  <div class="app-title">🎵 MISIA Mood Recommender</div>
  <div class="app-subtitle">今の気分に寄り添う MISIA の楽曲をおすすめします</div>
  <div class="status-strip">
    <span class="status-pill">Claude API</span>
    <span class="status-pill">{len(SONG_DATABASE)}曲の公式ベースDB</span>
    <span class="status-pill">発表用デモ対応</span>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown('<div class="examples-label">入力例</div>', unsafe_allow_html=True)
example_cols = st.columns(len(EXAMPLE_MOODS))
example_mood = None
for col, mood_text in zip(example_cols, EXAMPLE_MOODS):
    if col.button(mood_text, use_container_width=True):
        example_mood = mood_text

# バリデーション用タイトル集合
VALID_TITLES = {song["title"] for song in SONG_DATABASE}
SONGS_BY_TITLE = {song["title"]: song for song in SONG_DATABASE}
ALL_LABELS = sorted({label for song in SONG_DATABASE for label in song["mood"]})

KEYWORD_LABELS = [
    (["萎え", "しんど", "疲", "つかれ", "つら", "辛", "だる", "無理", "病み", "落ち込"], ["癒し", "安心", "優しい", "寄り添い", "立ち直り"]),
    (["泣", "悲", "寂", "さみ", "会いたい", "失恋"], ["悲しい", "寂しい", "切ない", "泣きたい", "恋愛"]),
    (["不安", "緊張", "怖", "プレッシャー", "発表"], ["不安", "応援", "勇気", "前向き", "励まし"]),
    (["頑張", "がんば", "前向き", "やる気", "挑戦", "再開"], ["前向き", "希望", "応援", "元気", "力強い"]),
    (["恋", "好き", "愛", "大切", "家族", "感謝"], ["愛", "恋愛", "感謝", "温かい", "安心"]),
    (["夜", "眠れ", "静か", "浸り", "一人", "ひとり"], ["夜", "静か", "切ない", "寂しい", "大人"]),
    (["楽しい", "最高", "テンション", "踊", "盛り上"], ["楽しい", "元気", "高揚感", "ダンス", "明るい"]),
    (["冬", "寒", "透明"], ["冬", "静か", "透明感", "切ない"]),
]


def select_candidates(labels: list, top_n: int = 3) -> list:
    """感情ラベルとの一致数でスコアリングし、上位 top_n 曲を返す"""
    scored = []
    for song in SONG_DATABASE:
        score = len(set(labels) & set(song["mood"]))
        if score > 0:
            scored.append((score, song))
    scored.sort(key=lambda x: x[0], reverse=True)
    candidates = [s for _, s in scored[:top_n]]
    # 一致なしの場合はデータベース先頭から返す
    return candidates if candidates else SONG_DATABASE[:top_n]


def local_classify(mood: str) -> tuple[str, list]:
    """APIなしデモ用の簡易ラベル分類。"""
    labels = []
    for keywords, keyword_labels in KEYWORD_LABELS:
        if any(keyword in mood for keyword in keywords):
            labels.extend(keyword_labels)

    if not labels:
        labels = ["癒し", "希望", "前向き"]

    labels = [label for label in dict.fromkeys(labels) if label in ALL_LABELS]

    if any(word in mood for word in ["萎え", "しんど", "疲", "つかれ", "つら", "辛", "だる"]):
        emotion = "沈んだ気持ちをゆっくりほどきたい夜"
    elif any(word in mood for word in ["緊張", "不安", "発表", "プレッシャー"]):
        emotion = "胸の奥が少し張りつめている状態"
    elif any(word in mood for word in ["頑張", "前向き", "やる気", "挑戦"]):
        emotion = "もう一歩踏み出したい前向きさ"
    else:
        emotion = "今の気持ちにそっと名前をつけたい時間"

    return emotion, labels


def build_demo_recommendation(mood: str) -> dict:
    """Anthropic API を使わず、ローカルデータだけで推薦を作る。"""
    emotion, labels = local_classify(mood)
    candidates = select_candidates(labels)
    songs = [
        {
            "title": song["title"],
            "reason": f'{song["description"]} 今の「{mood}」という気分に対して、{", ".join(song["mood"][:3])} の要素が自然に重なります。',
            "source_url": song.get("source_url", ""),
            "release_title": song.get("release_title", ""),
            "release_date": song.get("release_date", ""),
        }
        for song in candidates
    ]
    return {
        "emotion": emotion,
        "songs": songs,
        "message": "デモモードでは Claude API を使わず、ローカル曲DBと簡易ラベル判定だけで推薦しています。",
    }


def get_response_text(response) -> str:
    """Anthropic SDK のレスポンスからテキストだけを取り出す。"""
    parts = []
    for block in getattr(response, "content", []):
        text = getattr(block, "text", "")
        if text:
            parts.append(text)
    return "\n".join(parts)


# ─────────────────────────────────────────
# LLM プロンプト定義
# ─────────────────────────────────────────

# Step1: 気分を感情ラベルに分類する
CLASSIFY_SYSTEM = f"""ユーザーの「今の気分」を読み取り、以下の形式だけで出力してください。

感情表現: 〇〇（詩的に短く。例：「静かに溶けていくような切なさ」）
ラベル: ラベル1, ラベル2, ...

ラベルは以下のリストから当てはまるものを選んでください（複数可）:
{", ".join(ALL_LABELS)}"""

# Step2: 選ばれた候補曲だけを渡して推薦文を書かせる
RECOMMEND_SYSTEM = """あなたは MISIA の音楽に深く精通した、感性豊かな音楽コンシェルジュです。
優しく包み込むような言葉で、ユーザーの気持ちに寄り添いながら推薦文を書いてください。
必ず提示された楽曲リストの曲名をそのまま使い、リスト外の曲名は絶対に出力しないでください。"""


def build_recommend_prompt(mood: str, candidates: list) -> str:
    """候補曲リストをプロンプトに埋め込む"""
    songs_text = "\n".join(
        f'- 曲名:「{s["title"]}」 説明:{s["description"]}' for s in candidates
    )
    return f"""ユーザーの気分: 「{mood}」

以下の楽曲リストの中から、この気分に合う順に推薦してください。
曲名は必ずリスト内のものをそのままコピーしてください（変更・追加禁止）。

楽曲リスト:
{songs_text}

出力形式（曲ごとに繰り返す）:
---SONG---
曲名: 【リスト内の曲名をそのまま記載】
理由: 【この気分にこの曲が合う理由を1〜2文で】
---END_SONG---

一言: 「ユーザーへの温かいひとこと」"""


def parse_classify(raw: str) -> tuple[str, list]:
    """Step1 の出力から感情表現とラベルリストを取り出す"""
    emotion = ""
    labels = []
    for line in raw.strip().split("\n"):
        line = line.strip()
        if line.startswith("感情表現:"):
            emotion = line.replace("感情表現:", "").strip().strip("「」")
        elif line.startswith("ラベル:"):
            labels = [l.strip() for l in line.replace("ラベル:", "").split(",") if l.strip()]
    return emotion, labels


def parse_recommend(raw: str, emotion: str) -> dict:
    """Step2 の出力を解析し、VALID_TITLES 外の曲名を除外する"""
    result = {"emotion": emotion, "songs": [], "message": ""}

    lines = raw.strip().split("\n")
    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # 楽曲ブロック開始
        if line == "---SONG---":
            song = {"title": "", "reason": ""}
            i += 1
            while i < len(lines) and lines[i].strip() != "---END_SONG---":
                sl = lines[i].strip()
                if sl.startswith("曲名:"):
                    song["title"] = sl.replace("曲名:", "").strip().lstrip("【「").rstrip("】」")
                elif sl.startswith("理由:"):
                    song["reason"] = sl.replace("理由:", "").strip()
                elif song["reason"]:
                    song["reason"] = f'{song["reason"]} {sl}'
                i += 1
            # SONG_DATABASE に存在する曲名のみ採用
            if song["title"] in VALID_TITLES:
                result["songs"].append(song)

        # 一言行
        elif line.startswith("一言:"):
            result["message"] = line.replace("一言:", "").strip().strip("「」")

        i += 1

    return result


def render_recommendation(mood: str, parsed: dict) -> str:
    """解析済みデータを HTML カード文字列に変換する"""
    html_parts = []
    safe_mood = html.escape(mood)

    # ユーザー入力バブル
    html_parts.append(
        f'<div class="user-bubble">'
        f'<div class="user-label">💬 あなたの気分</div>'
        f'{safe_mood}'
        f'</div>'
    )

    # 推薦コンテナ開始
    html_parts.append('<div class="rec-container">')

    # 感情タグ
    if parsed["emotion"]:
        safe_emotion = html.escape(parsed["emotion"])
        html_parts.append(
            f'<div class="emotion-tag">🔮 {safe_emotion}</div>'
        )

    # 楽曲カード
    for song in parsed["songs"]:
        metadata = SONGS_BY_TITLE.get(song["title"], {})
        source_url = song.get("source_url") or metadata.get("source_url", "")
        release_title = song.get("release_title") or metadata.get("release_title", "")
        release_date = song.get("release_date") or metadata.get("release_date", "")
        safe_title = html.escape(song["title"])
        safe_reason = html.escape(song["reason"])
        safe_source_url = html.escape(source_url, quote=True)
        release_bits = [bit for bit in [release_date, release_title] if bit]
        safe_release = html.escape(" / ".join(release_bits))
        meta_html = ""
        if source_url or release_bits:
            link_html = ""
            if source_url:
                link_html = (
                    f'<a class="song-link" href="{safe_source_url}" '
                    f'target="_blank" rel="noopener noreferrer">公式ページ</a>'
                )
            meta_html = f'<div class="song-meta">{safe_release} {link_html}</div>'
        html_parts.append(
            f'<div class="song-card">'
            f'<div class="song-title">🎵 {safe_title}</div>'
            f'<div class="song-reason">{safe_reason}</div>'
            f'{meta_html}'
            f'</div>'
        )

    # 一言メッセージ
    if parsed["message"]:
        safe_message = html.escape(parsed["message"])
        html_parts.append(
            f'<div class="closing-message">✨ {safe_message}</div>'
        )

    html_parts.append("</div>")  # rec-container 閉じ
    html_parts.append('<hr class="divider">')

    return "\n".join(html_parts)


def generate_with_claude(mood_input: str, client) -> dict:
    """Claude API で感情分類と推薦文生成を行う。"""
    r1 = client.messages.create(
        model=MODEL_NAME,
        max_tokens=200,
        system=CLASSIFY_SYSTEM,
        messages=[{"role": "user", "content": f"今の気分: {mood_input}"}],
    )
    emotion, labels = parse_classify(get_response_text(r1))

    candidates = select_candidates(labels)
    r2 = client.messages.create(
        model=MODEL_NAME,
        max_tokens=800,
        system=RECOMMEND_SYSTEM,
        messages=[{"role": "user", "content": build_recommend_prompt(mood_input, candidates)}],
    )
    parsed = parse_recommend(get_response_text(r2), emotion)

    if not parsed["songs"]:
        parsed["songs"] = [
            {"title": candidate["title"], "reason": candidate["description"]}
            for candidate in candidates
        ]
        parsed["message"] = "あなたの気分に合う曲を選びました。"

    return parsed


# ─────────────────────────────────────────
# 過去の会話履歴を表示
# ─────────────────────────────────────────
for entry in st.session_state.history:
    st.markdown(entry["html"], unsafe_allow_html=True)

# ─────────────────────────────────────────
# API Key 未入力時の案内 / 入力済みの場合は推薦処理
# ─────────────────────────────────────────
if not api_key and not demo_mode:
    st.info("左のサイドバーに Anthropic API Key を入力すると、楽曲推薦を開始できます。")
else:
    client = None if demo_mode else anthropic.Anthropic(api_key=api_key)

    # ─────────────────────────────────────────
    # チャット入力
    # ─────────────────────────────────────────
    mood_input = st.chat_input(
        "今の気分を教えてください（例：疲れた、前向きになりたい、夜に浸りたい）"
    )

    # ─────────────────────────────────────────
    # 入力があったら推薦処理を実行
    # ─────────────────────────────────────────
    selected_mood = example_mood or mood_input
    if selected_mood:
        mood_input = selected_mood.strip()
        if not mood_input:
            st.warning("気分を入力してください。")
        else:
            with st.spinner("🎵 MISIA の楽曲を探しています…"):
                try:
                    if demo_mode:
                        parsed = build_demo_recommendation(mood_input)
                    else:
                        parsed = generate_with_claude(mood_input, client)

                    # HTML に変換して履歴に追加
                    html = render_recommendation(mood_input, parsed)
                    st.session_state.history.append({"mood": mood_input, "html": html})

                    # 画面に表示
                    st.markdown(html, unsafe_allow_html=True)

                except ANTHROPIC_AUTHENTICATION_ERROR:
                    st.markdown(
                        '<div class="error-box">🔑 API キーが無効です。正しい Anthropic API Key をサイドバーに入力してください。</div>',
                        unsafe_allow_html=True,
                    )
                except ANTHROPIC_API_ERROR as e:
                    st.markdown(
                        f'<div class="error-box">⚠️ API エラーが発生しました：{e}</div>',
                        unsafe_allow_html=True,
                    )
                except Exception as e:
                    st.markdown(
                        f'<div class="error-box">❌ 予期しないエラーが発生しました：{e}</div>',
                        unsafe_allow_html=True,
                    )

# ─────────────────────────────────────────
# フッター
# ─────────────────────────────────────────
st.markdown(
    '<div class="footer">MISIA Mood Recommender — powered by Claude &amp; Streamlit</div>',
    unsafe_allow_html=True,
)
