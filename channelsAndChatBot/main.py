from typing import Optional
import telegram
import telegram.ext
from os import getenv
from dotenv import load_dotenv
from telegram.ext._handlers.chatmemberhandler import ChatMemberHandler
from telegram.ext._handlers.commandhandler import CommandHandler
from telegram.ext._handlers.messagehandler import MessageHandler

load_dotenv()

BOT_API_TOKEN = getenv("BOT_API_TOKEN")

def extract_status_member(chat_member_update: telegram.ChatMemberUpdated) -> Optional[tuple[bool, bool]]:
    statue_change = chat_member_update.difference().get("status")
    old_is_member, new_is_member = chat_member_update.difference().get("is_member", (None, None))

    if statue_change is None:
        return None

    old_status, new_status = statue_change

    was_member = old_status in [
        telegram.ChatMember.MEMBER,
        telegram.ChatMember.ADMINISTRATOR,
        telegram.ChatMember.OWNER
    ] or (old_status == telegram.ChatMember.RESTRICTED and old_is_member is True)

    is_member = new_status in [
        telegram.ChatMember.MEMBER,
        telegram.ChatMember.ADMINISTRATOR,
        telegram.ChatMember.OWNER
    ] or (new_status == telegram.ChatMember.RESTRICTED and new_is_member is True)


    return was_member, is_member

async def track_chat_members(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat or not update.effective_user or not update.my_chat_member:
        return

    status_change = extract_status_member(update.my_chat_member)

    if status_change is None:
        return

    chat = update.effective_chat
    user_id = update.effective_user.id
    username = update.effective_user.full_name
    was_member, is_member = status_change

    if chat.type == telegram.Chat.PRIVATE:
        if not was_member and is_member:
            print(f"user {username} unblocked bot")
            context.bot_data.setdefault("users_ids", set()).add(user_id)
        elif was_member and not is_member:
            print(f"user {username} blocked bot")
            context.bot_data.setdefault("users_ids", set()).discard(user_id)
    elif chat.type == telegram.Chat.GROUP or chat.type == telegram.Chat.SUPERGROUP:
        if not was_member and is_member:
            print(f"{username} added bot to group {chat.title}")
            context.bot_data.setdefault("groups_ids", set()).add(chat.id)
        elif was_member and not is_member:
            print(f"{username} removed bot from group {chat.title}")
            context.bot_data.setdefault("groups_ids", set()).discard(chat.id)
    elif not was_member and is_member:
            print(f"{username} added bot to channel {chat.title}")
            context.bot_data.setdefault("channels_ids", set()).add(chat.id)
    elif was_member and not is_member:
            print(f"{username} removed bot from channel {chat.title}")
            context.bot_data.setdefault("channels_ids", set()).discard(chat.id)

async def show_chats(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    users = ", ".join(str(id) for id in context.bot_data.setdefault("users_ids", set()))
    groups = ", ".join(str(id) for id in context.bot_data.setdefault("groups_ids", set()))
    channles = ", ".join(str(id) for id in context.bot_data.setdefault("channels_ids", set()))

    text = (
        f"@{context.bot.username} is talking with users f{users}"
        f"and is in groups {groups}"
        f"and is added to channels {channles}"
    )

    await update.message.reply_text(text=text)

async def great_users(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.chat_member or not update.effective_chat:
        return

    results = extract_status_member(update.chat_member)

    if results is None or update.effective_chat.type == telegram.Chat.PRIVATE:
        return

    admin = update.chat_member.from_user.mention_html()
    user = update.chat_member.new_chat_member.user.mention_html()
    was_member, is_member = results

    if not was_member and is_member:
        await update.effective_chat.send_message(
            f"{admin} added user {user}",
            parse_mode=telegram.constants.ParseMode.HTML
        )
    if was_member and not is_member:
        await update.effective_chat.send_message(
            f"{admin} removed user {user}",
            parse_mode=telegram.constants.ParseMode.HTML
        )

async def private_chat(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.effective_message or not update.effective_user or not update.effective_chat or update.effective_chat.type != telegram.Chat.PRIVATE:
        return

    user_name = update.effective_user.full_name
    chat = update.effective_chat

    context.bot_data.setdefault("users_ids", set()).add(chat.id)

    await update.effective_message.reply_text(
        f"Welcome {user_name}. Use /show_chats to see what chats I'm in."
    )



def main():
    if not BOT_API_TOKEN:
        return

    application = telegram.ext.Application.builder().token(BOT_API_TOKEN).build()

    application.add_handler(ChatMemberHandler(track_chat_members, ChatMemberHandler.MY_CHAT_MEMBER))
    application.add_handler(CommandHandler("show_chats", show_chats))

    application.add_handler(ChatMemberHandler(great_users, ChatMemberHandler.CHAT_MEMBER))

    application.add_handler(MessageHandler(telegram.ext.filters.ALL, private_chat))

    application.run_polling()

if __name__ == "__main__":
    main()

