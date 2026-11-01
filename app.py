import os
import json
import time
import html
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta

# 優先採用標準時區模組，若環境不支援則以 UTC+8 備援
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

# 極致美業名媛奢華風 CSS (iPhone 18 Pro Max 完美自適應、絕不折字破版)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700&family=Noto+Serif+TC:wght@500;700;900&family=Noto+Sans+TC:wght@300;400;500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Noto Sans TC', -apple-system, BlinkMacSystemFont, sans-serif;
        -webkit-font-smoothing: antialiased;
    }
    
    .stApp {
        background: radial-gradient(circle at 50% 10%, #1C1917 0%, #0C0A09 100%) !important;
        color: #F5EBE1 !important;
    }
    
    .luxury-header {
        text-align: center;
        padding: 22px 14px 18px 14px;
        background: linear-gradient(145deg, rgba(38, 33, 29, 0.92) 0%, rgba(20, 18, 16, 0.98) 100%);
        border-radius: 20px;
        border: 1px solid rgba(212, 175, 55, 0.38);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.65), inset 0 1px 0 rgba(255, 223, 128, 0.22);
        margin-bottom: 16px;
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
        margin-bottom: 5px;
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
        font-size: clamp(11px, 3.1vw, 13px);
        color: #E8BE6B;
        letter-spacing: 0.5px;
        font-weight: 500;
        line-height: 1.4;
    }

    .logic-banner {
        background: rgba(212, 175, 55, 0.08);
        border: 1px solid rgba(212, 175, 55, 0.28);
        border-radius: 12px;
        padding: 10px 12px;
        margin-bottom: 14px;
        font-size: 12px;
        color: #E6CFA8;
        line-height: 1.55;
        text-align: center;
    }
    
    .status-card-gold {
        background: linear-gradient(145deg, rgba(42, 36, 30, 0.78) 0%, rgba(26, 22, 18, 0.92) 100%);
        border: 1px solid rgba(212, 175, 55, 0.28);
        border-radius: 14px;
        padding: 10px 12px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        margin-bottom: 10px;
    }
    .status-label {
        font-size: 10.5px;
        color: #A6917E;
        margin-bottom: 3px;
        letter-spacing: 0.8px;
    }
    .status-value {
        font-size: 13.5px;
        font-weight: 600;
        color: #F8E6C8;
    }

    .grid-bar {
        display: flex;
        flex-wrap: wrap;
        gap: 4px;
        justify-content: center;
        margin: 8px 0 14px 0;
    }
    .grid-pill {
        font-size: 11px;
        padding: 3px 8px;
        border-radius: 8px;
        background: rgba(38, 33, 29, 0.9);
        border: 1px solid rgba(212, 175, 55, 0.25);
        color: #D3C3B3;
    }
    .grid-pill-work {
        font-size: 11px;
        padding: 3px 8px;
        border-radius: 8px;
        background: rgba(212, 175, 55, 0.18);
        border: 1px solid #D4AF37;
        color: #FFF1D0;
        font-weight: 600;
    }
    
    div[data-baseweb="textarea"] {
        background-color: rgba(28, 25, 23, 0.88) !important;
        border: 1px solid rgba(212, 175, 55, 0.35) !important;
        border-radius: 14px !important;
        box-shadow: inset 0 2px 6px rgba(0, 0, 0, 0.5) !important;
    }
    div[data-baseweb="textarea"] textarea {
        color: #F5ECE3 !important;
        font-size: 14px !important;
        line-height: 1.6 !important;
    }
    label[data-testid="stWidgetLabel"] p {
        color: #E8D9CB !important;
        font-size: 13.5px !important;
        font-weight: 600 !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #F0CF86 0%, #D4AF37 50%, #9E7422 100%) !important;
        color: #1A1208 !important;
        font-weight: 700 !important;
        font-size: 15.5px !important;
        letter-spacing: 1px !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 12px 18px !important;
        box-shadow: 0 6px 20px rgba(212, 175, 55, 0.35) !important;
    }
    
    .story-card-luxury {
        background: linear-gradient(160deg, rgba(34, 30, 26, 0.94) 0%, rgba(20, 18, 16, 0.98) 100%);
        border-radius: 16px;
        padding: 16px 15px;
        margin-bottom: 14px;
        border: 1px solid rgba(212, 175, 55, 0.28);
        border-left: 5px solid #D4AF37;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.45);
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
        color: #1C1917;
        background: linear-gradient(135deg, #FFF1D0 0%, #E8BE6B 100%);
        padding: 2px 10px;
        border-radius: 20px;
    }
    .badge-time {
        font-size: 11px;
        color: #D3C3B3;
        background: rgba(255,255,255,0.06);
        padding: 2px 8px;
        border-radius: 12px;
    }
    .badge-category {
        font-size: 11.5px;
        font-weight: 600;
        color: #E6CFA8;
        background: rgba(212, 175, 55, 0.15);
        padding: 2px 10px;
        border-radius: 20px;
        border: 1px solid rgba(212, 175, 55, 0.35);
    }
    .role-tag {
        font-size: 11.5px;
        color: #F0CF86;
        font-weight: 600;
        margin-bottom: 8px;
        letter-spacing: 0.3px;
    }
    .luxury-hook-text {
        font-size: 14.5px;
        font-weight: 500;
        color: #FFFFFF;
        line-height: 1.6;
        margin-bottom: 10px;
        padding: 11px 13px;
        background: rgba(14, 12, 10, 0.7);
        border-radius: 10px;
        border-left: 3px solid #E8BE6B;
    }
    .meta-line {
        font-size: 12.5px;
        color: #C8B9A6;
        margin-bottom: 5px;
        line-height: 1.5;
    }
    .meta-tag-gold {
        color: #E8BE6B;
        font-weight: 600;
    }
    .highlight-box {
        margin-top: 8px;
        padding: 6px 10px;
        background: rgba(212, 175, 55, 0.1);
        border-radius: 8px;
        font-size: 11.5px;
        color: #F5E0B7;
        border: 1px dashed rgba(212, 175, 55, 0.35);
    }
    .safety-note {
        font-size: 11px;
        color: #8C7A6B;
        margin-top: 6px;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- 攻略資料庫 -----------------
OPENING_PATTERNS = {
    "自動依情境匹配最佳句型": "auto",
    "句型①：「有沒有人跟我一樣⋯⋯」＋投票": "有沒有人跟我一樣",
    "句型②：「你們會不會也⋯⋯」＋表情滑桿": "你們會不會也",
    "句型③：「你們猜猜看⋯⋯」＋測驗（下一篇揭曉）": "你們猜猜看",
    "句型④：「今天發生一件⋯⋯的事」＋先留懸念後面講": "今天發生一件"
}

INTERACTION_HOOKS = {
    "幫我選（A 還是 B？投票參與決定）": "幫我選",
    "猜猜看（測驗貼紙猜答案，下一篇揭曉）": "猜猜看",
    "留言領乾貨（回關鍵字，私訊傳資源）": "留言領乾貨",
    "QA 收題日（提問貼紙收題，隔天一題一篇）": "QA收題日",
    "小算命／心理測驗（回生日月份給專屬結果）": "心理測驗",
    "抽卡（選 1、2、3，一個個回解讀）": "抽卡"
}

LIFE_TOPICS_VISIBLE = {
    "☀️ 早晨儀式": "今天起床第一件事就是準備開啟美好的一天（你們起床第一件事做什麼？）",
    "🍰 今天吃什麼": "原本想隨便吃，最後還是忍不住買了最愛的美食甜點（想吃 A 最後吃了 B 的舉手）",
    "🚗 通勤路上": "今天去店裡的路上看到一家超有質感的店（路上有沒有一家店一直想進去？）",
    "💑 家人／另一半": "今天發生的日常對話真的讓我哭笑不得（你家那位也常讓你傻眼嗎？）",
    "🐠 毛小孩／店寵": "看著店裡魚缸的小魚小蝦游來游去超級療癒（你們家毛孩也會這樣看你嗎？）",
    "💆‍♀️ 運動／保養": "再忙還是要留時間給自己好好保養維持狀態（你們都怎麼逼自己運動或保養？）",
    "🕯️ 工作角落": "在真真美學待最久的溫馨小角落，點上香氛超放鬆（你待最久的角落長怎樣？）",
    "🌿 週末小出遊": "趁著空檔偷得浮生半日閒出門晃晃透氣（猜猜我今天放假跑去哪？）"
}

LIFE_TOPICS_THOUGHTS = {
    "🔋 今天的心情": "忙完一輪坐下來喝口咖啡，瞬間覺得電力滿滿（你們累了都怎麼充電？）",
    "💣 踩雷分享": "以前繳過好多保養冤枉錢，才懂成分跟手法有多重要（你們買過最後悔的東西是？）",
    "📚 正在學的事": "最近一直在研究怎麼讓膚況更穩更透亮的新技術（你們最近有在學什麼嗎？）",
    "📸 以前的我": "無意間翻到以前的照片，感嘆女人真的越懂得愛自己越美（你們敢翻三年前的照片嗎？）",
    "🙏 想謝謝的人": "心裡很感激每位願意把臉蛋跟信任交給我的客人（你最近最想謝謝誰？）",
    "💎 我的堅持": "寧可慢工細活也不做速成推銷，是我做美業不變的原則（你有默默堅持很久的事嗎？）",
    "✨ 最近在想": "把日子過得有質感、內心通透從容，就是最棒的狀態（你們覺得怎樣才叫過得好？）",
    "☕ 小確幸": "客人送了一杯超好喝的咖啡，心裡暖呼呼的（你們今天最開心的是什麼？）"
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
        # 僅去除外部多餘空格與誤包的引號，完整保留 Base64/Key 原生字符
        return key.strip().strip("'\"")
    return ""

# ----------------- 資料結構完整性驗證器 -----------------
def validate_story_data(data: dict, expected_count: int) -> tuple[bool, str]:
    if not isinstance(data, dict):
        return False, "模型回傳格式非 JSON 物件"
    
    day_theme = data.get("day_theme")
    if not isinstance(day_theme, str) or not day_theme.strip():
        return False, "缺少有效的 day_theme 主軸文字"
    
    stories = data.get("stories")
    if not isinstance(stories, list):
        return False, "stories 欄位必須為列表"
    
    if len(stories) != expected_count:
        return False, f"限動篇數不符 (預期 {expected_count} 則，實際回傳 {len(stories)} 則)"
    
    required_str_fields = [
        "time_slot", "category", "role_badge", 
        "hook_copy", "visual_guide", "sticker_suggestion", "highlight_tag"
    ]
    
    for i, s in enumerate(stories, start=1):
        if not isinstance(s, dict):
            return False, f"第 {i} 則限動非字典物件"
        
        # 嚴格驗證序號連續性
        raw_num = s.get("story_number")
        try:
            if int(raw_num) != i:
                return False, f"第 {i} 則限動編號不連續 (收到: {raw_num})"
        except (TypeError, ValueError):
            return False, f"第 {i} 則限動編號格式錯誤"
        
        # 檢查欄位非空字串
        for field in required_str_fields:
            val = s.get(field)
            if not isinstance(val, str) or not val.strip():
                return False, f"第 {i} 則限動缺少必填欄位或內容為空: {field}"
                
    return True, "驗證通過"

# ----------------- 本地保底備援引擎 -----------------
def peggy_master_engine(mode: str, day_idx: int, user_input: str, opening_choice: str, hook_choice: str, seed_idx: int = 0) -> dict:
    clean_in = user_input.strip().rstrip("。！!？?～~，,.")
    is_odd = (day_idx % 2 == 1)
    v = seed_idx % 3

    if mode == "生活版（一天 5 篇｜先連續發滿 7 天）":
        return {
            "day_theme": f"生活版 Day {day_idx}｜先讓大家喜歡妳的生活，早埋伏筆、晚給答案",
            "stories": [
                {
                    "story_number": 1,
                    "time_slot": "09:00 早上",
                    "category": "早上｜生活暖場",
                    "role_badge": "🌅 第一篇：看得到你＋一句共鳴＋互動貼紙（早上埋伏筆）",
                    "hook_copy": f"有沒有人跟我一樣，一早遇到「{clean_in}」整個人心情都亮起來了？猜猜我今天接下來要去忙什麼大事？你們起床第一件事都做什麼？",
                    "visual_guide": "真真露臉微笑自拍或手拿飲品/日常晨間視角（底圖調暗放安全區）",
                    "sticker_suggestion": "投票貼紙：已經起床開工🙋‍♀️ / 還在賴床充電😴",
                    "highlight_tag": "免存精選（日常破冰拉高首篇完播率）"
                },
                {
                    "story_number": 2,
                    "time_slot": "12:30 中午",
                    "category": "中午｜日常互動",
                    "role_badge": "☀️ 講話像聊天：「我」換成「你們」，結尾丟問題",
                    "hook_copy": "中午吃飯時間到啦～忙了一個早上終於能喘口氣！你們中午通常都吃便當還是輕食？有沒有推薦台南必吃的午餐口袋名單？",
                    "visual_guide": "午餐美食或私房餐點隨手拍（不發AI滿版圖，最多2種字體）",
                    "sticker_suggestion": "問答貼紙：推薦你們最愛的午餐給我👇",
                    "highlight_tag": "免存精選（收集私訊互動名單）"
                },
                {
                    "story_number": 3,
                    "time_slot": "15:30 下午",
                    "category": "下午｜工作角落",
                    "role_badge": f"🔥 第二互動高點｜套用鉤子：{hook_choice}",
                    "hook_copy": "下午窩在這個待最久的溫馨角落，看著魚缸的小魚游來游去超療癒✨ 你們工作累了都怎麼充電？選 A 喝下午茶還是 B 放空五分鐘？",
                    "visual_guide": "店內魚缸小魚小蝦或香氛角落短片（真實自然光）",
                    "sticker_suggestion": "投票貼紙：A 絕對要下午茶☕️ / B 安靜放空🌿",
                    "highlight_tag": "免存精選（誰投了票記得私訊聊兩句）"
                },
                {
                    "story_number": 4,
                    "time_slot": "19:00 晚上",
                    "category": "晚上｜伏筆揭曉",
                    "role_badge": "🌙 生活有連貫：早上埋伏筆，晚上給答案",
                    "hook_copy": f"來揭曉早上的伏筆啦！因為「{clean_in}」帶來的滿滿好心情，今天把整個空間與預約準備都整理妥當✨ 你們今天過得充實嗎？",
                    "visual_guide": "傍晚收工後的質感空間或完成事項的滿意隨手拍",
                    "sticker_suggestion": "表情滑桿：給今天的充實度打幾分💯",
                    "highlight_tag": "免存精選（前後連貫拉高鐵粉黏著度）"
                },
                {
                    "story_number": 5,
                    "time_slot": "22:00 睡前",
                    "category": "睡前｜價值共鳴",
                    "role_badge": "💫 睡前暖心收尾：你要影響別人什麼？",
                    "hook_copy": "睡前保養完看著鏡子，覺得女人把日子過得從容有底氣就是最美的狀態💛 你們覺得怎樣才叫過得好？晚安前跟我分享吧？",
                    "visual_guide": "柔和黃光下的居家或店內靜謐角落",
                    "sticker_suggestion": "問答貼紙：你們覺得怎樣才叫過得好？💭",
                    "highlight_tag": "📌 可存精選：【關於我】"
                }
            ]
        }

    # 賣貨版 / 招商版
    if mode == "招商版（一天 9 篇｜團隊與事業魅力）":
        cat3 = "團隊日常"
        cat4 = "夥伴反饋"
        cat5 = "公司介紹" if is_odd else "團隊 QA"
        cat9 = "關於我" if is_odd else "里程碑"
        hl3, hl4, hl5, hl9 = "團隊/公司介紹", "夥伴反饋", ("團隊/公司介紹" if is_odd else "團隊 QA"), cat9
    else:
        cat3 = "使用產品"
        cat4 = "客戶反饋"
        cat5 = "商品介紹" if is_odd else "商品 QA"
        cat9 = "關於我" if is_odd else "里程碑"
        hl3, hl4, hl5, hl9 = "產品介紹", "客戶反饋", ("產品介紹" if is_odd else "產品 QA"), cat9

    p_key = OPENING_PATTERNS.get(opening_choice, "auto")
    if p_key == "有沒有人跟我一樣" or (p_key == "auto" and v == 0):
        h1 = f"有沒有人跟我一樣，只要遇到「{clean_in}」整個人心情就瞬間變超好？而且今天還準備了一個小驚喜要忙，你們今天早上有沒有發生什麼小確幸？"
        s1 = "投票貼紙：我也是小確幸派🙋‍♀️ / 今天忙到飛起🔥"
    elif p_key == "你們會不會也" or (p_key == "auto" and v == 1):
        h1 = f"你們會不會也覺得，生活裡有「{clean_in}」這種溫暖小事就特別有動力？先留個小懸念，晚上再告訴你們今天忙了什麼！你們今天精神好嗎？"
        s1 = "表情滑桿：滑動告訴我你們今天的能量值✨"
    elif p_key == "你們猜猜看":
        h1 = f"你們猜猜看！今天因為「{clean_in}」開啟超棒的一天，接下來預約滿檔的我會先忙哪件事？答案下一篇揭曉，你們猜對了嗎？"
        s1 = "測驗貼紙：猜猜真真今天先做哪件事？（A 準備施作 / B 整理店內小花園）"
    else:
        h1 = f"今天發生一件超暖心的事：{clean_in}🥰 先留個懸念，後面接著講為什麼這件事讓我感動了一整天！你們今天起床第一件事做什麼？"
        s1 = "投票貼紙：想聽後續舉手🙋‍♀️ / 先幫真真按個讚💛"

    h2 = "接續上一篇～帶著滿滿好心情把工作室打理得香香亮亮的✨ 開場先跟你們聊聊天，你們平時最喜歡什麼味道的香氛或飲品？"

    if "招商" in mode:
        h3 = "看暖了來聊點正事✨ 很多姊妹問我們團隊平時怎麼共同切磋技術？看這專注打磨手法的畫面，你們是不是也喜歡這種一起成長的踏實感？"
        v3 = "團隊實操練習或專業手法討論紀錄照（字體最多2種）"
        h4 = "看著夥伴一步一腳印把護膚細節落實好，客人做完也給予肯定～看到大家靠專業贏得自信，你們是不是也想為熱愛的事勇敢一次？"
        v4 = "夥伴心得分享或日常操作交流對話截圖（隱去隱私個資）"
    else:
        h3 = "看暖了來看看今天的專業護膚時光💆‍♀️ 精華液搭配手法溫柔導入肌底，你們看這水潤細緻的質地是不是很舒壓？你們平時都怎麼保養肌膚？"
        v3 = "手部專業操作微距或精華液質地特寫（自然光線拍攝）"
        h4 = "剛剛客人護理後摸摸臉頰說感覺很水潤舒服，聽了心裡特別踏實～若你們平時遇到換季乾燥，最希望改善哪個肌膚困擾呢？"
        v4 = "真實客人反饋截圖或施作後透亮光澤側拍（無真實回饋時請依實況記錄）"

    h_type = INTERACTION_HOOKS.get(hook_choice, "幫我選")
    if is_odd:
        if h_type == "留言領乾貨":
            h5 = "為什麼深層保濕對肌膚這麼關鍵？因為基底水分做足，膚況自然穩定✨ 我整理了一份《日常基礎保養避雷指南》，你們想看嗎？回覆【保養】傳給你們？"
            s5 = "問答貼紙：輸入【保養】領取實用基礎指南🎁"
        elif h_type == "抽卡":
            h5 = "今天施作這道流程手感特別棒✨ 來玩個膚況小互動！你們現在最想加強 1水分保濕、2日常清潔、還是 3舒緩修護？選 1、2、3 我私訊跟你們交流？"
            s5 = "投票/問答貼紙：選 1、2、3 聊聊妳當前重視的護理重點🃏"
        else:
            h5 = "店裡很受歡迎的深層溫和護理流程👑 著重在軟化代謝角質並深層補水！你們日常保養時最在乎 A清爽透亮 還是 B潤澤細緻？幫我選一個？"
            s5 = "投票貼紙：A 清爽透亮✨ / B 潤澤細緻💧"
        v5 = "護理產品或專業設備乾淨擺拍（文字放安全區）"
    else:
        if h_type == "QA收題日":
            h5 = "今天是每週護膚 QA 交流日✨ 常有朋友問外油內乾怎麼保養？關鍵在做好溫和清潔與水分補給！先看我精選『產品 QA』，你們還有哪些保養疑問呢？"
            s5 = "提問貼紙：留下你們的護膚困擾，隔天一題一篇解答💬"
        else:
            h5 = "大家常問：護膚多久安排一次比較合適？建議順應肌膚代謝週期穩定調理～猜猜看護膚後頭幾天最重要的是什麼？你們平時洗臉都用溫水還是冷水？"
            s5 = "測驗貼紙：做完深層護膚後最需注意？（A 加強保濕與防曬 / B 馬上使用去角質）"
        v5 = "真真專業工作側拍或重點 QA 排版圖（字體顏色最多2種）"

    h6 = "聊完專業工作，切換回下午的放鬆生活模式🌿 泡杯熱茶喘口氣，你們下午累了都怎麼幫自己充電？會偷吃小點心嗎？"
    h7 = "在工作室待最久的角落，看著魚缸裡的小魚小蝦悠哉游動真的好解壓🐠 你們待最久的辦公或生活角落長怎樣？也有療癒小物嗎？"
    h8 = f"來給早上的伏筆答案啦🌙 今天因為「{clean_in}」心情很好，把每位客人都用心服務好，今天的排程也順利完成！你們今天最開心的一件事是什麼？"

    if is_odd:
        h9 = "走過生活起伏才懂得：女人最好的底氣是獨立與通透👑 在真真美學我堅持不強迫推銷，只給妳們真正安心的專業呵護。你們覺得怎樣才叫活得漂亮？"
        v9 = "真真知性優雅工作側拍或個人質感形象照"
        s9 = "表情滑桿：一起成為獨立發光的大女主👑"
    else:
        h9 = "看著預約表上熟悉的信任與交流，謝謝妳們願意把臉蛋交給我的專業✨ 流量很重要，但我更在乎帶給你們多少從容與自信！這週想預約的公主準備好了嗎？"
        v9 = "專業證書、進修日常紀錄或與客人間的溫暖互動照"
        s9 = "投票貼紙：準備好這週來放鬆護膚✨ / 想先詢問細節🙋‍♀️"

    return {
        "day_theme": f"DAY {day_idx}（{'奇數天：商品介紹＋關於我' if is_odd else '偶數天：商品 QA＋里程碑'}）｜早埋伏筆、晚給答案",
        "stories": [
            {"story_number": 1, "time_slot": "09:00", "category": "生活", "role_badge": "🌅 第一篇：看得到你＋一句共鳴＋互動貼紙（早上埋伏筆｜互動高點①）", "hook_copy": h1, "visual_guide": "真真露臉親切微笑或日常晨間第一視角（底圖調暗放安全區）", "sticker_suggestion": s1, "highlight_tag": "免存精選（誰回了這篇就是今天最熱的名單，一定要回！）"},
            {"story_number": 2, "time_slot": "10:30", "category": "生活", "role_badge": "☕ 第二篇：生活暖場延續，講話像閨蜜聊天", "hook_copy": h2, "visual_guide": "工作室晨間光線或飲品隨手拍（字體≤2種、字色≤2種）", "sticker_suggestion": "投票貼紙：咖啡派☕️ / 茶飲派🍵", "highlight_tag": "免存精選（把觀眾看暖了，下一篇準備進工作）"},
            {"story_number": 3, "time_slot": "12:00", "category": cat3, "role_badge": "💆‍♀️ 第三篇：看暖了再聊工作（專業過程展示）", "hook_copy": h3, "visual_guide": v3, "sticker_suggestion": "表情滑桿：這細緻質感給幾分✨", "highlight_tag": f"📌 建議存入精選：【{hl3}】"},
            {"story_number": 4, "time_slot": "13:30", "category": cat4, "role_badge": "🌟 第四篇：真實見證（讓效果自己說話）", "hook_copy": h4, "visual_guide": v4, "sticker_suggestion": "投票貼紙：想了解個人化護膚💡 / 私訊聊聊💬", "highlight_tag": f"📌 建議存入精選：【{hl4}】"},
            {"story_number": 5, "time_slot": "15:00", "category": cat5, "role_badge": f"🔥 第五篇：第二互動高點（隔天輪替：{cat5}｜鉤子：{hook_choice}）", "hook_copy": h5, "visual_guide": v5, "sticker_suggestion": s5, "highlight_tag": f"📌 建議存入精選：【{hl5}】（被問重複問題直接回：我精選有整理先看看～）"},
            {"story_number": 6, "time_slot": "16:30", "category": "生活", "role_badge": "🌿 第六篇：講完工作立刻回到生活（鬆弛感切換）", "hook_copy": h6, "visual_guide": "下午茶點心或隨手拍生活角落（不發AI生成滿版圖）", "sticker_suggestion": "投票貼紙：下午茶續命🍰 / 專注打拼中💪", "highlight_tag": "免存精選（洗掉商業感，維持帳號溫度）"},
            {"story_number": 7, "time_slot": "18:00", "category": "生活", "role_badge": "🐠 第七篇：店內療癒角落（看得到的日常）", "hook_copy": h7, "visual_guide": "魚缸小魚小蝦游動短片或店內香氛綠植特寫", "sticker_suggestion": "表情滑桿：療癒指數滿分💯", "highlight_tag": "免存精選（展現真真美學的舒適空間感）"},
            {"story_number": 8, "time_slot": "19:30", "category": "生活", "role_badge": "🌙 第八篇：生活有連貫（晚上給答案，呼應第 1 篇伏筆）", "hook_copy": h8, "visual_guide": "傍晚收工後乾淨靜謐的工作室或下班放鬆視角", "sticker_suggestion": "問答貼紙：你們今天最開心的小事是什麼？💛", "highlight_tag": "免存精選（有頭有尾，粉絲每天都會追劇）"},
            {"story_number": 9, "time_slot": "21:00", "category": cat9, "role_badge": f"👑 第九篇：最後一篇給他「為什麼要相信你」（隔天輪替：{cat9}）", "hook_copy": h9, "visual_guide": v9, "sticker_suggestion": s9, "highlight_tag": f"📌 建議存入精選：【{hl9}】（建立長期信任背書）"}
        ]
    }

# ----------------- 核心調用與診斷整合函式 -----------------
def generate_stories_service(mode: str, day_idx: int, user_input: str, opening_choice: str, hook_choice: str, seed_idx: int = 0) -> tuple[dict, dict]:
    api_key = get_api_key()
    fallback_data = peggy_master_engine(mode, day_idx, user_input, opening_choice, hook_choice, seed_idx)
    
    execution_log = {
        "timestamp": datetime.now(TAIPEI_TZ).strftime("%Y-%m-%d %H:%M:%S (台灣標準時間)"),
        "model": "gemini-3.8-flash",
        "api_requested": False,
        "api_success": False,
        "elapsed_seconds": 0.0,
        "http_code": None,
        "error_detail": None,
        "source": "本地備援引擎",
        "validation_result": "尚未驗證"
    }

    if not api_key:
        execution_log["error_detail"] = "系統未檢測到 GEMINI_API_KEY（請至 Streamlit Secrets 配置）"
        execution_log["validation_result"] = "本地引擎輸出驗證通過"
        return fallback_data, execution_log

    execution_log["api_requested"] = True
    is_odd = (day_idx % 2 == 1)
    story_count = 5 if "生活版" in mode else 9
    qa_or_intro = "商品介紹" if is_odd else "商品 QA"
    about_or_milestone = "關於我" if is_odd else "里程碑"

    prompt = f"""你是美業品牌「真真美學」首席操盤顧問，為創辦人「真真公主（鄭鈺真）」嚴格依據 Peggy《限動一頁式攻略》與《賣貨版 7 天模板》產出 {story_count} 則限動 JSON。
當前模式：{mode}｜DAY {day_idx}
真真日常輸入：「{user_input}」
指定第一篇開頭句型：{opening_choice}
指定第二互動高點鉤子：{hook_choice}

【絕對遵守的攻略鐵律】：
1. 順序與結構（若為9篇）：1生活、2生活、3使用產品、4客戶反饋、5{qa_or_intro}、6生活、7生活、8生活、9{about_or_milestone}。每篇建議間隔 1.5 小時（09:00~21:00）。
2. 第一篇必須套用開頭句型（如「有沒有人跟我一樣⋯」「你們會不會也⋯」「你們猜猜看⋯」「今天發生一件⋯的事」），看得到人+一句共鳴+互動貼紙，並在早上埋下日常伏筆。
3. 講話像聊天：所有 hook_copy 必須把自稱「我」換成跟粉絲對話的「你們」，且結尾必須丟出一個問題（以？結尾）！
4. 生活有連貫：第 1 篇早上埋伏筆，第 8 篇（或生活版第 4 篇）晚上給答案！
5. 第二個互動高點：在第 5 篇（或生活版第 3 篇）結合互動鉤子（{hook_choice}）拉高互動。
6. 誠實合規原則：未提供真實反饋時，客戶反饋篇應以詢問困擾或日常真實心得為準，不虛構絕對化行銷宣稱。
7. 精選歸檔標記：第 3、4、5、9 篇標註對應精選（關於我/產品介紹/客戶反饋/產品 QA/里程碑）。

請輸出純 JSON 格式：
{{"day_theme":"本日主軸","stories":[{{"story_number":1,"time_slot":"09:00","category":"分類","role_badge":"攻略定位說明","hook_copy":"文案(含你們+問號結尾)","visual_guide":"配圖建議","sticker_suggestion":"互動貼紙","highlight_tag":"精選歸檔提示"}}]}}"""

    clean_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key={api_key}"
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

    start_time = time.time()
    try:
        # 給予合理的 15 秒原生 HTTP 逾時時間
        with urllib.request.urlopen(req, timeout=15.0) as response:
            execution_log["http_code"] = response.getcode()
            res_bytes = response.read()
            res = json.loads(res_bytes.decode("utf-8"))
            
            content_text = res["candidates"][0]["content"]["parts"][0]["text"].strip()
            s_idx = content_text.find("{")
            e_idx = content_text.rfind("}")
            if s_idx == -1 or e_idx == -1:
                raise ValueError("回傳文字中找不到有效 JSON 邊界")
                
            parsed = json.loads(content_text[s_idx:e_idx+1])
            is_valid, val_msg = validate_story_data(parsed, story_count)
            execution_log["validation_result"] = val_msg
            
            if not is_valid:
                raise ValueError(f"資料結構校驗失敗: {val_msg}")

            execution_log["api_success"] = True
            execution_log["source"] = "Gemini 3.8 Flash (AI即時生成)"
            execution_log["elapsed_seconds"] = round(time.time() - start_time, 2)
            return parsed, execution_log

    except urllib.error.HTTPError as e:
        execution_log["http_code"] = e.code
        err_body = ""
        try:
            err_body = e.read().decode("utf-8")
        except Exception:
            pass
            
        if e.code == 429:
            execution_log["error_detail"] = f"HTTP 429 (請求頻率受限): 官方連線額度達上限或請求過於頻繁"
        elif e.code == 503:
            execution_log["error_detail"] = f"HTTP 503 (伺服器暫時忙碌): Google 模型目前尖峰滿載"
        elif e.code == 400:
            execution_log["error_detail"] = f"HTTP 400 (參數錯誤): 請檢查提示詞或設定格式"
        elif e.code == 403:
            execution_log["error_detail"] = f"HTTP 403 (權限不足): API Key 無效或未開通權限"
        else:
            execution_log["error_detail"] = f"HTTP {e.code} API 錯誤: {err_body[:160]}"

    except urllib.error.URLError as e:
        execution_log["error_detail"] = f"網路連線或逾時異常 (Timeout/URLError): {str(e.reason)}"
    except json.JSONDecodeError as e:
        execution_log["error_detail"] = f"JSON 解析失敗: {str(e)}"
    except Exception as e:
        execution_log["error_detail"] = f"執行異常 ({type(e).__name__}): {str(e)}"

    execution_log["elapsed_seconds"] = round(time.time() - start_time, 2)
    execution_log["source"] = "本地備援引擎 (API 調用未成功，自動安全接管)"
    return fallback_data, execution_log

# ----------------- 介面頂部：奢華 Header -----------------
st.markdown("""
<div class="luxury-header">
    <div class="brand-crown">👑</div>
    <div class="header-title">真真公主專用 ｜ 每日限動操盤助手</div>
    <div class="header-eng">PRINCESS ZHENZHEN · DAILY STORY CURATOR</div>
    <div class="header-subtitle">「流量很重要，但更重要的是：你要影響別人什麼？」</div>
</div>
<div class="logic-banner">
    ✨ <b>黃金順序邏輯</b>：開場先讓人看到你 ➔ 看暖了再聊工作 ➔ 講完就回到生活 ➔ 最後給他「為什麼要相信你」<br>
    ⏰ <b>發文節奏</b>：每篇隔 1–2 小時再發，千萬不要一次發完！
</div>
""", unsafe_allow_html=True)

# ----------------- 01 每日發文模板 & 7 天排程表 (台灣標準時間) -----------------
now_taipei = datetime.now(TAIPEI_TZ)
today_auto_idx = now_taipei.isoweekday()
day_labels = {
    1: "DAY 1（週一｜奇數天）",
    2: "DAY 2（週二｜偶數天）",
    3: "DAY 3（週三｜奇數天）",
    4: "DAY 4（週四｜偶數天）",
    5: "DAY 5（週五｜奇數天）",
    6: "DAY 6（週六｜偶數天）",
    7: "DAY 7（週日｜奇數天）"
}

c_mode, c_day = st.columns([1.2, 1])
with c_mode:
    selected_mode = st.selectbox(
        "📋 01 選擇發文模板",
        [
            "賣貨版（一天 9 篇｜生活夾心賣貨）",
            "招商版（一天 9 篇｜團隊與事業魅力）",
            "生活版（一天 5 篇｜先連續發滿 7 天）"
        ],
        index=0
    )
with c_day:
    selected_day_idx = st.selectbox(
        f"📅 七天排程表（已自動切換台灣時間：{now_taipei.strftime('%m/%d')} 週{['一','二','三','四','五','六','日'][today_auto_idx-1]}）",
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
        <span class="grid-pill">1 早上</span>
        <span class="grid-pill">2 中午</span>
        <span class="grid-pill-work">3 下午(互動)</span>
        <span class="grid-pill">4 晚上(給答案)</span>
        <span class="grid-pill-work">5 睡前(價值)</span>
    </div>
    """, unsafe_allow_html=True)
else:
    c3_label = "團隊日常" if "招商" in selected_mode else "使用產品"
    c4_label = "夥伴反饋" if "招商" in selected_mode else "客戶反饋"
    st.markdown(f"""
    <div class="grid-bar">
        <span class="grid-pill">1 生活(埋伏筆)</span>
        <span class="grid-pill">2 生活</span>
        <span class="grid-pill-work">3 {c3_label}</span>
        <span class="grid-pill-work">4 {c4_label}</span>
        <span class="grid-pill-work">5 {slot5_name}</span>
        <span class="grid-pill">6 生活</span>
        <span class="grid-pill">7 生活</span>
        <span class="grid-pill-work">8 生活(給答案)</span>
        <span class="grid-pill-work">9 {slot9_name}</span>
    </div>
    """, unsafe_allow_html=True)

# ----------------- 06 生活主題發想庫 -----------------
if "draft_input" not in st.session_state:
    st.session_state["draft_input"] = ""

with st.expander("💡 06 生活主題發想庫（不知道發什麼？點一下直接帶入話題！）", expanded=False):
    st.caption("👀 **看得到的日常**（點按鈕自動填入下方輸入框）：")
    vis_cols = st.columns(4)
    for idx, (k, val) in enumerate(LIFE_TOPICS_VISIBLE.items()):
        if vis_cols[idx % 4].button(k, key=f"vis_{idx}", use_container_width=True):
            st.session_state["draft_input"] = val

    st.caption("💭 **看不到的想法**（點按鈕自動填入下方輸入框）：")
    th_cols = st.columns(4)
    for idx, (k, val) in enumerate(LIFE_TOPICS_THOUGHTS.items()):
        if th_cols[idx % 4].button(k, key=f"th_{idx}", use_container_width=True):
            st.session_state["draft_input"] = val

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

# ----------------- 日常輸入框 -----------------
user_thought = st.text_area(
    "💬 公主今天有什麼日常、心情或客人對話？（隨興打一句，或從上方發想庫點選）",
    value=st.session_state["draft_input"],
    placeholder="例如：客人送了一杯咖啡很好喝，下午做完深層淨膚直呼臉亮得像燈泡...",
    height=85
)
st.session_state["draft_input"] = user_thought

# Session State 持久化
if "story_plan" not in st.session_state:
    st.session_state["story_plan"] = None
if "execution_log" not in st.session_state:
    st.session_state["execution_log"] = None
if "seed_counter" not in st.session_state:
    st.session_state["seed_counter"] = 0

generate_btn = st.button("✨ 照攻略一鍵排好今日限動腳本（含伏筆＋精選歸檔）", use_container_width=True)

if generate_btn:
    final_input = user_thought.strip() if user_thought.strip() else "今天在工作室準備迎接預約的公主們，心情特別充實美好"
    with st.spinner("👑 軍師正在依《限動一頁式攻略》與《7天模板》排定腳本..."):
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
    # 顯示來源狀態識別條
    source_str = log.get("source", "系統生成") if log else "系統生成"
    is_cloud_ai = "Gemini" in source_str
    
    badge_bg = "rgba(46, 125, 50, 0.2)" if is_cloud_ai else "rgba(212, 175, 55, 0.2)"
    badge_border = "#4CAF50" if is_cloud_ai else "#D4AF37"
    badge_color = "#A5D6A7" if is_cloud_ai else "#FFE082"
    badge_icon = "✨" if is_cloud_ai else "🛡️"

    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; align-items:center; margin: 12px 0 10px 0; padding: 8px 14px; background: {badge_bg}; border: 1px solid {badge_border}; border-radius: 10px;">
        <span style="font-size:12.5px; font-weight:600; color:{badge_color};">{badge_icon} 生成來源：{html.escape(source_str)}</span>
        <span style="font-size:11px; color:#D3C3B3;">耗時：{log.get('elapsed_seconds', 0.0) if log else 0.0}s</span>
    </div>
    """, unsafe_allow_html=True)

    escaped_theme = html.escape(str(plan.get('day_theme', '')))
    st.markdown(f"""
    <div style="margin: 6px 0 14px 0; padding: 11px 14px; background: rgba(212, 175, 55, 0.12); border-radius: 12px; border: 1px dashed rgba(212, 175, 55, 0.45); text-align: center;">
        <span style="color: #FFF1D0; font-size: 13.5px; font-weight: 600;">🌟 {escaped_theme}</span>
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
            <div class="safety-note">⚠️ 排版鐵律：字體最多2種、字色最多2種｜底圖太亮先調暗放安全區｜不發產品DM與AI滿版圖</div>
        </div>
        """, unsafe_allow_html=True)
        # 提供手機端一鍵複製原始純文字文案
        st.code(item.get('hook_copy', ''), language="text")

# ----------------- 系統執行日誌與除錯監控面板 -----------------
if log:
    with st.expander("📊 系統執行診斷與 API 監控紀錄", expanded=False):
        c1, c2, c3 = st.columns(3)
        c1.metric("指定調用模型", str(log.get("model")))
        c2.metric("HTTP 狀態碼", str(log.get("http_code")) if log.get("http_code") else "本地略過")
        c3.metric("總響應耗時", f"{log.get('elapsed_seconds', 0.0)} 秒")
        
        st.write(f"**執行時間點**：{log.get('timestamp')}")
        st.write(f"**資料校驗狀態**：`{log.get('validation_result')}`")
        if log.get("error_detail"):
            st.warning(f"⚠️ **連線狀態提示**：{log.get('error_detail')}")
        else:
            st.success("✅ **連線狀態**：Gemini API 呼叫並校驗成功，無任何錯誤。")

# ----------------- 底部常駐：02 發文前檢查 & 03 精選清單神回覆 -----------------
st.markdown("---")
with st.expander("✅ 02 發文前檢查表（發限動前打勾確認，確保高流量高轉化）", expanded=True):
    st.checkbox("第一篇：看得到你 ＋ 一句共鳴 ＋ 一個互動貼紙", value=True, key="chk1")
    st.checkbox("第二個互動高點：9 篇裡再挑一篇拉高互動（已鎖定於第 5 篇）", value=True, key="chk2")
    st.checkbox("講話像聊天：「我」換成「你們」，結尾丟一個問題", value=True, key="chk3")
    st.checkbox("生活有連貫：早上埋伏筆（第 1 篇），晚上給答案（第 8 篇）", value=True, key="chk4")
    st.checkbox("一張限動：字體最多兩種、字色最多兩種", value=False, key="chk5")
    st.checkbox("字放安全區，底圖太亮先調暗再放字", value=False, key="chk6")
    st.checkbox("不發產品 DM、不發 AI 生成的滿版圖", value=False, key="chk7")
    st.checkbox("🔥 有人回，就一定要回！那是你今天最熱的名單", value=False, key="chk8")

with st.expander("📌 03 精選清單配置 ＆ 私訊百問百答神回覆（一鍵複製）", expanded=False):
    st.markdown("""
    **【賣貨版必備 5 個精選】**：`關於我` · `產品介紹` · `客戶反饋` · `產品 QA` · `里程碑`  
    **【招商版必備 6 個精選】**：`關於我` · `團隊/公司介紹` · `夥伴反饋` · `團隊 QA` · `團隊理念` · `里程碑`  
    💡 *精選，是在替妳回答 80% 的問題。私訊的問題一直很像？代表精選還不完整，那就是要補的地方。*  
    👇 **再被客人問到重複問題，直接複製下面這句回她：**
    """)
    st.code("我精選的『QA』有整理，你先看看～有任何不清楚的隨時再問我喔💛", language="text")