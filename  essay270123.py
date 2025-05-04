import streamlit as st
import pandas as pd
import os
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import openai

# OpenAI APIキーの設定
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Google Sheets API認証情報の設定
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
worksheet = gc.open("streamlit_codes").worksheet("codes")  # あなたのシート名に合わせて変更

# UI
st.title("英作文 採点アプリ(認証コード式)")
code_input = st.text_input("使用コードを入力してください(例:A1B2-C3D4)")
code_verified = False

if st.button("コードを確認する"):
    codes = worksheet.get_all_records()
    for i, row in enumerate(codes):
        if row["code"] == code_input:
            if not row["used"]:
                st.success("認証成功!添削に進めます。")
                code_verified = True
                worksheet.update_cell(i+2, 2, "TRUE")  # "used" 列
                worksheet.update_cell(i+2, 3, datetime.now().isoformat())  # "used_at" 列
            else:
                st.error("このコードはすでに使用されています。")
            break
    else:
        st.error("無効なコードです。")

# 認証成功後の入力欄
if code_verified:
    name = st.text_input("あなたの名前を入力してください")

    if name:
        st.markdown("英作文とお題を入力してください。添削後、結果をダウンロードできます。")
        prompt = st.text_area("お題 (例: Do the benefits of online shopping outweigh the disadvantages?)", key="prompt")
        user_essay = st.text_area("あなたの英作文", key="essay")

        if st.button("採点を開始する"):
            if prompt and user_essay:
                with st.spinner("採点中です..."):
                    system_message = """
あなたは英語の採点官である。

以下の英作文について、次の手順に厳密に従い、日本語で出力せよ。

【基本方針】
- 評価対象はTOEFLのライティング基準に準拠する。
- 文法・語法・スペルミスなど、TOEFLで減点される要素のみを厳格に指摘せよ。
- 許容される表現のバリエーションやスタイルの違いは訂正してはならない。
- 誤りを訂正する際には、必ず明確な文法的・語法的な根拠を説明せよ。
- 内容が十分に良い場合は「内容は十分に良い」と明記せよ。
- 誤りが存在しない場合は「誤りは見つからなかった」と明記せよ。
- 説明はすべて「丁寧なである調」で書くこと(です・ます調は禁止する)。

【出力形式】
1. CEFRレベル(A1〜C2)を判定せよ。
2. TOEFLライティング基準に基づき、10点満点で採点せよ。
3. 文法・語法・単語・表現の誤りを、すべて漏れなく以下の順で記述せよ:
   【誤りのある元の文(英語)】
   【訂正文(英語)】
   【なぜ間違いなのか(日本語で丁寧に説明)】
4. 接続詞や接続副詞の使用を評価し、誤用があれば修正理由を説明せよ。
5. 内容と論理展開(序論・本論・結論)の自然さを評価し、必要なら改善提案をせよ。
6. 模範解答を140〜160語の英語で作成せよ。
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
                    st.text_area("添削結果", result, height=600)

                    # ダウンロード機能
                    full_content = f"【お題】\n{prompt}\n\n【あなたの英作文】\n{user_essay}\n\n【添削結果】\n{result}"
                    st.download_button("添削結果をダウンロード", data=full_content, file_name="feedback.txt")
            else:
                st.warning("お題と英作文の両方を入力してください。")
