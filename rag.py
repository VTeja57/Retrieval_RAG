from langchain_community.document_loaders import PyPDFLoader,CSVLoader,TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_ollama import ChatOllama
from langchain_classic.retrievers import MultiQueryRetriever
from langchain_classic.chains import RetrievalQA
import tempfile
import os


class RAG:
    def __init__(self,file):
        self.file=file
        self.doc=None
        self.embed=None
        self.prompt=None
        self.chat_model=None
        

    def load(self):
        extension=os.path.splitext(self.file)[1].lower()
        if extension==".txt":
            loader=TextLoader(file_path=self.file,encoding='utf-8-sig')
        elif extension==".csv":
            loader=CSVLoader(file_path=self.file)
        elif extension==".pdf":
            loader=PyPDFLoader(file_path=self.file)
        else:
            raise ValueError('Invalid filetype!')
        
        self.doc=loader.load()
        return self.doc
    
    def splitting(self):
        splitter=RecursiveCharacterTextSplitter(chunk_size=800,chunk_overlap=200)
        self.doc=splitter.split_documents(self.doc)
        return self.doc
    
    def models(self):
        self.embed=OllamaEmbeddings(model="nomic-embed-text:v1.5")

        self.chat_model=ChatOllama(model="phi3:3.8b",
                              temperature=0.3)
        return self.embed,self.chat_model

    def store(self):
        if self.embed is None:
            raise ValueError('No embeddings found!')
        
        temp=tempfile.mkdtemp()
        self.vectordb=Chroma.from_documents(documents=self.doc,
                                            embedding=self.embed,
                                            persist_directory=temp)
    
    def prompting(self):
        prompt_template="""
            You are a professional assistant providing information based solely on provided documentation.
            Always be polite and helpful.
            Only answer using information explicitly stated in the retrieved context.
            If information is not available in the documents, politely inform the user that the specific information is not mentioned in the available documentation.
            Please provide an answer based strictly on the context above.
            If the answer is not in the context, politely indicate that the information is not available in the documentation.
            CONTEX:
            {context}

            QUESTION:
            {question}
            """
        self.prompt=PromptTemplate(template=prompt_template,
                                   input_variables=["context","question"])

        
    def chain(self,question):
        retriever=MultiQueryRetriever.from_llm(
            retriever=self.vectordb.as_retriever(search_kwargs={'k':5}),
            llm=self.chat_model
        )
        qa_chain=RetrievalQA.from_chain_type(
            llm=self.chat_model,
            retriever=retriever,
            chain_type="stuff",
            chain_type_kwargs={"prompt":self.prompt}
        )
        self.respone=qa_chain.invoke({"query":question})
        # print('answer:',self.respone['result'])
        return self.respone['result']
        


    
        
if __name__=='__main__':
    obj=RAG()
    load=obj.load()
    split=obj.splitting()
    mod=obj.models()
    store=obj.store()
    prompt=obj.prompting()
    chain=obj.chain(question='what is genai?')
    
