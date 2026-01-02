import streamlit as st
import google.generativeai as genai
import datetime

# --- ページ設定 ---
st.set_page_config(page_title="My Teacher Mentor", page_icon="🌱")
st.title("🌱 My Teacher Mentor (Cloud)")
st.markdown("お疲れ様です。これはごっしー専用アプリです。GitHub,PythonやSteamlitを使って開発しています。")

# --- セッション状態の初期化 ---
if 'response_text' not in st.session_state:
    st.session_state.response_text = ""
if 'user_query' not in st.session_state:
    st.session_state.user_query = ""

# --- APIキーの自動読み込み ---
# 金庫(Secrets)にキーがあればそれを使い、なければサイドバーで聞く仕様
api_key = None
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    with st.sidebar:
        st.header("設定")
        api_key = st.text_input("Google AI API Key", type="password")

# --- モデル設定とメイン処理 ---
# キーがある場合のみモデル選択を表示
selected_model_name = "models/gemini-1.5-flash"
if api_key:
    try:
        genai.configure(api_key=api_key)
        # モデルリスト取得（エラー回避のため簡易化）
        # Cloud環境で安定させるため、リスト取得に失敗したら固定値を使います
        try:
            model_list = []
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    model_list.append(m.name)
            gemini_models = [m for m in model_list if 'gemini' in m]
            if gemini_models:
                with st.sidebar:
                    selected_model_name = st.selectbox("使用モデル", gemini_models, index=0)
        except:
            pass # リスト取得できなくてもデフォルト(Flash)で動かす
            
    except Exception as e:
        st.error(f"APIキーエラー: {e}")

# --- メインエリア ---
user_input = st.text_area("今日の悩みや出来事", height=150, value=st.session_state.user_query)

if st.button("メンターに相談する"):
    if not api_key:
        st.error("APIキーが設定されていません。Secretsを設定するかサイドバーに入力してください。")
    elif not user_input:
        st.warning("どのような状況に、どう悩んでいますか")
    else:
        st.session_state.user_query = user_input
        model = genai.GenerativeModel(selected_model_name)
        
        prompt = f"""
        あなたはTA(交流分析)とコー・アクティブコーチング、中国の古典、７つの習慣（コヴィー氏の著作）の専門家です。教師の悩みに対し以下を行ってください：
        1. 【受容】50文字以内：温かい言葉で労う、できれば勇気づけをする。    
        2. 【分析】200文字以内：文章から見える「ドライバー(完全であれ、急げ等)、ラケット感情（後悔など）、乗ってしまっている心理ゲーム、７つの習慣からのずれ」が感じられれば、それぞれ指摘(Adult)
        3. 【許可】200文字以内：そのドライバーを緩める言葉、そのラケット感情を捨て去る言葉、心理ゲームから降りるための言葉、７つの習慣に沿わせる言葉を融合する、また、言葉中国の名言名句を提供する
        4. 【問い】気づきを促す、コーアクティブ・コーチング的な問いを1つ
        
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
    st.download_button(
        label="💾 この対話をダウンロードする",
        data=save_content,
        file_name=filename,
        mime="text/plain"
    )
