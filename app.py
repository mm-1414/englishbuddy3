import streamlit as st

# 正しいコード（例：Stripe決済後に表示するコード）
VALID_CODE = "goukaku0428"

# セッション状態で認証フラグを管理
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("認証コードを入力してください")
    code = st.text_input("コード", type="password")
    if st.button("送信"):
        if code == VALID_CODE:
            st.session_state["authenticated"] = True
            st.success("認証に成功しました！アプリを利用できます。")
            st.experimental_rerun()
        else:
            st.error("無効なコードです。")
    st.stop()import streamlit as st
import pandas as pd
from datetime import datetime
import openai
import gspread
from google.oauth2.service_account import Credentials

# secretsからキー取得
openai.api_key = st.secrets["OPENAI_API_KEY"]

service_account_info = {
    "type": st.secrets["GSHEET_TYPE"],
    "project_id": st.secrets["GSHEET_PROJECT_ID"],
    "private_key_id": st.secrets["GSHEET_PRIVATE_KEY_ID"],
    "private_key": st.secrets["GSHEET_PRIVATE_KEY"],
    "client_email": st.secrets["GSHEET_CLIENT_EMAIL"],
    "client_id": st.secrets["GSHEET_CLIENT_ID"],
    "auth_uri": st.secrets["GSHEET_AUTH_URI"],
    "token_uri": st.secrets["GSHEET_TOKEN_URI"],
    "auth_provider_x509_cert_url": st.secrets["GSHEET_AUTH_PROVIDER_X509_CERT_URL"],
    "client_x509_cert_url": st.secrets["GSHEET_CLIENT_X509_CERT_URL"]
}

# Google Sheets 認証
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = Credentials.from_service_account_info(service_account_info, scopes=scope)
gc = gspread.authorize(credentials)
worksheet = gc.open("streamlit_codes").worksheet("codes")  # 本番シート名に合わせて修正

# アプリUI
st.title("英作文 採点アプリ(コード認証付き)")
code_input = st.text_input("使用コードを入力してください")
code_verified = False

if st.button("コードを確認"):
    codes = worksheet.get_all_records()
    for i, row in enumerate(codes):
        if row["code"] == code_input:
            if not row["used"]:
                st.success("認証成功!")
                code_verified = True
                worksheet.update_cell(i+2, 2, "TRUE")
                worksheet.update_cell(i+2, 3, datetime.now().isoformat())
            else:
                st.error("このコードはすでに使われました。")
            break
    else:
        st.error("無効なコードです。")

if code_verified:
    name = st.text_input("あなたの名前を入力してください")
    if name:
        prompt = st.text_area("お題(例:Do the benefits of online shopping outweigh the disadvantages?)")
        user_essay = st.text_area("あなたの英作文")

        if st.button("採点を開始する"):
            if prompt and user_essay:
                with st.spinner("採点中..."):
                    system_message = """
あなたは英語の採点官である。以下の英作文についてTOEFLのライティング基準で採点し、日本語で丁寧に説明せよ。
(中略:省略可能)
"""
                    response = openai.ChatCompletion.create(
                        model="gpt-4",
                        messages=[
                            {"role": "system", "content": system_message},
                            {"role": "user", "content": f"{prompt}\n\n{user_essay}"}
                        ]
                    )
                    result = response["choices"][0]["message"]["content"]
                    st.success("採点完了!")
                    st.text_area("添削結果", result, height=400)
