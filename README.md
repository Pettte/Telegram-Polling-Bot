# Polling Bot by Bot Studios

# Requirements

Before running the Telegram Polling Bot, make sure you have the following installed:

## Required Software

* Python 3.10 or newer
* pip (Python package manager)
* Git (optional)

## Required Python Packages

Install all required packages with:

```bash
pip install -r requirements.txt
```

If you do not have a `requirements.txt` file yet, install these manually:

```bash
pip install pyrogram tgcrypto requests asyncio
```

## Environment Variables

You must set the following environment variables before starting the bot:

```python
TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHANNEL_ID = os.environ["POLLING_CHANNEL_ID"]
```

Replace them with:

* Your Telegram Bot Token
* Your Telegram Channel ID

## How To Get A Telegram Bot Token

1. Open Telegram
2. Search for @BotFather
3. Create a new bot using `/newbot`
4. Copy the token you receive

## How To Get Your Channel ID

1. Add your bot to your Telegram channel
2. Make the bot an admin
3. Use a Channel ID finder bot or Telegram API to get the channel ID

## Start The Bot

Run the bot with:

```bash
python bot.py
```

## Notes

* This project is currently in BETA
* Bugs may occur
* Report issues to:
  https://t.me/botstudioss
