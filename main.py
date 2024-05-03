import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import cf
import plotly.graph_objects as go
import matplotlib.image as mpimg

st.set_page_config(layout="wide")

@st.cache_data
def calculate_metrics(df, column, condition):
    df_filtered = df[df[column].str.contains(condition, case=False, na=False)]
    return df_filtered.shape[0]

@st.cache_data
def calculate_metrics_numeric(df, column, value):
    df_filtered = df[df[column] > value]
    return df_filtered.shape[0]

@st.cache_data
def filter_dataframe(df, column, condition):
    return df[df[column].str.contains(condition, case=False, na=False)]

def is_short_hole(hole):
    short_hole = (4,7,10,17) #タプルで宣言
    return hole in short_hole

@st.cache_data
def generate_sub_dataframe(hole, df_holef): 
    # 1st OBのデータフレーム、2nd OBのデータフレーム、GIRのGonのデータフレーム,OB数と最後のOBになった日付データ
    countTOB = pd.DataFrame() if is_short_hole(hole) else filter_dataframe(df_holef, "TR", "OB")
    OBnumbers = countTOB.shape[0]

    # 2ndShotのOB数
    count2OB = filter_dataframe(df_holef, "GR", "OB")
    # GIRのGreenOnの数
    countGon = filter_dataframe(df_holef, "GR", "GO")
    lastdateOB = "なし" if OBnumbers == 0 else countTOB.iloc[0]["Date"] #countTOB.iat[0,12]

    return countTOB, count2OB, countGon, OBnumbers, lastdateOB

def get_hole_value(hole, hole_dict):
    for key, value in hole_dict.items():
        if isinstance(key, tuple) and hole in key:
            return value
    return hole_dict["default"]

@st.cache_data
def generate_sub_dataframe_ODB(hole, df_holef):#DoubleBoggy以上
    hole_dict = {
        (4, 7, 10, 17): (4, 2, ":o:", ":three:"),
        (6, 8, 14, 18): (6, 4, ":ok_woman:", ":five:"),
        "default": (5, 3, ":ok_woman:", ":four:")
    }
    hole_value, PH_value, iconOB, iconp = get_hole_value(hole, hole_dict)

    temp_hole = df_holef[df_holef[str(hole)] > hole_value]
    df_db_on = df_holef[df_holef["PH"] > PH_value]
    lastdate = "なし" if temp_hole.empty else temp_hole.iloc[0]["Date"]

    return temp_hole, df_db_on, lastdate, iconOB, iconp

@st.cache_data
def generate_sub_dataframe_HP(hole, df_holef):# Holeの位置高さと3pattのデータフレームの作成
    hole_icon_dict = {
        (12, 5, 4, 7, 16, 17): ":full_moon_with_face:",
        (2, 9, 10, 15): ":first_quarter_moon_with_face:",
        "default": ":new_moon_with_face:"
    }
    icon_visible_green = get_hole_value(hole, hole_icon_dict)

    df_temp_hole = df_holef[df_holef["PN"] > 2]
    lastdate_3 = "なし" if df_temp_hole.empty else df_temp_hole.iat[0,12]

    return icon_visible_green, df_temp_hole, lastdate_3

def get_filtered_dataframe(df_holef, countGon, hole):
    df_to_show = df_holef
    short_hole = (4,7,10,17) #タプルで宣言

    if hole not in short_hole:
        df_holef_F = filter_dataframe(df_holef, "TR", "F")
        countGon_F = filter_dataframe(countGon, "TR", "F")

        FONFON = st.checkbox("Only FW keep")
        GONGON = st.checkbox("Only Green On")

        if FONFON and GONGON:
            df_to_show = countGon_F
        elif GONGON:
            df_to_show = countGon
        elif FONFON:
            df_to_show = df_holef_F

    return df_to_show

def show_dataframe(hole, df_holef, countGon):
    #データフレームをFirst Patt視点で表示
    df_to_show = get_filtered_dataframe(df_holef, countGon, hole)
    display_list = ["PP","TR","Comment","G","GR","SN","PN",str(hole),"Date"]
    st.dataframe(df_to_show[display_list].style.background_gradient(cmap="Greens"),hide_index=True)

@st.cache_data
def reference_dataframe(df_h, thisyear, hole):#メトリクス 比較のためのReference作成
    df_ref = filter_dataframe(df_h, "y", str(thisyear))
    ref_num = df_ref.shape[0]
    short_hole = (4,7,10,17) #タプルで宣言

    if hole in short_hole:
        TOB = 0 #Shortholeの1打目のOB数は Green OnのShot結果に記載している
    else:
        TOB = calculate_metrics(df_ref, "TR", "OB") #TeeshotのOB数

    ref_OB = TOB + calculate_metrics(df_ref, "GR", "OB") #green on のOB数
    ref_paron = ref_num - calculate_metrics(df_ref, "GR", "GO") #FixMe ref_paronはParONしていない値なので間違いを生みそう
    ref_3patt = calculate_metrics_numeric(df_ref, "PN", 2) #3pattの数

    return ref_num, ref_OB, ref_paron, ref_3patt


@st.cache_data
def gauge_view(totalobnumbers,base,df_3patt,df_db_on):
    # ゲージチャートの値を計算
    totalobnumbers_value = totalobnumbers * 2 / base
    df_db_on_value = (df_db_on.shape[0] - totalobnumbers) * 2 / base
    df_3patt_value = df_3patt.shape[0] / base
    #other_value = 1.1 - totalobnumbers_value - df_db_on_value - df_3patt_value
    # ゲージチャートの作成
    gauge_steps = [
        {'range': [0, totalobnumbers_value], 'color': "pink"},
        {'range': [totalobnumbers_value, totalobnumbers_value + df_db_on_value], 'color': "indianred"},
        {'range': [totalobnumbers_value + df_db_on_value, totalobnumbers_value + df_db_on_value + df_3patt_value], 'color': "firebrick"},
        {'range': [totalobnumbers_value + df_db_on_value + df_3patt_value, 1.1], 'color': "white"}
    ]

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=totalobnumbers_value + df_db_on_value + df_3patt_value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "主要因 : OBs : ダボオン : 3パット", 'font': {'size': 14}},
        gauge={
            'axis': {'range': [None, 0.85], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "red"},
            'steps': gauge_steps,
            'threshold': {'line': {'color': "green", 'width': 4}, 'thickness': 0.75, 'value': 0.5}
        }
    ))

    # サイズの調整
    fig.update_layout(autosize=False, width=300, height=300, paper_bgcolor="white", font={'color': "darkblue", 'family': "Arial"})

    return fig

def hole_selection():
    # イン アウト選択により絞り込む 
    out_in = st.radio("Out / In",("Out","In"), horizontal=True)
    # 選択に応じてホールのリストを変更
    hole_list = (1,2,3,4,5,6,7,8,9) if out_in == "Out" else (10,11,12,13,14,15,16,17,18)
    # ラジオボタンでホールを選択
    hole = st.radio(f"{out_in}", hole_list, horizontal=True)
    return hole

def the_latest_record(df):
    if st.sidebar.checkbox("最近のスコア表示"):
        st.sidebar.table(df[['Score','OB',"Out","In"]].head(10))

def selection_in_sidebar(df_h):
    # 年と月でフィルタリングするオプション
    for time_unit in ["y", "m"]:
        unit_list = list(df_h[time_unit].unique())
        default_list = ["23","22","21"] if time_unit == "y" else unit_list
        selected_units = st.sidebar.multiselect(f"{time_unit}でFilterling", unit_list, default=default_list)
        df_h = df_h[df_h[time_unit].isin(selected_units)]

    return df_h

def main():
    df = cf.main_dataframe()             #csvからデータフレームに取り込み
    hole = hole_selection()              #選択するホール番号
    df_h = cf.dataframe_by_hole(df,hole) #holeに関する情報にスライスし、データフレーム作成する。

    ######################
    # サイドバー表示      #
    #　sidebarを加える   #
    ######################
    the_latest_record(df) #最近のスコア表示
    #年や月でフィルタリングする。
    df_holef = selection_in_sidebar(df_h) #df_holef = 年 月 PinPosition で Filterしたもの 

    #############################
    ###ここから Subdataframeの生成
    #dataframeは 変数名に 必ず "df_" を加えることとする。
    #############################
    
    # fixme 要リファクタリング 3つのDatafleme 統合すべし

    #1st OBのデータフレーム、2nd OBのデータフレーム、GIRのGonのデータフレーム,OB数と最後のOBになった日付データ
    df_countTOB,df_count2OB,df_countGon,OBnumbers,lastdateOB = generate_sub_dataframe(hole,df_holef)
    #overDBのデータフレーム、ダボオン以上 、最後にたたいたダボの日付, OBのアイコン(Par3の場合1stOBないから)、ParNumberアイコン
    df_ODB,df_db_on,lastdate,iconOB,iconp = generate_sub_dataframe_ODB(hole,df_holef)
    #グリーンが上にありピンが見えないホールなのかアイコン化する。
    icon_visible_green,df_3patt,lastdate_3 = generate_sub_dataframe_HP(hole,df_holef)

    #リファレンス 年間のデータを集計 年間ラウンド 年間OB Teeingのリザルト＋GIRのリザルトの合計のみ Hazard columnは含まず
    #GONしなかった数 3パットの数
    this_year = 23 #比較する年を記載する 2023年
    ref_num,ref_OB,ref_paron,ref_3patt = reference_dataframe(df_h,this_year,hole)

    ###################
    ### 表示       ####
    ###################
    # 1  # タイトルは、In/OUT Hole Number、回数 打数アベレージを記載
    bun_title = f"No.{str(hole)}  :golfer: {df_holef.shape[0]} {iconp} {df_holef[str(hole)].mean():.3f} "
    st.subheader(bun_title)

    #メトリクス
    base = df_holef.shape[0] if df_holef.shape[0] else 1000  # 分母で使用するので0にしない。
    totalobnumbers = OBnumbers + df_count2OB.shape[0]
    pattave = df_holef["PN"].mean()

    labelCB = f" patt {pattave:.2f}"
    meterG, percentageS, numberS = st.tabs([labelCB,":deer: ％",":deer: 数"])
    with meterG:
        fig = gauge_view(totalobnumbers,base,df_3patt,df_db_on)
        st.plotly_chart(fig)

    with percentageS:
       #アベレージ表示 （デフォルト）
        col1,col2,col3=st.columns((1,1,1))
        with col1:            
            dbon = (df_db_on.shape[0] - totalobnumbers) /base *100
            a = totalobnumbers/base*100
            b = ref_OB/ref_num*100
            st.metric(label=f"{iconOB} TOB {OBnumbers} : 2OB {df_count2OB.shape[0]}  __ DBon-2OB {dbon:.2f} %",value=f"{a:.1f}",delta=f"{b:.1f}")
            
        with col2:
            a = (df_holef.shape[0]-df_countGon.shape[0]-totalobnumbers)/(base-totalobnumbers)*100
            b = ref_paron/ref_num*100
            pattave=df_holef["SN"].mean()
            st.metric(
                label=f"{icon_visible_green} NOT GOn _ 1st Patt Ave {pattave:.2f}",
                value=f"{a:.1f}",delta=f"{b:.1f}")
            
        with col3:
            a = df_3patt.shape[0]/base*100
            b = ref_3patt/ref_num*100
            label = f":man-facepalming: :field_hockey_stick_and_ball: :field_hockey_stick_and_ball: :field_hockey_stick_and_ball: :calendar:{lastdate_3}"
            st.metric(label=label,value=f"{a:.1f}",delta=f"{b:.1f}")

    with numberS:
        #カウント表示
        col1,col2,col3=st.columns((1,1,1))
        with col1:
            dbon = df_db_on.shape[0] - totalobnumbers
            st.metric(label=f"{iconOB} TOB {OBnumbers} : 2OB {df_count2OB.shape[0]} : DBon-2OB {dbon}",value=totalobnumbers,delta=ref_OB)
            
        with col2:
            pattave=df_holef["SN"].mean()
            st.metric(
                label=f"{icon_visible_green} NOT GOn _ 1st Patt Ave {pattave:.2f}",
                value=df_holef.shape[0]-df_countGon.shape[0],delta=str(ref_paron))
            
        with col3:
            label = f":man-facepalming: :field_hockey_stick_and_ball: :field_hockey_stick_and_ball: :field_hockey_stick_and_ball: :calendar:{lastdate_3}"
            st.metric(label=label,value=df_3patt.shape[0],delta=str(ref_3patt))

    # 3  # スコアのヒストグラム表示 
    if st.checkbox(f"Score_hist.: :skull: DB以上 {lastdate}"):
        fig, ax = plt.subplots()              #グラフ設定 matplotlib
        ax.hist(df_holef[str(hole)],bins=10,) #ヒストグラム
        st.pyplot(fig, use_container_width=True)

    # 4 # データフレーム表示
    with st.expander(f"Dataframe:ラウンド数は {str(df_holef.shape[0])} 回"):
        show_dataframe(hole,df_holef,df_countGon)


if __name__ == "__main__":
    main()
