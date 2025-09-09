import os
import threading
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# -----------------------
# CONFIG
# -----------------------
ADMIN_ID = 5734988616  # Your Telegram user ID
BOT_TOKEN = os.environ.get("BOT_TOKEN")  # Must be set in Render Environment Variables
VOTE_THRESHOLD = 3  # Votes needed to ban

# Track votes
votes = {}

# -----------------------
# LOGGING
# -----------------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# -----------------------
# COMMAND HANDLERS
# -----------------------
async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Report command received from {update.message.from_user.id}")
    if update.message.reply_to_message:
        reported_user = update.message.reply_to_message.from_user
        await context.bot.forward_message(
            chat_id=ADMIN_ID,
            from_chat_id=update.message.chat_id,
            message_id=update.message.reply_to_message.message_id,
        )
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"⚠️ Reported user: @{reported_user.username or reported_user.id}"
        )
        await update.message.reply_text("Message reported to admin.")
    elif context.args:
        username = context.args[0]
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"⚠️ Reported username: {username}"
        )
        await update.message.reply_text("Username reported to admin.")
    else:
        await update.message.reply_text("Reply to a message or provide a username to report.")

async def votetoban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"VoteToBan command received from {update.message.from_user.id}")
    if not update.message.reply_to_message and not context.args:
        await update.message.reply_text("Reply to a message or type a username to vote to ban.")
        return

    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        target = target_user.id
        target_name = f"@{target_user.username}" if target_user.username else str(target_user.id)
    else:
        target = context.args[0]
        target_name = target

    user_id = update.message.from_user.id
    if target not in votes:
        votes[target] = set()
    votes[target].add(user_id)
    vote_count = len(votes[target])

    if vote_count >= VOTE_THRESHOLD:
        try:
            await context.bot.ban_chat_member(update.message.chat_id, target)
            await update.message.reply_text(f"{target_name} has been banned after {vote_count} votes.")
            votes.pop(target, None)
        except Exception as e:
            await update.message.reply_text(f"Failed to ban {target_name}: {e}")
    else:
        await update.message.reply_text(f"{target_name} has {vote_count}/{VOTE_THRESHOLD} votes to be banned.")

# -----------------------
# BOT SETUP
# -----------------------
def run_bot():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("report", report))
    app.add_handler(CommandHandler("votetoban", votetoban))
    logger.info("Bot started polling...")
    app.run_polling()

# -----------------------
# DUMMY HTTP SERVER
# -----------------------
class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    httpd = HTTPServer(("", port), DummyHandler)
    logger.info(f"Dummy HTTP server listening on port {port}")
    httpd.serve_forever()

# -----------------------
# MAIN
# -----------------------
if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    run_dummy_server()
