import os
from datetime import datetime
import threading
import time
import streamlit as st
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

# ----------------- 防休眠常駐心跳機制 (Keep-Alive) -----------------
def start_keep_alive():
    if "keep_alive_started" not in st.session_state:
        st.session_state["keep_alive_started"] = True
        def ping_loop():
            while True:
                time.sleep(600)
        thread = threading.Thread(target=ping_loop, daemon=True)
        thread.start()

start_keep_alive()

# ----------------- 頁面與品牌配置 -----------------
st.set_page_config(
    page_title="真真公主專用｜每日限動操盤助手",
    page_icon="👑",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 極致美業名媛奢華風 CSS (iPhone 18 Pro Max 手機端專屬自適應、絕不折字破版)
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
    
    /* 頂部奢華 Header (針對 iPhone Pro Max 大螢幕自適應優化) */
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
    
    /* 主標題：自適應字體大小，白金漸層，單行不爆字 */
    .header-title {
        font-family: 'Noto Serif TC', serif;
        font-size: clamp(17px, 4.8vw, 22px);
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
        font-size: clamp(9px, 2.5vw, 11px);
        letter-spacing: 2.5px;
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
    
    /* 狀態卡片區塊 */
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
    
    /* 輸入框客製化 */
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
    
    /* 尊榮黑金漸層按鈕 */
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
    
    /* 限動卡片 */
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

# ----------------- 資料結構定義 -----------------
class StoryItem(BaseModel):
    story_number: int = Field(description="第 1 到 9 篇限動順序")
    category: str = Field(description="分類：生活暖場/使用產品/客戶反饋/商品介紹/商品QA/生活放鬆/關於我/里程碑")
    hook_copy: str = Field(description="口語、成熟優雅、像閨蜜聊天的精煉文案（45字以內，方便手機直接複製）")
    sticker_suggestion: str = Field(description="建議搭配的 IG 互動貼圖（如投票、表情滑桿、問答貼紙、私訊關鍵字等）")
    visual_guide: str = Field(description="建議配圖（如：今天拍的切蛋糕照片、做臉施作微距、魚缸小短片、客人好評對話截圖等）")

class DailyStoryPlan(BaseModel):
    day_theme: str = Field(description="本日限動核心氛圍或情感金句")
    stories: list[StoryItem]

# ----------------- 生成核心函數 -----------------
def generate_stories(day_idx: int, user_input: str) -> DailyStoryPlan:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        st.error("⚠️ 請確認系統環境已配置 GEMINI_API_KEY")
        st.stop()
        
    client = genai.Client(api_key=api_key)
    
    qa_or_intro = "商品介紹" if day_idx % 2 == 1 else "商品QA"
    about_or_milestone = "關於我" if day_idx % 2 == 1 else "里程碑"
    
    prompt = f"""
    你是美業高質感品牌「真真美學」的首席自媒體幕僚顧問。
    使用者為創辦人「真真（鄭鈺真）」，她是獨立自主、優雅大氣、經歷過人生起伏但越活越通透的品牌大女主。
    
    請嚴格遵守【天使傳聲機·限動一頁式攻略】與【賣貨版 7 天模板】SOP 規範：
    1. 產出 9 篇三明治夾心限動（生活暖場 ➔ 專業見證 ➔ 生活放鬆 ➔ 信任背書）：
       - 第 1 篇：【生活暖場】露臉或日常視角，第一句共鳴句，必須有強互動鉤子（投票/滑桿）。
       - 第 2 篇：【生活暖場】接續早晨/中午生活狀態，延續共鳴。
       - 第 3 篇：【使用產品】專業施作畫面、手法細節、原料特寫。
       - 第 4 篇：【客戶反饋】顧客見證、滿意回饋對話、施作前後透亮對比。
       - 第 5 篇：指定主題【{qa_or_intro}】（痛點解答或好物亮點）。
       - 第 6 篇：【生活放鬆】生活瑣碎小事、下午茶、隨筆抒發。
       - 第 7 篇：【生活放鬆】店內放鬆氛圍（如魚缸游動、店內香氛、小植物）。
       - 第 8 篇：【生活放鬆】傍晚/收工心境，真實不裝的生活感。
       - 第 9 篇：指定主題【{about_or_milestone}】（品牌堅持、進修收穫、證照或大女主價值觀）。
    
    2. 文案語氣：
       - 成熟知性、鬆弛自然、像懂生活的老友在聊日常，堅決避免生硬叫賣與推銷感。
       - 文字精練，每則文案在 40~50 字以內，方便手機一鍵複製。
    
    今日真真輸入的真實日常或想分享的點滴：
    「{user_input}」
    """
    
    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=DailyStoryPlan,
            temperature=0.75
        )
    )
    return DailyStoryPlan.model_validate_json(response.text)

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

generate_btn = st.button("✨ 一鍵排好今日 9 格限動腳本", use_container_width=True)

if generate_btn:
    if not user_thought.strip():
        st.warning("請先隨興打一句今天的瑣事或心情吧～不用動腦隨便寫就好！")
    else:
        with st.spinner("軍師正在為公主排定本日 9 則高轉化限動腳本..."):
            try:
                plan = generate_stories(today_idx, user_thought)
                
                st.markdown(f"""
                <div style="margin: 20px 0 16px 0; padding: 12px 16px; background: rgba(212, 175, 55, 0.1); border-radius: 12px; border: 1px dashed rgba(212, 175, 55, 0.4); text-align: center;">
                    <span style="color: #E8BE6B; font-size: 14px; font-weight: 600;">🌟 本日主軸定調：{plan.day_theme}</span>
                </div>
                """, unsafe_allow_html=True)
                
                for item in plan.stories:
                    st.markdown(f"""
                    <div class="story-card-luxury">
                        <div class="card-meta-bar">
                            <span class="badge-number">STORY 0{item.story_number}</span>
                            <span class="badge-category">{item.category}</span>
                        </div>
                        <div class="luxury-hook-text">「{item.hook_copy}」</div>
                        <div class="meta-line"><span class="meta-tag-gold">📸 建議配圖：</span>{item.visual_guide}</div>
                        <div class="meta-line"><span class="meta-tag-gold">🏷️ 互動貼圖：</span>{item.sticker_suggestion}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.code(item.hook_copy, language="text")
            except Exception as e:
                st.error(f"生成出錯：{str(e)}")