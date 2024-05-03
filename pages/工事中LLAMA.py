import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image

from pathlib import Path
import os

from llama_index import (
    download_loader,
    GPTVectorStoreIndex, #index化
    StorageContext,
    ServiceContext,     #サービス全般の設定
)
from llama_index.storage.docstore import SimpleDocumentStore    #
from llama_index.storage.index_store import SimpleIndexStore    #
from llama_index.vector_stores import SimpleVectorStore         #

from llama_index.embeddings.openai import OpenAIEmbedding       #
from llama_index.readers.faiss import FaissReader               #queryに類似したテキストのみ使ってindex化
from llama_index.callbacks import CallbackManager, LlamaDebugHandler #処理のロギング
from llama_index.prompts.prompts import QuestionAnswerPrompt #コンテキストに対して回答を求める

import faiss #Facebookが開発したベクター検索ライブラリ。意味が近い文書を検索

import openpyxl

os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

excelfile = r"event.xlsx" #別階層がうまく働かない

def make_doc():
    #インスタンス化
    PandasExcelReader = download_loader("PandasExcelReader")

    loader = PandasExcelReader(pandas_config={"header":0}) #Excelファイルのヘッダーが0行目
    documents = loader.load_data(file=Path("./event.xlsx")) # #改造必要 とりあえずオリジナル
    return documents


def add_row():
    df = pd.read_excel(excelfile,sheet_name="Sheet1",index_col=0)
    with st.expander("df",expanded=False):
        st.table(df)

    with st.form("form"):
        add_text = st.text_input("追加する情報を入力",key="add_info")
        submitted = st.form_submit_button("submitted")

    if submitted:
        len_df=len(df)
        df.loc[len_df]=add_text

        df.to_excel(excelfile)
        with st.expander("行追加後のdf",expanded=False):
            st.table(df)

def drop_row():
    df = pd.read_excel(excelfile,sheet_name="Sheet1",index_col=0)
    with st.expander("df",expanded=False):
        st.table(df)

    with st.form("form"):
        num_delete = st.number_input("削除する行番号を入力",0,key="num_delete")
        submitted = st.form_submit_button("submitted")

    if submitted:
        #行を削除
        df = df.drop(num_delete)
        #indexをリセット。元のindexを使用しない
        df = df.reset_index(drop=True)

        df.to_excel(excelfile)
        with st.expander("行削除後のdf",expanded=False):
            st.table(df)


### index化 上のmake_doc()必要
def make_index():
    #Excelドキュメントテキストデータの取得
    documents = make_doc()

    ### テキストデータの読み込み ・ index化

    # Indexの作成
    index = GPTVectorStoreIndex.from_documents(documents)
    #persistでstorage_contectを保存
    index.storage_context.persist(persist_dir="./storage_context")

    st.info("index化完了")

    docs = []
    with st.expander("index化されたテキストの確認",expanded=False):
        for (_,node) in index.docstore.docs.items():
            #文書ノード(node)からテキストを取得
            text = node.get_text()
            #リストに保存
            docs.append(text)
            st.write(docs)


def q_and_a():
    st.markdown("##### Q&A")
    with st.form("入力"):
        #質問の入力
        question = st.text_input("キーワードまたはフレーズを入力",key="question")
        num_node = st.number_input("ノード数指定",value=1,key="num_node")

        submitted = st.form_submit_button("submitted")
    
    if submitted:
        question = question + "についての情報を教えてください。"

        def read_storage():
            storage_context = StorageContext.from_defaults(
                docstore=SimpleDocumentStore.from_persist_dir(persist_dir="./storage_context"),
                vector_store=SimpleVectorStore.from_persist_dir(persist_dir="./storage_context"),
                index_store=SimpleIndexStore.from_persist_dir(persist_dir="./storage_context"),
            )
            return storage_context

        storage_context = read_storage()

        #embeddingモデルのインスタンス化 特定のテキストに対して個別にベクトルを生成
        embed_model = OpenAIEmbedding()

        #準備
        docs = [] #埋め込みベクトルを保持するためのリスト
        id_to_text_map = {} #文書のIDとテキストの対応を保持するための辞書

        #文書データを格納しているstorage_contextから文書の一覧を取得
        #docstoreは、文書のIDと文書ノード(node)のペアを持つ辞書
        for i, (_,node) in enumerate(storage_context.docstore.docs.items()):
            #文書ノード(node)からテキストを取得
            text = node.get_text()
            #テキストの埋め込みベクトルを生成、リストに保存
            docs.append(embed_model.get_text_embedding(text))
            id_to_text_map[i] = text
        #listをnp配列化　高速化
        docs = np.array(docs)

        #text-ada-embedding-002から出力されるベクトル長を指定
        d = 1536
        # faiss 高次元ベクトルを高速に検索
        # IndexFlatL2 faissの中で最も基本的な索引 (index)の種類
        # 索引とは、ベクトルの集合を管理し、検索を効率的に行うためのデータ構造
        # L2距離(ユークリッド距離)を使って、全てのベクトルとの距離を計算して、最も近いベクトルを返す
        # 精度は高いが、メモリや計算時間が多く必要

        #インスタンス化
        index = faiss.IndexFlatL2(d)
        #Faissにベクトルを登録
        index.add(docs)

        # questionのベクトル化
        query = embed_model.get_text_embedding(question)
        # queryをnp配列化
        query = np.array([query])

        #FaissReader クエリに類似したテキストのみをつかってインデックスを作成
        # インスタンス化
        reader = FaissReader(index)
        #類似度の高い kこのテキストを返す
        documents = reader.load_data(query=query, id_to_text_map=id_to_text_map, k=num_node)

        st.write(f"count_node:{len(documents)}")

        #### デバッグ用
        # 処理の進行状況や結果をロギングを扱うHandler作成
        llma_debug_handler = LlmaDebugHandler()
        # 各処理フェーズの開始時や終了時に呼び出されるコールバック関数を管理するオブジェクト
        # を作成しています。ここでは、ロギング用のハンドラーをコールバックとして登録しています。
        callback_manager = CallbackManager([llma_debug_handler])

        # インデックスを作成したりクエリを実行する際に必要になる部品 （LLMの予測器、埋め込みモデル、プロンプト
        # をまとめたオブジェクトを作成するメソッド
        # デフォルトの設定、コールバックマネージャだけは指定。
        service_context = ServiceContext.from_defaults(callback_manager=callback_manager)

        # Faissで抽出した類似したテキストを使って、GPTモデルでインデックスを作成
        # 文書の内容を検索しやすくする目次のようなもの
        index = GPTVectorStoreIndex.from_documents(documents, service_context=service_context)

        #質問用のQAプロンプトを生成
        QA_PROMPT_TMPL = (
            "私たちは以下の情報をコンテキスト情報として与えます。\n"
            "------\n"
            "{context_str}"
            "------\n"
            "あなたはAIとして、この情報をもとに質問に対して必ず日本語で答えます。:{query_str}\n"
        )
        
        # QuestionAnswerPrompt 外部データから必要な情報を探して答える形式
        # コンテキストに対して回答を求めるようなプロンプト形式
        qa_prompt = QuestionAnswerPrompt(QA_PROMPT_TMPL)

        # インデックスとQAプロンプトを使って、質問に対する回答を生成するエンジンを作成
        query_engine = index.as_query_engine(text_qa_template=qa_prompt)

        # エンジンに質問を送り、回答を受け取る
        response = query_engine.query(question)

        # responseからtextの取り出し。sourceも取り出し可
        response_text = response.response.replace("\n","")

        #チャット画面に表示
        with st.chat_message("user"):
            st.write(question)

        message = st.chat_message("assistant")
        message.write(response_text)



def main():
    #アプリケーション名と対応する関数のマッピング
    apps = {
        "行の追加":add_row,
        "行の削除":drop_row,
        "txtのindex化":make_index,
        "Q and A":q_and_a,
    }
    selected_app_name = st.selectbox(label="項目の選択",options=list(apps.keys()))
    #選択されたアプリケーションを処理する関数を呼び出す
    render_func = apps[selected_app_name]
    render_func()

    st.write(os.getcwd())
    image = Image.open("./pict/01_1m.png")

    st.image(image, caption="イメージ")


if __name__ == "__main__":
    main()
