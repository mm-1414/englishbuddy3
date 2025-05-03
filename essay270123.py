from openai import OpenAI
import streamlit as st
import pandas as pd
import os
from datetime import datetime
from supabase import create_client

# --- Supabase設定(自分の情報に置き換えてください) ---
SUPABASE_URL = "https://vseylemehskmfrwpuoey.supabase.co"  # あなたのSupabaseのURL
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZzZXlsZW1laHNrbWZyd3B1b2V5Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NjI3MTQwOSwiZXhwIjoyMDYxODQ3NDA5fQ.uFXUDYFDY9KvARgbiOFMVukbtjUIHITJce59ghH76as"      # Service Role Key(秘密鍵)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- OpenAI設定 ---
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- タイトルとコード入力 ---
st.title("英作文 採点アプリ(コード認証付き)")

code_input = st.text_input("使用コードを入力してください(例:A1B2-C3D4)")

code_verified = False

if st.button("コードを確認する"):
    result = supabase.table("access_codes").select("*").eq("code", code_input).execute()
    if result.data and not result.data[0]["used"]:
        st.success("認証成功!添削に進めます。")
        code_verified = True

        # 使用済みに更新
        supabase.table("access_codes").update({
            "used": True,
            "used_at": datetime.now().isoformat()
        }).eq("code", code_input).execute()
    else:
        st.error("このコードは無効、またはすでに使用済みです。")

# --- 認証に成功した場合のみ、採点フォームを表示 ---
if code_verified:
    LOG_FILE = "user_log.csv"
    name = st.text_input("あなたの名前を入力してください")

    if name:
        st.markdown("解答や解説を保存したい場合は、添削後に「添削結果をダウンロードする」ボタンが出ますので、それを押してください。")

        prompt = st.text_area("お題を入力してください(例: Do the benefits of online shopping outweigh the disadvantages?)", key="prompt")
        user_essay = st.text_area("あなたの英作文を入力してください(文字数は自由です)", key="essay")

        if st.button("採点を開始する"):
            if prompt and user_essay:
                with st.spinner("採点中です。お待ちください。"):
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
   ※スペルミスや冠詞、語順などの小さなミスも省略せず記載すること。
4. 接続詞や接続副詞について:
   - 適切に使用されているかを評価せよ。
   - 誤用されている場合は、どこがどう誤っているか、なぜ修正が必要かを示せ。
   - 類義表現の違いも、意味・ニュアンスの観点から明確に解説せよ。
5. 内容と論理展開(Introduction → Body → Conclusion)の自然さを評価し、必要があれば改善案を提案せよ。
6. 模範解答を140〜160語以内で英語で作成せよ。

以上すべてを厳格に守り、内容の信頼性と一貫性を最優先せよ。
                    """

                    response = client.chat.completions.create(
                        model="gpt-4-turbo",
                        messages=[
                            {"role": "system", "content": system_message},
                            {"role": "user", "content": f"{prompt}\n\n{user_essay}"}
                        ]
                    )
                    result = response.choices[0].message.content

                    st.success("採点が完了しました。")
                    st.text_area("添削結果", result, height=600)

                    st.subheader("あなたの解答")
                    st.text_area("あなたの英文", value=user_essay, height=150)

                    st.subheader("お題")
                    st.text_area("お題", value=prompt, height=100)

                    full_content = f"【お題】\n{prompt}\n\n【あなたの英作文】\n{user_essay}\n\n【添削結果】\n{result}"
                    st.download_button("添削結果をダウンロードする", data=full_content, file_name="feedback.txt")

                    st.markdown("別の問題を解きたい場合は、この画面を更新してください。(画面を下に引っ張る、または右上のぐるっとした矢印ボタンを押してください)")

                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    log_data = pd.DataFrame([[timestamp, name]], columns=["日時", "名前"])
                    log_data.to_csv(LOG_FILE, mode='a', header=not os.path.exists(LOG_FILE), index=False)

            else:
                st.warning("お題と英作文の両方を入力してください。")
