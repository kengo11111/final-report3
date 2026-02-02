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

# 年度は識別用の列として保持する
id_cols = ['調査年']

# Mから始まる列（性別・年齢層ごとの平均時間）だけを抽出する
value_cols = [c for c in df.columns if c.startswith('M')]

# melt を利用し、講義で扱った資料のように横に並んだ年齢層・性別ごとの平均時間の列を横に並んだ指標列を1列にまとめて縦持ちデータに変換する
df_long = df.melt(
    id_vars=id_cols,
    value_vars=value_cols,
    var_name='raw_col',
    value_name='minutes'
)

# 列名（例: M100220_1次活動の平均時間（25～34歳）（女））から、
# 「項目名」「年齢層」「性別」を抽出するための正規表現パターン
pattern = r'_(.*?)（(.*?)）（(.*?)）'