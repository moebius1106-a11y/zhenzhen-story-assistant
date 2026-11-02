import os
import json
import time
import html
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime, timezone, timedelta

# 優先採用標準時區模組 (Asia/Taipei)，若環境不支援則以 UTC+8 備援
try:
    import zoneinfo
    TAIPEI_TZ = zoneinfo.ZoneInfo("Asia/Taipei")
except Exception:
    TAIPEI_TZ = timezone(timedelta(hours=8))

import streamlit as st

# ----------------- 頁面與品牌配置 -----------------
st.set_page_config(
    page_title="真真公主專用｜每日限動操盤助手",
    page_icon="👑",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 極致美業名媛高奢奶油白金風 CSS (iPhone 18 Pro Max 完美自適應、徹底根除反白看不見問題)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700&family=Noto+Serif+TC:wght@600;700;900&family=Noto+Sans+TC:wght@400;500;600;700&display=swap');
    
    :root {
        color-scheme: light !important;
    }

    html, body, [class*="css"] {
        font-family: 'Noto Sans TC', -apple-system, BlinkMacSystemFont, sans-serif;
        -webkit-font-smoothing: antialiased;
        color: #2C221E !important;
    }
    
    /* 全域溫潤珍珠奶油白底色 */
    .stApp {
        background: linear-gradient(180deg, #FDFBF7 0%, #F7F2EA 100%) !important;
        color: #2C221E !important;
    }

    /* 頂部隱藏多餘裝飾但保留清爽空間 */
    header[data-testid="stHeader"] {
        background: rgba(253, 251, 247, 0.85) !important;
    }
    
    /* 頂部名媛白金奢華 Header */
    .luxury-header {
        text-align: center;
        padding: 22px 14px 18px 14px;
        background: linear-gradient(145deg, #FFFFFF 0%, #FAF5EC 100%);
        border-radius: 20px;
        border: 1.5px solid #DEC393;
        box-shadow: 0 8px 24px rgba(158, 123, 62, 0.12), inset 0 1px 0 #FFFFFF;
        margin-bottom: 14px;
    }
    
    .brand-crown {
        font-size: 28px;
        margin-bottom: 4px;
        filter: drop-shadow(0 2px 6px rgba(184, 138, 68, 0.35));
    }
    
    .header-title {
        font-family: 'Noto Serif TC', serif;
        font-size: clamp(15.5px, 4.4vw, 21px);
        font-weight: 700;
        letter-spacing: 0.5px;
        white-space: nowrap;
        color: #7A541B !important;
        margin-bottom: 5px;
    }
    
    .header-eng {
        font-family: 'Cinzel', serif;
        font-size: clamp(8.5px, 2.4vw, 11px);
        letter-spacing: 2px;
        color: #9A815C !important;
        text-transform: uppercase;
        margin-bottom: 8px;
        white-space: nowrap;
        font-weight: 600;
    }
    
    .header-subtitle {
        font-size: clamp(11.5px, 3.2vw, 13px);
        color: #8C6224 !important;
        letter-spacing: 0.5px;
        font-weight: 600;
        line-height: 1.45;
    }

    /* 黃金邏輯橫幅 */
    .logic-banner {
        background: #FAF3E6;
        border: 1px solid #DEC393;
        border-radius: 12px;
        padding: 10px 12px;
        margin-bottom: 14px;
        font-size: 12px;
        color: #523D24 !important;
        line-height: 1.55;
        text-align: center;
    }

    /* 9格與5格排程膠囊條 */
    .grid-bar {
        display: flex;
        flex-wrap: wrap;
        gap: 5px;
        justify-content: center;
        margin: 8px 0 14px 0;
    }
    .grid-pill {
        font-size: 11px;
        padding: 4px 9px;
        border-radius: 8px;
        background: #FFFFFF;
        border: 1px solid #E2D5C1;
        color: #6E5A47 !important;
        font-weight: 500;
    }
    .grid-pill-work {
        font-size: 11px;
        padding: 4px 9px;
        border-radius: 8px;
        background: #FDF3DF;
        border: 1px solid #C89B4B;
        color: #7A5114 !important;
        font-weight: 700;
    }

    /* 徹底修復 Expander 展開與收合時的反白問題：固定溫潤白金底＋深褐字 */
    div[data-testid="stExpander"] {
        background: #FFFFFF !important;
        border: 1px solid #E3D2B6 !important;
        border-radius: 14px !important;
        box-shadow: 0 3px 10px rgba(158, 123, 62, 0.06) !important;
        margin-bottom: 10px !important;
        overflow: hidden !important;
    }
    div[data-testid="stExpander"] details {
        background: #FFFFFF !important;
        border: none !important;
    }
    div[data-testid="stExpander"] summary,
    div[data-testid="stExpander"] summary:hover,
    div[data-testid="stExpander"] summary:focus,
    div[data-testid="stExpander"] summary:active,
    div[data-testid="stExpander"] details[open] > summary {
        background: #FAF5EC !important;
        color: #4A3722 !important;
        padding: 11px 14px !important;
        border-radius: 13px !important;
        border-bottom: 1px solid #EFE6D5 !important;
    }
    div[data-testid="stExpander"] summary p,
    div[data-testid="stExpander"] summary span,
    div[data-testid="stExpander"] summary div {
        color: #4A3722 !important;
        font-weight: 700 !important;
        font-size: 13.5px !important;
    }
    div[data-testid="stExpander"] summary svg {
        fill: #8C6224 !important;
        color: #8C6224 !important;
    }
    div[data-testid="stExpanderDetails"] {
        background: #FFFFFF !important;
        color: #2C221E !important;
        padding: 12px 14px !important;
    }

    /* 七天排程表專屬亮白金樣式 */
    .schedule-table-wrap {
        overflow-x: auto;
        margin: 6px 0 10px 0;
        border-radius: 12px;
        border: 1px solid #DEC393;
        background: #FFFFFF;
    }
    .schedule-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 11px;
        text-align: center;
        min-width: 520px;
    }
    .schedule-table th {
        background: #F7EFE0;
        color: #6B4915 !important;
        padding: 7px 4px;
        font-weight: 700;
        border-bottom: 1px solid #DEC393;
    }
    .schedule-table td {
        padding: 6px 4px;
        border-bottom: 1px solid #F2ECE1;
        color: #5C4B3B !important;
        background: #FFFFFF;
    }
    .schedule-row-active td {
        background: #FEF6E6 !important;
        color: #6B4915 !important;
        font-weight: 700 !important;
        border-top: 1.5px solid #C89B4B !important;
        border-bottom: 1.5px solid #C89B4B !important;
    }
    .cell-work {
        background: #FBF2E1 !important;
        color: #8A5D1A !important;
        font-weight: 700;
    }
    
    /* 徹底修復下拉選單 Selectbox 與輸入框 Textarea 在手機端的配色與清晰度 */
    label[data-testid="stWidgetLabel"] p {
        color: #4A3722 !important;
        font-size: 13.5px !important;
        font-weight: 700 !important;
    }
    div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        border: 1.2px solid #DEC393 !important;
        border-radius: 12px !important;
        color: #2C221E !important;
    }
    div[data-baseweb="select"] span,
    div[data-baseweb="select"] div {
        color: #2C221E !important;
        font-weight: 500 !important;
    }
    ul[data-baseweb="menu"],
    div[data-baseweb="popover"] {
        background-color: #FFFFFF !important;
        color: #2C221E !important;
    }
    li[role="option"] {
        background-color: #FFFFFF !important;
        color: #2C221E !important;
    }
    li[role="option"]:hover,
    li[aria-selected="true"] {
        background-color: #FAF2E1 !important;
        color: #6B4915 !important;
        font-weight: 600 !important;
    }

    /* 修復 Textarea 輸入框白底白字反白問題 */
    div[data-baseweb="textarea"] {
        background-color: #FFFFFF !important;
        border: 1.5px solid #DEC393 !important;
        border-radius: 14px !important;
        box-shadow: inset 0 1px 4px rgba(158, 123, 62, 0.08) !important;
    }
    div[data-baseweb="textarea"] textarea {
        background-color: #FFFFFF !important;
        color: #2C221E !important;
        -webkit-text-fill-color: #2C221E !important;
        caret-color: #8C6224 !important;
        font-size: 14.5px !important;
        font-weight: 500 !important;
        line-height: 1.6 !important;
    }
    div[data-baseweb="textarea"] textarea::placeholder {
        color: #9E8F7F !important;
        -webkit-text-fill-color: #9E8F7F !important;
        opacity: 1 !important;
    }
    
    /* 尊榮香檳金按鈕 */
    .stButton > button {
        background: linear-gradient(135deg, #F3D999 0%, #D9AE56 55%, #B8862D 100%) !important;
        color: #23180B !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        letter-spacing: 0.6px !important;
        border: 1px solid #C59B47 !important;
        border-radius: 14px !important;
        padding: 11px 16px !important;
        box-shadow: 0 5px 15px rgba(184, 134, 45, 0.25) !important;
    }
    .stButton > button p,
    .stButton > button span {
        color: #23180B !important;
        font-weight: 700 !important;
    }
    .stButton > button:active {
        transform: scale(0.98) !important;
    }
    
    /* 限動腳本卡片：名媛珍珠白＋香檳金邊框 */
    .story-card-luxury {
        background: #FFFFFF;
        border-radius: 16px;
        padding: 16px 15px;
        margin-bottom: 12px;
        border: 1px solid #E5D4B7;
        border-left: 5px solid #C89B4B;
        box-shadow: 0 6px 18px rgba(158, 123, 62, 0.09);
    }
    .card-meta-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
        flex-wrap: wrap;
        gap: 6px;
    }
    .badge-number {
        font-family: 'Cinzel', serif;
        font-size: 11px;
        font-weight: 700;
        color: #FFFFFF !important;
        background: linear-gradient(135deg, #C89B4B 0%, #9E7123 100%);
        padding: 3px 11px;
        border-radius: 20px;
    }
    .badge-time {
        font-size: 11.5px;
        color: #6E5A47 !important;
        background: #F6F1E9;
        padding: 2px 9px;
        border-radius: 12px;
        font-weight: 600;
    }
    .badge-category {
        font-size: 11.5px;
        font-weight: 700;
        color: #7A5114 !important;
        background: #FDF3DF;
        padding: 2px 10px;
        border-radius: 20px;
        border: 1px solid #DEC393;
    }
    .role-tag {
        font-size: 12px;
        color: #8C6224 !important;
        font-weight: 700;
        margin-bottom: 8px;
        letter-spacing: 0.2px;
    }
    .luxury-hook-text {
        font-size: 15px;
        font-weight: 600;
        color: #23180B !important;
        line-height: 1.65;
        margin-bottom: 10px;
        padding: 12px 14px;
        background: #FAF5EC;
        border-radius: 10px;
        border-left: 3.5px solid #C89B4B;
    }
    .meta-line {
        font-size: 13px;
        color: #4A3B2C !important;
        margin-bottom: 5px;
        line-height: 1.5;
    }
    .meta-tag-gold {
        color: #8C6224 !important;
        font-weight: 700;
    }
    .highlight-box {
        margin-top: 8px;
        padding: 7px 11px;
        background: #FDF8EE;
        border-radius: 8px;
        font-size: 12px;
        color: #7A5114 !important;
        font-weight: 600;
        border: 1px dashed #C89B4B;
    }
    .safety-note {
        font-size: 11px;
        color: #8A7968 !important;
        margin-top: 7px;
    }

    /* 修復 Checkbox 打勾清單文字顏色 */
    div[data-testid="stCheckbox"] label span,
    div[data-testid="stCheckbox"] label p {
        color: #3B2D20 !important;
        font-weight: 500 !important;
    }

    /* 一鍵複製程式碼區塊美化 */
    div[data-testid="stCodeBlock"] pre {
        background-color: #F7F2E9 !important;
        border: 1px solid #E3D2B6 !important;
        border-radius: 10px !important;
    }
    div[data-testid="stCodeBlock"] code {
        color: #2C221E !important;
        font-weight: 500 !important;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- 攻略資料庫 (100% 對齊兩張教材圖) -----------------
OPENING_PATTERNS = {
    "自動依情境匹配最佳句型": "auto",
    "句型①：「有沒有人跟我一樣⋯⋯」＋投票": "有沒有人跟我一樣",
    "句型②：「你們會不會也⋯⋯」＋表情滑桿": "你們會不會也",
    "句型③：「你們猜猜看⋯⋯」＋測驗，答案下一篇揭曉": "你們猜猜看",
    "句型④：「今天發生一件⋯⋯的事」先留懸念，後面接著講": "今天發生一件"
}

INTERACTION_HOOKS = {
    "幫我選（A 還是 B？投票參與決定）": "幫我選",
    "猜猜看（測驗貼紙猜答案，下一篇揭曉）": "猜猜看",
    "留言領乾貨（回關鍵字，私訊傳資源）": "留言領乾貨",
    "QA 收題日（提問貼紙收題，隔天一題一篇）": "QA收題日",
    "小算命／心理測驗（回生日月份給專屬結果）": "心理測驗",
    "抽卡（選 1、2、3，一個個回解讀）": "抽卡"
}

# 分離「日常情節」與「互動問句」，避免放進句型時雙重括號打架
LIFE_TOPICS_VISIBLE = {
    "☀️ 早晨儀式": "今天起床第一件事就是泡杯溫水開啟美好的一天",
    "🍰 今天吃什麼": "原本想隨便吃，最後還是忍不住買了最愛的美食甜點",
    "🚗 通勤路上": "今天去店裡的路上看到一家超有質感的店",
    "💑 家人／另一半": "今天發生的日常對話真的讓我哭笑不得",
    "🐠 毛小孩／店寵": "看著店裡魚缸的小魚小蝦游來游去超級療癒",
    "💆‍♀️ 運動／保養": "再忙還是要留時間給自己好好保養維持狀態",
    "🕯️ 工作角落": "在真真美學待最久的溫馨小角落，點上香氛超放鬆",
    "🌿 週末小出遊": "趁著空檔偷得浮生半日閒出門晃晃透氣"
}

LIFE_TOPICS_THOUGHTS = {
    "🔋 今天的心情": "忙完一輪坐下來喝口咖啡，瞬間覺得電力滿滿",
    "💣 踩雷分享": "以前繳過好多保養冤枉錢，才懂成分跟手法有多重要",
    "📚 正在學的事": "最近一直在研究怎麼讓膚況更穩更細緻的新技術",
    "📸 以前的我": "無意間翻到以前的照片，感嘆女人真的越懂得愛自己越美",
    "🙏 想謝謝的人": "心裡很感激每位願意把臉蛋跟信任交給我的客人",
    "💎 我的堅持": "寧可慢工細活也不做速成推銷，是我做美業不變的原則",
    "✨ 最近在想": "把日子過得有質感、內心通透從容，就是最棒的狀態",
    "☕ 小確幸": "客人送了一杯超好喝的咖啡，心裡暖呼呼的"
}

# 對應圖三 06 生活主題發想庫的原版互動問句
TOPIC_QUESTIONS_MAP = {
    "☀️ 早晨儀式": "你們起床第一件事做什麼？",
    "🍰 今天吃什麼": "想吃 A 最後吃了 B 的舉手，你們今天吃什麼？",
    "🚗 通勤路上": "路上有沒有一家店你們一直想進去？",
    "💑 家人／另一半": "你們家那位也常讓你傻眼嗎？",
    "🐠 毛小孩／店寵": "你們家毛孩也會這樣看你嗎？",
    "💆‍♀️ 運動／保養": "你們都怎麼逼自己運動或保養？",
    "🕯️ 工作角落": "你們待最久的角落長怎樣？",
    "🌿 週末小出遊": "猜猜我今天放假跑去哪？你們週末去哪玩？",
    "🔋 今天的心情": "你們累了都怎麼充電？",
    "💣 踩雷分享": "你們買過最後悔的東西是什麼？",
    "📚 正在學的事": "你們最近有在學什麼嗎？",
    "📸 以前的我": "你們敢翻三年前的照片嗎？",
    "🙏 想謝謝的人": "你們最近最想謝謝誰？",
    "💎 我的堅持": "你們有默默堅持很久的事嗎？",
    "✨ 最近在想": "你們覺得怎樣才叫過得好？",
    "☕ 小確幸": "你們今天最開心的是什麼？"
}

# ----------------- 安全獲取 API 金鑰 -----------------
def get_api_key() -> str:
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
        return key.strip().strip("'").strip('"')
    return ""

# ----------------- 清理輸入文字（移除不小心附帶的括號問句，讓語句自然通順） -----------------
def sanitize_user_scenario(raw_input: str) -> tuple[str, str]:
    text = raw_input.strip()
    extracted_q = ""
    # 若包含全形或半形括號問句，將其拆出作為結尾互動問句
    if "（" in text and text.endswith("）"):
        idx = text.rfind("（")
        extracted_q = text[idx+1:-1].strip()
        text = text[:idx].strip()
    elif "(" in text and text.endswith(")"):
        idx = text.rfind("(")
        extracted_q = text[idx+1:-1].strip()
        text = text[:idx].strip()
    text = text.rstrip("。！!？?～~，,.")
    if not text:
        text = "在工作室準備迎接預約的公主們，心情特別充實美好"
    return text, extracted_q

# ----------------- 04 第一篇開頭句型生成器 -----------------
def build_opening_story(raw_input: str, opening_choice: str, v: int) -> tuple[str, str, str]:
    clean_in, custom_q = sanitize_user_scenario(raw_input)
    p_key = OPENING_PATTERNS.get(opening_choice, "auto")
    end_q = custom_q if (custom_q and "你們" in custom_q) else "你們今天早上有遇到什麼小確幸嗎？"
    if not end_q.endswith("？"):
        end_q = end_q.rstrip("?。！") + "？"

    if p_key == "有沒有人跟我一樣" or (p_key == "auto" and v == 0):
        h1 = f"有沒有人跟我一樣，只要「{clean_in}」整個人心情就瞬間變超好✨ 而且今天還準備了一件特別的事要忙，{end_q}"
        s1 = "投票貼紙：我也是小確幸派🙋‍♀️ / 今天忙到飛起🔥"
        h2 = "接續上一篇～帶著滿滿好心情把工作室打理得香香亮亮的✨ 開場先跟你們聊聊天，你們平時起床第一件事都做什麼？"
    elif p_key == "你們會不會也" or (p_key == "auto" and v == 1):
        h1 = f"你們會不會也覺得，日常裡「{clean_in}」這種溫暖時刻特別有動力✨ 先留個小伏筆，晚上再告訴你們今天忙了什麼！{end_q}"
        s1 = "表情滑桿：滑動告訴我你們今天的能量值✨"
        h2 = "接續早上的日常～趁著預約空檔泡了杯熱飲暖暖胃☕️ 你們平時工作前最喜歡喝咖啡還是喝茶？"
    elif p_key == "你們猜猜看":
        h1 = f"你們猜猜看！今天因為「{clean_in}」開啟超棒的一天，接下來進工作室我第一件事會先忙什麼？答案下一篇揭曉，你們猜對了嗎？"
        s1 = "測驗貼紙：猜猜真真第一件事做什麼？（A 準備護膚器具 / B 餵魚缸小魚小蝦）"
        h2 = "公佈上一篇測驗答案啦✨ 我進店第一件事就是先看魚缸的小魚小蝦再把器具消毒備好！你們猜對了嗎？"
    else:
        h1 = f"今天發生一件超暖心的事：{clean_in}🥰 先留個懸念，後面接著講為什麼這件事讓我開心了一整天！{end_q}"
        s1 = "投票貼紙：想聽後續舉手🙋‍♀️ / 先幫真真按個讚💛"
        h2 = "接續剛剛說的暖心事～其實生活裡越簡單真誠的互動越讓人感動✨ 你們最近也有遇到讓你心頭一暖的小事嗎？"
    return h1, s1, h2

# ----------------- 05 第二高點互動鉤子生成器 (支援全 6 種鉤子 × 奇偶日，無多餘中括號) -----------------
def build_hook_story(hook_choice: str, is_odd: bool, is_recruit: bool, is_life_mode: bool = False) -> tuple[str, str, str]:
    h_type = INTERACTION_HOOKS.get(hook_choice, "幫我選")
    
    if is_life_mode:
        v_guide = "店內魚缸小魚小蝦或溫馨工作角落實拍（真實自然光）"
        if h_type == "留言領乾貨":
            return "下午窩在待最久的角落整理筆記✨ 我把平時自己維持好氣色的《日常作息與補水清單》整理好了，你們想看嗎？回覆關鍵字「清單」我私訊傳給你們？", v_guide, "問答貼紙：回覆「清單」私訊領取日常保養筆記🎁"
        elif h_type == "心理測驗":
            return "下午休息時間來玩個趣味心理測驗✨ 憑直覺選一樣你現在最想做的事，測出你最近的壓力指數！你們是幾月生的？回覆生日月份我私訊給專屬結果？", v_guide, "問答貼紙：回覆你的「生日月份」領取專屬解析🔮"
        elif h_type == "QA收題日":
            return "下午在工作室角落放空充電🌿 今天開放日常QA收題！你們平時對美業工作或日常保養有什麼好奇的事嗎？在提問貼紙問我，明天一題一篇回答你們？", v_guide, "提問貼紙：有什麼好奇的問題？丟過來明天解答💬"
        elif h_type == "抽卡":
            return "下午茶時間來玩個今日能量抽卡🃏 憑直覺選 1、2、3 其中一張牌，看看今天宇宙想給你什麼溫柔提醒？選好留言告訴我，我一個個私訊回你們解讀？", v_guide, "投票/問答貼紙：直覺選 1、2、3 領取今日解讀🃏"
        elif h_type == "猜猜看":
            return "下午待在工作室最舒服的角落充電✨ 你們猜猜看，我在店裡最常待超過三小時的是哪個角落？先用測驗貼紙猜答案，下一篇揭曉你們猜對了嗎？", v_guide, "測驗貼紙：猜猜我待最久的地方？（A 護膚施作區 / B 魚缸香氛沙發區）"
        else:
            return "下午窩在這個待最久的溫馨角落，看著魚缸的小魚游來游去超療癒✨ 你們工作累了都怎麼充電？選 A 喝下午茶 還是 B 安靜放空五分鐘？幫我投票選一個？", v_guide, "投票貼紙：A 絕對要下午茶☕️ / B 安靜放空🌿"

    v_guide = "護理產品或專業設備乾淨擺拍（字放安全區）" if is_odd else "真真專業工作側拍或重點 QA 排版圖（字體顏色最多2種）"

    if h_type == "留言領乾貨":
        if is_odd:
            h5 = "為什麼做好基底保濕對肌膚這麼重要？因為水分充足膚況自然穩定✨ 我整理了一份《日常基礎養膚避雷指南》，你們想要嗎？回關鍵字「養膚」我私訊傳資源給你們？"
        else:
            h5 = "大家常問換季乾燥怎麼照顧？先看我精選「產品 QA」，我還額外整理了《居家保濕步驟圖》，你們想領取嗎？回關鍵字「保濕」我私訊傳給你們？"
        s5 = "問答貼紙：回覆關鍵字「養膚/保濕」私訊傳資源給你🎁"
    elif h_type == "心理測驗":
        if is_odd:
            h5 = "每種膚質都有專屬的溫和調理節奏✨ 來玩個小算命！你們是幾月出生的呢？回覆你的「生日月份」，我私訊告訴你專屬的換季保養重點結果？"
        else:
            h5 = "常有朋友問怎麼挑對護理方向？先看精選「產品 QA」，再來測測你的肌膚性格！回覆你的「生日月份」，我私訊給你專屬保養建議，你們幾月生呢？"
        s5 = "問答貼紙：回覆「生日月份」私訊領取專屬結果🔮"
    elif h_type == "QA收題日":
        if is_odd:
            h5 = "店裡溫和調理流程最重視油水平衡💧 今天也是每週 QA 收題日！你們平時保養最常卡關哪一步？在提問貼紙留問題，隔天我一題一篇為你們解答？"
        else:
            h5 = "今天是每週護膚 QA 收題日✨ 很多朋友問外油內乾怎麼保養？關鍵在溫和清潔與補水！先看我精選「產品 QA」，你們還有什麼保養疑問想在貼紙提問嗎？"
        s5 = "提問貼紙：留下你的保養疑問，隔天一題一篇解答💬"
    elif h_type == "抽卡":
        if is_odd:
            h5 = "今天施作這道溫和補水流程手感特別好✨ 來玩個保養抽卡！你們目前最想加強 1水分補給、2溫和清潔、還是 3舒緩穩定？選 1、2、3 我一個個私訊幫你們解讀？"
        else:
            h5 = "保養 QA 抽卡時間✨ 面對換季膚況，你們最困擾 1上妝不服貼、2T字易出油、還是 3臉頰乾繃？選 1、2、3 我一個個私訊回你們解讀建議？"
        s5 = "投票/問答貼紙：選 1、2、3 我一個個回你專屬解讀🃏"
    elif h_type == "猜猜看":
        if is_odd:
            h5 = "溫和深層護理能幫肌膚維持水潤細緻✨ 你們猜猜看，做完深層補水後頭三天最關鍵的保養動作是什麼？先在測驗貼紙猜答案，下一篇揭曉你們猜對了嗎？"
        else:
            h5 = "大家常問：多久安排一次深層管理最合適？建議順應肌膚代謝週期調理～猜猜看洗臉水溫太高會發生什麼事？測驗貼紙猜答案，下一篇揭曉你們猜對了嗎？"
        s5 = "測驗貼紙：猜猜正確保養關鍵？（A 加強純保濕與防曬 / B 立刻用去角質酸類）"
    else:
        if is_odd:
            h5 = "店裡很受歡迎的深層溫和護理👑 著重在溫和代謝角質並補充水分！你們日常保養時最在乎 A清爽透亮 還是 B水潤細緻？A 還是 B 幫我投票參與決定？"
        else:
            h5 = "整理精選「產品 QA」時發現大家最常問保養順序✨ 你們平時休假在家喜歡 A敷臉做足全套保養 還是 B精簡擦保濕就睡覺？A 還是 B 投票告訴我？"
        s5 = "投票貼紙：A 清爽透亮派✨ / B 水潤細緻派💧"

    return h5, v_guide, s5

# ----------------- 內建「Peggy 攻略全精髓引擎」(100% 符合圖二與圖三規範) -----------------
def peggy_master_engine(mode: str, day_idx: int, user_input: str, opening_choice: str, hook_choice: str, seed_idx: int = 0) -> dict:
    clean_in, _ = sanitize_user_scenario(user_input)
    is_odd = (day_idx % 2 == 1)
    v = seed_idx % 3
    h1, s1, h2 = build_opening_story(user_input, opening_choice, v)

    # 1. 生活版 (一天 5 篇：早上 / 中午 / 下午 / 晚上 / 睡前)
    if mode == "生活版（一天 5 篇｜先連續發滿 7 天）":
        h3_life, v3_life, s3_life = build_hook_story(hook_choice, is_odd, False, is_life_mode=True)
        return {
            "day_theme": f"生活版 DAY {day_idx}｜還沒有產品就從這裡開始，先連續發滿 7 天（早埋伏筆、晚給答案）",
            "stories": [
                {
                    "story_number": 1,
                    "time_slot": "09:00 早上",
                    "category": "早上",
                    "role_badge": "🌅 第一篇：看得到你＋一句共鳴＋互動貼紙（早上埋伏筆｜互動高點①）",
                    "hook_copy": h1,
                    "visual_guide": "真真露臉微笑自拍或手拿飲品/日常晨間視角（字放安全區，底圖太亮先調暗）",
                    "sticker_suggestion": s1,
                    "highlight_tag": "免存精選（有人回就一定要回，那是今天最熱的名單！）"
                },
                {
                    "story_number": 2,
                    "time_slot": "12:30 中午",
                    "category": "中午",
                    "role_badge": "☀️ 第二篇：講話像聊天，「我」換成「你們」，結尾丟一個問題",
                    "hook_copy": "中午吃飯時間到啦～忙了一個早上終於能喘口氣！你們中午通常都吃便當還是輕食？有沒有推薦必吃的口袋名單？",
                    "visual_guide": "午餐美食或私房餐點隨手拍（不發AI生成滿版圖，字體最多2種）",
                    "sticker_suggestion": "問答貼紙：推薦你們最愛的午餐給我👇",
                    "highlight_tag": "免存精選（日常破冰拉近距離）"
                },
                {
                    "story_number": 3,
                    "time_slot": "15:30 下午",
                    "category": "下午",
                    "role_badge": f"🔥 第三篇：第二個互動高點｜套用鉤子：{hook_choice}",
                    "hook_copy": h3_life,
                    "visual_guide": v3_life,
                    "sticker_suggestion": s3_life,
                    "highlight_tag": "免存精選（拉高互動率，觸發演算法推播）"
                },
                {
                    "story_number": 4,
                    "time_slot": "19:00 晚上",
                    "category": "晚上",
                    "role_badge": "🌙 第四篇：生活有連貫（早上埋伏筆，晚上給答案）",
                    "hook_copy": f"來給早上的伏筆答案啦🌙 今天因為「{clean_in}」開啟好心情，把工作空間與日常排程都整理得超舒心✨ 你們今天累了都怎麼充電？",
                    "visual_guide": "傍晚收工後的質感空間或完成事項的日常隨手拍",
                    "sticker_suggestion": "表情滑桿：給今天的充實度打幾分💯",
                    "highlight_tag": "免存精選（前後連貫養出每天追劇的鐵粉）"
                },
                {
                    "story_number": 5,
                    "time_slot": "22:00 睡前",
                    "category": "睡前",
                    "role_badge": "💫 第五篇：最後一篇給他「為什麼要相信你」（你要影響別人什麼？）",
                    "hook_copy": "睡前保養完看著鏡子，覺得女人把日子過得從容有底氣就是最棒的狀態💛 你們覺得怎樣才叫過得好？晚安前跟我分享吧？",
                    "visual_guide": "柔和黃光下的店內或居家靜謐角落（字色最多2種）",
                    "sticker_suggestion": "問答貼紙：你們覺得怎樣才叫過得好？💭",
                    "highlight_tag": "📌 建議存入精選：【關於我】"
                }
            ]
        }

    # 2. 賣貨版 / 招商版 (一天 9 篇三明治結構，嚴格對齊圖二 7 天模板)
    is_recruit = ("招商" in mode)
    if is_recruit:
        cat3 = "團隊日常"
        cat4 = "夥伴反饋"
        cat5 = "公司介紹" if is_odd else "團隊 QA"
        cat9 = "關於我" if is_odd else "里程碑"
        hl3, hl4, hl5, hl9 = "團隊/公司介紹", "夥伴反饋", ("團隊/公司介紹" if is_odd else "團隊 QA"), cat9
        h3 = "看暖了來聊點工作日常✨ 很多姊妹好奇我們平時怎麼切磋手法？看這專注練習細節的畫面，你們是不是也喜歡這種踏實成長的氛圍？"
        v3 = "團隊實操練習或專業手法交流畫面（不發AI生成滿版圖，字放安全區）"
        h4 = "今天跟夥伴交流近期服務的心得，大家都覺得把每個護膚步驟做到位最踏實～看到夥伴們一步步累積實力，你們最近也有正在努力學習的事嗎？"
        v4 = "日常技術交流筆記或真實團隊學習紀錄（無真實反饋時依當日實況記錄）"
    else:
        cat3 = "使用產品"
        cat4 = "客戶反饋"
        cat5 = "商品介紹" if is_odd else "商品 QA"
        cat9 = "關於我" if is_odd else "里程碑"
        hl3, hl4, hl5, hl9 = "產品介紹", "客戶反饋", ("產品介紹" if is_odd else "產品 QA"), cat9
        h3 = "看暖了來看看今天的專業護膚時光💆‍♀️ 精華液搭配手法溫柔導入肌底，你們看這水潤細緻的質地是不是很療癒？你們平時在家都怎麼做保濕？"
        v3 = "手部專業施作微距或使用產品真實畫面（底圖太亮先調暗再放字）"
        h4 = "每次幫客人做完深層保濕調理，最喜歡聽你們分享臉蛋摸起來水潤放鬆的真實感受✨ 你們遇到換季時最想改善哪個肌膚小困擾呢？"
        v4 = "真實客人回饋紀錄或施作工具整潔實拍（無真實反饋時請依當日實況分享，不發產品DM）"

    h5, v5, s5 = build_hook_story(hook_choice, is_odd, is_recruit, is_life_mode=False)

    if INTERACTION_HOOKS.get(hook_choice) == "猜猜看":
        h6 = "先公佈上一篇的保養測驗答案：做完深層護理頭三天最關鍵就是加強純保濕與防曬喔✨ 聊完工作切換回生活，你們下午累了都怎麼幫自己充電？"
    else:
        h6 = "講完工作立刻切換回下午的生活放鬆模式🌿 泡杯溫熱茶飲喘口氣，你們下午忙完一輪都怎麼幫自己充電？會吃點小點心嗎？"

    h7 = "在工作室待最久的角落，看著魚缸裡的小魚小蝦悠哉游動真的好解壓🐠 你們待最久的辦公或生活角落長怎樣？也有喜歡的療癒小物嗎？"
    h8 = f"來給早上的伏筆答案啦🌙 今天因為「{clean_in}」開啟好心情，把預約與手邊的計畫都細心完成了！你們今天最開心的一件事是什麼？"

    if is_odd:
        h9 = "走過人生起伏才更懂得：女人最好的底氣是獨立與通透👑 在真真美學我堅持不強迫推銷，只給你們真誠安心的專業呵護。你們覺得怎樣才叫活得漂亮？"
        v9 = "真真知性優雅工作側拍或個人大女主形象照（字體≤2種、字色≤2種）"
        s9 = "表情滑桿：一起成為獨立發光的大女主👑"
    else:
        h9 = "看著預約表上熟悉的信任與日常點滴累積，謝謝你們願意把臉蛋交給我的專業✨ 流量很重要，但我更在乎能帶給你們多少自信！這週想預約放鬆的公主準備好了嗎？"
        v9 = "專業證照、進修紀錄或日常用心準備的工作室實景"
        s9 = "投票貼紙：想預約本週時段🙋‍♀️ / 先看精選『QA』了解✨"

    return {
        "day_theme": f"DAY {day_idx}（第5篇：{cat5} ｜ 第9篇：{cat9}）｜早埋伏筆、晚給答案",
        "stories": [
            {"story_number": 1, "time_slot": "09:00", "category": "生活", "role_badge": "🌅 第一篇：看得到你＋一句共鳴＋互動貼紙（早上埋伏筆｜互動高點①）", "hook_copy": h1, "visual_guide": "真真露臉親切微笑或日常晨間第一視角（底圖調暗放安全區）", "sticker_suggestion": s1, "highlight_tag": "免存精選（有人回就一定要回，那是你今天最熱的名單！）"},
            {"story_number": 2, "time_slot": "10:30", "category": "生活", "role_badge": "☕ 第二篇：生活暖場延續，講話像聊天（「我」換成「你們」）", "hook_copy": h2, "visual_guide": "工作室晨間光線或飲品隨手拍（字體≤2種、字色≤2種）", "sticker_suggestion": "投票貼紙：咖啡派☕️ / 茶飲派🍵", "highlight_tag": "免存精選（開場先讓人看到你，看暖了下一篇再聊工作）"},
            {"story_number": 3, "time_slot": "12:00", "category": cat3, "role_badge": f"💆‍♀️ 第三篇：看暖了再聊工作（固定工作篇：{cat3}）", "hook_copy": h3, "visual_guide": v3, "sticker_suggestion": "表情滑桿：這水潤細緻感給幾分✨", "highlight_tag": f"📌 建議存入精選：【{hl3}】"},
            {"story_number": 4, "time_slot": "13:30", "category": cat4, "role_badge": f"🌟 第四篇：專業見證與互動（固定工作篇：{cat4}）", "hook_copy": h4, "visual_guide": v4, "sticker_suggestion": "投票貼紙：想了解日常養膚💡 / 私訊我聊聊💬", "highlight_tag": f"📌 建議存入精選：【{hl4}】"},
            {"story_number": 5, "time_slot": "15:00", "category": cat5, "role_badge": f"🔥 第五篇：第二個互動高點（隔天輪替：{cat5}｜鉤子：{hook_choice}）", "hook_copy": h5, "visual_guide": v5, "sticker_suggestion": s5, "highlight_tag": f"📌 建議存入精選：【{hl5}】（再被問到直接回：我精選的『QA』有整理，你先看看～）"},
            {"story_number": 6, "time_slot": "16:30", "category": "生活", "role_badge": "🌿 第六篇：講完工作就回到生活（鬆弛感切換）", "hook_copy": h6, "visual_guide": "下午茶點心或隨手拍生活角落（不發產品DM、不發AI生成滿版圖）", "sticker_suggestion": "投票貼紙：下午茶續命🍰 / 繼續專注打拼💪", "highlight_tag": "免存精選（每篇隔 1–2 小時再發，不要一次發完）"},
            {"story_number": 7, "time_slot": "18:00", "category": "生活", "role_badge": "🐠 第七篇：工作角落與日常溫度（看得到的日常）", "hook_copy": h7, "visual_guide": "魚缸小魚小蝦游動短片或店內香氛綠植特寫", "sticker_suggestion": "表情滑桿：療癒指數滿分💯", "highlight_tag": "免存精選（展現真真美學的舒適空間感）"},
            {"story_number": 8, "time_slot": "19:30", "category": "生活", "role_badge": "🌙 第八篇：生活有連貫（早上埋伏筆，晚上給答案）", "hook_copy": h8, "visual_guide": "傍晚收工後乾淨靜謐的工作室或下班放鬆視角", "sticker_suggestion": "問答貼紙：你們今天最開心的是什麼？💛", "highlight_tag": "免存精選（前後呼應第 1 篇伏筆，拉高完播率）"},
            {"story_number": 9, "time_slot": "21:00", "category": cat9, "role_badge": f"👑 第九篇：最後一篇給他「為什麼要相信你」（隔天輪替：{cat9}）", "hook_copy": h9, "visual_guide": v9, "sticker_suggestion": s9, "highlight_tag": f"📌 建議存入精選：【{hl9}】（建立長期信任背書）"}
        ]
    }

# ----------------- 資料結構正規化與完整性驗證器 -----------------
def normalize_and_validate_story_data(raw_data: dict, fallback_data: dict, expected_count: int) -> tuple[bool, str, dict]:
    if not isinstance(raw_data, dict):
        return False, "模型回傳格式非 JSON 物件", fallback_data

    stories = raw_data.get("stories")
    if not isinstance(stories, list) or len(stories) != expected_count:
        actual_len = len(stories) if isinstance(stories, list) else 0
        return False, f"限動篇數不符 (預期 {expected_count} 則，實際回傳 {actual_len} 則)", fallback_data

    day_theme = str(raw_data.get("day_theme") or fallback_data["day_theme"]).strip()
    if not day_theme:
        day_theme = fallback_data["day_theme"]

    normalized_stories = []
    fb_stories = fallback_data["stories"]

    for idx in range(expected_count):
        item = stories[idx]
        fb_item = fb_stories[idx]
        if not isinstance(item, dict):
            return False, f"第 {idx+1} 則限動非字典結構", fallback_data

        hook_copy = str(item.get("hook_copy") or "").strip()
        visual_guide = str(item.get("visual_guide") or fb_item["visual_guide"]).strip()
        sticker_suggestion = str(item.get("sticker_suggestion") or fb_item["sticker_suggestion"]).strip()

        if not hook_copy:
            return False, f"第 {idx+1} 則限動缺少核心文案 hook_copy", fallback_data

        if hook_copy.endswith("?"):
            hook_copy = hook_copy[:-1] + "？"
        elif not hook_copy.endswith("？"):
            hook_copy = hook_copy.rstrip("。！!～~.") + "，你們覺得呢？"

        if "你們" not in hook_copy and "妳們" not in hook_copy:
            hook_copy = hook_copy[:-1] + "，你們也會這樣嗎？"

        normalized_stories.append({
            "story_number": idx + 1,
            "time_slot": str(item.get("time_slot") or fb_item["time_slot"]).strip(),
            "category": fb_item["category"],
            "role_badge": str(item.get("role_badge") or fb_item["role_badge"]).strip(),
            "hook_copy": hook_copy,
            "visual_guide": visual_guide,
            "sticker_suggestion": sticker_suggestion,
            "highlight_tag": str(item.get("highlight_tag") or fb_item["highlight_tag"]).strip()
        })

    final_data = {
        "day_theme": day_theme,
        "stories": normalized_stories
    }

    required_str_fields = [
        "time_slot", "category", "role_badge",
        "hook_copy", "visual_guide", "sticker_suggestion", "highlight_tag"
    ]
    for i, s in enumerate(final_data["stories"], start=1):
        if int(s.get("story_number", 0)) != i:
            return False, f"第 {i} 則限動編號不連續", fallback_data
        for f_name in required_str_fields:
            val = s.get(f_name)
            if not isinstance(val, str) or not val.strip():
                return False, f"第 {i} 則限動欄位 {f_name} 為空", fallback_data

    return True, "結構與攻略鐵律驗證通過", final_data

# ----------------- 核心調用與診斷整合函式 -----------------
def generate_stories_service(mode: str, day_idx: int, user_input: str, opening_choice: str, hook_choice: str, seed_idx: int = 0) -> tuple[dict, dict]:
    api_key = get_api_key()
    fallback_data = peggy_master_engine(mode, day_idx, user_input, opening_choice, hook_choice, seed_idx)
    
    execution_log = {
        "timestamp": datetime.now(TAIPEI_TZ).strftime("%Y-%m-%d %H:%M:%S (Asia/Taipei)"),
        "model": "gemini-3.8-flash",
        "api_requested": False,
        "api_success": False,
        "attempts": 0,
        "elapsed_seconds": 0.0,
        "http_code": None,
        "error_detail": None,
        "source": "攻略智慧引擎（Peggy 7天模板＋一頁式攻略標準庫）",
        "validation_result": "標準庫驗證通過"
    }

    if not api_key:
        execution_log["error_detail"] = "未設定 GEMINI_API_KEY，已直接啟用內建攻略智慧引擎"
        return fallback_data, execution_log

    execution_log["api_requested"] = True
    is_odd = (day_idx % 2 == 1)
    story_count = 5 if "生活版" in mode else 9
    is_recruit = ("招商" in mode)
    qa_or_intro = ("公司介紹" if is_odd else "團隊 QA") if is_recruit else ("商品介紹" if is_odd else "商品 QA")
    about_or_milestone = "關於我" if is_odd else "里程碑"
    c3_name = "團隊日常" if is_recruit else "使用產品"
    c4_name = "夥伴反饋" if is_recruit else "客戶反饋"

    if story_count == 5:
        struct_desc = "1早上(露臉+共鳴+埋伏筆)、2中午(日常聊天)、3下午(工作角落+第二互動高點)、4晚上(揭曉早上伏筆答案)、5睡前(價值共鳴/關於我)"
    else:
        struct_desc = f"1生活(露臉+共鳴+早埋伏筆)、2生活(暖場延續)、3{c3_name}、4{c4_name}(誠實分享不虛構誇大)、5{qa_or_intro}(第二互動高點)、6生活(講完工作回生活)、7生活(店內魚缸/香氛角落)、8生活(晚給答案呼應第1篇伏筆)、9{about_or_milestone}(為什麼要相信你)"

    prompt = f"""你是美業品牌「真真美學」首席操盤顧問，請為創辦人「真真公主（鄭鈺真）」嚴格依據 Peggy《限動一頁式攻略》與《7天模板》產出 {story_count} 則限動 JSON。
模式：{mode}｜DAY {day_idx}
今日日常輸入：「{user_input}」
第一篇開頭句型：{opening_choice}
第二互動高點鉤子：{hook_choice}
排程結構：{struct_desc}

【必須遵守的攻略鐵律】：
1. 第一篇必須結合指定開頭句型與日常輸入，早上埋下伏筆，第 {4 if story_count==5 else 8} 篇晚上給答案。
2. 講話像聊天：每則 hook_copy 必須包含「你們」，且結尾必須丟出一個問題（以「？」結尾），字數 35~55 字自然口語，文案開頭不要加中括號分類標籤。
3. 未提供真實客戶或夥伴對話時，第 4 篇請以日常服務心得與詢問粉絲困擾為主，不虛構誇大宣稱。
4. 只輸出純 JSON 物件，包含 day_theme 與 stories 陣列（共 {story_count} 筆，每筆含 story_number, category, hook_copy, visual_guide, sticker_suggestion）。"""

    encoded_key = urllib.parse.quote(api_key, safe="-_.")
    clean_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key={encoded_key}"
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.7
        }
    }
    
    req_data = json.dumps(payload).encode("utf-8")
    start_time = time.time()

    for attempt in range(1, 3):
        execution_log["attempts"] = attempt
        req = urllib.request.Request(
            clean_url,
            data=req_data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=25.0) as response:
                execution_log["http_code"] = response.getcode()
                res_bytes = response.read()
                res = json.loads(res_bytes.decode("utf-8"))
                
                candidates = res.get("candidates")
                if not candidates or not isinstance(candidates, list):
                    raise ValueError("API 回傳無有效 candidates 欄位")
                    
                content_text = candidates[0]["content"]["parts"][0]["text"].strip()
                s_idx = content_text.find("{")
                e_idx = content_text.rfind("}")
                if s_idx == -1 or e_idx == -1:
                    raise ValueError("回傳文字中找不到有效 JSON 邊界")
                    
                parsed = json.loads(content_text[s_idx:e_idx+1])
                is_valid, val_msg, normalized_data = normalize_and_validate_story_data(parsed, fallback_data, story_count)
                execution_log["validation_result"] = val_msg
                
                if not is_valid:
                    raise ValueError(f"資料結構校驗未通過: {val_msg}")

                execution_log["api_success"] = True
                execution_log["error_detail"] = None
                execution_log["source"] = "Gemini 3.8 Flash（AI 雲端即時生成）"
                execution_log["elapsed_seconds"] = round(time.time() - start_time, 2)
                return normalized_data, execution_log

        except urllib.error.HTTPError as e:
            execution_log["http_code"] = e.code
            err_body = ""
            try:
                err_body = e.read().decode("utf-8")
            except Exception:
                pass
                
            if e.code == 429:
                execution_log["error_detail"] = "HTTP 429 (請求頻率受限): API 請求過於頻繁或達配額上限"
            elif e.code == 503:
                execution_log["error_detail"] = "HTTP 503 (官方伺服器尖峰忙碌): 模型節點短暫滿載"
            elif e.code == 400:
                execution_log["error_detail"] = f"HTTP 400 (請求格式錯誤): {err_body[:120]}"
            elif e.code == 403:
                execution_log["error_detail"] = "HTTP 403 (權限拒絕): API Key 無效或未授權"
            elif e.code == 404:
                execution_log["error_detail"] = "HTTP 404 (找不到模型節點): 請確認模型名稱支援狀態"
            else:
                execution_log["error_detail"] = f"HTTP {e.code} 錯誤: {err_body[:120]}"
                
            if e.code in (503, 429) and attempt < 2:
                time.sleep(1.2)
                continue
            break

        except urllib.error.URLError as e:
            execution_log["error_detail"] = f"網路連線或讀取逾時 (URLError/Timeout): {str(e.reason)}"
            if attempt < 2:
                time.sleep(1.0)
                continue
            break
        except json.JSONDecodeError as e:
            execution_log["error_detail"] = f"JSON 格式解析錯誤: {str(e)}"
            break
        except Exception as e:
            execution_log["error_detail"] = f"系統驗證或處理異常 ({type(e).__name__}): {str(e)}"
            break

    execution_log["elapsed_seconds"] = round(time.time() - start_time, 2)
    execution_log["source"] = "攻略智慧引擎（Peggy 7天模板＋一頁式攻略標準庫）"
    return fallback_data, execution_log

# ----------------- 渲染 7 天排程總表 HTML 函式 -----------------
def render_7day_schedule_table(active_day: int, mode: str) -> str:
    if "生活版" in mode:
        headers = ["排程日", "第1篇 (早上)", "第2篇 (中午)", "第3篇 (下午)", "第4篇 (晚上)", "第5篇 (睡前)"]
        rows_html = ""
        for d in range(1, 8):
            cls = "schedule-row-active" if d == active_day else ""
            marker = "👑 " if d == active_day else ""
            rows_html += f"""
            <tr class="{cls}">
                <td>{marker}DAY {d}</td>
                <td>早上 (埋伏筆)</td>
                <td>中午 (日常聊天)</td>
                <td class="cell-work">下午 (互動高點)</td>
                <td>晚上 (給答案)</td>
                <td class="cell-work">睡前 (價值共鳴)</td>
            </tr>"""
        return f"""
        <div class="schedule-table-wrap">
            <table class="schedule-table">
                <thead><tr>{''.join(f'<th>{h}</th>' for h in headers)}</tr></thead>
                <tbody>{rows_html}</tbody>
            </table>
        </div>"""

    is_recruit = ("招商" in mode)
    c3 = "團隊日常" if is_recruit else "使用產品"
    c4 = "夥伴反饋" if is_recruit else "客戶反饋"
    headers = ["排程日", "第1篇", "第2篇", "第3篇", "第4篇", "第5篇 (輪替)", "第6篇", "第7篇", "第8篇", "第9篇 (輪替)"]
    rows_html = ""
    for d in range(1, 8):
        odd = (d % 2 == 1)
        c5 = ("公司介紹" if odd else "團隊 QA") if is_recruit else ("商品介紹" if odd else "商品 QA")
        c9 = "關於我" if odd else "里程碑"
        cls = "schedule-row-active" if d == active_day else ""
        marker = "👑 " if d == active_day else ""
        rows_html += f"""
        <tr class="{cls}">
            <td>{marker}DAY {d}</td>
            <td>生活</td>
            <td>生活</td>
            <td class="cell-work">{c3}</td>
            <td class="cell-work">{c4}</td>
            <td class="cell-work">{c5}</td>
            <td>生活</td>
            <td>生活</td>
            <td>生活</td>
            <td class="cell-work">{c9}</td>
        </tr>"""
    return f"""
    <div class="schedule-table-wrap">
        <table class="schedule-table">
            <thead><tr>{''.join(f'<th>{h}</th>' for h in headers)}</tr></thead>
            <tbody>{rows_html}</tbody>
        </table>
    </div>"""

# ----------------- 介面頂部：白金奢華 Header -----------------
st.markdown("""
<div class="luxury-header">
    <div class="brand-crown">👑</div>
    <div class="header-title">真真公主專用 ｜ 每日限動操盤助手</div>
    <div class="header-eng">PRINCESS ZHENZHEN · DAILY STORY CURATOR</div>
    <div class="header-subtitle">「照著排、照著檢查、不知道發什麼就從主題庫挑。每天出現，就對了。」</div>
</div>
<div class="logic-banner">
    ✨ <b>順序的邏輯</b>：開場先讓人看到你 ➔ 看暖了再聊工作 ➔ 講完就回到生活 ➔ 最後一篇給他「為什麼要相信你」<br>
    ⏰ <b>發文節奏</b>：每篇隔 1–2 小時再發，不要一次發完！
</div>
""", unsafe_allow_html=True)

# ----------------- 01 每日發文模板 & 七天排程表 (台灣標準時間 Asia/Taipei) -----------------
now_taipei = datetime.now(TAIPEI_TZ)
today_auto_idx = now_taipei.isoweekday()
day_labels = {
    1: "DAY 1（週一｜商品介紹＋關於我）",
    2: "DAY 2（週二｜商品 QA＋里程碑）",
    3: "DAY 3（週三｜商品介紹＋關於我）",
    4: "DAY 4（週四｜商品 QA＋里程碑）",
    5: "DAY 5（週五｜商品介紹＋關於我）",
    6: "DAY 6（週六｜商品 QA＋里程碑）",
    7: "DAY 7（週日｜商品介紹＋關於我）"
}

c_mode, c_day = st.columns([1.15, 1])
with c_mode:
    selected_mode = st.selectbox(
        "📋 01 每日發文模板",
        [
            "賣貨版（一天 9 篇｜生活夾心賣貨）",
            "招商版（一天 9 篇｜團隊與事業魅力）",
            "生活版（一天 5 篇｜先連續發滿 7 天）"
        ],
        index=0
    )
with c_day:
    selected_day_idx = st.selectbox(
        f"📅 七天排程表（台灣時間：{now_taipei.strftime('%m/%d')} 週{['一','二','三','四','五','六','日'][today_auto_idx-1]}）",
        options=[1, 2, 3, 4, 5, 6, 7],
        format_func=lambda x: day_labels[x],
        index=today_auto_idx - 1
    )

is_odd_day = (selected_day_idx % 2 == 1)
slot5_name = "商品介紹" if is_odd_day else "商品 QA"
slot9_name = "關於我" if is_odd_day else "里程碑"
if "招商" in selected_mode:
    slot5_name = "公司介紹" if is_odd_day else "團隊 QA"

if "生活版" in selected_mode:
    st.markdown("""
    <div class="grid-bar">
        <span class="grid-pill">第1篇 早上(埋伏筆)</span>
        <span class="grid-pill">第2篇 中午(聊天)</span>
        <span class="grid-pill-work">第3篇 下午(互動高點)</span>
        <span class="grid-pill">第4篇 晚上(給答案)</span>
        <span class="grid-pill-work">第5篇 睡前(價值)</span>
    </div>
    """, unsafe_allow_html=True)
else:
    c3_label = "團隊日常" if "招商" in selected_mode else "使用產品"
    c4_label = "夥伴反饋" if "招商" in selected_mode else "客戶反饋"
    st.markdown(f"""
    <div class="grid-bar">
        <span class="grid-pill">第1篇 生活(埋伏筆)</span>
        <span class="grid-pill">第2篇 生活</span>
        <span class="grid-pill-work">第3篇 {c3_label}</span>
        <span class="grid-pill-work">第4篇 {c4_label}</span>
        <span class="grid-pill-work">第5篇 {slot5_name}</span>
        <span class="grid-pill">第6篇 生活</span>
        <span class="grid-pill">第7篇 生活</span>
        <span class="grid-pill">第8篇 生活(給答案)</span>
        <span class="grid-pill-work">第9篇 {slot9_name}</span>
    </div>
    """, unsafe_allow_html=True)

with st.expander("📊 查看完整《七天排程表 · 賣貨版 / 招商版 / 生活版》對照表", expanded=False):
    st.caption("💡 **生活篇天天都在，工作篇輪流換：照著這張表發，七天不會重複，也不會卡住**（第 5 篇與第 9 篇隔天輪替）：")
    st.markdown(render_7day_schedule_table(selected_day_idx, selected_mode), unsafe_allow_html=True)

# ----------------- 04 第一篇開頭句型 & 05 互動鉤子設定 -----------------
col_op, col_hk = st.columns([1, 1])
with col_op:
    opening_choice = st.selectbox(
        "🎯 04 第一篇開頭句型",
        list(OPENING_PATTERNS.keys()),
        index=0
    )
with col_hk:
    hook_choice = st.selectbox(
        "🪝 05 第二高點互動鉤子",
        list(INTERACTION_HOOKS.keys()),
        index=0
    )

# ----------------- Session State 初始化與 06 生活主題發想庫 Callback 連動 -----------------
if "draft_input" not in st.session_state:
    st.session_state["draft_input"] = ""
if "story_plan" not in st.session_state:
    st.session_state["story_plan"] = None
if "execution_log" not in st.session_state:
    st.session_state["execution_log"] = None
if "seed_counter" not in st.session_state:
    st.session_state["seed_counter"] = 0
if "selected_topic_notice" not in st.session_state:
    st.session_state["selected_topic_notice"] = ""

def on_select_topic(topic_label: str, topic_text: str):
    """點擊 06 生活主題發想庫按鈕時：1. 同步寫入乾淨日常語句至輸入框 2. 直接秒排今日限動腳本"""
    q_hint = TOPIC_QUESTIONS_MAP.get(topic_label, "")
    full_seed_text = f"{topic_text}（{q_hint}）" if q_hint else topic_text
    st.session_state["draft_input"] = topic_text
    st.session_state["selected_topic_notice"] = f"✅ 已套用話題【{topic_label}】：「{topic_text}」，並為公主自動排好下方今日限動腳本！"
    plan_res = peggy_master_engine(
        selected_mode,
        selected_day_idx,
        full_seed_text,
        opening_choice,
        hook_choice,
        st.session_state["seed_counter"]
    )
    st.session_state["story_plan"] = plan_res
    st.session_state["execution_log"] = {
        "timestamp": datetime.now(TAIPEI_TZ).strftime("%Y-%m-%d %H:%M:%S (Asia/Taipei)"),
        "model": "gemini-3.8-flash",
        "api_requested": False,
        "api_success": False,
        "attempts": 0,
        "elapsed_seconds": 0.01,
        "http_code": None,
        "error_detail": None,
        "source": f"06 主題庫一鍵快排（{topic_label}）",
        "validation_result": "標準庫驗證通過"
    }
    st.session_state["seed_counter"] += 1

with st.expander("💡 06 生活主題發想庫（不知道發什麼？點一下直接帶入並秒出腳本！）", expanded=False):
    st.caption("👀 **看得到的日常**（點擊任一按鈕，自動帶入下方輸入框並立即排好腳本）：")
    vis_cols = st.columns(2)
    for idx, (k, val) in enumerate(LIFE_TOPICS_VISIBLE.items()):
        vis_cols[idx % 2].button(
            k,
            key=f"vis_{idx}",
            use_container_width=True,
            on_click=on_select_topic,
            args=(k, val)
        )

    st.caption("💭 **看不到的想法**（點擊任一按鈕，自動帶入下方輸入框並立即排好腳本）：")
    th_cols = st.columns(2)
    for idx, (k, val) in enumerate(LIFE_TOPICS_THOUGHTS.items()):
        th_cols[idx % 2].button(
            k,
            key=f"th_{idx}",
            use_container_width=True,
            on_click=on_select_topic,
            args=(k, val)
        )

if st.session_state["selected_topic_notice"]:
    st.success(st.session_state["selected_topic_notice"])

# ----------------- 日常輸入框 (深褐清晰字體，不反白) -----------------
user_thought = st.text_area(
    "💬 公主今天有什麼日常、心情或客人對話？（隨興打一句，或從上方 06 主題庫點選）",
    key="draft_input",
    placeholder="例如：客人送了一杯咖啡很好喝，心裡暖呼呼的...",
    height=85
)

generate_btn = st.button("✨ 照攻略一鍵排好今日限動腳本（早埋伏筆＋晚給答案＋精選歸檔）", use_container_width=True)

if generate_btn:
    st.session_state["selected_topic_notice"] = ""
    final_input = user_thought.strip() if user_thought.strip() else "今天在工作室準備迎接預約的公主們，心情特別充實美好"
    with st.spinner("👑 軍師正在依《限動一頁式攻略》與《7天模板》排定今日腳本..."):
        plan_res, log_res = generate_stories_service(
            selected_mode,
            selected_day_idx,
            final_input,
            opening_choice,
            hook_choice,
            st.session_state["seed_counter"]
        )
        st.session_state["story_plan"] = plan_res
        st.session_state["execution_log"] = log_res
        st.session_state["seed_counter"] += 1

# ----------------- 渲染產出腳本卡片 (含 XSS 逃逸保護) -----------------
plan = st.session_state.get("story_plan")
log = st.session_state.get("execution_log")

if plan and isinstance(plan, dict):
    source_str = log.get("source", "系統生成") if log else "系統生成"
    is_cloud_ai = bool(log and log.get("api_success"))
    
    badge_bg = "#EBF7EE" if is_cloud_ai else "#FAF3E4"
    badge_border = "#81C784" if is_cloud_ai else "#DEC393"
    badge_color = "#2E7D32" if is_cloud_ai else "#7A5114"
    badge_icon = "✨" if is_cloud_ai else "👑"

    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; align-items:center; margin: 12px 0 10px 0; padding: 9px 14px; background: {badge_bg}; border: 1px solid {badge_border}; border-radius: 10px;">
        <span style="font-size:12.5px; font-weight:700; color:{badge_color};">{badge_icon} 生成引擎：{html.escape(source_str)}</span>
        <span style="font-size:11.5px; font-weight:600; color:#6E5A47;">耗時：{log.get('elapsed_seconds', 0.0) if log else 0.0}s</span>
    </div>
    """, unsafe_allow_html=True)

    escaped_theme = html.escape(str(plan.get('day_theme', '')))
    st.markdown(f"""
    <div style="margin: 6px 0 14px 0; padding: 11px 14px; background: #FDF8EE; border-radius: 12px; border: 1.5px dashed #C89B4B; text-align: center;">
        <span style="color: #6B4915; font-size: 13.5px; font-weight: 700;">🌟 {escaped_theme}</span>
    </div>
    """, unsafe_allow_html=True)
    
    for item in plan.get("stories", []):
        story_num = html.escape(str(item.get('story_number', '')))
        time_slot = html.escape(str(item.get('time_slot', '間隔1.5hr')))
        category = html.escape(str(item.get('category', '')))
        role_badge = html.escape(str(item.get('role_badge', '')))
        hook_copy = html.escape(str(item.get('hook_copy', '')))
        visual_guide = html.escape(str(item.get('visual_guide', '')))
        sticker_suggestion = html.escape(str(item.get('sticker_suggestion', '')))
        highlight_tag = html.escape(str(item.get('highlight_tag', '')))

        st.markdown(f"""
        <div class="story-card-luxury">
            <div class="card-meta-bar">
                <span class="badge-number">STORY 0{story_num}</span>
                <span class="badge-time">⏰ 建議發佈：{time_slot}</span>
                <span class="badge-category">{category}</span>
            </div>
            <div class="role-tag">{role_badge}</div>
            <div class="luxury-hook-text">「{hook_copy}」</div>
            <div class="meta-line"><span class="meta-tag-gold">📸 建議配圖：</span>{visual_guide}</div>
            <div class="meta-line"><span class="meta-tag-gold">🏷️ 互動貼圖：</span>{sticker_suggestion}</div>
            <div class="highlight-box">{highlight_tag}</div>
            <div class="safety-note">⚠️ 排版檢查：一張限動字體最多2種、字色最多2種｜字放安全區，底圖太亮先調暗再放字｜不發產品DM、不發AI生成滿版圖</div>
        </div>
        """, unsafe_allow_html=True)
        st.code(item.get('hook_copy', ''), language="text")

# ----------------- 底部常駐：02 發文前檢查 & 03 精選清單神回覆 -----------------
st.markdown("---")
with st.expander("✅ 02 發文前檢查表（發限動前打勾確認，每天出現就對了）", expanded=True):
    st.checkbox("第一篇：看得到你 ＋ 一句共鳴 ＋ 一個互動貼紙", value=True, key="chk1")
    st.checkbox("第二個互動高點：9 篇裡再挑一篇拉高互動（已鎖定於第 5 篇／生活版第 3 篇）", value=True, key="chk2")
    st.checkbox("講話像聊天：「我」換成「你們」，結尾丟一個問題", value=True, key="chk3")
    st.checkbox("生活有連貫：早上埋伏筆，晚上給答案", value=True, key="chk4")
    st.checkbox("一張限動：字體最多兩種、字色最多兩種", value=False, key="chk5")
    st.checkbox("字放安全區，底圖太亮先調暗再放字", value=False, key="chk6")
    st.checkbox("不發產品 DM、不發 AI 生成的滿版圖", value=False, key="chk7")
    st.checkbox("🔥 有人回，就一定要回，那是你今天最熱的名單", value=False, key="chk8")

with st.expander("📌 03 精選清單配置 ＆ 私訊秒回話術（一鍵複製）", expanded=False):
    st.markdown("""
    **【賣貨版 5 個精選】**：`關於我` · `產品介紹` · `客戶反饋` · `產品 QA` · `里程碑`  
    **【招商版 6 個精選】**：`關於我` · `團隊／公司介紹` · `夥伴反饋` · `團隊 QA` · `團隊理念` · `里程碑`  
    💡 *精選，是在替你回答 80% 的問題。私訊的問題一直很像？代表精選還不完整，那就是你要補的地方。*  
    👇 **再被問到，直接複製下面這句回她：**
    """)
    st.code("我精選的『QA』有整理，你先看看～", language="text")

if log:
    with st.expander("📊 系統執行診斷與 API 監控紀錄", expanded=False):
        c1, c2, c3 = st.columns(3)
        c1.metric("指定調用模型", str(log.get("model")))
        c2.metric("HTTP 狀態碼", str(log.get("http_code")) if log.get("http_code") else "內建引擎")
        c3.metric("總響應耗時", f"{log.get('elapsed_seconds', 0.0)} 秒")
        
        st.write(f"**執行時間點**：{log.get('timestamp')}")
        st.write(f"**實際使用來源**：`{log.get('source')}`")
        st.write(f"**資料校驗狀態**：`{log.get('validation_result')}`")
        if log.get("error_detail"):
            st.info(f"ℹ️ **連線診斷紀錄**：{log.get('error_detail')}（系統已自動由內建攻略智慧引擎無縫輸出）")
        else:
            st.success("✅ **連線狀態**：呼叫並校驗成功，無任何錯誤。")

st.markdown("""
<div style="text-align:center; padding: 14px 0 8px 0; color:#8A7968; font-size:12px; letter-spacing:1px;">
    最後記得：<b style="color:#7A5114;">流量很重要，但更重要的是：你要影響別人什麼？</b>
</div>
""", unsafe_allow_html=True)
