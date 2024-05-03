import streamlit as st
import numpy as np
import pandas as pd
import datetime
import pytz
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import sys
sys.path.append('../')  # 上位フォルダをパスに追加

import cf  # 上位フォルダにあるモジュールをインポート

import time

# ボタンが押されたときの処理
def main():

    # タイムゾーンを設定
    jst = pytz.timezone('Asia/Tokyo')


    # ラジオボタンの作成
    options = ["BD", "PAR", "Boggy", "DB", "+DB"]
    default_radio = "PAR"
    selected_radio = st.radio("Select one:", options, index=options.index(default_radio), horizontal=True)

    # スライダーの作成
    default_slider = 110
    selected_slider = st.slider("Select a value:", 50, 200, default_slider)

    # 入力フォームの作成
    user_input = st.text_input("Enter text to save to Excel")


    # ボタンが押されたときの処理
    if st.button("Save to Excel"):
        # 入力された文字と日付をDataFrameに追加
        current_time = datetime.datetime.now(tz=jst)
        # タイムゾーン情報を削除
        current_time = current_time.replace(tzinfo=None)
        current_time
        new_data = {'Date': [current_time], 'Radio': [selected_radio], 'Slider': [selected_slider],'Input': [user_input], }
        new_df = pd.DataFrame(new_data)
        
        # 既存のExcelファイルがあるかどうかを確認
        try:
            existing_df = pd.read_excel('user_input_data.xlsx')
            updated_df = pd.concat([existing_df, new_df], ignore_index=True)
        except FileNotFoundError:
            updated_df = new_df
        
        # Excelファイルに保存
        updated_df.to_excel('user_input_data.xlsx', index=False)
        st.write("Data saved to Excel")
        st.table(updated_df)

    progress_bar = st.progress(0)
    status_text = st.empty()
    chart = st.line_chart(np.random.randn(10, 3))

    for i in range(10):
        # Update progress bar.
        progress_bar.progress(i + 1)

        new_rows = np.random.randn(10, 3)

        # Update status text.
        status_text.text(
            'The latest random number is: %s' % new_rows[-1, 1])

        # Append data to the chart.
        chart.add_rows(new_rows)

        # Pretend we're doing some computation that takes time.
        time.sleep(0.5)

    status_text.text('Done!')
    st.balloons()



if __name__ == "__main__":
    main()