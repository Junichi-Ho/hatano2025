import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image
import matplotlib.pyplot as plt
import datetime
import plotly.graph_objects as go
import matplotlib.image as mpimg
import time
import sys
sys.path.append('../')  # 上位フォルダをパスに追加
import cf

### Start 基本データフレームの作成
st.set_page_config(layout="wide")

@st.cache_data
def generate_sub_dataframe(hole,df_holef): #OB x2 、GIR Dataframe、Dateを作成
    #3つのDataframe,2つのデータ
    #1st OBのデータフレーム、2nd OBのデータフレーム、GIRのGonのデータフレーム,OB数と最後のOBになった日付データ
    #TeeingShotのOB数
    if hole == 17 or hole == 10 or hole == 4 or hole == 7:
        countTOB=0
        OBnumbers=0
        #OBnumbers_latest=0
    else:
        countTOB=df_holef[df_holef["TR"].str.contains("OB", case=False, na=False)]
        OBnumbers=countTOB.shape[0]
        #OBnumbers_latest=countTOB[countTOB["y"] == this_year].shape[0]
    #2ndShotのOB数
    count2OB=df_holef[df_holef["GR"].str.contains("OB", case=False, na=False)]
    #GIRのGreenOnの数 #ParOn率に変更予定
    countGon=df_holef[df_holef["GR"].str.contains("GO", case=False, na=False)]

    if OBnumbers == 0:
        lastdateOB = "なし"
    else:
        lastdateOB = countTOB.iat[0,12]
    #3つのDataframe,2つのデータ
    #1st OBのデータフレーム、2nd OBのデータフレーム、GIRのGonのデータフレーム,OB数と最後のOBになった日付データ
    return(countTOB,count2OB,countGon,OBnumbers,lastdateOB)

@st.cache_data
def generate_sub_dataframe_ODB(hole,df_holef):#DoubleBoggy以上
    #DoubleBoggy以上
    #overDBのデータフレーム、最後にたたいたダボの日付, OBのアイコン(Par3の場合1stOBないから)、ParNumberアイコン 
    if hole == 17 or hole == 10 or hole == 4 or hole == 7:
        temp_hole = df_holef[df_holef[str(hole)] > 4 ]
        df_db_on = df_holef[df_holef["PH"] > 2]
        iconOB = ":o:"
        iconp = ":three:"
    elif hole == 6 or hole == 8 or hole == 14 or hole == 18:
        temp_hole = df_holef[df_holef[str(hole)] > 6 ]
        df_db_on = df_holef[df_holef["PH"] > 4]
        iconOB = ":ok_woman:"
        iconp = ":five:"
    else:
        temp_hole = df_holef[df_holef[str(hole)] > 5 ]
        df_db_on = df_holef[df_holef["PH"] > 3]
        iconOB = ":ok_woman:"
        iconp = ":four:"

    if temp_hole.shape[0] == 0:
        lastdate = "なし"
    else:
        lastdate = temp_hole.iat[0,12] 

    #overDBのデータフレーム、最後にたたいたダボの日付, OBのアイコン(Par3の場合1stOBないから)、ParNumberアイコン 
    return(temp_hole,df_db_on,lastdate,iconOB,iconp)

@st.cache_data
def generate_sub_dataframe_HP(hole,df_holef):# Holeの位置高さと3pattのデータフレームの作成
    # Holeの位置高さ
    if hole == 12 or hole == 5 or hole == 4 or hole == 7 or hole == 16 or hole == 17 :
        icon_visible_green = ":full_moon_with_face:"
    elif hole == 2 or hole == 9 or hole == 10 or hole == 15 :
        icon_visible_green = ":first_quarter_moon_with_face:"
    else:
        icon_visible_green = ":new_moon_with_face:"

    # ３Patt
    #
    df_temp_hole = df_holef[df_holef["PN"] > 2 ]
    if df_temp_hole.shape[0] == 0:
        lastdate_3 = "なし"
    else:
        lastdate_3 = df_temp_hole.iat[0,12]

    return(icon_visible_green,df_temp_hole,lastdate_3)

#キャッシュ入れるとCheckboxの整合性が取れない警告出る。
def show_dataframe(hole,df_holef,countGon):
    if hole == 17 or hole == 10 or hole == 4 or hole == 7:
        df_holef[["PP","TR","Comment","G","GR","SN","PN",str(hole),"Date"]]
    else:
        col1,col2=st.columns((1,1))
        with col1:
            FONFON = st.checkbox("Only FW keep")
        with col2:
            GONGON = st.checkbox("Only Green On")
        FONFON = int(FONFON)
        GONGON = int(GONGON) * 10
        showswitch = GONGON + FONFON
        df_holef_F=df_holef[df_holef["TR"].str.contains("F", case=False, na=False)]
        countGon_F=countGon[countGon["TR"].str.contains("F", case=False, na=False)]
        if showswitch == 11:
            countGon_F.shape[0]
            countGon_F[["PP","TR","Comment","G","GR","SN","PN",str(hole),"Date"]]
        elif showswitch == 10:
            countGon.shape[0]
            countGon[["PP","TR","Comment","G","GR","SN","PN",str(hole),"Date"]]
        elif showswitch == 1:
            df_holef_F.shape[0]
            df_holef_F[["PP","TR","Comment","G","GR","SN","PN",str(hole),"Date"]]
        else:
            st.dataframe(df_holef[["PP","TR","Comment","G","GR","SN","PN",str(hole),"Date"]].style.background_gradient(cmap="Greens"),hide_index=True)

@st.cache_data
def reference_dataframe(df_h,thisyear,hole):#メトリクス 比較のためのReference作成
    df_ref = df_h[df_h["y"].str.contains(str(thisyear),case=False,na=False)]
    if hole == 17 or hole == 10 or hole == 4 or hole == 7:
        TOB = 0
    else:
        df_refOB = df_ref[df_ref["TR"].str.contains("OB", case=False, na=False)]
        TOB = df_refOB.shape[0] 
    df_ref2O = df_ref[df_ref["GR"].str.contains("OB", case=False, na=False)]
    df_refFW = df_ref[df_ref["GR"].str.contains("GO", case=False, na=False)]
    df_ref3P = df_ref[df_ref["PN"] > 2 ]
    ref_num = df_ref.shape[0]
    ref_OB = TOB + df_ref2O.shape[0]
    ref_paron = df_ref.shape[0]-df_refFW.shape[0]
    ref_3patt = df_ref3P.shape[0]
    return(ref_num,ref_OB,ref_paron,ref_3patt)

@st.cache_data
def gauge_view(totalobnumbers,base,df_3patt,df_db_on):
    # ゲージチャートの値を計算
    totalobnumbers_value = totalobnumbers * 2 / base
    df_db_on_value = (df_db_on.shape[0] - totalobnumbers) * 2 / base
    df_3patt_value = df_3patt.shape[0] / base
    other_value = 1.1 - totalobnumbers_value - df_db_on_value - df_3patt_value
    # ゲージチャートの作成
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = totalobnumbers_value + df_db_on_value + df_3patt_value,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "主要因 : OBs : ダボオン : 3パット", 'font': {'size': 14}},
        gauge = {
            'axis': {'range': [None, 0.85], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "red"},
            'steps' : [
                {'range': [0, totalobnumbers_value], 'color': "pink"},
                {'range': [totalobnumbers_value, totalobnumbers_value + df_db_on_value], 'color': "indianred"},
                {'range': [totalobnumbers_value + df_db_on_value, totalobnumbers_value + df_db_on_value + df_3patt_value], 'color': "firebrick"},
                {'range': [totalobnumbers_value + df_db_on_value + df_3patt_value, 1.1], 'color': "white"}],
            'threshold' : {'line': {'color': "green", 'width': 4}, 'thickness': 0.75, 'value': 0.5}
        }
    ))
    # サイズの調整
    fig.update_layout(autosize=False, width=300, height=300)
    fig.update_layout(paper_bgcolor = "white", font = {'color': "darkblue", 'family': "Arial"})
    return fig

@st.cache_data
def ref_GIR_iron(df_holef,hole):
    # "Comment"列からr-yard:が含まれる要素を抜き取り、数値に変換して"残りヤード"列に追加
    df_holef["残りヤード"] = df_holef["Comment"].str.extract(r'r-yard:\s*(\d+)').astype(float)

    # 指定の列を含むデータフレームを作成
    df_holef_temp = df_holef[df_holef["残りヤード"].notnull()]
    # 残りヤードを整数型に変換
    df_holef_temp["残りヤード"] = df_holef_temp["残りヤード"].astype(int)
    df_holef_temp = df_holef_temp[["残りヤード","G","GR","SN","PN",str(hole),"TR","PP","Date"]]
    df_holef_temp = df_holef_temp.sort_values(by="残りヤード", ascending=False)
    df_holef_temp_GO = df_holef_temp[df_holef_temp["GR"] == "GO"]
    df_holef_temp_GO["SN"] = df_holef_temp_GO["SN"].astype(int)
    return df_holef_temp_GO

@st.cache_data
def plot_teeing_club(df_holef,hole):
    club_list = list(df_holef["T"].unique())
    # "T"の要素別に頻度ヒストグラムを作成
    fig, ax = plt.subplots(figsize=(3, 3))
    for club in club_list:
        data = df_holef[df_holef["T"] == club][str(hole)]
        ax.hist(data, bins=15, alpha=0.5, label=club)
    ax.legend()

    return(club_list,fig)

@st.cache_data
def plot_teeing_club2(select_club,df_holef,hole): 
    # 選択されたTの要素=クラブのScoreヒストグラムを作成
    df_temp_bante = df_holef[df_holef["T"].isin([select_club])]
    fig3, ax3 = plt.subplots(figsize=(3,3))
    ax3.hist(df_temp_bante[str(hole)],bins=15,color="red")

    return(df_temp_bante,fig3)

def hole_selection():
    #イン アウト選択により絞り込む 
    out_in = st.radio("Out / In",("Out","In"), horizontal=True)
    if out_in == "Out" :
        #hole = st.sidebar.selectbox(
        #"Hole",[1,2,3,4,5,6,7,8,9]
        #)
        hole = st.radio("Par5 >> 6, 8",(1,2,3,4,5,6,7,8,9), horizontal=True)
    else:
        hole = st.radio("Par5 >> 14,18",(10,11,12,13,14,15,16,17,18), horizontal=True)
    return hole

def the_latest_record(df):
    if st.sidebar.checkbox("最近のスコア表示"):
        df3 = df[['Score','OB',"Out","In"]]
        st.sidebar.table(df3.head(10))

def selection_in_sidebar(df_h):
    #年でFilterするオプション#Streamlitのマルチセレクト
    year_list = list(df_h["y"].unique())
    default_list = ["23","22"]
    select_year = st.sidebar.multiselect("年でFilterling",year_list,default=default_list)
    df_holef = df_h[(df_h["y"].isin(select_year))]

    #Ｇｒｅｅｎの画像表示
    #image = green_image(str(hole),"HN")[0]
    #caption = green_image(str(hole),"HN")[1]
    #st.sidebar.image(image,caption=caption)

    #PinポジでFilterするオプション　#Streamlitのマルチセレクト
    #PP_list = list(df_h["PP"].unique())
    #select_PP = st.sidebar.multiselect("Pin PositionでFilterling",PP_list,default=PP_list)
    #df_holef = df_holef[(df_holef["PP"].isin(select_PP))]

    #月でFilterするオプション　#Streamlitのマルチセレクト
    month_list = list(df_h["m"].unique())
    select_month = st.sidebar.multiselect("月でFilterling",month_list,default=month_list)
    df_holef = df_holef[(df_holef["m"].isin(select_month))]
    return df_holef

def deletefunction(df_holef,hole,df_ODB,lastdateOB,OBnumbers,df_count2OB,df_countTOB,totalobnumbers,base,df_3patt,df_db_on):
    
    # 2  # メトリクス       
    if df_holef.shape[0]:
        base = df_holef.shape[0]
    else:
        base = 1000 #分母で使用するので0にしない。
    totalobnumbers = OBnumbers + df_count2OB.shape[0]

    pattave = df_holef["PN"].mean()
    labelCB = f" patt {pattave:.2f}"


    meterG, percentageS, numberS = st.tabs([labelCB,":deer: ％",":deer: 数"])
    with meterG:
        # Streamlitでゲージチャートの表示
        if(1): #function enabled/disabled option
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
    with st.expander(f"Score_hist.: :skull: DB以上 {lastdate}"):
            #グラフ設定 matplotlib
            fig, ax = plt.subplots()
            #ヒストグラム
            ax.hist(df_holef[str(hole)],bins=10,)
            st.pyplot(fig, use_container_width=True)

    # 4 # データフレーム表示
    with st.expander(f"Dataframe:ラウンド数は {str(df_holef.shape[0])} 回"):
            show_dataframe(hole,df_holef,df_countGon)



def main():
    debug_mode = 0
    if(debug_mode):
        #プログレスバー
        progress_bar = st.progress(0)
        process_name = st.empty()
        progress_text1 = st.empty()
        progress_text2 = st.empty()
        progress_text3 = st.empty()
        progress_text4 = st.empty()
        progress_text5 = st.empty()
        progress_text6 = st.empty()
        progress_text7 = st.empty()
        progress_text8 = st.empty()

        progress_text = st.empty()
        start_time = time.time()
        ini_start_time = time.time()
    
    df = cf.main_dataframe()             #csvからデータフレームに取り込み
    hole = hole_selection()              #選択するホール番号
    df_h = cf.dataframe_by_hole(df,hole) #holeに関する情報にスライスし、データフレーム作成する。

    #######################
    # サイドバー表示       #
    #　sidebarを加える    #
    ######################
    #df_h = ホールにフィルター
    #df_holef = 年 月 PinPosition で Filterしたもの 
    ######################
    #最近のスコア表示
    if(0): #function disabled
        the_latest_record(df)

    if(debug_mode):
        # プログレスバーとテキストの更新
        progress_bar.progress(10)


    #年や月でフィルタリングする。
    df_holef = selection_in_sidebar(df_h) #df_holef = 年 月 PinPosition で Filterしたもの 

    #############################
    ###ここから Subdataframeの生成
    #dataframeは 変数名に 必ず "df_" を加えることとする。
    #############################
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



    # 2  # メトリクス       
    if df_holef.shape[0]:
        base = df_holef.shape[0]
    else:
        base = 1000 #分母で使用するので0にしない。
    totalobnumbers = OBnumbers + df_count2OB.shape[0]

    pattave = df_holef["PN"].mean()
    labelCB = f" patt {pattave:.2f}"

    ### 表示       ####
    ###################
    # 1  # タイトルは、In/OUT Hole Number、回数 打数アベレージを記載
    bun_title = f"No.{str(hole)}  :golfer: {df_holef.shape[0]} {iconp} {df_holef[str(hole)].mean():.3f} "
    st.subheader(bun_title)

    if(0):
        meterG, percentageS, numberS = st.tabs([labelCB,":deer: ％",":deer: 数"])
        with meterG:
            # Streamlitでゲージチャートの表示
            if(1): #function enabled/disabled option
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
    ## if st.checkbox(f"Score_hist.: :skull: DB以上 {lastdate}"):
    ##        #グラフ設定 matplotlib
    ##        fig, ax = plt.subplots(figsize=(6, 4))
    ##        #ヒストグラム
    ##        ax.hist(df_holef[str(hole)],bins=10,)
    ##        st.pyplot(fig, use_container_width=True)

    # 4 # データフレーム表示
    ## with st.expander(f"Dataframe:ラウンド数は {str(df_holef.shape[0])} 回"):
    ##        show_dataframe(hole,df_holef,df_countGon)


    if(debug_mode):
        elapsed_time = time.time() - start_time
        start_time = time.time()
        progress_text1.text(f"to dataframe Elapsed time: {elapsed_time:.2f} seconds")
    


    # 5 # #多様な深堀のためのデータ提供
    tabITG, tabIHN ,tabPP, tabHist, tabOBs, tab3P, tabdbs, tabmeter = st.tabs([" :man-golfing: "," :golf: "," :1234: "," :musical_score: ", " :ok_woman: ", " :field_hockey_stick_and_ball: ","DBon","Teeing"])
    with tabITG: #ホールイメージ TG00.png
        if(debug_mode):        # プログレスバーとテキストの更新
            progress_bar.progress(20)
            process_name.text(f"残りヤードとホールイメージ")

        #reference GIRで使用する アイアンの過去良い軌跡
        df_holef_temp_GO = ref_GIR_iron(df_holef,hole)
        st.dataframe(df_holef_temp_GO[["残りヤード","G","SN","PN",str(hole),"TR","PP","Date"]].style.background_gradient(cmap="Blues"),hide_index=True)


        image = cf.green_image(str(hole),"TG")[0]
        caption = cf.green_image(str(hole),"TG")[1]
        st.image(image,caption=caption)

        if(debug_mode):# プログレスバーとテキストの更新
            elapsed_time = time.time() - start_time
            start_time = time.time()
            progress_text2.text(f"残りヤードとホールイメージ Elapsed time: {elapsed_time:.2f} seconds")



    with tabIHN: #グリーンイメージ HN00.png
        if(debug_mode):# プログレスバーとテキストの更新
            progress_bar.progress(30)
            process_name.text(f"グリーンと番手戦略")

        if st.checkbox("グリーン表示",value=False):
            image = cf.green_image(str(hole),"HN")[0]
            caption = cf.green_image(str(hole),"HN")[1]
            st.image(image,caption=caption) 

        club_list = list(df_holef["G"].unique())

        if st.checkbox("TeeingのClub別で頻度/打数のグラフ表示",value=False):
            fig, ax = plt.subplots(figsize=(3, 3))
            for club in club_list:
                data = df_holef[df_holef["G"] == club][str(hole)]
                ax.hist(data, bins=15, alpha=0.5, label=club)
            ax.legend()
            st.pyplot(fig, use_container_width=False)

        if st.checkbox("番手別で頻度/打数のグラフ表示",value=False):
            select_club = st.selectbox("Club選択",club_list)
            df_temp_bante = df_holef[df_holef["G"].isin([select_club])]
            fig3, ax3 = plt.subplots(figsize=(3,3))
            ax3.hist(df_temp_bante[str(hole)],bins=15,color="red")
            st.pyplot(fig3, use_container_width=False)
            df_temp_bante

        if(debug_mode): # プログレスバーとテキストの更新
            elapsed_time = time.time() - start_time
            start_time = time.time()
            progress_text3.text(f"グリーンと番手戦略 Elapsed time: {elapsed_time:.2f} seconds")



    with tabPP: #PinポジでFilterするオプション　#Streamlitのマルチセレクト
        if(debug_mode): # プログレスバーとテキストの更新
            progress_bar.progress(40)
            process_name.text(f"PinPosition別データフレーム")


        PP_list = list(df_holef["PP"].unique())
        #select_PP = st.multiselect("Pin PositionでFilterling",PP_list,default=PP_list)
        #df_holef = df_holef[(df_holef["PP"].isin(select_PP))]

        #文字列化 PP_listは整数なので、st.tabsに使えないので。
        str_list = [str(num) for num in PP_list]
        # タブの作成
        tabs = st.tabs(str_list)
        # 各タブにコンテンツを追加
        for i, tab in enumerate(tabs):
            with tab:
                #st.write(f"This is the Dataframe filter by {str_list[0]}")
                df_temp_hole = df_holef[df_holef["PP"] == PP_list[i] ]
                st.write(f"数 {df_temp_hole.shape[0]}")
                st.dataframe(df_temp_hole[["TR","Comment","G","GR","SN","PN",str(hole),"Date"]].style.background_gradient(cmap="Reds"),hide_index=True)

        if(debug_mode):# プログレスバーとテキストの更新
            elapsed_time = time.time() - start_time
            start_time = time.time()
            progress_text4.text(f"PinPosition別データフレーム Elapsed time: {elapsed_time:.2f} seconds")



    with tabHist:# スコアの時系列図 
        if(debug_mode):# プログレスバーとテキストの更新
            progress_bar.progress(50)
            process_name.text(f"スコアの時系列")

        subtab1, subtab2 = st.tabs(["chart","database"])
        with subtab1:
            st.caption("左が最新")
            df_areac = df_holef[[str(hole),"PN"]]
            st.line_chart(df_areac)
        with subtab2:
            st.write("DB On以上にフィルター")
            st.dataframe(df_ODB.style.background_gradient(cmap="Blues"),hide_index=True)

        if(debug_mode):# プログレスバーとテキストの更新
            elapsed_time = time.time() - start_time
            start_time = time.time()
            progress_text5.text(f"スコアの時系列 Elapsed time: {elapsed_time:.2f} seconds")


    with tabOBs:# OBの深堀 
        if(debug_mode):# プログレスバーとテキストの更新
            progress_bar.progress(60)
            process_name.text(f"OBデータ")

        st.write(f":calendar:{lastdateOB}")
        st.metric(label="TeeingOB数",value=OBnumbers,)
        st.metric(label="2ndOB率",value=df_count2OB.shape[0],)
        df_countTOB
        #データフレーム表示
        with st.expander("データフレーム詳細"):
            st.write("データフレーム詳細")
            df_holef[[str(hole),"T","TR","GR","Comment","PP","SN","PN"]]

        if(debug_mode):# プログレスバーとテキストの更新
            elapsed_time = time.time() - start_time
            start_time = time.time()
            progress_text5.text(f"OBデータ Elapsed time: {elapsed_time:.2f} seconds")


    with tab3P:# Pattの深堀 
        if(debug_mode):# プログレスバーとテキストの更新
            progress_bar.progress(70)
            process_name.text(f"3Pattデータ")

        pattave = df_3patt["SN"].mean()
        patt3 = f"3 PATTの数 {df_3patt.shape[0]}  _ 3patt時の距離 {pattave:.2f} scatterchart"

        if st.checkbox(patt3,value=False):
            #グラフ設定 matplotlib
            fig, ax = plt.subplots()
            #scatter
            ax.scatter(
                x=df_holef["SN"],
                y=df_holef["PN"],
                c=df_holef[str(hole)],
                #c=df_holef[PP],
                alpha=0.8,
                #vmin=df_holef[str(hole)].min(),
                #vmax=df_holef[str(hole)].max()
                )
            st.pyplot(fig, use_container_width=True)

        #ヒストグラム
        if st.checkbox("1st Patt 残り歩数 ヒストグラム",value=False):
            fig2, ax2 = plt.subplots()
            ax2.hist(df_holef["SN"],bins=30,)
            st.pyplot(fig2, use_container_width=True)

        if(debug_mode):# プログレスバーとテキストの更新
            elapsed_time = time.time() - start_time
            start_time = time.time()
            progress_text6.text(f"3 PATTの数 Elapsed time: {elapsed_time:.2f} seconds")


    with tabdbs:
        if(debug_mode):
            # プログレスバーとテキストの更新
            progress_bar.progress(80)
            process_name.text(f"ダボOnデータ")

        fig = gauge_view(totalobnumbers,base,df_3patt,df_db_on)
        # Streamlitでゲージチャートの表示
        st.plotly_chart(fig)
        df_db_on

        if(debug_mode):# プログレスバーとテキストの更新
            elapsed_time = time.time() - start_time
            start_time = time.time()
            progress_text7.text(f"ダボOnデータ Elapsed time: {elapsed_time:.2f} seconds")


    with tabmeter:
        club_list,fig = plot_teeing_club(df_holef,hole)
        if st.checkbox("Teeingshot 打数と頻度チャート",value=False):
            st.pyplot(fig, use_container_width=False)
        
        if st.checkbox("Teeing Club別 打数と頻度チャート",value=False):
            select_club = st.selectbox("Club選択",club_list)
            df_temp_bante,fig3 = plot_teeing_club2(select_club,df_holef,hole)
            st.pyplot(fig3, use_container_width=False)
            st.dataframe(df_temp_bante)

        if(debug_mode):# プログレスバーとテキストの更新
            elapsed_time = time.time() - start_time
            progress_text8.text(f"Teeing 番手 Elapsed time: {elapsed_time:.2f} seconds")


    if(debug_mode):# プログレスバーとテキストの更新
        progress_bar.progress(100)
        process_name.text(f"完了")
        elapsed_time = time.time() - ini_start_time
        progress_text.text(f"Elapsed time: {elapsed_time:.2f} seconds")



if __name__ == "__main__":
    main()
