import os
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Poll
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHANNEL_ID = os.environ["POLLING_CHANNEL_ID"]

# Conversation states
CHOOSING, MK_OPT1, MK_OPT2, ALIAS_NAME, DUO_TEAM1, DUO_TEAM2 = range(6)

POLL_MENU = InlineKeyboardMarkup([
    [InlineKeyboardButton("MK", callback_data="mk")],
    [InlineKeyboardButton("Alias Claim", callback_data="alias")],
    [InlineKeyboardButton("Duo Poll", callback_data="duo")],
])


# ── /poll entry point ──────────────────────────────────────────────────────────

async def poll_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "What type of poll would you like to create?",
        reply_markup=POLL_MENU,
    )
    return CHOOSING


# ── Button handlers ────────────────────────────────────────────────────────────

async def mk_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("Enter Option 1 (alias name):")
    return MK_OPT1


async def alias_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("Which alias would you like to claim?")
    return ALIAS_NAME


async def duo_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        "Enter Poll Option 1 aliases (e.g. Stabbing x Social):"
    )
    return DUO_TEAM1


# ── MK flow ───────────────────────────────────────────────────────────────────

async def mk_opt1(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["mk_opt1"] = update.message.text.strip()
    await update.message.reply_text("Enter Option 2 (alias name):")
    return MK_OPT2


async def mk_opt2(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    opt1 = context.user_data.pop("mk_opt1")
    opt2 = update.message.text.strip()
    try:
        await context.bot.send_poll(
            chat_id=CHANNEL_ID,
            question="MK",
            options=[opt1, opt2],
            is_anonymous=True,
            type=Poll.REGULAR,
        )
        await update.message.reply_text("Poll posted to the channel!")
    except Exception as e:
        logger.error("Failed to send MK poll: %s", e)
        await update.message.reply_text(
            "Failed to post the poll. Make sure the bot is an admin in the channel."
        )
    return ConversationHandler.END


# ── Alias Claim flow ──────────────────────────────────────────────────────────

async def alias_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    alias = update.message.text.strip()
    user = update.effective_user
    mention = f"@{user.username}" if user.username else user.first_name
    question = f'Is the Alias "{alias}" claimed? If not {mention} claims it'

    if len(question) > 300:
        await update.message.reply_text(
            "That alias is too long — please use a shorter one and try again."
        )
        return ALIAS_NAME

    try:
        await context.bot.send_poll(
            chat_id=CHANNEL_ID,
            question=question,
            options=["Yes, it is claimed", "No, it is available"],
            is_anonymous=True,
            type=Poll.REGULAR,
        )
        await update.message.reply_text("Alias claim poll posted to the channel!")
    except Exception as e:
        logger.error("Failed to send alias poll: %s", e)
        await update.message.reply_text(
            "Failed to post the poll. Make sure the bot is an admin in the channel."
        )
    return ConversationHandler.END


# ── Duo Poll flow ─────────────────────────────────────────────────────────────

async def duo_team1(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["duo_team1"] = update.message.text.strip()
    await update.message.reply_text(
        "Enter Poll Option 2 aliases (e.g. Player3 x Player4):"
    )
    return DUO_TEAM2


async def duo_team2(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    team1 = context.user_data.pop("duo_team1")
    team2 = update.message.text.strip()
    try:
        await context.bot.send_poll(
            chat_id=CHANNEL_ID,
            question="DUO POLL",
            options=[team1, team2],
            is_anonymous=True,
            type=Poll.REGULAR,
        )
        await update.message.reply_text("Duo poll posted to the channel!")
    except Exception as e:
        logger.error("Failed to send duo poll: %s", e)
        await update.message.reply_text(
            "Failed to post the poll. Make sure the bot is an admin in the channel."
        )
    return ConversationHandler.END


# ── Fallback ──────────────────────────────────────────────────────────────────

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text(
        "Cancelled. Send /poll to start again."
    )
    return ConversationHandler.END


# ── App setup ─────────────────────────────────────────────────────────────────

def main() -> None:
    app = Application.builder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("poll", poll_command)],
        states={
            CHOOSING: [
                CallbackQueryHandler(mk_chosen, pattern="^mk$"),
                CallbackQueryHandler(alias_chosen, pattern="^alias$"),
                CallbackQueryHandler(duo_chosen, pattern="^duo$"),
            ],
            MK_OPT1:    [MessageHandler(filters.TEXT & ~filters.COMMAND, mk_opt1)],
            MK_OPT2:    [MessageHandler(filters.TEXT & ~filters.COMMAND, mk_opt2)],
            ALIAS_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, alias_name)],
            DUO_TEAM1:  [MessageHandler(filters.TEXT & ~filters.COMMAND, duo_team1)],
            DUO_TEAM2:  [MessageHandler(filters.TEXT & ~filters.COMMAND, duo_team2)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_message=False,
    )

    app.add_handler(conv)
    logger.info("Bot starting...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
