import yfinance as yf
import pandas as pd
import streamlit as st
from datetime import datetime

# --- 定数定義 ---
RSI_PERIOD = 14
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70
HISTORY_PERIOD = "6mo"

def calculate_rsi(series, period=RSI_PERIOD):
    """RSI（相対力指数）を計算する関数"""
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    # 提案1: ゼロ除算を回避
    rs = gain / loss.replace(0, 1e-10)
    rsi = 100 - (100 / (1 + rs))
    return rsi

def analyze_stock(ticker_symbol, entry_price, status):
    st.markdown(f"### 🔍 銘柄コード: {ticker_symbol} の調査を開始します...")
    
    # --- ステップ1: 調査 (Research) ---
    try:
        stock = yf.Ticker(ticker_symbol)
        
        # 株価データを取得 (提案2: 定数を使用)
        hist = stock.history(period=HISTORY_PERIOD)
        
        if hist.empty:
            st.error(f"❌ エラー: データが見つかりませんでした。銘柄コード '{ticker_symbol}' を確認してください。")
            return

        # 企業情報の取得
        info = stock.info
        current_price = hist['Close'].iloc[-1]
        
        # ニュースの取得（最新3件）
        news = stock.news[:3] if stock.news else []

    except Exception as e:
        st.error(f"❌ データ取得中にエラーが発生しました: {e}")
        return

    # --- ステップ2: 分析 (Analysis) ---
    st.text("📊 データを分析中...")

    # A. テクニカル分析: RSI (14日)
    hist['RSI'] = calculate_rsi(hist['Close'], period=RSI_PERIOD)
    current_rsi = hist['RSI'].iloc[-1]

    # B. ファンダメンタル・ESG指標
    esg_score = info.get('sustainabilityScore', "N/A") # ESGスコア
    forward_pe = info.get('forwardPE', "N/A")          # 予想PER
    short_name = info.get('shortName', ticker_symbol)

    # --- ステップ3: 判断 (Decision) ---
    decision = "HOLD (様子見)"
    reason = []

    if current_rsi < RSI_OVERSOLD:
        decision = "BUY (買い検討)"
        reason.append(f"RSIが {current_rsi:.2f} で、売られすぎ水準({RSI_OVERSOLD}以下)です。反発の可能性があります。")
    elif current_rsi > RSI_OVERBOUGHT:
        decision = "SELL (売り検討)"
        reason.append(f"RSIが {current_rsi:.2f} で、買われすぎ水準({RSI_OVERBOUGHT}以上)です。過熱感があります。")
    else:
        reason.append(f"RSIは {current_rsi:.2f} で、中立的な水準です。")

    # --- ステップ4: ポジション分析 (Position Analysis) ---
    position_advice = _get_position_advice(status, entry_price, current_price, current_rsi)

    # --- 結果出力 (The Commander) ---
    st.divider()
    st.subheader(f"📢 分析結果レポート: {short_name} ({ticker_symbol})")
    st.text(f"📅 日付: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 現在価格", f"${current_price:.2f}")
    col2.metric("📈 RSI(14)", f"{current_rsi:.2f}")
    col3.metric("🌱 ESGスコア", f"{esg_score}")
    col4.metric("🏢 予想PER", f"{forward_pe}")
    
    st.subheader("📰 最新ニュース (ヘッドライン)")
    if news:
        for i, item in enumerate(news):
            st.markdown(f"- [{item.get('title', 'No Title')}]({item.get('link', '#')})")
    else:
        st.info("ニュースが見つかりませんでした。")

    st.subheader(f"🤖 投資判断: 【 {decision} 】")
    st.write("📝 **理由:**")
    for r in reason:
        st.write(f"- {r}")
    
    if position_advice:
        st.subheader("🤔 ポジション分析 & アドバイス")
        st.write(f"**設定:** {status} @ ${entry_price:.2f}")
        for advice in position_advice:
            st.write(f"- {advice}")

    # 提案4: 詳細情報をExpander内に表示
    with st.expander("詳細情報を表示..."):
        col1_detail, col2_detail = st.columns(2)
        with col1_detail:
            st.write("**企業情報**")
            st.text(f"セクター: {info.get('sector', 'N/A')}")
            st.text(f"業種: {info.get('industry', 'N/A')}")
            st.text(f"ウェブサイト: {info.get('website', 'N/A')}")
        with col2_detail:
            st.write("**市場データ**")
            st.text(f"時価総額: {info.get('marketCap', 'N/A'):,}")
            st.text(f"52週高値: {info.get('fiftyTwoWeekHigh', 'N/A')}")
            st.text(f"52週安値: {info.get('fiftyTwoWeekLow', 'N/A')}")
            st.text(f"配当利回り: {info.get('dividendYield', 0) * 100:.2f}%")

    # チャート表示
    st.subheader("📉 株価チャート (6ヶ月)")
    st.line_chart(hist['Close'])

def _get_position_advice(status, entry_price, current_price, current_rsi):
    """提案3: ポジション状況に応じたアドバイスを生成するヘルパー関数"""
    position_advice = []
    if entry_price <= 0:
        return position_advice

    if status == "保有中 (エントリー済み)":
        diff = current_price - entry_price
        pct_change = (diff / entry_price) * 100
        
        if diff >= 0:
            position_advice.append(f"💰 **含み益:** +${diff:.2f} (+{pct_change:.2f}%)")
            if current_rsi > RSI_OVERBOUGHT:
                position_advice.append(f"⚠️ RSIが高値圏({RSI_OVERBOUGHT}超)です。利益確定を検討しても良いタイミングかもしれません。")
            else:
                position_advice.append("✅ 利益が出ています。トレンド継続を期待しつつ、RSIの過熱感に注意しましょう。")
        else:
            position_advice.append(f"💸 **含み損:** ${diff:.2f} ({pct_change:.2f}%)")
            if current_rsi < RSI_OVERSOLD:
                position_advice.append(f"ℹ️ RSIが底値圏({RSI_OVERSOLD}未満)です。反発を待つか、ナンピン買いの検討余地があるかもしれません。")
            else:
                position_advice.append("⚠️ 損失が出ています。損切りラインに達していないか確認してください。")
    
    elif status == "検討中 (これからエントリー)":
        if current_price > entry_price:
            diff = current_price - entry_price
            pct_diff = (diff / entry_price) * 100 # 分母を希望価格に変更し、より直感的に
            position_advice.append(f"📉 現在価格は希望額より **${diff:.2f} ({pct_diff:.2f}%) 高い**です。")
            position_advice.append("⏳ 希望価格まで落ちてくるのを待つ「押し目待ち」の状態です。")
        else:
            position_advice.append("✅ 現在価格は希望額以下です。エントリーの好機かもしれません。")
    
    return position_advice

if __name__ == "__main__":
    st.title("📈 米国株 AI アナライザー")
    st.write("分析したい米国株のティッカーシンボルを入力してください (例: NVDA, AAPL, MSFT)")
    
    col1, col2 = st.columns(2)
    with col1:
        ticker = st.text_input("ティッカーシンボル", "").strip().upper()
    with col2:
        entry_price = st.number_input("エントリー価格 (USD) ※0なら無視", min_value=0.0, value=0.0, step=0.1, format="%.2f")
    
    status = st.radio("現在のステータス", ("保有中 (エントリー済み)", "検討中 (これからエントリー)"), horizontal=True)
    
    if st.button("分析開始") and ticker:
        analyze_stock(ticker, entry_price, status)
