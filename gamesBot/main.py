from dotenv import load_dotenv
from os import getenv
import telegram
import telegram.ext
from draft import start_draft_game_command_handler,  new_draft_game_command_handler, join_draft_game_command_handler, set_draft_game_state_command_handler, cancel_draft_game_command_handler, vote_recive_poll_answer_handler, position_draft_message_handler, join_draft_game_callback_handler, random_team_draft_game_callback_handler
from guess_the_player import guess_the_player_start_game_command_handler, guess_the_player_join_game_command_handler, guess_the_player_new_game_command_handler,guess_the_player_ask_question_command_handler, guess_the_player_answer_question_command_handler, guess_the_player_proccess_answer_command_handler, guess_the_player_cancel_game_command_handler, guess_the_player_join_game_callback_handler, guess_the_player_start_round_command_handler

load_dotenv()

BOT_API_TOKEN = getenv("BOT_API_TOKEN")


async def handle_start(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.message or context == None:
        return

    await update.message.reply_text("")



def main():
    if not BOT_API_TOKEN:
        return

    application = telegram.ext.Application.builder().token(BOT_API_TOKEN).build()
    application.add_handler(guess_the_player_new_game_command_handler)
    application.add_handler(guess_the_player_join_game_command_handler)
    application.add_handler(guess_the_player_join_game_callback_handler)
    application.add_handler(guess_the_player_start_game_command_handler)
    application.add_handler(guess_the_player_ask_question_command_handler)
    application.add_handler(guess_the_player_answer_question_command_handler)
    application.add_handler(guess_the_player_proccess_answer_command_handler)
    application.add_handler(guess_the_player_cancel_game_command_handler)
    application.add_handler(guess_the_player_start_round_command_handler)

    application.run_polling(allowed_updates=telegram.Update.ALL_TYPES)

if __name__ == "__main__":
    main()
