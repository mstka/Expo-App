import streamlit as st

# レイアウト: サイドバー
st.sidebar.title("SNS メニュー")
#st.sidebar.write(f"ようこそ, {user('userId')}")
mode = st.sidebar.radio("画面選択", ['ホーム', 'プロフィール', '設定'])

params = st.query_params
#jwt_token = params.get("token", [None])[0]

# メインコンテンツ
st.title("My SNS")

if mode == 'ホーム':
    st.subheader("投稿する")
    new_post = st.text_area("何を投稿しますか？", height=100)
    if st.button("投稿"):  
        if new_post.strip():
            st.success("投稿しました！")
        else:
            st.error("投稿内容を入力してください。")

    st.markdown("---")
    st.subheader("タイムライン")
    '''if st.session_state.posts:
        for post in st.session_state.posts:
            st.write(f"**{post['user']}** さんの投稿:")
            st.write(post['content'])
            st.markdown("---")
    else:
        st.info("まだ投稿がありません。")'''

elif mode == 'プロフィール':
    st.subheader("プロフィール")
    #st.write(f"ユーザーID: {user.get('userId')}")
    # プロフィール情報表示・編集用UIをここに追加

else:
    st.subheader("設定")
    st.write("アカウント設定やログアウト機能をここに実装")

##st.experimental_set_query_params(**kwargs)


'''
# ① 初期化
if "count" not in st.session_state:
    st.session_state.count = 0

# ② UI で状態を更新
if st.button("カウントを増やす"):
    st.session_state.count += 1

# ③ 表示
st.write("現在のカウント:", st.session_state.count)
'''