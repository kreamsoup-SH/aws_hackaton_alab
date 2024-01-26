import streamlit as st
# import chatbot_page
import testing2


def main():
    # 애플리케이션 초기화 및 페이지 설정
    st.set_page_config(page_title="Welfare King", layout="wide")


    # 페이지 상태 관리
    if 'page' not in st.session_state:
        st.session_state.page = 'home'

    # 홈 화면
    if st.session_state.page == "home":
        st.title("복지왕")
        st.write("복지정보는 클릭 한 번, 복지왕과 챗 하세요!")
        if st.button("챗봇 시작"):
            st.session_state.page = "chatbot"

    # 챗봇 화면
    if st.session_state.page == "chatbot":
        testing2.display_chatbot()

if __name__ == "__main__":
    main()