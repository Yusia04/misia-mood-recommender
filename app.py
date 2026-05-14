"""
MISIA Mood Recommender
今の気分に合った MISIA の楽曲を推薦する Streamlit アプリ
"""

import streamlit as st
import anthropic

# ─────────────────────────────────────────
# ページ設定（必ず最初に呼び出す）
# ─────────────────────────────────────────
st.set_page_config(
    page_title="MISIA Mood Recommender",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────
# カスタム CSS：ダークテーマ・音楽アプリ風
# ─────────────────────────────────────────
st.markdown(
    """
<style>
/* ===== 全体背景 ===== */
.stApp {
    background: linear-gradient(135deg, #0d0d1a 0%, #0f0c29 40%, #1a0a2e 70%, #0d1b2a 100%);
    color: #e8e0f0;
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
    padding: 2.5rem 1rem 2rem;
    background: linear-gradient(180deg, rgba(106, 17, 203, 0.15) 0%, transparent 100%);
    border-bottom: 1px solid rgba(150, 100, 255, 0.2);
    margin-bottom: 2rem;
    border-radius: 0 0 20px 20px;
}

.app-title {
    font-size: 2.6rem;
    font-weight: 700;
    background: linear-gradient(90deg, #a78bfa, #818cf8, #c084fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: 0.05em;
    margin-bottom: 0.4rem;
}

.app-subtitle {
    font-size: 1.05rem;
    color: #9ca3c8;
    letter-spacing: 0.08em;
}

/* ===== 会話バブル ===== */
.user-bubble {
    background: linear-gradient(135deg, #2d1b6b, #1e1654);
    border: 1px solid rgba(139, 92, 246, 0.4);
    border-radius: 16px 16px 4px 16px;
    padding: 1rem 1.4rem;
    margin: 1rem 0 0.5rem auto;
    max-width: 75%;
    color: #e0d7f7;
    box-shadow: 0 4px 15px rgba(139, 92, 246, 0.15);
}

.user-label {
    font-size: 0.75rem;
    color: #a78bfa;
    margin-bottom: 0.3rem;
    font-weight: 600;
    letter-spacing: 0.05em;
}

/* ===== 推薦カードコンテナ ===== */
.rec-container {
    margin: 1rem 0 1.5rem;
}

.emotion-tag {
    display: inline-block;
    background: rgba(99, 102, 241, 0.2);
    border: 1px solid rgba(99, 102, 241, 0.5);
    border-radius: 20px;
    padding: 0.3rem 1rem;
    font-size: 0.9rem;
    color: #c4b5fd;
    margin-bottom: 1.2rem;
}

/* ===== 楽曲カード ===== */
.song-card {
    background: linear-gradient(135deg, rgba(30, 20, 60, 0.8), rgba(20, 30, 60, 0.8));
    border: 1px solid rgba(129, 140, 248, 0.3);
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255,255,255,0.05);
    transition: border-color 0.2s;
}

.song-card:hover {
    border-color: rgba(167, 139, 250, 0.5);
}

.song-title {
    font-size: 1.3rem;
    font-weight: 700;
    color: #e2d9f3;
    margin-bottom: 0.6rem;
}

.song-reason {
    font-size: 0.95rem;
    color: #a5b4d4;
    line-height: 1.65;
    margin-bottom: 0.8rem;
    padding-left: 0.5rem;
    border-left: 2px solid rgba(139, 92, 246, 0.5);
}

.closing-message {
    font-size: 0.92rem;
    color: #c084fc;
    font-style: italic;
    text-align: right;
    margin-top: 0.4rem;
}

/* ===== 区切り線 ===== */
.divider {
    border: none;
    border-top: 1px solid rgba(100, 80, 180, 0.2);
    margin: 2rem 0;
}

/* ===== チャット入力欄のオーバーライド ===== */
.stChatInput textarea {
    background-color: rgba(20, 15, 45, 0.9) !important;
    border: 1px solid rgba(139, 92, 246, 0.4) !important;
    color: #e0d7f7 !important;
    border-radius: 12px !important;
}

/* ===== スピナー文字色 ===== */
.stSpinner > div {
    color: #a78bfa !important;
}

/* ===== エラーメッセージ ===== */
.error-box {
    background: rgba(220, 38, 38, 0.1);
    border: 1px solid rgba(220, 38, 38, 0.4);
    border-radius: 10px;
    padding: 1rem 1.4rem;
    color: #fca5a5;
    margin: 1rem 0;
}

/* ===== フッター ===== */
.footer {
    text-align: center;
    color: rgba(150, 130, 200, 0.4);
    font-size: 0.78rem;
    margin-top: 3rem;
    letter-spacing: 0.1em;
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

# ─────────────────────────────────────────
# タイトルエリア
# ─────────────────────────────────────────
st.markdown(
    """
<div class="title-area">
  <div class="app-title">🎵 MISIA Mood Recommender</div>
  <div class="app-subtitle">今の気分に寄り添う MISIA の楽曲をおすすめします</div>
</div>
""",
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────
# 会話履歴を session_state で管理
# ─────────────────────────────────────────
if "history" not in st.session_state:
    # history は {"mood": str, "html": str} のリスト
    st.session_state.history = []

# ─────────────────────────────────────────
# MISIA 楽曲データベース（推薦はここからのみ）
# ─────────────────────────────────────────
SONG_DATABASE = [
    {"title": "Everything", "mood": ["癒し", "恋愛", "安心", "切ない"],
     "description": "包み込むようなバラードで、疲れた心や切ない気持ちに寄り添う曲。"},
    {"title": "アイノカタチ feat. HIDE(GReeeeN)", "mood": ["愛", "感謝", "家族", "温かい"],
     "description": "大切な人への感謝や愛情を感じたい時に合う曲。"},
    {"title": "逢いたくていま", "mood": ["悲しい", "切ない", "喪失", "泣きたい"],
     "description": "会いたい人を想う気持ちや深い切なさに寄り添うバラード。"},
    {"title": "明日へ", "mood": ["希望", "前向き", "応援", "立ち直り"],
     "description": "つらい状況から少しずつ前を向きたい時に背中を押してくれる曲。"},
    {"title": "陽のあたる場所", "mood": ["元気", "前向き", "明るい", "希望"],
     "description": "明るく前向きな気持ちになりたい時に合う曲。"},
    {"title": "BELIEVE", "mood": ["勇気", "前向き", "自信", "力強い"],
     "description": "自分を信じて進みたい時に合う力強い曲。"},
    {"title": "眠れぬ夜は君のせい", "mood": ["恋愛", "切ない", "夜", "寂しい"],
     "description": "夜に恋しさや寂しさを感じる時に合う曲。"},
    {"title": "果てなく続くストーリー", "mood": ["壮大", "希望", "人生", "前向き"],
     "description": "人生を前向きに捉えたい時に合う壮大なバラード。"},
    {"title": "忘れない日々", "mood": ["思い出", "切ない", "恋愛", "静か"],
     "description": "過去の大切な記憶に浸りたい時に合う曲。"},
    {"title": "オルフェンズの涙", "mood": ["祈り", "悲しみ", "壮大", "深い"],
     "description": "深い悲しみや祈りの気持ちに寄り添う重厚な曲。"},
    {"title": "つつみ込むように...", "mood": ["元気", "ソウルフル", "前向き", "高揚感"],
     "description": "エネルギッシュで温かい歌声が前向きな気持ちを引き出してくれる代表曲。"},
    {"title": "ラストダンスは私に", "mood": ["大人", "夜", "ジャズ", "静か", "切ない"],
     "description": "夜に静かに感情へ浸りたい時に合う、大人っぽくムーディな楽曲。"},
    {"title": "THE GLORY DAY", "mood": ["祝福", "感動", "希望", "壮大", "前向き"],
     "description": "スケール感のあるサウンドが、特別な瞬間や前向きな気持ちをさらに高めてくれる曲。"},
    {"title": "INTO THE LIGHT", "mood": ["ダンス", "高揚感", "元気", "クラブ", "楽しい"],
     "description": "気分を一気に切り替えたい時や、テンションを上げたい時にぴったりのダンスナンバー。"},
    {"title": "Escape", "mood": ["解放", "夜", "気分転換", "かっこいい", "都会"],
     "description": "閉塞感から抜け出したい時に、クールな空気感で背中を押してくれる楽曲。"},
    {"title": "BACK BLOCKS", "mood": ["自信", "力強い", "クール", "夜", "都会"],
     "description": "自分らしく前へ進みたい時に合う、都会的で力強い雰囲気の曲。"},
    {"title": "LAILA", "mood": ["情熱", "大人", "夜", "異国感", "高揚感"],
     "description": "情熱的でミステリアスな雰囲気に浸りたい夜に合う一曲。"},
    {"title": "Sea of Dreams", "mood": ["夢", "癒し", "希望", "穏やか", "優しい"],
     "description": "心をふっと軽くしてくれるような、夢と希望に満ちた優しい楽曲。"},
    {"title": "飛び方を忘れた小さな鳥", "mood": ["不安", "孤独", "再出発", "優しい", "励まし"],
     "description": "自信をなくした時に、優しく寄り添いながら前を向かせてくれる曲。"},
    {"title": "名前のない空を見上げて", "mood": ["静か", "祈り", "空", "切ない", "希望"],
     "description": "静かな時間の中で、自分の気持ちと向き合いたい時に合うバラード。"},
    {"title": "冬のエトランジェ", "mood": ["冬", "寂しい", "恋愛", "静か", "切ない"],
     "description": "冬の夜のような透明感と寂しさを感じさせる、大人っぽい楽曲。"},
    {"title": "太陽の地図", "mood": ["旅", "希望", "前向き", "明るい", "元気"],
     "description": "新しい場所へ踏み出したい時に、明るく背中を押してくれる曲。"},
    {"title": "星のように...", "mood": ["夜", "優しい", "祈り", "切ない", "温かい"],
     "description": "大切な人を想いながら、静かな夜に聴きたくなる優しいバラード。"},
    {"title": "幸せをフォーエバー", "mood": ["幸せ", "愛", "祝福", "結婚", "温かい"],
     "description": "幸せな気持ちや大切な人への愛情を感じたい時にぴったりの楽曲。"},
    {"title": "白い季節", "mood": ["冬", "恋愛", "静か", "透明感", "切ない"],
     "description": "冬の澄んだ空気のような切なさと美しさを感じられる曲。"},
    {"title": "あなたにスマイル:)", "mood": ["笑顔", "元気", "前向き", "明るい", "応援"],
     "description": "落ち込んだ気分を少し軽くして、自然と笑顔になれるポジティブな曲。"},
    {"title": "SUPER RAINBOW", "mood": ["楽しい", "カラフル", "高揚感", "元気", "前向き"],
     "description": "明るいエネルギーに満ちていて、楽しい気分をさらに盛り上げてくれる曲。"},
    {"title": "君のそばにいるよ", "mood": ["寄り添い", "安心", "優しい", "温かい", "癒し"],
     "description": "ひとりで抱え込んでしまった時に、そっと寄り添ってくれるような楽曲。"},
    {"title": "僕はペガサス 君はポラリス", "mood": ["絆", "壮大", "希望", "物語", "力強い"],
     "description": "ドラマチックな世界観の中で、強い絆や希望を感じられる一曲。"},
    {"title": "恋は終わらないずっと", "mood": ["恋愛", "一途", "温かい", "切ない", "想い"],
     "description": "変わらない想いを大切にしたい時に、優しく寄り添ってくれるラブソング。"},
    {"title": "DEEPNESS", "mood": ["深い", "夜", "祈り", "悲しみ", "壮大"],
     "description": "深い感情や孤独感に静かに寄り添う、重厚感のあるバラード。"},
    {"title": "MAWARE MAWARE", "mood": ["祝祭", "元気", "ダンス", "高揚感", "楽しい"],
     "description": "開放感があり、楽しく盛り上がりたい時にぴったりのエネルギッシュな曲。"},
    {"title": "CATCH THE RAINBOW", "mood": ["未来", "希望", "前向き", "元気", "明るい"],
     "description": "未来へ向かって明るく進みたい時に、前向きな気持ちをくれる曲。"},
    {"title": "銀河", "mood": ["宇宙", "幻想的", "静か", "夜", "壮大"],
     "description": "広い宇宙を漂うような感覚で、静かに感情へ浸れる幻想的な楽曲。"},
    {"title": "Royal Chocolate Flush", "mood": ["大人", "クール", "都会", "自信", "ダンス"],
     "description": "都会的でスタイリッシュな雰囲気があり、自信を高めたい時に合う曲。"},
    {"title": "ANY LOVE", "mood": ["愛", "優しい", "安心", "温かい", "恋愛"],
     "description": "穏やかな愛情に包まれたい時に、優しく心へ染み込む楽曲。"},
    {"title": "そばにいて...", "mood": ["寂しい", "会いたい", "恋愛", "夜", "切ない"],
     "description": "誰かにそばにいてほしい夜の寂しさへ、静かに寄り添ってくれる曲。"},
    {"title": "約束の翼", "mood": ["旅立ち", "希望", "応援", "壮大", "前向き"],
     "description": "新しい一歩を踏み出す時に、力強く背中を押してくれる楽曲。"},
    {"title": "少しずつ 大切に", "mood": ["日常", "穏やか", "優しい", "安心", "癒し"],
     "description": "焦らずゆっくり進みたい時に、穏やかな気持ちになれる曲。"},
]

# バリデーション用タイトル集合
VALID_TITLES = {song["title"] for song in SONG_DATABASE}


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


# ─────────────────────────────────────────
# LLM プロンプト定義
# ─────────────────────────────────────────

# Step1: 気分を感情ラベルに分類する
CLASSIFY_SYSTEM = """ユーザーの「今の気分」を読み取り、以下の形式だけで出力してください。

感情表現: 〇〇（詩的に短く。例：「静かに溶けていくような切なさ」）
ラベル: ラベル1, ラベル2, ...

ラベルは以下のリストから当てはまるものを選んでください（複数可）:
癒し, 恋愛, 安心, 切ない, 愛, 感謝, 家族, 温かい, 悲しい, 喪失, 泣きたい, 希望, 前向き, 応援, 立ち直り, 元気, 明るい, 勇気, 自信, 力強い, 夜, 寂しい, 壮大, 人生, 思い出, 静か, 祈り, 悲しみ, 深い, ソウルフル, 高揚感, 大人, ジャズ"""

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

    # ユーザー入力バブル
    html_parts.append(
        f'<div class="user-bubble">'
        f'<div class="user-label">💬 あなたの気分</div>'
        f'{mood}'
        f'</div>'
    )

    # 推薦コンテナ開始
    html_parts.append('<div class="rec-container">')

    # 感情タグ
    if parsed["emotion"]:
        html_parts.append(
            f'<div class="emotion-tag">🔮 {parsed["emotion"]}</div>'
        )

    # 楽曲カード
    for song in parsed["songs"]:
        html_parts.append(
            f'<div class="song-card">'
            f'<div class="song-title">🎵 {song["title"]}</div>'
            f'<div class="song-reason">{song["reason"]}</div>'
            f'</div>'
        )

    # 一言メッセージ
    if parsed["message"]:
        html_parts.append(
            f'<div class="closing-message">✨ {parsed["message"]}</div>'
        )

    html_parts.append("</div>")  # rec-container 閉じ
    html_parts.append('<hr class="divider">')

    return "\n".join(html_parts)


# ─────────────────────────────────────────
# 過去の会話履歴を表示
# ─────────────────────────────────────────
for entry in st.session_state.history:
    st.markdown(entry["html"], unsafe_allow_html=True)

# ─────────────────────────────────────────
# API Key 未入力時の案内 / 入力済みの場合は推薦処理
# ─────────────────────────────────────────
if not api_key:
    st.info("左のサイドバーに Anthropic API Key を入力すると、楽曲推薦を開始できます。")
else:
    client = anthropic.Anthropic(api_key=api_key)

    # ─────────────────────────────────────────
    # チャット入力
    # ─────────────────────────────────────────
    mood_input = st.chat_input(
        "今の気分を教えてください（例：疲れた、前向きになりたい、夜に浸りたい）"
    )

    # ─────────────────────────────────────────
    # 入力があったら推薦処理を実行
    # ─────────────────────────────────────────
    if mood_input:
        mood_input = mood_input.strip()
        if not mood_input:
            st.warning("気分を入力してください。")
        else:
            with st.spinner("🎵 MISIA の楽曲を探しています…"):
                try:
                    # Step1: 気分 → 感情ラベルに分類
                    r1 = client.messages.create(
                        model="claude-haiku-4-5-20251001",
                        max_tokens=200,
                        system=CLASSIFY_SYSTEM,
                        messages=[{"role": "user", "content": f"今の気分: {mood_input}"}],
                    )
                    emotion, labels = parse_classify(r1.content[0].text or "")

                    # Step2: ラベルで候補曲を絞り込み → 推薦文を生成
                    candidates = select_candidates(labels)
                    r2 = client.messages.create(
                        model="claude-haiku-4-5-20251001",
                        max_tokens=800,
                        system=RECOMMEND_SYSTEM,
                        messages=[{"role": "user", "content": build_recommend_prompt(mood_input, candidates)}],
                    )
                    parsed = parse_recommend(r2.content[0].text or "", emotion)

                    # バリデーション後に曲が残らない場合のフォールバック
                    if not parsed["songs"]:
                        parsed["songs"] = [
                            {"title": c["title"], "reason": c["description"]} for c in candidates
                        ]
                        parsed["message"] = "あなたの気分に合う曲を選びました。"

                    # HTML に変換して履歴に追加
                    html = render_recommendation(mood_input, parsed)
                    st.session_state.history.append({"mood": mood_input, "html": html})

                    # 画面に表示
                    st.markdown(html, unsafe_allow_html=True)

                except anthropic.AuthenticationError:
                    st.markdown(
                        '<div class="error-box">🔑 API キーが無効です。正しい Anthropic API Key をサイドバーに入力してください。</div>',
                        unsafe_allow_html=True,
                    )
                except anthropic.APIError as e:
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
