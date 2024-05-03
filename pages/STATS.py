import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import sys
sys.path.append('../')  # 上位フォルダをパスに追加

import cf  # 上位フォルダにあるモジュールをインポート

@st.cache_data
def pickup_frame():
    df = cf.main_dataframe()
    df = df.copy()
    columns = ["Date","Year","Month",
               "Event","OB",
               "Penalty","Total","Score",
               "Out","In","Gon-Patt+36",
               "1st","2nd","green",
               "approach","Double Total",
               "3 shot in 100","Total.1","Score.1"
               ]
    df = df[columns]
    df["Year"] = df["Year"].astype(int)
    df["Month"] = df["Month"].astype(int)

    #整数化
    #columns_to_convert = ["OB", "Penalty", "Total", "1st", "2nd","green","approach","Double Total",
    #           "3 shot in 100","Total.1","Score.1"]
    #for column in columns_to_convert:
    #    df[column] = pd.to_numeric(df[column], errors='coerce').fillna(0).astype(int)

    df["Gon-Patt+36"] = pd.to_numeric(df["Gon-Patt+36"], errors='coerce').fillna(0).astype(int) + 30
    rename_dict = {"Score.1": "Birdie","Total.1":"X","Gon-Patt+36":"Patt数"}
    df.rename(columns=rename_dict, inplace=True)
    df_event = df[["Date","Year","Month","Event","OB","Score"]]
    df_stadata = df[["Year","Month","OB","Penalty","Total","Score",
               "Out","In","Patt数",
               "1st","2nd","green",
               "approach","Double Total",
               "3 shot in 100","X","Birdie"]]

    
    return (df,df_event,df_stadata)

@st.cache_data
def sidebar_display(df,df_event,df_stadata):

    df3 = df[['Score','OB',"Out","In"]]
    st.sidebar.table(df3.head(10))

@st.cache_data
def average_per_year(df_stadata):
    # 'Year' 列でグループ化し、各列の平均値を計算
    df_yearly_average = df_stadata.groupby('Year').mean()
    df_grouped_size = df_stadata.groupby('Year').size()
    df_yearly_average["Count"]=df_grouped_size
    return df_yearly_average

@st.cache_data
def average_per_month(df_stadata):
    # 'Year' 列でグループ化し、各列の平均値を計算
    df_monthly_average = df_stadata.groupby('Month').mean()
    df_grouped_size = df_stadata.groupby('Month').size()
    df_monthly_average["Count"]=df_grouped_size
    return df_monthly_average

@st.cache_data
def plot_distribution(df_stadata, selected_years, selected_score_type):
    # 選択された年のデータのみをフィルタリング
    df_filtered = df_stadata[df_stadata['Year'].isin(selected_years)]

    # 選択されたスコアタイプと'Year'でグループ化し、各'Year'の出現頻度を計算
    df_grouped = df_filtered.groupby([selected_score_type, 'Year']).size().unstack(fill_value=0)
    
    # 'Year'で降順にソート
    df_grouped = df_grouped.sort_index(axis=1, ascending=False)

    # 積み上げバーチャートを描画
    df_grouped.plot(kind='bar', stacked=True)

    plt.title(f'{selected_score_type} Distribution by Year')
    plt.xlabel(selected_score_type)
    plt.ylabel('Frequency')

    # 凡例が存在する場合のみ削除
    #legend = plt.legend()
    #if legend:
    #    legend.remove()

    st.pyplot(plt)

def plot_chart(kind,df_yearly_average):
        # df_yearly_averageを使用して折れ線グラフを作成
        plt.figure(figsize=(10, 5))
        
        if(kind=="Score"):
            plt.plot(df_yearly_average.index, df_yearly_average['Score'])
            plt.xlabel('Year')
            plt.ylabel('Score')
            plt.title('Yearly Average Score')

        elif(kind=="OutInPatt"):
            # df_yearly_averageを使用して折れ線グラフを作成
            plt.plot(df_yearly_average.index, df_yearly_average['In'], label='In')
            plt.plot(df_yearly_average.index, df_yearly_average['Out'], label='Out')
            plt.plot(df_yearly_average.index, df_yearly_average['Patt数'], label='Patt数')
            plt.xlabel('Year')
            plt.ylabel('Value')
            plt.title('Yearly Average Values')
            plt.legend()

        elif(kind=="Xx"):
            # df_yearly_averageを使用して折れ線グラフを作成
            plt.plot(df_yearly_average.index, df_yearly_average['OB'], label='OB')
            plt.plot(df_yearly_average.index, df_yearly_average['Penalty'], label='Penalty')
            plt.xlabel('Year')
            plt.ylabel('Value')
            plt.title('Yearly Average Values')
            plt.legend()

        elif(kind=="Bvs3100"):
            # df_yearly_averageを使用して折れ線グラフを作成
            plt.plot(df_yearly_average.index, df_yearly_average['3 shot in 100'], label='3 shot in 100')
            plt.plot(df_yearly_average.index, df_yearly_average['Birdie'], label='Birdie')
            plt.xlabel('Year')
            plt.ylabel('Value')
            plt.title('Yearly Average Values')
            plt.legend()

        else:
            # df_yearly_averageを使用して折れ線グラフを作成
            plt.plot(df_yearly_average.index, df_yearly_average['1st'], label='DB Factor 1st')
            plt.plot(df_yearly_average.index, df_yearly_average['2nd'], label='DB Factor 2nd')
            plt.plot(df_yearly_average.index, df_yearly_average['green'], label='DB Factor GIR')
            plt.plot(df_yearly_average.index, df_yearly_average['approach'], label='DB Factor around green')
            plt.xlabel('Year')
            plt.ylabel('Value')
            plt.title('Yearly Average Values')
            plt.legend()       

        return(plt)

def main_display(df,df_event,df_stadata):
    df_yearly_average = average_per_year(df_stadata)
    df_monthly_average = average_per_month(df_stadata)

    st.title("STATS")
    #with st.expander(f"For Developping"):
    #    st.dataframe(df)
    
    with st.expander(f"年ごとのScore分布"):
        # 年の一覧を取得
        years = sorted(df_stadata['Year'].unique())

        # 最新の3年を取得
        latest_years = years[-3:]

        # ユーザーに年を選択させる（初期選択は最新の3年）
        selected_years = st.multiselect('Select years', options=years, default=latest_years)

        # ユーザーにスコアタイプを選択させる
        score_types = ['Score', 'Out', 'In']
        selected_score_type = st.radio('Select score type', options=score_types, index=0, horizontal=True)

        # 選択された年とスコアタイプに基づいてバーチャートを描画
        plot_distribution(df_stadata, selected_years, selected_score_type)

    DT_event, DT_stats, DT_year, DT_month = st.tabs(["event","Stats","year","month"])
    with DT_event:
        st.dataframe(df_event.style.background_gradient(cmap="Greens"),hide_index=True)

    with DT_stats: #st.expander(f"Stats表示"):
        st.dataframe(df_stadata.style.background_gradient(cmap="Blues"),hide_index=True)
    
    with DT_year: #st.expander(f"年ごとの集計"):
        st.dataframe(df_yearly_average.style.background_gradient(cmap="Oranges"))
        # df_yearly_averageを使用して折れ線グラフを作成
        Score,OutInPatt,Xx, DBFa, Bvs3100 =st.tabs(["Score","OutInPatt","OBHazard","DB factor","Birdie"])
        with Score:
            st.write("Score")
            st.pyplot(plot_chart("Score",df_yearly_average))
        with OutInPatt:
            st.write("OutInPatt")
            st.pyplot(plot_chart("OutInPatt",df_yearly_average))
        with Xx:
            st.write("OBHazard")
            st.pyplot(plot_chart("Xx",df_yearly_average))
        with DBFa:
            st.write("DB factor")
            st.pyplot(plot_chart("DBF",df_yearly_average))
        with Bvs3100:
            st.write("Birdie vs 3shotin100")
            st.pyplot(plot_chart("Bvs3100",df_yearly_average))



    with DT_month: #st.expander(f"月ごとの集計"):
        st.dataframe(df_monthly_average.style.highlight_max(axis=0))

def main():
    df,df_event,df_stadata = pickup_frame()
    sidebar_display(df,df_event,df_stadata)
    main_display(df,df_event,df_stadata)
    

if __name__ == "__main__":
    main()