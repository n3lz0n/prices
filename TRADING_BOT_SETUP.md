# 🤖 XRP/USDT Trading Bot Setup Guide

## 📋 Overview

This is a **Stochastic RSI-based trading bot** that:
- ✅ Trades XRP/USDT on **Binance Testnet** (paper trading)
- ✅ Checks price every **4 hours** via GitHub Actions
- ✅ Buys when oversold (Stochastic RSI < 20)
- ✅ Sells at **5% profit** or when overbought (Stochastic RSI > 80)
- ✅ Trades **$5 per trade** (configurable)
- ✅ Sends **Telegram notifications** for every trade
- ✅ Logs all trades in `trade_log.json`

---

## 🔑 Step 1: Get Binance Testnet API Keys

1. Visit: **https://testnet.binance.vision/**
2. Sign up or login
3. Go to **API Management**
4. Create new API key (enable trading permissions)
5. Save your:
   - **API Key** (copy this)
   - **Secret Key** (copy this)

⚠️ **NEVER share these publicly!**

---

## 📱 Step 2: Create Telegram Bot

### Get Bot Token:
1. Open Telegram and search for **`@BotFather`**
2. Type `/newbot`
3. Follow the prompts to create your bot
4. Copy your **Bot Token** (looks like: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)

### Get Chat ID:
1. Send any message to your new bot
2. Visit this URL in your browser:
   ```
   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
   ```
   Replace `<YOUR_BOT_TOKEN>` with your token
3. Find `"chat":{"id":YOUR_CHAT_ID`
4. Copy your **Chat ID** (looks like: `123456789`)

---

## 🔐 Step 3: Add GitHub Secrets

Your repo needs 4 encrypted secrets to run safely.

### How to add them:

1. Go to your GitHub repo
2. Click **Settings** (top menu)
3. Click **Secrets and variables** → **Actions**
4. Click **New repository secret**
5. Add these 4 secrets one by one:

| Secret Name | Value | Example |
|-------------|-------|---------|
| `BINANCE_API_KEY` | Your Binance Testnet API Key | `ruofqCKyan944pPPsLWWIp7NnCj01jxb5tRonKxIHK9DobsZ4xX6Lk5ZHDsvWtDO` |
| `BINANCE_API_SECRET` | Your Binance Testnet Secret Key | `tyydz4cjrEeJco4XSpdmGr73319YKW0QRLBNag1LjP0BblwP3sBBTt0NDtUu9Q7a` |
| `TELEGRAM_TOKEN` | Your Telegram Bot Token | `8797949871:AAGGZ_GL8M60BLg0fJTNbooPobkNHQIHiiI` |
| `TELEGRAM_CHAT_ID` | Your Telegram Chat ID | `123456789` |

⚠️ **IMPORTANT**: These are encrypted and never exposed in logs!

---

## 🧪 Step 4: Test the Bot

### Manual Test:

1. Go to your repo → **Actions** tab
2. Click **XRP Trading Bot** workflow
3. Click **Run workflow** → **Run workflow**
4. Watch it execute!
5. Check your **Telegram** for notifications

### Automatic Execution:

The bot runs automatically **every 4 hours**:
- 00:00 UTC
- 04:00 UTC
- 08:00 UTC
- 12:00 UTC
- 16:00 UTC
- 20:00 UTC

---

## 📊 Configuration (Optional)

Edit `trading_bot.py` to customize:

```python
SYMBOL = 'XRPUSDT'              # Trading pair
TRADE_AMOUNT = 5                # $5 per trade
TAKE_PROFIT_PERCENT = 5         # 5% target profit
STOCH_PERIOD = 14               # RSI period
STOCH_K_SMOOTH = 3              # K-line smoothing
STOCH_D_SMOOTH = 3              # D-line smoothing
```

---

## 📈 How the Strategy Works

### **Buy Signal**: Stochastic RSI < 20 (Oversold)
- Bot buys $5 worth of XRP
- Sends Telegram notification 🟢

### **Sell Signal**: 
- **When price rises 5%**: Automatic sell at target profit ✅
- **When Stochastic RSI > 80** (Overbought): Sell signal
- Sends Telegram notification 🔴

### **Hold**: Between signals, bot does nothing ⏳

---

## 📋 Trade Log

All trades are saved in **`trade_log.json`**:

```json
[
  {
    "timestamp": "2026-05-25T10:30:00",
    "action": "BUY",
    "symbol": "XRPUSDT",
    "quantity": 2.5,
    "price": 2.00,
    "amount_usdt": 5,
    "status": "OPEN"
  },
  {
    "timestamp": "2026-05-25T14:45:00",
    "action": "SELL",
    "symbol": "XRPUSDT",
    "quantity": 2.5,
    "sell_price": 2.10,
    "buy_price": 2.00,
    "profit": 0.25,
    "profit_percent": 5.0,
    "status": "CLOSED"
  }
]
```

---

## 🚀 Going Live (When Ready)

To trade with **real money** on Binance Testnet→Main:

1. Generate **real Binance API keys** (not testnet)
2. Update GitHub Secrets with real keys
3. Change bot to real exchange
4. Start small! ($5 trades = LOW RISK)

---

## ⚠️ Important Notes

- **Paper Trading**: Uses Binance Testnet (no real money)
- **GitHub Actions**: Free tier = 2000 minutes/month (plenty!)
- **Security**: All API keys encrypted via GitHub Secrets
- **Timezone**: Runs on UTC schedule
- **Logs**: Check Actions tab to see bot output

---

## 🆘 Troubleshooting

### Bot not running?
- Check Actions tab for errors
- Verify all 4 GitHub Secrets are set
- Make sure `trading_bot.yml` is in `.github/workflows/`

### No Telegram messages?
- Verify `TELEGRAM_TOKEN` and `TELEGRAM_CHAT_ID`
- Send a test message to your bot first

### API errors?
- Check Binance Testnet is accessible
- Verify API key has trading permissions
- Ensure testnet has some USDT balance

---

## 📞 Support

For issues:
1. Check GitHub Actions logs
2. Review `trade_log.json` for trade history
3. Verify all GitHub Secrets are correct
4. Test with manual workflow run first

---

**Happy Trading! 🚀📊**

Remember: This is a **bot**, not financial advice. Trade responsibly! 💡
