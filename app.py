import streamlit as st
import pandas as pd
import os
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import openai

# --- 仮のOpenAI APIキー(必ずあとでsecretsに戻す) ---
openai.api_key = "sk-dummy"

# --- 仮のGoogle認証情報(必ずあとでsecretsに戻す) ---
service_account_info = {
    "type": "service_account",
    "project_id": "dummy-project",
    "private_key_id": "dummy_key_id",
    "private_key": "-----BEGIN PRIVATE KEY-----\\ndummykey\\n-----END PRIVATE KEY-----\\n",
    "client_email": "dummy@dummy.iam.gserviceaccount.com",
    "client_id": "dummy-client-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/dummy.iam.gserviceaccount.com"
}

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = Credentials.from_service_account_info(service_account_info, scopes=scope)
gc = gspread.authorize(credentials)

# ダミーシート名(存在しなくてもOK。あとで本番に置き換える)
worksheet = gc.open("dummy_sheet").sheet1

# --- UI ---
st.title("英作文 採点アプリ (仮デプロイ用)")

code_input = st.text_input("使用コードを入力してください")
code_verified = True  # 仮に常に認証成功とする

if code_verified:
    name = st.text_input("あなたの名前を入力してください")

    if name:
        st.markdown("英作文とお題を入力してください。添削は仮動作です。")
        prompt = st.text_area("お題 (例: Do the benefits of online shopping outweigh the disadvantages?)")
        user_essay = st.text_area("あなたの英作文")

        if st.button("採点を開始する"):
            if prompt and user_essay:
                with st.spinner("採点中(ダミー応答)..."):
                    result = "仮の結果: 実際のOpenAI APIが動作していません。secretsを設定してください。"
                    st.success("採点完了!")
                    st.text_area("添削結果", result, height=400)
            else:
                st.warning("お題と英作文の両方を入力してください。")
