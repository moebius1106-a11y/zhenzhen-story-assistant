import streamlit as st
import os
from datetime import datetime
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

# ----------------- 頁面與品牌配置 -----------------
st.set_page_config(
    page_title="真真美學｜每日限動操盤助手",
    page_icon="👑",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 手機端專屬高級美學 CSS (莫蘭迪香檳金 + 柔和奶杏調)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Noto Sans TC', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(180deg, #FDFBF7 0%, #F8F5F0 100%);
    }
    
    .header-box {
        text-align: center;
        padding: 24px 16px 16px 16px;
        background: #FFFFFF;
        border-radius: 18px;
        box-shadow: 0 4px 20px rgba(184, 150, 106, 0.08);
        border: 1px solid #F0E6D8;
        margin-bottom: 20px;
    }
    
    .header-title {
        font-size: 22px;
        font-weight: 700;
        color: #3C332A;
        letter-spacing: 1px;
        margin-bottom: 6px;
    }
    
    .header-subtitle {
        font-size: 13px;
        color: #8C7A6B;
        line-height: 1.5;
    }
    
    .schedule-badge {
        display: inline-block;
        background: #F4EBE1;
        color: #936B3C;
        padding: 6px 14px;
        border-radius: 30px;
        font-size: 13px;
        font-weight: 600;
        margin-top: 10px;
    }
    
    .story-card {
        background: #FFFFFF;
        border-radius: 16px;
        padding: 18px;
        margin-bottom: 16px;
        border-left: 6px solid #C4A482;
        box-shadow: 0 3px 12px rgba(0, 0, 0, 0.03);
        border-top: 1px solid #FAF6F0;
        border-right: 1px solid #FAF6F0;
        border-bottom: 1px solid #FAF6F0;
    }
    
    .card-top {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
    }
    
    .story-num {
        font-size: 12px;
        font-weight: 700;
        color: #FFFFFF;
        background: #3C332A;
        padding: 3px 10px;
        border-radius: 12px;
    }
    
    .story-cat {
        font-size: 12px;
        font-weight: 600;
        color: #936B3C;
        background: #FBF6EE;
        padding: 3px 10px;
        border-radius: 12px;
        border: 1px solid #EEDDC9;
    }
    
    .hook-title {
        font-size: 16px;
        font-weight: 600;
        color: #2B2621;
        line-height: 1.55;
        margin-bottom: 12px;
        padding: 10px 12px;
        background: #FAF7F2;
        border-radius: 10px;
        border: 1px dashed #E2D3C2;
    }
    
    .meta-row {
        font-size: 13px;
        color: #554D45;
        margin-bottom: 6px;
        line-height: 1.45;
    }
    
    .meta-tag {
        font-weight: 600;
        color: #936B3C;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- 資料結構定義 -----------------
class StoryItem(BaseModel):
    story_number: int = Field(description="第 1 到 9 篇限動順序")
    category: str = Field(description="分類：生活暖場/使用產品/客戶反饋/商品介紹/商品QA/生活放鬆/關於我/里程碑")
    hook_copy: str = Field(description="適合直接複製到限動的口語化文案（像閨蜜聊天、真誠有感染力，45字以內）")
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
    
    # 嚴格遵循【賣貨版 7 天模板】輪播機制
    # 第 5 篇：奇數天(商品介紹) / 偶數天(商品QA)
    # 第 9 篇：奇數天(關於我) / 偶數天(里程碑)
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
       - 成熟知性、鬆弛自然、像懂生活的老友在聊日常，堅決避免生硬叫賣與行銷感。
       - 文字精練，每則文案在 40~50 字以內，方便手機一鍵複製。
    
    今日真真輸入的真實日常或想分享的點滴：
    「{user_input}」
    """
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
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
<div class="header-box">
    <div class="header-title">👑 真真美學 ｜ 每日限動操盤助手</div>
    <div class="header-subtitle">把生活瑣碎變成吸睛流量 · 讓專業悄悄變現</div>
</div>
""", unsafe_allow_html=True)

now = datetime.now()
day_map = {1: "週一", 2: "週二", 3: "週三", 4: "週四", 5: "週五", 6: "週六", 7: "週日"}
today_idx = now.isoweekday()

col1, col2 = st.columns([1, 1])
with col1:
    st.info(f"📅 **今天是 {day_map[today_idx]}**")
with col2:
    st.success(f"🎯 核心任務：**{'商品介紹' if today_idx % 2 == 1 else '商品QA'}** + **{'關於我' if today_idx % 2 == 1 else '里程碑'}**")

user_thought = st.text_area(
    "💬 今天有什麼日常、心情或客人對話？（隨興打一句就好）",
    placeholder="例如：今天偷得半日閒去吃私房甜點切蛋糕，順道買了小魚小蝦回店裡放，下午客人做完深層淨膚直呼臉亮得像燈泡...",
    height=100
)

col_btn, _ = st.columns([2, 1])
with col_btn:
    generate_btn = st.button("✨ 一鍵排好今天 9 格限動", type="primary", use_container_width=True)

if generate_btn:
    if not user_thought.strip():
        st.warning("公主先隨興打一句今天的瑣事或心情吧～不用動腦隨便寫就好！")
    else:
        with st.spinner("軍師正在為公主排定本日 9 則高轉化限動腳本..."):
            try:
                plan = generate_stories(today_idx, user_thought)
                st.markdown(f"### 🌟 本日主軸：{plan.day_theme}")
                
                for item in plan.stories:
                    st.markdown(f"""
                    <div class="story-card">
                        <div class="card-top">
                            <span class="story-num">第 {item.story_number} 篇</span>
                            <span class="story-cat">{item.category}</span>
                        </div>
                        <div class="hook-title">「{item.hook_copy}」</div>
                        <div class="meta-row"><span class="meta-tag">📸 建議配圖：</span>{item.visual_guide}</div>
                        <div class="meta-row"><span class="meta-tag">🏷️ 互動貼圖：</span>{item.sticker_suggestion}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.code(item.hook_copy, language="text") # 提供一鍵複製按鈕
            except Exception as e:
                st.error(f"生成出錯：{str(e)}")
