#!/usr/bin/python3

import logging
import json
import os

from shared_space import getinfo_by_bursa_stockcode

from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# TODO: 
# 1. help 
# 2. Ideas for interactive components for the Telegram Bot
#   2a. Do an ad-hoc check on a specific company
#   2b. Pull data for specific company
#   2c. Add/remove company cashtags to stockcodes.txt

def check_authorized(chatid):

    """ This function is unused, for now """
    str_chatid = str(chatid)

    # Read file which contains a list of authorized users
    authorized_ids = []
    
    with open('conf/authorized.lst') as readfile:
        authorized_ids = [line.rstrip() for line in readfile]
    
    if str_chatid in authorized_ids:
        return True
    else:
        return False


def get_authorized_list():
    # Reads file which contains a list of authorized users
    authorized_list = []
    
    with open('conf/authorized.lst') as readfile:
        authorized_list = [int(line.rstrip()) for line in readfile]

    return authorized_list


def get_admin_list():
    # Reads file which contains a list of authorized users with admin privileges
    adm_list = []
    
    with open('conf/admin.lst') as readfile:
        adm_list = [int(line.rstrip()) for line in readfile]

    return adm_list


# Message Handler which filters out unauthorized users
async def restrict_user (update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="User Unauthorized."
        )

# Message Handler which filters out non-admin users
async def restrict_admin (update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Admin privilege is required for this action."
        )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    """Send a message when the command /start is issued."""
    user = update.effective_user

    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")


async def check_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    """Helps user find out their Telegram IDs"""
    await update.message.reply_text(str(update.effective_chat.id))


async def get_tracked_stockcodes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    """Prints out content of stockcodes.txt"""
    with open("conf/stockcodes.txt", "r") as readfile:
        file_content = readfile.read()
    
    await update.message.reply_text(file_content)

    
async def get_tracked_stocks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    """Prints out content of stockcodes.txt plus names of stocks"""
    with open("conf/stockcodes.txt", "r") as readfile:
        stockcodes_list = readfile.readlines()
    
    msg_response = "List of Tracked Stocks: \n\n"
    
    for stockcode_raw in stockcodes_list:
        stockname = "Nil"
        stockcode = stockcode_raw[:-1]
        
        if os.path.exists(f"data/{stockcode}.json"):
            # Get stock name from existing json data file
            with open(f"data/{stockcode}.json", "r") as readjson:
                json_data = json.load(readjson)
            
            stockname = json_data.get("name", "StockNameNotFound")
        else:
            # If stock name not found, call API to get stock name
            r1 = getinfo_by_bursa_stockcode(stockcode)
            stockname = r1.json().get("name", "StockNameNotFoundOnline")
            
        msg_response += f"{stockcode}: {str(stockname)}\n"
    
    await update.message.reply_text(msg_response)


async def update_authorized(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    try:
        """Updates the list of authorized users"""
        current_list = chatid_filter.chat_ids
        chatid_filter.remove_chat_ids(current_list)

        chatid_filter.add_chat_ids(get_authorized_list())

        """Updates the list of authorized admins"""
        current_admin_list = admin_chatid_filter.chat_ids
        admin_chatid_filter.remove_chat_ids(current_admin_list)

        admin_chatid_filter.add_chat_ids(get_admin_list())

        await update.message.reply_text("Updated List of Authorized IDs.")
    
    except Exception as e:
        await update.message.reply_text("An error occured: " + str(e))


async def add_authorized(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    """Adds a user's Chat ID to authorized.lst"""
    return_msg = "Adding User to Authorized Users List"
    original_msg = return_msg

    # Check if the argument supplied is an integer
    try:
        int_chatid = int(context.args[0])
    except:
        return_msg = 'Usage: /add_authorized <chat_id>'

    # Checks if user is already in the list
    with open('conf/authorized.lst') as readfile:
        for line in readfile:
            if line.strip() == str(context.args[0]):
                return_msg = "User is already authorized"

    # Proceeds to add user to authorized list if:
    #   1. Argument provided is valid (int)
    #   2. User does not exist in the list yet
    if return_msg == original_msg:
        with open('conf/authorized.lst', 'a') as writefile:
            writefile.write(str(context.args[0]) + "\n")

        chatid_filter.add_chat_ids(int(context.args[0]))

    await update.message.reply_text(return_msg)


async def remove_authorized(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    """Removes a user's Chat ID from authorized.lst"""
    return_msg = "Removing User from Authorized Users List"
    original_msg = return_msg

    # Check if the argument supplied is an integer
    try:
        int_chatid = int(context.args[0])
    except:
        return_msg = 'Usage: /remove_authorized <chat_id>'

    # Make sure that the user exists in the list in the first place
    # also, use this opportunity to extract list of users for later use 
    return_msg = "Error: User not found"
    user_list = []

    with open('conf/authorized.lst') as readfile:
        for line in readfile:
            user_list.append(line.strip())

            if line.strip() == str(context.args[0]):
                return_msg = original_msg

    # Proceeds to remove user from authorized list if:
    #   1. Argument provided is valid (int)
    #   2. User already exists in the list
    if return_msg == original_msg:
        user_list.remove(str(context.args[0]))

        # Add the list back to the file
        with open('conf/authorized.lst', 'w') as writefile:
            for user_id in user_list:
                writefile.write(str(user_id) + "\n")
        
        # Remove user from existing filter (white)list
        chatid_filter.remove_chat_ids(int(context.args[0]))

    await update.message.reply_text(return_msg)


#async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#
#    """Echo the user message."""
#    await update.message.reply_text(update.message.text)


def main() -> None:

    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(telg_token).build()
    
    # Users are able to check their ID regardless authorized or not
    application.add_handler(CommandHandler("check_id", check_id))

    """Applies restrictions to Chat IDs that are not found in authorized.lst"""
    restrict_user_handler = MessageHandler(~chatid_filter, restrict_user)
    application.add_handler(restrict_user_handler)

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("get_tracked_stockcodes", get_tracked_stockcodes))
    application.add_handler(CommandHandler("get_tracked_stocks", get_tracked_stocks))
    
    """Another restriction handler to restrict Chat IDs which are not admins"""
    restrict_admin_handler = MessageHandler(~admin_chatid_filter, restrict_admin)
    application.add_handler(restrict_admin_handler)

    application.add_handler(CommandHandler("update_authorized", update_authorized))
    application.add_handler(CommandHandler("add_authorized", add_authorized))
    application.add_handler(CommandHandler("remove_authorized", remove_authorized))

    # on non command i.e message - echo the message on Telegram
    #application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    # Enable logging
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
        level=logging.INFO,
        filename='receptionist.log'
    )

    # set higher logging level for httpx to avoid all GET and POST requests being logged
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logger = logging.getLogger(__name__)

    # Initialize the chat ID filter objects
    chatid_filter = filters.Chat(get_authorized_list())
    admin_chatid_filter = filters.Chat(get_admin_list())

    # Get the token for Telegram Bot
    with open('conf/telg_token', 'r') as token_file:
        telg_token = token_file.read()
        telg_token = telg_token[:-1]

    main()
