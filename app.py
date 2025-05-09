import streamlit as st
import pandas as pd
import os
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import openai

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

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = Credentials.from_service_account_info(service_account_info, scopes=scope)
gc = gspread.authorize(credentials)

# ダミーシート名(存在しなくてもOK。あとで本番に置き換える)
worksheet = gc.open("dummy_sheet").sheet1

# --- UI ---
st.title("英作文 採点アプリ (仮デプロイ用)")

code_input = st.text_input("使用コードを入力してください")
code_verified = True  # 仮に常に認証成功とする

if code_verified:
    name = st.text_input("あなたの名前を入力してください")

    if name:
        st.markdown("英作文とお題を入力してください。添削は仮動作です。")
        prompt = st.text_area("お題 (例: Do the benefits of online shopping outweigh the disadvantages?)")
        user_essay = st.text_area("あなたの英作文")

        if st.button("採点を開始する"):
            if prompt and user_essay:
                with st.spinner("採点中(ダミー応答)..."):
                    result = "仮の結果: 実際のOpenAI APIが動作していません。secretsを設定してください。"
                    st.success("採点完了!")
                    st.text_area("添削結果", result, height=400)
            else:
                st.warning("お題と英作文の両方を入力してください。")
