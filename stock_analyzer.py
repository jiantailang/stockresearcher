import yfinance as yf
import pandas as pd
import streamlit as st
from datetime import datetime

def calculate_rsi(series, period=14):
    """RSI（相対力指数）を計算する関数"""
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def analyze_stock(ticker_symbol):
    st.markdown(f"### 🔍 銘柄コード: {ticker_symbol} の調査を開始します...")
    
    # --- ステップ1: 調査 (Research) ---
    try:
        stock = yf.Ticker(ticker_symbol)
        
        # 直近6ヶ月のデータを取得
        hist = stock.history(period="6mo")
        
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
    hist['RSI'] = calculate_rsi(hist['Close'])
    current_rsi = hist['RSI'].iloc[-1]

    # B. ファンダメンタル・ESG指標
    esg_score = info.get('sustainabilityScore', "N/A") # ESGスコア
    forward_pe = info.get('forwardPE', "N/A")          # 予想PER
    short_name = info.get('shortName', ticker_symbol)

    # --- ステップ3: 判断 (Decision) ---
    decision = "HOLD (様子見)"
    reason = []

    if current_rsi < 30:
        decision = "BUY (買い検討)"
        reason.append(f"RSIが {current_rsi:.2f} で、売られすぎ水準(30以下)です。反発の可能性があります。")
    elif current_rsi > 70:
        decision = "SELL (売り検討)"
        reason.append(f"RSIが {current_rsi:.2f} で、買われすぎ水準(70以上)です。過熱感があります。")
    else:
        reason.append(f"RSIは {current_rsi:.2f} で、中立的な水準です。")

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
    
    # チャート表示
    st.subheader("📉 株価チャート (6ヶ月)")
    st.line_chart(hist['Close'])

if __name__ == "__main__":
    st.title("📈 米国株 AI アナライザー")
    st.write("分析したい米国株のティッカーシンボルを入力してください (例: NVDA, AAPL, MSFT)")
    
    ticker = st.text_input("ティッカーシンボル", "").strip().upper()
    
    if st.button("分析開始") and ticker:
        analyze_stock(ticker)
