import streamlit as st
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
import os
import boto3
s3 = boto3.client('s3')
filename="faiss_index_ALAB"

# streamlit config
## Initialize chat history

############ function ############
def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "대화내용이 초기화되었습니다. 궁금한 점을 언제든지 물어보세요!"}]

def display_chatbot():
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "복지왕 챗봇이 여러분의 복지 관련 질문에 답변 드립니다. 정부 복지정책에 대해 알고 싶은 것이 있으신가요?"}]

    # Title
    st.title("맞춤 서비스를 위한 개인 정보 작성")
    # Get user information
    age = st.number_input("나이를 입력하세요.", min_value=0, max_value=120, step=1, key="age")
    gender = st.selectbox("성별을 선택하세요.", ["남성", "여성"], key="gender")
    location = st.text_input("사는 곳을 입력하세요.", key="location")
    user_info = {"age":str(age), "gender":str(gender) ,"location":(location)}

    if age and gender and location:
        st.button('Clear Chat History', on_click=clear_chat_history)
        # Display chat messages from history on app rerun
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        prompt = st.chat_input('User: ')
        if prompt:
            # update(append) chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)
        # Here... text streamer does not work as well as I intended with streamlit
        # I will try to fix this later
        if st.session_state.messages[-1]["role"] == "user":
            with st.chat_message("assistant"):
                # model inference
                print(st.session_state.messages[-1]["content"])
                output_text = get_response(st.session_state.messages[-1]["content"],user_info) ### 여기가 언어모델로부터 받은 답변이 들어가야함.
                placeholder = st.empty()
                placeholder.markdown(output_text)
            st.session_state.messages.append({"role": "assistant", "content": output_text})

def get_response(message,user_info):


    # OpenAI API 키 설정
    os.environ['OPENAI_API_KEY'] = "<OPENAI_API_KEY_HERE>"
    embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
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
    # print(pages)
    faiss_index = FAISS.from_documents(pages, embeddings)
    faiss_index.save_local("./db","faiss_index_VOL12")
    retriever = faiss_index.as_retriever()
    template = """다음 정보들을 바탕으로 대답하세요:
    {context}
    다음 사용자 정보도 함께 고려하세요:
    """+ \
    "이용자의 나이는 "+user_info["age"]+"세, 성별은 "+ \
    user_info["gender"]+", 거주지는 "+user_info["location"]+"입니다."+ \
    """
    질문:
    {question}
    """
    prompt = ChatPromptTemplate.from_template(template)
    llm = ChatOpenAI(model_name="gpt-3.5-turbo-16k", temperature=0, max_tokens= 300)
    retrieval = RunnableParallel({"context": retriever,
                                "question": RunnablePassthrough()
                })
    rag_chain = retrieval | prompt | llm | StrOutputParser()
    result = rag_chain.invoke(message)
    return result