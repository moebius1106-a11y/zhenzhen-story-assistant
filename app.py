import os
import json
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
        return key.strip().strip("'\"[] ")
    return None

# ----------------- 核心調用函數 (精簡 Token + 極速秒出) -----------------
def generate_stories(day_idx: int, user_input: str):
    api_key = get_api_key()
    if not api_key:
        raise ValueError("系統找不到 GEMINI_API_KEY，請確認 Streamlit App Settings -> Secrets 已設定！")
        
    qa_or_intro = "商品介紹" if day_idx % 2 == 1 else "商品QA"
    about_or_milestone = "關於我" if day_idx % 2 == 1 else "里程碑"
    
    prompt = f"""
    你是美業高質感品牌「真真美學」的首席操盤顧問，使用者為創辦人「真真公主（鄭鈺真）」。
    請遵守【限動一頁式攻略】與【賣貨版 7 天模板】SOP，根據日常輸入產出 9 則精煉限動：
    1. 生活暖場 (露臉+共鳴互動)
    2. 生活暖場 (日常狀態)
    3. 使用產品 (手法細節)
    4. 客戶反饋 (好評對比)
    5. 指定主題：{qa_or_intro}
    6. 生活放鬆 (隨筆小事)
    7. 生活放鬆 (魚缸香氛店內氛圍)
    8. 生活放鬆 (下班心境)
    9. 指定主題：{about_or_milestone} (品牌理念/大女主價值觀)
    
    【核心要求】：
    - 語氣：鬆弛知性、閨蜜聊天感。
    - 每篇 hook_copy 嚴格限制在 25-35 字以內（兩行內，手機極速閱讀）。
    - visual_guide 與 sticker_suggestion 10 字以內簡短具體。
    
    日常輸入：「{user_input}」
    
    輸出純 JSON：
    {{"day_theme":"本日主題","stories":[{{"story_number":1,"category":"分類","hook_copy":"文案","visual_guide":"配圖","sticker_suggestion":"貼圖"}}]}}
    """
    
    clean_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key={api_key}"
    clean_url = clean_url.strip().replace("[", "").replace("]", "").replace("'", "").replace('"', "")
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.7,
            "maxOutputTokens": 1000
        }
    }
    
    req = urllib.request.Request(
        clean_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=40) as response:
            result = json.loads(response.read().decode("utf-8"))
            if "candidates" not in result or not result["candidates"]:
                raise RuntimeError("API 回傳為空，請重試。")
                
            content_text = result["candidates"][0]["content"]["parts"][0]["text"].strip()
            start_idx = content_text.find("{")
            end_idx = content_text.rfind("}")
            if start_idx != -1 and end_idx != -1:
                json_str = content_text[start_idx:end_idx+1]
            else:
                json_str = content_text
            return json.loads(json_str)
    except urllib.error.HTTPError as e:
        err_body = e.read().decode('utf-8')
        raise RuntimeError(f"Google API 錯誤 ({e.code}): {err_body}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"連線超時或網路失敗: {str(e.reason)}")
    except Exception as e:
        raise RuntimeError(f"系統處理異常: {str(e)}")

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
    placeholder="例如：客人送一杯咖啡，下午做完深層淨膚直呼臉亮得像燈泡...",
    height=95
)

st.write("")

# 狀態持久化：避免手機操作或微小重繪導致產出內容遺失
if "story_plan" not in st.session_state:
    st.session_state["story_plan"] = None

generate_btn = st.button("✨ 一鍵排好今日 9 格限動腳本", use_container_width=True)

if generate_btn:
    if not user_thought.strip():
        st.warning("請先隨興打一句今天的瑣事或心情吧～不用動腦隨便寫就好！")
    else:
        with st.spinner("👑 軍師正在構思本日 9 格限動腳本（約需 3~5 秒）..."):
            try:
                st.session_state["story_plan"] = generate_stories(today_idx, user_thought)
            except Exception as e:
                st.error(f"❌ 執行中斷提示：{str(e)}")

# 渲染持久化結果
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