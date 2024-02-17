import json
import os
import boto3
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders.csv_loader import CSVLoader

# CONFIGPATH = "s3://~~~/config.json"
CONFIGPATH = "../config.json" ## here, you need to put your config file path

# open json file to import the api key
with open(CONFIGPATH) as f:
    cfg = json.load(f)

# set OpenAI API KEY
os.environ['OPENAI_API_KEY'] = cfg['API_KEY']['OPENAI']


def lambda_handler(event, context):
    s3 = boto3.client('s3') # should we put this in the function? or put it outside of the function?
    
    csvloadpath='s3://alab-s3/data/gov_portal.csv'
    outfilename="faiss_index_ALAB"

    # index 생성
    faiss_index = make_index(csvloadpath, outfilename)
    
    # s3에 업로드
    # s3.upload_file(f'./{outfilename}.faiss', 'alab-s3', f'{outfilename}.faiss')
    # s3.upload_file(f'./{outfilename}.pkl', 'alab-s3', f'{outfilename}.pkl')
    faiss_index.save_local("s3://alab-s3/db/",outfilename)

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

def make_index(csvloadpath):
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
    return faiss_index


