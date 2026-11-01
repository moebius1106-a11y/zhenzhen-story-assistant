import os
import json
import random
import threading
import urllib.request
import urllib.error
from datetime import datetime
import streamlit as st

# ----------------- 頁面與品牌配置 -----------------
st.set_page_config(
    page_title="真真公主專用｜每日限動操盤助手",
    page_icon="👑",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 極致美業名媛奢華風 CSS (iPhone 18 Pro Max 完美自適應、絕不折字破版)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700&family=Noto+Serif+TC:wght@500;700;900&family=Noto+Sans+TC:wght@300;400;500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Noto Sans TC', -apple-system, BlinkMacSystemFont, sans-serif;
        -webkit-font-smoothing: antialiased;
    }
    
    .stApp {
        background: radial-gradient(circle at 50% 12%, #1C1917 0%, #0C0A09 100%) !important;
        color: #F5EBE1 !important;
    }
    
    .luxury-header {
        text-align: center;
        padding: 24px 14px 20px 14px;
        background: linear-gradient(145deg, rgba(38, 33, 29, 0.9) 0%, rgba(20, 18, 16, 0.98) 100%);
        border-radius: 20px;
        border: 1px solid rgba(212, 175, 55, 0.35);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6), inset 0 1px 0 rgba(255, 223, 128, 0.2);
        margin-bottom: 20px;
    }
    
    .brand-crown {
        font-size: 26px;
        margin-bottom: 4px;
        filter: drop-shadow(0 2px 8px rgba(212, 175, 55, 0.6));
    }
    
    .header-title {
        font-family: 'Noto Serif TC', serif;
        font-size: clamp(15px, 4.3vw, 20px);
        font-weight: 700;
        letter-spacing: 0.5px;
        white-space: nowrap;
        background: linear-gradient(135deg, #FFF5DE 0%, #E8BE6B 50%, #B38634 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 6px;
    }
    
    .header-eng {
        font-family: 'Cinzel', serif;
        font-size: clamp(8.5px, 2.4vw, 11px);
        letter-spacing: 2px;
        color: #A3907F;
        text-transform: uppercase;
        margin-bottom: 8px;
        white-space: nowrap;
    }
    
    .header-subtitle {
        font-size: clamp(11.5px, 3.2vw, 13px);
        color: #D3C3B3;
        letter-spacing: 0.5px;
        font-weight: 300;
        line-height: 1.4;
    }
    
    .status-card-gold {
        background: linear-gradient(145deg, rgba(42, 36, 30, 0.75) 0%, rgba(26, 22, 18, 0.9) 100%);
        border: 1px solid rgba(212, 175, 55, 0.28);
        border-radius: 14px;
        padding: 12px 14px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        margin-bottom: 10px;
    }
    .status-label {
        font-size: 11px;
        color: #A6917E;
        margin-bottom: 4px;
        letter-spacing: 1px;
    }
    .status-value {
        font-size: 14px;
        font-weight: 600;
        color: #F8E6C8;
    }
    
    div[data-baseweb="textarea"] {
        background-color: rgba(28, 25, 23, 0.85) !important;
        border: 1px solid rgba(212, 175, 55, 0.3) !important;
        border-radius: 14px !important;
        box-shadow: inset 0 2px 6px rgba(0, 0, 0, 0.5) !important;
    }
    div[data-baseweb="textarea"] textarea {
        color: #F5ECE3 !important;
        font-size: 14px !important;
        line-height: 1.6 !important;
    }
    div[data-baseweb="textarea"]:focus-within {
        border-color: #E8BE6B !important;
        box-shadow: 0 0 12px rgba(232, 190, 107, 0.3) !important;
    }
    label[data-testid="stWidgetLabel"] p {
        color: #E8D9CB !important;
        font-size: 13.5px !important;
        font-weight: 500 !important;
        letter-spacing: 0.3px !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #F0CF86 0%, #D4AF37 50%, #9E7422 100%) !important;
        color: #1A1208 !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        letter-spacing: 1.5px !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 13px 20px !important;
        box-shadow: 0 6px 20px rgba(212, 175, 55, 0.35) !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 8px 24px rgba(232, 190, 107, 0.5) !important;
        color: #0A0704 !important;
    }
    
    .story-card-luxury {
        background: linear-gradient(160deg, rgba(34, 30, 26, 0.92) 0%, rgba(20, 18, 16, 0.98) 100%);
        border-radius: 16px;
        padding: 18px 16px;
        margin-bottom: 16px;
        border: 1px solid rgba(212, 175, 55, 0.25);
        border-left: 5px solid #D4AF37;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4);
    }
    .card-meta-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
    }
    .badge-number {
        font-family: 'Cinzel', serif;
        font-size: 11px;
        font-weight: 700;
        color: #1C1917;
        background: linear-gradient(135deg, #FFF1D0 0%, #E8BE6B 100%);
        padding: 3px 10px;
        border-radius: 20px;
        letter-spacing: 1px;
    }
    .badge-category {
        font-size: 11.5px;
        font-weight: 600;
        color: #E6CFA8;
        background: rgba(212, 175, 55, 0.12);
        padding: 3px 10px;
        border-radius: 20px;
        border: 1px solid rgba(212, 175, 55, 0.3);
    }
    .luxury-hook-text {
        font-size: 14.5px;
        font-weight: 500;
        color: #FFFFFF;
        line-height: 1.6;
        margin-bottom: 12px;
        padding: 12px 14px;
        background: rgba(14, 12, 10, 0.65);
        border-radius: 10px;
        border-left: 3px solid #E8BE6B;
    }
    .meta-line {
        font-size: 12.5px;
        color: #C8B9A6;
        margin-bottom: 6px;
        line-height: 1.5;
    }
    .meta-tag-gold {
        color: #E8BE6B;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- 獲取 API 金鑰 -----------------
def get_api_key():
    key = None
    try:
        if "GEMINI_API_KEY" in st.secrets:
            key = str(st.secrets["GEMINI_API_KEY"]).strip()
    except Exception:
        pass
    if not key:
        val = os.environ.get("GEMINI_API_KEY")
        if val:
            key = val.strip()
    if key:
        for ch in [" ", "'", '"', "[", "]"]:
            key = key.replace(ch, "")
        return key.strip()
    return None

# ----------------- 內建「真真美學·智慧動態語義引擎」(零延遲秒出保底) -----------------
def smart_local_engine(day_idx: int, user_input: str, seed_idx: int = 0) -> dict:
    clean_input = user_input.strip().rstrip("。！!？?～~，,.")
    is_odd = (day_idx % 2 == 1)
    qa_or_intro = "商品介紹" if is_odd else "商品QA"
    about_or_milestone = "關於我" if is_odd else "里程碑"

    # 依據輸入內容動態調整視覺建議
    if any(k in clean_input for k in ["咖啡", "茶", "拿鐵", "美式", "喝", "飲料"]):
        v1 = "手拿飲品杯搭配工作室柔和光線視角或露臉微笑側拍"
        s1 = "投票貼紙：今天喝咖啡續命☕️ / 我是喝茶派🍵"
        themes = ["醇香暖心與精緻美學交織的日常", "在忙碌節奏裡品味溫柔小確幸", "帶著滿滿暖意開啟發光的一天"]
    elif any(k in clean_input for k in ["蛋糕", "甜點", "吃", "美食", "下午茶", "湯"]):
        v1 = "精緻餐點或甜點特寫搭配真真優雅露臉日常照"
        s1 = "投票貼紙：甜點胃永遠有空間🍰 / 先忍住維持體態✨"
        themes = ["懂得寵愛自己，才能把美好帶給客人", "美食與美麗兼具的質感日常", "偷得浮生半日閒的優雅充電時刻"]
    elif any(k in clean_input for k in ["魚", "蝦", "植物", "花", "店裡", "陽光", "天氣", "雨"]):
        v1 = "店內質感角落、光影或日常露臉暖心隨手拍"
        s1 = "表情滑桿：喜歡這種舒服療癒的節奏✨"
        themes = ["把日子過成自己喜歡的模樣", "在靜謐質感空間裡，遇見更美的自己", "生活細節裡的溫柔與專業堅持"]
    else:
        v1 = "真真露臉親切微笑自拍或工作室晨間準備日常視角"
        s1 = "投票貼紙：今天也是充實派🙋‍♀️ / 想要悠閒放空派✨"
        themes = ["把生活瑣碎化為光彩，讓專業自然綻放", "溫柔而堅定的美業日常", "用心對待每一份信任與日常美好"]

    v = seed_idx % 3

    hook_1_list = [
        f"今天的小確幸：{clean_input}✨ 心情瞬間被點亮了～你們今天過得還好嗎？",
        f"剛發生一件暖心事：{clean_input}🥰 帶著滿滿能量開工，大家今天忙嗎？",
        f"今日份的美好紀錄：{clean_input}💛 生活裡的溫度最迷人，你們今天充電了嗎？"
    ]
    hook_2_list = [
        "喜歡這種忙碌卻很有溫度的節奏，把狀態調整到最好，準備迎接預約的公主們✨",
        "被日常的小美好療癒後，整個人都神清氣爽起來～今天也要讓每位客人美美走出門！",
        "把工作室打理得香香亮亮的，只要心態鬆弛有度，連空氣都覺得特別舒服🌿"
    ]
    hook_3_list = [
        "進入專注施作模式💆‍♀️ 看這精華液滲透肌底的水潤光澤，每個手法細節都絕不馬虎。",
        "很多客人問為什麼做完臉特別透亮？因為從清潔到導入，每一步都是溫柔慢工細活✨",
        "療癒的施作時光💧 聽著輕音樂、搭配高濃度保濕導入，幫疲憊的肌膚好好喝飽水。"
    ]
    hook_4_list = [
        "客人剛照鏡子直呼：『天啊臉也太亮了吧！原本的暗沉感全沒了～』聽到這句最開心🥰",
        "收到熟客傳來的回饋：『做完回去連上妝都超服貼，完全不卡粉！』妳們的滿意就是我的動力💛",
        "看到客人做完深層護理後，素顏就自帶透亮水光感，那種自信的笑容真的太迷人了✨"
    ]

    if is_odd:
        hook_5_list = [
            "最近換季超多人問的秘密武器就是它✨ 深層補水同時穩定膚況，敏感肌也能安心養出燈泡肌。",
            "店裡點名率最高的深層淨膚修護👑 不只溫和代謝老廢角質，做完當下毛孔彷彿會呼吸！",
            "為什麼我們家的護理能維持這麼久？關鍵就在這瓶高純度修護安瓶，把營養真正鎖進肌底💧"
        ]
        v5 = "明星保養品或修護安瓶微距質感擺拍"
        s5 = "問答貼紙：想改善什麼膚況？私訊我聊聊💬"
    else:
        hook_5_list = [
            "Q：多久做一次深層管理最適合？其實順應肌膚28天代謝週期，定期溫和養護比急救更有效喔✨",
            "Q：皮膚乾又容易出油怎麼辦？那是外油內乾缺水警訊！先把基底水補足，油水平衡自然就透亮💧",
            "Q：做完臉回去怎麼維持？頭三天加強純保濕與防曬，少用酸類刺激，光澤感可以維持超久喔👑"
        ]
        v5 = "真真專業解說側拍或保養QA重點文字底圖"
        s5 = "問答貼紙：還有保養疑問嗎？留言告訴我👇"

    hook_6_list = [
        f"下午空檔回想今天「{clean_input}」，還是覺得很美好～忙碌之餘別忘了給自己喘口氣喔☕️",
        "偷得浮生半日閒，在緊湊的排程中間給自己留一點空白，喝口溫水讓身心都慢下來🌿",
        "偶爾放慢腳步看看身邊的小風景，越懂得好好生活的人，散發出來的氣場越柔和迷人✨"
    ]
    hook_7_list = [
        "看著店裡魚缸的小魚小蝦悠哉游來游去，搭配淡淡的室內香氛，連等待的時光都好療癒🐠",
        "工作室角落的柔和光線與綠意🌿 很多客人說一走進來就覺得壓力少了一半，這就是我要的溫度。",
        "喜歡店裡安靜舒服的氛圍，不用趕時間、沒有壓迫感，讓每次變美都是一場身心放鬆之旅✨"
    ]
    hook_8_list = [
        "送走今天最後一位客人，把器具細心消毒歸位，充實又滿足地準備收工下班啦🌙",
        "傍晚收工後的靜謐時刻✨ 感謝今天每位公主的信任，晚安前別忘了好好幫臉蛋擦上保養品喔！",
        "結束忙碌的一天，雖然充實但心裡滿滿踏實感💛 準備切換成下班放鬆模式，你們也下班了嗎？"
    ]

    if is_odd:
        hook_9_list = [
            "走過人生起伏才更懂得：女人最好的狀態，是經濟獨立、內心通透，把日子活成自己喜歡的模樣👑",
            "經營真真美學這麼久，我始終相信「真誠與專業」是最好的名片，不強迫推銷，只給妳真正需要的✨",
            "美從來不是討好別人，而是當妳看著鏡子裡的自己時，打從心底升起的那份從容與底氣💛"
        ]
        v9 = "真真知性優雅工作側拍或個人質感形象照"
        s9 = "表情滑桿：一起成為閃閃發光的大女主👑"
    else:
        hook_9_list = [
            "看著預約表上滿滿的熟客名字，謝謝妳們一路以來的信任，讓真真美學成為妳們安心變美的秘密基地👑",
            "每一次進修與手法升級，都是為了不辜負妳們把臉蛋交給我的信任✨ 我們一起越來越美！",
            "從最初的堅持到現在累積無數好口碑，最珍貴的里程碑不是數字，而是每位客人找回自信的笑臉💛"
        ]
        v9 = "店內專業證照、進修紀錄或與客人溫馨互動側拍"
        s9 = "投票貼紙：準備好月底前來幫肌膚大掃除✨ / 舉手預約🙋‍♀️"

    return {
        "day_theme": themes[v],
        "stories": [
            {"story_number": 1, "category": "生活暖場", "hook_copy": hook_1_list[v], "visual_guide": v1, "sticker_suggestion": s1},
            {"story_number": 2, "category": "生活暖場", "hook_copy": hook_2_list[v], "visual_guide": "工作室整潔溫馨環境或個人準備開工日常照", "sticker_suggestion": "表情滑桿：今日元氣指數💯"},
            {"story_number": 3, "category": "使用產品", "hook_copy": hook_3_list[v], "visual_guide": "手部專業施作微距或精華液水潤質地特寫短片", "sticker_suggestion": "表情滑桿：這水潤光澤太療癒✨"},
            {"story_number": 4, "category": "客戶反饋", "hook_copy": hook_4_list[v], "visual_guide": "客人施作前後透亮對比照或LINE好評對話截圖", "sticker_suggestion": "投票貼紙：我也想要燈泡肌💡 / 私訊預約體驗"},
            {"story_number": 5, "category": qa_or_intro, "hook_copy": hook_5_list[v], "visual_guide": v5, "sticker_suggestion": s5},
            {"story_number": 6, "category": "生活放鬆", "hook_copy": hook_6_list[v], "visual_guide": "午後茶飲、小點心或隨手拍的生活愜意角落", "sticker_suggestion": "投票貼紙：下午茶時間到☕️ / 繼續打拼中💪"},
            {"story_number": 7, "category": "生活放鬆", "hook_copy": hook_7_list[v], "visual_guide": "店內魚缸小魚游動短片、香氛蠟燭或柔和燈光角落", "sticker_suggestion": "表情滑桿：療癒感滿分🌿"},
            {"story_number": 8, "category": "生活放鬆", "hook_copy": hook_8_list[v], "visual_guide": "傍晚收工後乾淨靜謐的工作室全景或下班視角", "sticker_suggestion": "投票貼紙：已經下班放鬆🌙 / 還在忙收尾✨"},
            {"story_number": 9, "category": about_or_milestone, "hook_copy": hook_9_list[v], "visual_guide": v9, "sticker_suggestion": s9},
        ]
    }

# ----------------- 混合極速調用函數 (3.5 秒硬上限，絕不卡死) -----------------
def generate_stories(day_idx: int, user_input: str, seed_idx: int = 0) -> dict:
    api_key = get_api_key()
    if not api_key:
        return smart_local_engine(day_idx, user_input, seed_idx)

    qa_or_intro = "商品介紹" if day_idx % 2 == 1 else "商品QA"
    about_or_milestone = "關於我" if day_idx % 2 == 1 else "里程碑"

    prompt = f"""你是「真真美學」首席操盤顧問，為創辦人「真真公主（鄭鈺真）」依日常輸入產出今日9則IG限動JSON。
結構：1生活暖場(露臉共鳴)、2生活暖場、3使用產品、4客戶反饋、5{qa_or_intro}、6生活放鬆、7生活放鬆(店內魚缸/香氛)、8生活放鬆(收工)、9{about_or_milestone}。
要求：語氣優雅鬆弛如閨蜜聊天，hook_copy每則25-35字內，visual_guide與sticker_suggestion各12字內。
日常輸入：「{user_input}」
純JSON格式：{{"day_theme":"主題","stories":[{{"story_number":1,"category":"分類","hook_copy":"文案","visual_guide":"配圖","sticker_suggestion":"貼圖"}}]}}"""

    result_holder = {}

    def api_worker():
        try:
            clean_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key={api_key}"
            for ch in ["[", "]", "'", '"', " "]:
                clean_url = clean_url.replace(ch, "")
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "responseMimeType": "application/json",
                    "temperature": 0.7
                }
            }
            req = urllib.request.Request(
                clean_url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=3.5) as response:
                res = json.loads(response.read().decode("utf-8"))
                content_text = res["candidates"][0]["content"]["parts"][0]["text"].strip()
                s_idx = content_text.find("{")
                e_idx = content_text.rfind("}")
                if s_idx != -1 and e_idx != -1:
                    parsed = json.loads(content_text[s_idx:e_idx+1])
                    if isinstance(parsed.get("stories"), list) and len(parsed["stories"]) >= 9:
                        result_holder["data"] = parsed
        except Exception:
            pass

    t = threading.Thread(target=api_worker, daemon=True)
    t.start()
    t.join(timeout=3.8)

    if "data" in result_holder:
        return result_holder["data"]
    return smart_local_engine(day_idx, user_input, seed_idx)

# ----------------- 介面與交互 -----------------
st.markdown("""
<div class="luxury-header">
    <div class="brand-crown">👑</div>
    <div class="header-title">真真公主專用 ｜ 每日限動操盤助手</div>
    <div class="header-eng">PRINCESS ZHENZHEN · DAILY STORY CURATOR</div>
    <div class="header-subtitle">把生活瑣碎化為動人光彩 · 讓專業於無形中綻放</div>
</div>
""", unsafe_allow_html=True)

now = datetime.now()
day_map = {1: "週一", 2: "週二", 3: "週三", 4: "週四", 5: "週五", 6: "週六", 7: "週日"}
today_idx = now.isoweekday()

col1, col2 = st.columns([1, 1])
with col1:
    st.markdown(f"""
    <div class="status-card-gold">
        <div class="status-label">TODAY ｜ 當前排程</div>
        <div class="status-value">📅 {day_map[today_idx]}</div>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
    <div class="status-card-gold">
        <div class="status-label">KEY FOCUS ｜ 今日重點</div>
        <div class="status-value">✨ {'商品介紹' if today_idx % 2 == 1 else '商品QA'} ＋ {'關於我' if today_idx % 2 == 1 else '里程碑'}</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

user_thought = st.text_area(
    "💬 公主今天有什麼日常、心情或客人對話？（隨興打一句就好）",
    placeholder="例如：客人送了一杯咖啡很好喝，下午做完深層淨膚直呼臉亮得像燈泡...",
    height=95
)

st.write("")

if "story_plan" not in st.session_state:
    st.session_state["story_plan"] = None
if "seed_counter" not in st.session_state:
    st.session_state["seed_counter"] = 0

generate_btn = st.button("✨ 一鍵排好今日 9 格限動腳本", use_container_width=True)

if generate_btn:
    if not user_thought.strip():
        st.warning("請先隨興打一句今天的瑣事或心情吧～不用動腦隨便寫就好！")
    else:
        with st.spinner("👑 軍師正在為公主排定本日 9 格限動腳本..."):
            st.session_state["story_plan"] = generate_stories(
                today_idx,
                user_thought,
                st.session_state["seed_counter"]
            )
            st.session_state["seed_counter"] += 1

plan = st.session_state.get("story_plan")
if plan and isinstance(plan, dict):
    st.markdown(f"""
    <div style="margin: 20px 0 16px 0; padding: 12px 16px; background: rgba(212, 175, 55, 0.1); border-radius: 12px; border: 1px dashed rgba(212, 175, 55, 0.4); text-align: center;">
        <span style="color: #E8BE6B; font-size: 14px; font-weight: 600;">🌟 本日主軸定調：{plan.get('day_theme', '')}</span>
    </div>
    """, unsafe_allow_html=True)
    
    for item in plan.get("stories", []):
        st.markdown(f"""
        <div class="story-card-luxury">
            <div class="card-meta-bar">
                <span class="badge-number">STORY 0{item.get('story_number', '')}</span>
                <span class="badge-category">{item.get('category', '')}</span>
            </div>
            <div class="luxury-hook-text">「{item.get('hook_copy', '')}」</div>
            <div class="meta-line"><span class="meta-tag-gold">📸 建議配圖：</span>{item.get('visual_guide', '')}</div>
            <div class="meta-line"><span class="meta-tag-gold">🏷️ 互動貼圖：</span>{item.get('sticker_suggestion', '')}</div>
        </div>
        """, unsafe_allow_html=True)
        st.code(item.get('hook_copy', ''), language="text")
