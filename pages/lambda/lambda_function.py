import os
import boto3
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders.csv_loader import CSVLoader
s3 = boto3.client('s3')

def make_index(csvloadpath,outfilename):
    # OpenAI API 키 설정
    os.environ['OPENAI_API_KEY'] = "<OPENAI_API_KEY_HERE>"
    embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
    # FAISS 인덱스 로드 또는 생성
    print('CSV에서 embedding 생성')
    loader = CSVLoader(
            file_path=csvloadpath,
            csv_args={
                "delimiter": ",",
                "quotechar": '"',
                "fieldnames": ["url","title","content"],
            },
        )
    pages = loader.load()
    # print(pages)
    faiss_index = FAISS.from_documents(pages, embeddings)
    faiss_index.save_local("./",outfilename)

loadpath='s3://alab-s3/data/gov_portal.csv'
filename="faiss_index_ALAB"
make_index(loadpath,filename)
s3.upload_file(f'./{filename}.faiss', 'alab-s3', f'{filename}.faiss')
s3.upload_file(f'./{filename}.pkl', 'alab-s3', f'{filename}.pkl')