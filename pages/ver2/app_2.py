import streamlit as st
# import chatbot_page
import testing2
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
import os, time


def main():
    # 애플리케이션 초기화 및 페이지 설정
    st.set_page_config(page_title="Welfare King", layout="wide")
    # 페이지 상태 관리
    if 'page' not in st.session_state:
        st.session_state.page = 'loading'
    if st.session_state.page == 'loading':
        st.title("필요한 정보를 불러오는중")
        st.write("잠시 기다려주세요...")
        # OpenAI API 키 설정
        os.environ['OPENAI_API_KEY'] = "<OPENAI_API_KEY_HERE>"
        embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
        st.write("임베딩 호출 완료")
        print('임베딩 호출 완료')
        # FAISS 인덱스 로드 또는 생성
        print('CSV에서 embedding 생성')
        loader = CSVLoader(
                file_path='data/gov_portal.csv',
                csv_args={
                    "delimiter": ",",
                    "quotechar": '"',
                    "fieldnames": ["url","title","content"],
                },
            )
        pages = loader.load()
        st.write("로더 준비 완료!")
        print('로더 준비 완료!')
        # print(pages)
        faiss_index = FAISS.from_documents(pages, embeddings)
        st.write("문서 벡터화 완료!")
        print('문서 벡터화 완료!')
        
        faiss_index.save_local("./db","faiss_index_VOL12")
        st.write("작업 완료!")
        print('작업 완료!')
        
        st.session_state.page = "home"
        print('session_state.page is home now')

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