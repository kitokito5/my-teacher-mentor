import streamlit as st
import google.generativeai as genai
import datetime

# --- ページ設定 ---
st.set_page_config(page_title="My Teacher Mentor", page_icon="🌱")
st.title("🌱 My Teacher Mentor (Cloud)")
st.markdown("先生、お疲れ様です。場所を選ばず、いつでも心を整えましょう。")

# --- セッション状態の初期化 ---
if 'response_text' not in st.session_state:
    st.session_state.response_text = ""
if 'user_query' not in st.session_state:
    st.session_state.user_query = ""

# --- サイドバー設定 ---
with st.sidebar:
    st.header("設定")
    api_key = st.text_input("Google AI API Key", type="password")
    
    selected_model_name = "models/gemini-1.5-flash"
    if api_key:
        try:
            genai.configure(api_key=api_key)
            model_list = []
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    model_list.append(m.name)
            
            gemini_models = [m for m in model_list if 'gemini' in m]
            if gemini_models:
                selected_model_name = st.selectbox("使用モデル", gemini_models, index=0)
        except Exception:
            pass

# --- メインエリア ---
user_input = st.text_area("今日の悩みや出来事", height=150, value=st.session_state.user_query)

if st.button("メンターに相談する"):
    if not api_key:
        st.error("APIキーを入力してください")
    elif not user_input:
        st.warning("悩みを入力してください")
    else:
        st.session_state.user_query = user_input
        model = genai.GenerativeModel(selected_model_name)
        
        prompt = f"""
        あなたはTA(交流分析)とコーチングの専門家です。教師の悩みに対し以下を行ってください：
        1. 【受容】温かい言葉で労う(NP)
        2. 【分析】文章から見える「ドライバー(完全であれ等)」を指摘(Adult)
        3. 【許可】そのドライバーを緩める言葉かけ
        4. 【問い】気づきを促すコーチング的な問いを1つ
        
        悩み：{user_input}
        """
        
        with st.spinner(f"{selected_model_name} が執筆中..."):
            try:
                response = model.generate_content(prompt)
                st.session_state.response_text = response.text
            except Exception as e:
                st.error(f"エラー: {e}")

if st.session_state.response_text:
    st.markdown("---")
    st.subheader("メンターからのメッセージ")
    st.write(st.session_state.response_text)
    
    st.markdown("---")
    
    # ★ここが変更点：ダウンロードボタン★
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    filename = f"diary_{timestamp}.txt"
    
    save_content = f"""日時: {now.strftime("%Y-%m-%d %H:%M:%S")}
モデル: {selected_model_name}
-------------------------
【先生の悩み】
{st.session_state.user_query}
-------------------------
【メンターのアドバイス】
{st.session_state.response_text}
-------------------------
"""
    # データをダウンロードさせるボタン
    st.download_button(
        label="💾 この対話をダウンロードする",
        data=save_content,
        file_name=filename,
        mime="text/plain"
    )
