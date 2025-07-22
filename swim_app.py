import pandas as pd
import streamlit as st

# タイトルとページ設定
st.set_page_config(page_title="女子エントリー検索", layout="wide")
st.title("🏊‍♀️ 女子エントリー情報検索ツール")
st.markdown("年代区分・種目・距離で絞り込み、選手名を選択してください。選手ごとの出場情報が一覧で表示されます。")

# データ読み込み
@st.cache_data
def load_data():
    df_raw = pd.read_csv("entry_list_women.csv", header=0, usecols=[2,3,4,5,6,7,8,9])
    df_raw.columns = ["名前", "年", "年代区分", "所属", "エントリータイム", "性別", "距離", "種目"]

    # 文字列に変換して空白除去
    for col in df_raw.columns:
        df_raw[col] = df_raw[col].astype(str).str.strip()
    
    return df_raw

df = load_data()

# フィルター UI
cols = st.columns(3)
with cols[0]:
    selected_age = st.selectbox("年代区分", ["すべて"] + sorted(df["年代区分"].unique()))
with cols[1]:
    selected_event = st.selectbox("出場種目", ["すべて"] + sorted(df["種目"].unique()))
with cols[2]:
    selected_distance = st.selectbox("距離", ["すべて"] + sorted(df["距離"].unique()))

# 条件でフィルタリング
df_filtered = df.copy()
if selected_age != "すべて":
    df_filtered = df_filtered[df_filtered["年代区分"] == selected_age]
if selected_event != "すべて":
    df_filtered = df_filtered[df_filtered["種目"] == selected_event]
if selected_distance != "すべて":
    df_filtered = df_filtered[df_filtered["距離"] == selected_distance]

# 選手名プルダウン（フィルタ済の中から）
unique_names = sorted(df_filtered["名前"].dropna().unique())
name_query = st.selectbox("選手名を選択してください", unique_names if unique_names else ["該当なし"])

# 表示処理
if name_query and name_query != "該当なし":
    result = df[df["名前"] == name_query]
    st.success(f"{name_query} さんの出場情報（{len(result)} 件）")

    for _, row in result.iterrows():
        subset = df[(df["種目"] == row["種目"]) & (df["年代区分"] == row["年代区分"])]

        # タイムを秒に変換する関数
        def clean_time(t):
            t = str(t).strip().replace("　", "").replace(" ", "")
            try:
                if ":" in t:
                    parts = t.split(":")
                    return int(parts[0]) * 60 + float(parts[1])
                else:
                    return float(t)
            except:
                return float("inf")

        subset = subset.copy()
        subset["順位"] = subset["エントリータイム"].apply(clean_time).rank(method="min")
        rank = int(subset[subset["名前"] == row["名前"]]["順位"].values[0])

        st.markdown("---")
        st.markdown(f"- 🏊‍♀️ **種目**: {row['距離']} {row['種目']}")
        st.markdown(f"- 👤 **年代区分**: {row['年代区分']}")
        st.markdown(f"- 🏢 **所属**: {row['所属']}")
        st.markdown(f"- ⏱️ **エントリータイム**: {row['エントリータイム']}")
        st.markdown(f"- 📊 **同年代・同種目内順位**: **{rank} 位**")
