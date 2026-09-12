#!/usr/bin/env python3
"""
XRP/USDT Trading Bot Backtester
Simulates 3 years of trading using Stochastic RSI strategy
"""

import json
from datetime import datetime, timedelta
import statistics

try:
    import yfinance as yf
    import pandas as pd
    import numpy as np
except ImportError:
    print("Installing required packages...")
    import subprocess
    subprocess.check_call(['pip', 'install', 'yfinance', 'pandas', 'numpy'])
    import yfinance as yf
    import pandas as pd
    import numpy as np


def calculate_stochastic_rsi(prices, period=14, k_smooth=3, d_smooth=3):
    """
    Calculate Stochastic RSI indicator
    
    Returns:
        stoch_k: %K line
        stoch_d: %D line (SMA of %K)
    """
    # Calculate RSI
    deltas = np.diff(prices)
    seed = deltas[:period+1]
    up = seed[seed >= 0].sum() / period
    down = -seed[seed < 0].sum() / period
    rs = up / down if down != 0 else 0
    rsi = np.zeros_like(prices, dtype=float)
    rsi[:period] = 100.0 - 100.0 / (1.0 + rs)
    
    for i in range(period, len(prices)):
        delta = deltas[i-1]
        if delta > 0:
            upval = delta
            downval = 0.0
        else:
            upval = 0.0
            downval = -delta
        
        up = (up * (period - 1) + upval) / period
        down = (down * (period - 1) + downval) / period
        rs = up / down if down != 0 else 0
        rsi[i] = 100.0 - 100.0 / (1.0 + rs)
    
    # Calculate Stochastic RSI
    rsi_min = pd.Series(rsi).rolling(window=period).min().values
    rsi_max = pd.Series(rsi).rolling(window=period).max().values
    
    stoch = np.zeros_like(rsi)
    for i in range(period, len(rsi)):
        if rsi_max[i] - rsi_min[i] != 0:
            stoch[i] = ((rsi[i] - rsi_min[i]) / (rsi_max[i] - rsi_min[i])) * 100
        else:
            stoch[i] = 50
    
    # Smooth with K
    stoch_k = pd.Series(stoch).rolling(window=k_smooth).mean().values
    stoch_d = pd.Series(stoch_k).rolling(window=d_smooth).mean().values
    
    return stoch_k, stoch_d


def backtest_trading_bot(symbol="XRP-USD", years=3, trade_amount=5, take_profit_percent=5):
    """
    Run backtesting simulation for trading bot
    """
    print(f"\n{'='*80}")
    print(f"🤖 XRP/USDT Trading Bot Backtester")
    print(f"{'='*80}")
    print(f"Symbol: {symbol}")
    print(f"Timeframe: 4 hours")
    print(f"Indicator: Stochastic RSI (Period=14, K=3, D=3)")
    print(f"Duration: {years} years")
    print(f"Trade Amount: ${trade_amount} per trade")
    print(f"Take Profit Target: {take_profit_percent}%")
    print(f"{'='*80}\n")
    
    # Download historical data
    print("📥 Downloading 3 years of historical data...")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365*years)
    
    try:
        df = yf.download(symbol, start=start_date, end=end_date, interval="4h", progress=False)
    except Exception as e:
        print(f"❌ Error downloading data: {e}")
        print("Note: Make sure you have internet connection and yfinance installed")
        return None
    
    print(f"✅ Downloaded {len(df)} candles ({len(df)*4/24:.1f} days of 4-hour data)\n")
    
    # Calculate Stochastic RSI
    print("📊 Calculating Stochastic RSI...")
    prices = df['Close'].values
    stoch_k, stoch_d = calculate_stochastic_rsi(prices, period=14, k_smooth=3, d_smooth=3)
    
    df['StochK'] = stoch_k
    df['StochD'] = stoch_d
    df['Price'] = prices
    
    # Simulate trading
    print("🎯 Running simulation...\n")
    
    trades = []
    open_position = None
    starting_capital = 1000
    capital = starting_capital
    total_profit = 0
    
    for i in range(14, len(df)):  # Start after Stochastic RSI can be calculated
        current_price = df['Price'].iloc[i]
        stoch_k_current = df['StochK'].iloc[i]
        date = df.index[i]
        
        # BUY SIGNAL: Stochastic RSI < 20 (Oversold)
        if open_position is None and stoch_k_current < 20:
            quantity = trade_amount / current_price
            open_position = {
                'entry_date': date,
                'entry_price': current_price,
                'quantity': quantity,
                'stoch_entry': stoch_k_current
            }
            print(f"🟢 BUY  | {date.strftime('%Y-%m-%d %H:%M')} | Price: ${current_price:.4f} | Stoch K: {stoch_k_current:.2f} | Qty: {quantity:.2f}")
        
        # SELL SIGNAL: Take profit (5%) OR Stochastic RSI > 80 (Overbought)
        elif open_position is not None:
            profit_percent = ((current_price - open_position['entry_price']) / open_position['entry_price']) * 100
            
            sell_reason = None
            if profit_percent >= take_profit_percent:
                sell_reason = f"Take Profit ({profit_percent:.2f}%)"
            elif stoch_k_current > 80:
                sell_reason = f"Overbought (Stoch K: {stoch_k_current:.2f})"
            
            if sell_reason:
                profit_usdt = (current_price - open_position['entry_price']) * open_position['quantity']
                total_profit += profit_usdt
                capital += profit_usdt
                
                trade_log = {
                    'entry_date': open_position['entry_date'],
                    'exit_date': date,
                    'entry_price': open_position['entry_price'],
                    'exit_price': current_price,
                    'quantity': open_position['quantity'],
                    'profit_usdt': profit_usdt,
                    'profit_percent': profit_percent,
                    'reason': sell_reason,
                    'duration_hours': (date - open_position['entry_date']).total_seconds() / 3600
                }
                trades.append(trade_log)
                
                print(f"🔴 SELL | {date.strftime('%Y-%m-%d %H:%M')} | Price: ${current_price:.4f} | Stoch K: {stoch_k_current:.2f} | Profit: ${profit_usdt:.2f} (+{profit_percent:.2f}%) | Reason: {sell_reason}")
                open_position = None
    
    # Close any open position at end
    if open_position is not None:
        current_price = df['Price'].iloc[-1]
        profit_percent = ((current_price - open_position['entry_price']) / open_position['entry_price']) * 100
        profit_usdt = (current_price - open_position['entry_price']) * open_position['quantity']
        total_profit += profit_usdt
        capital += profit_usdt
        
        trade_log = {
            'entry_date': open_position['entry_date'],
            'exit_date': df.index[-1],
            'entry_price': open_position['entry_price'],
            'exit_price': current_price,
            'quantity': open_position['quantity'],
            'profit_usdt': profit_usdt,
            'profit_percent': profit_percent,
            'reason': 'End of backtest',
            'duration_hours': (df.index[-1] - open_position['entry_date']).total_seconds() / 3600
        }
        trades.append(trade_log)
        print(f"🔴 CLOSE| {df.index[-1].strftime('%Y-%m-%d %H:%M')} | Price: ${current_price:.4f} | Profit: ${profit_usdt:.2f} (+{profit_percent:.2f}%)")
    
    # Calculate statistics
    print(f"\n{'='*80}")
    print(f"📈 BACKTEST RESULTS")
    print(f"{'='*80}\n")
    
    win_trades = [t for t in trades if t['profit_usdt'] > 0]
    loss_trades = [t for t in trades if t['profit_usdt'] < 0]
    
    print(f"💰 Starting Capital:      ${starting_capital:.2f}")
    print(f"💰 Final Capital:         ${capital:.2f}")
    print(f"📊 Total Profit/Loss:     ${total_profit:.2f}")
    print(f"📈 ROI:                   {(total_profit/starting_capital)*100:.2f}%")
    print(f"\n")
    print(f"📋 Total Trades:          {len(trades)}")
    print(f"✅ Winning Trades:        {len(win_trades)} ({(len(win_trades)/len(trades)*100 if trades else 0):.1f}%)")
    print(f"❌ Losing Trades:         {len(loss_trades)} ({(len(loss_trades)/len(trades)*100 if trades else 0):.1f}%)")
    
    if trades:
        profits = [t['profit_usdt'] for t in trades]
        avg_profit = statistics.mean(profits)
        print(f"\n")
        print(f"📊 Average Profit/Trade: ${avg_profit:.2f}")
        print(f"🔝 Best Trade:           ${max(profits):.2f} ({max([t['profit_percent'] for t in trades]):.2f}%)")
        print(f"🔻 Worst Trade:          ${min(profits):.2f} ({min([t['profit_percent'] for t in trades]):.2f}%)")
        
        durations = [t['duration_hours'] for t in trades]
        avg_duration = statistics.mean(durations)
        print(f"⏱️  Avg Trade Duration:   {avg_duration:.1f} hours")
        
        if win_trades:
            win_profits = [t['profit_usdt'] for t in win_trades]
            print(f"💚 Avg Win:              ${statistics.mean(win_profits):.2f}")
        if loss_trades:
            loss_profits = [t['profit_usdt'] for t in loss_trades]
            print(f"💔 Avg Loss:             ${statistics.mean(loss_profits):.2f}")
    
    print(f"\n{'='*80}\n")
    
    return {
        'trades': trades,
        'starting_capital': starting_capital,
        'final_capital': capital,
        'total_profit': total_profit,
        'roi_percent': (total_profit/starting_capital)*100 if starting_capital > 0 else 0,
        'win_rate': (len(win_trades)/len(trades)*100) if trades else 0,
        'data': df
    }


if __name__ == "__main__":
    results = backtest_trading_bot(symbol="XRP-USD", years=3, trade_amount=5, take_profit_percent=5)
    
    if results:
        # Save detailed results to JSON
        trades_json = []
        for trade in results['trades']:
            trades_json.append({
                'entry_date': trade['entry_date'].isoformat(),
                'exit_date': trade['exit_date'].isoformat(),
                'entry_price': float(trade['entry_price']),
                'exit_price': float(trade['exit_price']),
                'quantity': float(trade['quantity']),
                'profit_usdt': float(trade['profit_usdt']),
                'profit_percent': float(trade['profit_percent']),
                'reason': trade['reason'],
                'duration_hours': float(trade['duration_hours'])
            })
        
        backtest_results = {
            'backtest_date': datetime.now().isoformat(),
            'symbol': 'XRP-USD',
            'timeframe': '4 hours',
            'indicator': 'Stochastic RSI (14, 3, 3)',
            'duration': '3 years',
            'trade_amount': 5,
            'take_profit_percent': 5,
            'starting_capital': results['starting_capital'],
            'final_capital': float(results['final_capital']),
            'total_profit': float(results['total_profit']),
            'roi_percent': float(results['roi_percent']),
            'total_trades': len(results['trades']),
            'win_rate_percent': float(results['win_rate']),
            'trades': trades_json
        }
        
        with open('backtest_results.json', 'w') as f:
            json.dump(backtest_results, f, indent=2)
        
        print("✅ Backtest results saved to backtest_results.json")
