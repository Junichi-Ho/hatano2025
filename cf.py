import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image
import matplotlib.pyplot as plt
import datetime

@st.cache_data
def green_image(holenum,pfile): #ホールごとのイメージの取り込み
    im = "./pict/"+ pfile +("0"+holenum)[-2:]+".png"
    #st.sidebar.write(im)
    image = Image.open(im)
    caption = im[-6:-4]
    return image,caption


@st.cache_data 
def main_dataframe(): # Main Dataframe CSVファイルの読み込み
    # CSVファイルを読み込む（Shift_JISエンコーディング）
    df = pd.read_csv("Hatanoscore.csv", header=0, encoding='shift_jis')
    
    # ヘッダーを文字列に変換
    df.columns = df.columns.map(str)
    
    df["Date"] = pd.to_datetime(df["Date"], format="mixed")

    # YearとMonthを抽出
    for time_unit in ["Year", "Month", "Date"]:
        df[time_unit] = df["Date"].dt.strftime("%y" if time_unit == "Year" else "%m" if time_unit == "Month" else "%y.%m.%d")

    # 整数化
    columns_to_convert = ["OB", "Penalty", "Total", "1st", "2nd","green","approach","Double Total",
               "3 shot in 100","Total.1","Score.1"]
    df[columns_to_convert] = df[columns_to_convert].apply(pd.to_numeric, errors='coerce').fillna(0).astype(int)

    return df

@st.cache_data
def dataframe_by_hole(df,hole): # ホールごとのデータフレームの作成
    #ホールごとの左のデータを成型する。 str(hole),"Teeing番手","結果","GIR番手","結果.1","Hazard","Pin位置","歩数","Patt数","Patt数.1"
    #ホールごとのデータフレーム df_holeの整形
    if hole > 1 :
        Teeing = "Teeing番手" + "." + str(hole-1)
        T_result = "結果" + "." + str((hole-1)*2)
        GIR = "GIR番手" + "." + str(hole-1)
        GIR_result = "結果" + "." + str((hole-1)*2+1)
        Haz = "Hazard" + "." + str(hole-1)
        PP = "Pin位置" + "." + str(hole-1)
        SN = "歩数" + "." + str(hole-1)
        PN = "Patt数" + "." + str((hole-1)*2)
        PH = "Patt数" + "." + str((hole-1)*2+1)
    else:
        Teeing = "Teeing番手"
        T_result = "結果"
        GIR = "GIR番手"
        GIR_result = "結果" + ".1" 
        Haz = "Hazard"
        PP = "Pin位置"
        SN = "歩数"
        PN = "Patt数"
        PH = "Patt数" + ".1"
    df_hole = df[[str(hole),Teeing,T_result,GIR,GIR_result,Haz,PP,SN,PN,PH,"Year","Month","Date"]]
    rename_dict = {Teeing:"T",T_result:"TR",GIR:"G",GIR_result:"GR",Haz:"Comment",PP:"PP",SN:"SN",PN:"PN",PH:"PH","Year":"y","Month":"m"}
    df_hole = df_hole.copy()
    df_hole.rename(columns=rename_dict,inplace=True)
    #整数化
    columns_to_convert = ["PP", "PN", "PH"]
    df_hole[columns_to_convert] = df_hole[columns_to_convert].apply(pd.to_numeric, errors='coerce').fillna(0).astype(int)

    return df_hole

def main():
    st.write("this is function file for streamlit project")

if __name__ == "__main__":
    main()