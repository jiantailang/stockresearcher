import yfinance as yf
import pandas as pd
import sys
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
    print(f"\n{'='*50}")
    print(f"🔍 銘柄コード: {ticker_symbol} の調査を開始します...")
    print(f"{'='*50}")
    
    # --- ステップ1: 調査 (Research) ---
    try:
        stock = yf.Ticker(ticker_symbol)
        
        # 直近6ヶ月のデータを取得
        hist = stock.history(period="6mo")
        
        if hist.empty:
            print(f"❌ エラー: データが見つかりませんでした。銘柄コード '{ticker_symbol}' を確認してください。")
            return

        # 企業情報の取得
        info = stock.info
        current_price = hist['Close'].iloc[-1]
        
        # ニュースの取得（最新3件）
        news = stock.news[:3] if stock.news else []

    except Exception as e:
        print(f"❌ データ取得中にエラーが発生しました: {e}")
        return

    # --- ステップ2: 分析 (Analysis) ---
    print("📊 データを分析中...")

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
    print(f"\n{'='*50}")
    print(f"📢 分析結果レポート: {short_name} ({ticker_symbol})")
    print(f"📅 日付: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'-'*50}")
    
    print(f"💰 現在価格: ${current_price:.2f}")
    print(f"📈 RSI(14): {current_rsi:.2f}")
    print(f"🌱 ESGスコア: {esg_score}")
    print(f"🏢 予想PER: {forward_pe}")
    
    print(f"\n📰 最新ニュース (ヘッドライン):")
    if news:
        for i, item in enumerate(news):
            print(f"  {i+1}. {item.get('title', 'No Title')}")
    else:
        print("  ニュースが見つかりませんでした。")

    print(f"\n🤖 投資判断: 【 {decision} 】")
    print("📝 理由:")
    for r in reason:
        print(f"  - {r}")
    print(f"{'='*50}\n")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        ticker = sys.argv[1]
    else:
        print("分析したい米国株のティッカーシンボルを入力してください (例: NVDA, AAPL, MSFT)")
        ticker = input(">> ").strip().upper()
    
    if ticker:
        analyze_stock(ticker)
    else:
        print("銘柄コードが入力されませんでした。")