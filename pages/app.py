# chatbot_page
import chatengine

# external packages
import streamlit as st
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
import os

def main():
    # 애플리케이션 초기화 및 페이지 설정
    st.set_page_config(page_title="Welfare King", layout="wide")
    # 페이지 상태 관리
    if 'page' not in st.session_state:
        st.session_state.page = 'loading'


    # 로딩 화면
    if st.session_state.page == 'loading':
        st.title("필요한 정보를 불러오는중")
        st.write("잠시 기다려주세요...")
        # OpenAI API 키 설정
        os.environ['OPENAI_API_KEY'] = "<APIKEY HERE>"
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        st.write("임베딩 호출 완료")
        print('임베딩 호출 완료')
        # FAISS 인덱스 로드 또는 생성
        print('FAISS 인덱스 존재여부 확인')
        if os.path.exists("./db"):
            st.write("FAISS 인덱스 로드");print('FAISS 인덱스 로드')
            faiss_index = FAISS.load_local(folder_path="./db",
                                           embeddings=embeddings,
                                           index_name="index")
            # "./db":FAISS index folder path -> "s3://db"
            # "index":FAISS index file name -> "index"
        else:
            print('CSV에서 embedding 생성')
            loader = CSVLoader(
                file_path='data/gov_portal.csv',
                csv_args={
                    "delimiter": ",",
                    "quotechar": '"',
                    "fieldnames": ["url","title","content"],
                },
                encoding="utf-8",
            )
            # "file_path":csv file path -> "s3://~~~/~~~.csv"

            pages = loader.load()
            st.write("로더 준비 완료!");print('로더 준비 완료!')
            # print(pages)
            faiss_index = FAISS.from_documents(pages, embeddings)
            st.write("문서 벡터화 완료!");print('문서 벡터화 완료!')
            faiss_index.save_local("./db","index")
            # "./db":FAISS index folder path -> "s3://db"
            # "index":FAISS index file name -> "index"
            
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
        chatengine.display_chatbot()

if __name__ == "__main__":
    main()