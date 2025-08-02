import json

import requests
import streamlit as st
from streamlit_lottie import st_lottie

import numpy as np
import math
import re
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import sys
import seaborn as sns
sys.path.append('../')  # 上位フォルダをパスに追加

import cf  # 上位フォルダにあるモジュールをインポート

st.set_page_config(layout="wide")


def load_lottiefile(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)
    
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code:
        return None
    return r.json()

def calculate_php(row): #パーオン計算列
    hole_adjustments = {4: 1, 7: 1, 10: 1, 17: 1, 6: 3, 8: 3, 14: 3, 18: 3}
    return row["PH"] - hole_adjustments.get(row["hole"], 2)

def process_hole_dataframe(df, hole):
    temp_df = cf.dataframe_by_hole(df, hole)
    rename_dict = {str(hole): "Score"}
    temp_df = temp_df.rename(columns=rename_dict)
    temp_df["hole"] = hole
    return temp_df

@st.cache_data
def create_dataframe_from():
    df = cf.main_dataframe()
    dfs = [process_hole_dataframe(df, i) for i in range(1, 19)]
    combined_df = pd.concat(dfs, ignore_index=True)
    combined_df = combined_df.dropna(subset=["SN"])
    combined_df["PHP"] = combined_df.apply(calculate_php, axis=1)
    return combined_df


def lottie_display():
    lottie_coding = load_lottiefile(r"lottiefiles\golf.json")
    lottie_cry = load_lottieurl("https://app.lottiefiles.com/animation/472708c7-f54b-4667-8f64-24f539709645")

    col1,col2,col3 = st.columns((3,1,3))

    with col1:
        st.write()
    with col2:
        
        st_lottie(
            lottie_coding,
            speed=1,
            reverse=False,
            loop=True,
            quality="low",
            #renderer="svg",
            height="50%",
            #witdth="10%",
            key=None,

        )
    with col3:
        st.write("")
        #st_lottie(lottie_cry,key="cry")


def main():
    #各ホール縦持ちデータの取得
    combined_df = create_dataframe_from()

    # 日付列をdatetime型に変換
    combined_df['Date'] = pd.to_datetime(combined_df['Date'], format='%y.%m.%d')

    # ユーザーに年と月を選択させる
    years = sorted(combined_df['Date'].dt.year.unique())
    months = sorted(combined_df['Date'].dt.month.unique())

    col1,col2,col3 = st.columns((1,1,1))

    with col1:
        selected_year = st.selectbox('年を選択してください', years,index=years.index(2023))
    with col2:
        selected_month = st.selectbox('月を選択してください', months)
    
    # 選択された年と月に該当する日付のリストを作成
    date_list = combined_df[(combined_df['Date'].dt.year == selected_year) & (combined_df['Date'].dt.month == selected_month)]['Date'].unique()

    with col3:
        # ユーザーに日付を選択させる
        selected_date = st.selectbox('日付を選択してください', date_list)

    # 選択された日付にヒットするデータを抽出
    filtered_df = combined_df[combined_df['Date'] == selected_date]

    # "hole"列をインデックスに設定
    filtered_df = filtered_df.set_index('hole')

    # ユーザーに列を選択させる
    cols = st.multiselect('表示する列を選択してください', filtered_df.columns.tolist(), default=['Score',"PN","PHP","T","TR","PP","Comment","G","GR","SN"])

    # "Score"の合計を計算
    total_score = filtered_df['Score'].sum()
    patt_total_score = filtered_df["PN"].sum()

    # 結果を表示
    st.write(f'Total Score: {total_score}, Patt: {patt_total_score}')

    ## "PN"が3以上の場合、emoji :boom: をつけて表示
    #filtered_df['PN'] = filtered_df['PN'].apply(lambda x: f'!!{x}!!' if x >= 3 else x)

    # "Comment"の"r-yard:"をemoji :1234:に変更
    filtered_df['Comment'] = filtered_df['Comment'].replace('r-yard:', 'R', regex=True)
    
    if st.checkbox("モバイル表示"):
        # 選択された列と必須の列を表示
        st.dataframe(filtered_df[cols].style.background_gradient(cmap="coolwarm"),use_container_width=True)
    else:
        # 選択された列と必須の列を表示
        #df_t = filtered_df[cols].T
        #st.dataframe(df_t.style.background_gradient(cmap="Blues"),use_container_width=True)
        st.dataframe(filtered_df[cols].T,use_container_width=True)


if __name__ == "__main__":
    main()