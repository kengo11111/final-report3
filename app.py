import streamlit as st
import pandas as pd
import plotly.express as px
import re

st.title('時間使用調査（活動別・性別・年齢層）')
# 活動種別の表示を英語から日本語に変更
activity = st.sidebar.selectbox(
    '活動種別を選択してください',
    ['一次活動', '二次活動', '三次活動']
)

# 日本語表示とCSVファイル名（英語）の対応関係を定義
activity_map = {
    '一次活動': 'Primary',
    '二次活動': 'Secondary',
    '三次活動': 'Tertiary'
}

# 選択された日本語ラベルをCSVファイル名用の英語に変換
activity_en = activity_map[activity]

# 読み込むCSVを日本語選択に応じて切り替える
df = pd.read_csv(f'{activity_en}.csv', encoding='shift_jis')