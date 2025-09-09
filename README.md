# Telegram Moderator Bot

Simple moderation bot for Telegram groups:
- `/report` → forward a message or username to the admin
- `/votetoban` → users can vote to ban someone

## Deploy on Render
1. Fork or upload this repo to your GitHub.
2. Go to [Render](https://render.com).
3. Create a **Web Service**:
   - Environment: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python bot.py`
4. Add Environment Variable:
   - Key: `BOT_TOKEN`
   - Value: your bot token from BotFather
5. Replace `ADMIN_ID` in `bot.py` with your Telegram ID.
6. Deploy 🚀
