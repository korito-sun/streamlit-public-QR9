# """"""
# 実行は
# streamlit run .\as_st9_fileUp.py
#
# 停止は
# ctr+C
#
# 更新履歴
# 20251127: 折れ線グラフ、棒グラフ追加
# 20251202: 読み込み時に重複行を削除する機能を追加
# 20251202: 円グラフをドーナツグラフ（中央50%白抜き）に変更
# 20251202: ドーナツグラフの中央にカテゴリ名と合計値を表示するよう変更
# 20251202: 全データグラフの下にNGデータの詳細一覧表を追加
# 20251202: NG一覧表の表示列をQR3までに制限
# 20251202: st.dataframeの警告対応（use_container_width -> width='stretch'）
# 20251202: NG一覧表からPCB_Name列を除外
# 20251202: NG一覧表内の"ERROR"赤文字化対応（applymap -> map へ修正）
# 20251202: 円グラフの件数表示ズレ（計算誤差による切り捨て）を修正
# 20251203: UploadFileするように追加
# 20251203: セッションステートで表示期間管理 /全期間表示ボタン追加　/スライドバーで1か月毎にデータ表示を変化できるようにデータアップロードの下に機能追加
# """"""


import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import platform # OS判定用に追加

# ページ設定
st.set_page_config(page_title="Trace Log Analysis", layout="wide")

# --- 日本語フォント設定 (Windows/Mac対応) ---
system_name = platform.system()
if system_name == "Windows":
    plt.rcParams['font.family'] = 'MS Gothic'
elif system_name == "Darwin": # Mac
    plt.rcParams['font.family'] = 'AppleGothic'
else:
    # Linux系やその他（必要に応じて設定）
    plt.rcParams['font.family'] = 'IPAGothic'

st.title("ＡＧ６液晶演出生産時QRコード検査推移ダッシュボード:\nTrace Log Analysis Dashboard")

# --- セッションステートの初期化 ---
if 'filter_mode' not in st.session_state:
    st.session_state.filter_mode = 'ALL'

# --- コールバック関数 ---
def set_all_mode():
    st.session_state.filter_mode = 'ALL'

def set_month_mode():
    st.session_state.filter_mode = 'MONTH'

# --- サイドバー設定 ---
st.sidebar.header("データ読み込み設定")
uploaded_file = st.sidebar.file_uploader("CSVファイルをアップロードしてください", type="csv")

DATE_COL = 'DateTime' 

# データ読み込みとキャッシュ
@st.cache_data
def load_data(file):
    try:
        df = pd.read_csv(file)
        
        # 重複行を削除
        before_count = len(df)
        df = df.drop_duplicates()
        after_count = len(df)
        
        filename = file.name if hasattr(file, 'name') else "Uploaded File"
        print(f"Loaded {filename}: {before_count} -> {after_count} (Dropped {before_count - after_count})")
        st.sidebar.success(f"読込完了: {after_count}件")
        
    except Exception as e:
        st.error(f"ファイル読み込みエラー: {e}")
        return None

    target_cols = ['Model', 'FCT_ID', 'QRresult']
    for col in target_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
    
    # 日付列の変換
    if DATE_COL in df.columns:
        df[DATE_COL] = pd.to_datetime(df[DATE_COL], errors='coerce')
        df['YYYY-MM'] = df[DATE_COL].dt.strftime('%Y-%m')
        
    return df

# 単一の円グラフ描画関数
def plot_single_pie_chart(data, value_col='QRresult', title='All Data'):
    counts = data[value_col].value_counts()
    if len(counts) > 0:
        fig, ax = plt.subplots(figsize=(6, 6))
        colors = {'OK': '#66b3ff', 'NG': '#ff9999'}
        labels = counts.index
        sizes = counts.values
        pie_colors = [colors.get(l, '#cccccc') for l in labels]
        
        ax.pie(sizes, labels=labels, 
               autopct=lambda p: f'{p:.1f}%\n({int(round(p*sum(sizes)/100))})',
               startangle=90, colors=pie_colors, textprops={'fontsize': 12},
               wedgeprops={'width': 0.5, 'edgecolor': 'white'}, pctdistance=0.75)
        
        ax.text(0, 0, f'Total\n{sum(sizes)}', ha='center', va='center', fontsize=14, fontweight='bold')
        ax.set_title(title, fontsize=16)
        return fig
    else:
        return None

# 日別推移の棒グラフ描画関数
def plot_daily_trend(data, date_col, value_col='QRresult'):
    df_temp = data.copy()
    df_temp = df_temp.dropna(subset=[date_col])
    df_temp['date_only'] = df_temp[date_col].dt.date
    
    daily_counts = df_temp.groupby(['date_only', value_col]).size().unstack(fill_value=0)
    
    if 'OK' not in daily_counts.columns: daily_counts['OK'] = 0
    if 'NG' not in daily_counts.columns: daily_counts['NG'] = 0
    daily_counts = daily_counts.sort_index()

    if len(daily_counts) > 0:
        fig, ax = plt.subplots(figsize=(10, 6))
        x = range(len(daily_counts))
        width = 0.35
        ok_vals = daily_counts['OK'].values
        ng_vals = daily_counts['NG'].values

        bars_ok = ax.bar([i - width/2 for i in x], ok_vals, width, label='OK', color='#66b3ff')
        bars_ng = ax.bar([i + width/2 for i in x], ng_vals, width, label='NG', color='#ff9999')

        ax.set_xticks(x)
        ax.set_xticklabels([d.strftime('%y/%m/%d') for d in daily_counts.index])
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")

        ax.set_title('Daily Trend (OK vs NG)', fontsize=16)
        ax.set_ylabel('Count')
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.7, axis='y')

        for bars in [bars_ok, bars_ng]:
            for rect in bars:
                h = rect.get_height()
                if h > 0:
                    ax.text(rect.get_x() + rect.get_width() / 2, h, f'{int(h)}', ha='center', va='bottom', fontsize=9)
        plt.tight_layout()
        return fig
    else:
        return None

# グループ別円グラフ
def plot_grouped_pie_charts(data, category_col, value_col='QRresult'):
    unique_cats = sorted(data[category_col].unique())
    n_cats = len(unique_cats)
    if n_cats == 0: return None
    
    fig, axes = plt.subplots(1, n_cats, figsize=(6 * n_cats, 6))
    if n_cats == 1: axes = [axes]
    
    colors = {'OK': '#66b3ff', 'NG': '#ff9999'}
    
    for ax, cat in zip(axes, unique_cats):
        subset = data[data[category_col] == cat]
        counts = subset[value_col].value_counts()
        
        if len(counts) > 0:
            labels = counts.index
            sizes = counts.values
            pie_colors = [colors.get(l, '#cccccc') for l in labels]
            
            ax.pie(sizes, labels=labels, 
                   autopct=lambda p: f'{p:.1f}%\n({int(round(p*sum(sizes)/100))})',
                   startangle=90, colors=pie_colors, textprops={'fontsize': 12},
                   wedgeprops={'width': 0.5, 'edgecolor': 'white'}, pctdistance=0.75)
            
            label_text = f'{cat}\n({sum(sizes)})'
            ax.text(0, 0, label_text, ha='center', va='center', fontsize=14, fontweight='bold')
            ax.set_title(f'{category_col}: {cat}', fontsize=16)
        else:
            ax.text(0.5, 0.5, 'No Data', ha='center')
            ax.axis('off')

    plt.tight_layout()
    return fig

# --- メイン処理 ---
if uploaded_file is not None:
    try:
        df_original = load_data(uploaded_file)
        
        if df_original is not None:
            
            # --- 表示期間設定機能 ---
            st.sidebar.markdown("---")
            st.sidebar.subheader("📅 表示期間設定")
            
            st.sidebar.button("全期間を表示 (リセット)", on_click=set_all_mode, use_container_width=True)

            if 'YYYY-MM' in df_original.columns:
                month_list = sorted(df_original['YYYY-MM'].dropna().unique())
                
                if len(month_list) > 0:
                    if 'selected_month' not in st.session_state or st.session_state.selected_month not in month_list:
                        st.session_state.selected_month = month_list[-1]

                    selected_month = st.sidebar.select_slider(
                        "月を選択してください",
                        options=month_list,
                        value=st.session_state.selected_month,
                        key='selected_month', 
                        on_change=set_month_mode 
                    )
                else:
                    st.sidebar.warning("日付データが無いため期間選択できません")
                    selected_month = None
            else:
                selected_month = None

            # --- フィルタリング実行 ---
            if st.session_state.filter_mode == 'MONTH' and selected_month:
                df = df_original[df_original['YYYY-MM'] == selected_month].copy()
                display_title_suffix = f"【期間: {selected_month}】"
                st.sidebar.info(f"表示中: {selected_month}")
            else:
                df = df_original.copy()
                display_title_suffix = "【全期間データ】"
                st.sidebar.info("表示中: 全期間")


            # --- 分析画面描画 ---
            st.subheader(f"分析結果 {display_title_suffix}")

            if len(df) == 0:
                st.warning("選択された期間にデータがありません。")
            
            elif 'QRresult' in df.columns:
                
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.markdown("#### OK/NG 比率")
                    fig_all = plot_single_pie_chart(df, title=f"Summary {display_title_suffix}")
                    if fig_all: st.pyplot(fig_all)
                
                with col2:
                    st.markdown("#### 日別 推移")
                    if DATE_COL in df.columns:
                        fig_trend = plot_daily_trend(df, DATE_COL)
                        if fig_trend: st.pyplot(fig_trend)
                    else:
                        st.warning("日付列が見つかりません")

                # --- NG詳細リスト ---
                st.markdown("### ⚠️ NG発生データ詳細")
                df_ng = df[df['QRresult'] == 'NG'].copy()
                
                if not df_ng.empty:
                    st.write(f"期間内 NG件数: {len(df_ng)} 件")
                    if DATE_COL in df_ng.columns:
                        df_ng = df_ng.sort_values(by=DATE_COL, ascending=False)
                    
                    df_display = df_ng
                    if 'QR3' in df_ng.columns:
                        df_display = df_ng.loc[:, :'QR3']
                    elif 'QRresult' in df_ng.columns:
                        cols = df_ng.columns.tolist()
                        idx = cols.index('QRresult')
                        df_display = df_ng.iloc[:, :idx]
                    
                    if 'PCB_Name' in df_display.columns:
                        df_display = df_display.drop(columns=['PCB_Name'])
                        
                    def highlight_error(val):
                        if isinstance(val, str) and 'ERROR' in val:
                            return 'color: red; font-weight: bold;'
                        return ''
                    
                    # 修正箇所: width='stretch' に変更
                    #st.dataframe(df_display.style.map(highlight_error), width=None) 
                    # ※注意: width='stretch' は一部のstreamlitバージョンで警告が出る場合があります。
                    # その場合は単に st.dataframe(..., use_container_width=True) のままでも動作はします。
                    # 今回の警告に従い、引数を調整しました。もしエラーになる場合は下記を使ってください。
                    # st.dataframe(df_display.style.map(highlight_error), use_container_width=True)
                    # 横幅いっぱいに広げたい場合
                    st.dataframe(df_display.style.map(highlight_error), width='stretch')

                else:
                    st.success("この期間のNGデータはありません。")

                st.markdown("---")

                st.subheader("Model別 QRresult内訳")
                if 'Model' in df.columns:
                    fig1 = plot_grouped_pie_charts(df, 'Model')
                    if fig1: st.pyplot(fig1)

                st.markdown("---")

                st.subheader("FCT_ID別 QRresult内訳")
                if 'FCT_ID' in df.columns:
                    fig2 = plot_grouped_pie_charts(df, 'FCT_ID')
                    if fig2: st.pyplot(fig2)

            else:
                st.error("CSVに 'QRresult' 列がありません。")

        else:
            st.error("データの読み込みに失敗しました。")

    except Exception as e:
        st.error(f"予期せぬエラーが発生しました: {e}")
else:
    st.info("👈 左側のサイドバーから分析したいCSVファイルをアップロードしてください。")