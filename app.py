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


# 「地域」と「年齢層」に一致する行だけを抽出
df_plot = df_long[
    (df_long['age'].isin(age))
]

# 「年度」という文字列を除去し、調査年を数値型に変換する
df_plot['year'] = df_plot['調査年'].str.replace('年度', '').astype(int)

# 散布図の作成
fig = px.scatter(
    df_plot,
    x='year',
    y='minutes',
    color=color,
    labels={
        'year': '調査年',
        'minutes': '平均時間（分）'
    },
    trendline='ols',
    title='年次別平均活動時間の推移'
)

fig2 = px.box(
    df_plot,
    x=color,
    y='minutes',
    labels={
        'minutes': '平均時間（分）'
    },
    title='分類別平均活動時間の分布'
)

tab_info, tab1, tab2 = st.tabs(['アプリの概要', '年次推移', '分布の比較'])

# アプリ説明タブ
with tab_info:
    st.header('アプリの概要')
    st.write(
        '本アプリは、e-stat(政府統計の総合窓口)のデータを用いて、'
        '活動別・性別・年齢層ごとの1日あたり平均活動時間を可視化するアプリです。'
        '※ 表示されている平均時間は、対象年齢人口における1日あたりの平均値（分）です。'
        '調査は5年ごとに実施されており、年度によっては一部の年齢層で欠損値があります。'
    )

    st.header('目的')
    st.write(
        '年齢層や性別による生活時間の違いを把握するとともに、'
        '時間使用の長期的な変化を視覚的に理解することを目的としています。'
    )

    st.header('使い方')
    st.write(
        '1. サイドバーから活動種別（一次活動・二次活動・三次活動）を選択します。\n'
        '2. 年齢層や色分けの分類条件を指定します。\n'
        '3. 「年次推移」タブで時系列変化を確認します。\n'
        '4. 「分布の比較」タブで分類別の分布状況を確認します。'
    )

with tab1:
    st.plotly_chart(fig)

with tab2:
    st.plotly_chart(fig2)