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

# 列名を1つずつ解析し、項目名・年齢層・性別を取り出す関数を定義する
def parse(col):
    m = re.search(pattern, col)
    if m:   #None → False,　何か入ってるオブジェクト → True
        return m.group(1), m.group(2), m.group(3)
    return None, None, None

# 列名（raw_col）を解析し、項目名・年齢層・性別をそれぞれ新しい列として追加する
df_long[['item', 'age', 'sex']] = (
    df_long['raw_col']
    .apply(lambda x: pd.Series(parse(x)))  #タプルを Series（1行分の小さな表）に変換
)

# 年度によって存在しない分類があるため、平均時間が欠損している行を除外する
df_long = df_long.dropna(subset=['minutes'])   #minutes 列だけを見る

# 抽出条件の指定
with st.sidebar:
    st.subheader('抽出条件')

    age = st.multiselect(
        '年齢層を選択してください（複数可）',
        df_long['age'].unique(),
        default=df_long['age'].unique()   # 初期表示時にすべての年齢層を選択状態にするための設定
    )

    st.subheader('色分け')

    color = st.selectbox(
        '分類を選択してください',
        ['性別', '年齢層']
    )

    if color == '性別':
        color = 'sex'
    else:
        color = 'age'
