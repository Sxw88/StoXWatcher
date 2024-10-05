#!/usr/bin/python3

import os
import json
import logging

from shared_space import update_json_data, getinfo_by_bursa_stockcode, check_discount_threshold

from logging.handlers import RotatingFileHandler
from telegram import ForceReply, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler, CallbackContext


# TODO: 
# X. help menu with fancy buttons
# 2. Ideas for interactive components for the Telegram Bot
#   Xa. Do an ad-hoc check on a specific company
#   2b. Pull data for specific company
#   xc. Add/remove company cashtags to stockcodes.txt
# X. Rotational logging


# Global variables for help menu
# These string variables hold the usage instructions
usage_check_id  = """Usage: /check_id
Returns the Telegram user ID / group ID.
The resultant ID can be added to authorized.lst via add_authorized to allow the user to access further commands."""

usage_get_tracked_stocks = """Usage: /get_tracked_stocks
Return list of currently tracked stocks. 
The list is used by other components of the Telegram bot to perform daily scheduled checks.
To get the raw contents of the list, use /get_tracked_stockcodes"""

usage_check_stock = """Usage: /check_stock <CASHTAG>
Returns basic information of the stock pulled from Bursa based on the provided cashtag.

Also checks the stock price against a threshold and determine whether it is a good time to buy in.

threshold = yrhigh - [(yrhigh - yrlow) * 0.7]"""

usage_modify_tracked_stocks = """Usage: /add_tracked_stocks <CASHTAG>
Adds a stock by its cashtag to the list of currently tracked stocks.

Usage: /remove_tracked_stocks <CASHTAG>
Removes a stock by its cashtag from the list of currently tracked stocks.

* A cashtag is a 4-letter identifier in the Bursa stock market"""

usage_modify_authorized_users = """Usage: /add_authorized <User ID or Group ID>
Adds a user / group to the list of authorized bot users.

Usage: /remove_authorized <User ID or Group ID>
Removes a user / group from the list of authorized bot users.

* Authorized users are able to use more functions, but certain functions are restricted to admin only.
* User ID / group ID can be retrieved using the /check_id command"""

usage_update_authorized_lst = """Usage: /update_authorized
Updates the list of authorized users and administrators to the currently running bot.
This is required when adding a new admin user for the changes to take effect. (Either that or restart the bot)"""


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
        rf"Hi {user.mention_html()}! Use /help to see available commands.",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    """Display a list of available commands."""
    keyboard = [
        [InlineKeyboardButton("Check your Telegram ID", callback_data='check_id')],
        [InlineKeyboardButton("Get a list of tracked stocks", callback_data='get_tracked_stocks')],
        [InlineKeyboardButton("Check a stock", callback_data='check_stock')],
        [InlineKeyboardButton("Add/remove tracked stocks by Bursa cashtags", callback_data='modify_tracked_stocks')],
        [InlineKeyboardButton("Add/remove authorized users", callback_data='modify_authorized_users')],
        [InlineKeyboardButton("Update authorized.lst", callback_data='update_authorized_lst')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Help Menu:', reply_markup=reply_markup)


# This function returns help messages
async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    
    command_responses = {
        'check_id'                  : usage_check_id,
        'get_tracked_stocks'        : usage_get_tracked_stocks,
        'check_stock'               : usage_check_stock, 
        'modify_tracked_stocks'     : usage_modify_tracked_stocks,
        'modify_authorized_users'   : usage_modify_authorized_users,
        'update_authorized_lst'     : usage_update_authorized_lst
    }

    if query.data in command_responses:
        await context.bot.send_message(chat_id=query.message.chat.id, text=command_responses[query.data])


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
        stockcode = stockcode_raw.replace("\n", "")
        
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


async def check_stock(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    """Checks the stock price against a threshold and determine whether it is a good time to buy in

    threshold = yrhigh - [(yrhigh - yrlow) * t]
    
    Higher value of t, lower the threshold - default t = 0.7 """
    
    return_msg = "Checking stock with cashtag $"
    original_msg = return_msg
    stockcode = "N.A."
    
    # Check if the argument supplied is an valid cashtag
    try:
        stockcode = str(context.args[0])
    
        # Perform the check via an API call to bursaonline
        r1 = getinfo_by_bursa_stockcode(stockcode)
        stockname = r1.json().get("name", "StockNameNotFoundOnline")
        
        if stockname == "StockNameNotFoundOnline":
            return_msg = 'Usage: /check_discount <cashtag>'
            
    except:
        return_msg = 'Usage: /check_discount <cashtag>'
    
    if return_msg == original_msg:
        return_msg += stockcode
        original_msg = return_msg
    
    await update.message.reply_text(return_msg)
    
    if return_msg == original_msg:
        r2 = getinfo_by_bursa_stockcode(stockcode)
        check_discount_threshold(r2.json(), t=0.7, return_desired_only=False)
    
        if os.path.exists(f"data/{stockcode}.json"):
            await update.message.reply_text(f"Updating {stockcode}.json")
            update_json_data(r2)


async def add_tracked_stocks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    """Adds cashtag to stockcodes.txt"""
    
    return_msg = "Adding tracked stock with cashtag $"
    original_msg = return_msg
    
    # Check if the argument supplied is an valid cashtag
    try:
        # Perform the check via an API call to bursaonline
        r1 = getinfo_by_bursa_stockcode(str(context.args[0]))
        stockname = r1.json().get("name", "StockNameNotFoundOnline")
        
        if stockname == "StockNameNotFoundOnline":
            return_msg = 'Usage: /add_tracked_stocks <cashtag>'
            
        # Also check if provided cashtag is already in the list
        with open('conf/stockcodes.txt', "r") as readfile:
            for line in readfile:
                if line.strip() == str(context.args[0]):
                    return_msg = f"Provided cashtag ${context.args[0]} already exists."
    except:
        return_msg = 'Usage: /add_tracked_stocks <cashtag>'
    
    if return_msg == original_msg:
        with open("conf/stockcodes.txt", "a") as apefile:
            apefile.write(str(context.args[0]))
            
        return_msg += str(context.args[0])
    
    await update.message.reply_text(return_msg)


async def remove_tracked_stocks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    """Remove a cashtag from stockcodes.txt"""
    
    return_msg = "Removing tracked stock with cashtag $"
    original_msg = return_msg
    cashtag_list = []
    
    # Check if the argument supplied is valid
    try:
        # Check if the provided cashtag already exists in stockcodes.txt
        return_msg = f"Stock with cashtag ${context.args[0]} does not exist.\n"
        return_msg += "Usage: /remove_tracked_stocks <cashtag>"
        
        # Logic here is to create a new list (cashtag_list) without the cashtag to be removed
        with open('conf/stockcodes.txt', "r") as readfile:
            for line in readfile:
                if line.strip() == str(context.args[0]):
                    return_msg = original_msg
                else:
                    cashtag_list.append(line.strip())
    except:
        return_msg = 'Usage: /remove_tracked_stocks <cashtag>'
    
    if return_msg == original_msg:
        # Overwrite stockcodes.txt with the new list (cashtag_list)
        with open("conf/stockcodes.txt", "w") as writefile:
            for cashtag in cashtag_list[:-1]:
                writefile.write(str(cashtag) + "\n")
            writefile.write(str(cashtag_list[-1]))
            
        return_msg += str(context.args[0])
    
    await update.message.reply_text(return_msg)


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

    # These functions are only accessible if user is authorized
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(CommandHandler("get_tracked_stockcodes", get_tracked_stockcodes))
    application.add_handler(CommandHandler("get_tracked_stocks", get_tracked_stocks))
    application.add_handler(CommandHandler("check_stock", check_stock))
    
    """Another restriction handler to restrict Chat IDs which are not admins"""
    restrict_admin_handler = MessageHandler(~admin_chatid_filter, restrict_admin)
    application.add_handler(restrict_admin_handler)

    # These functions are only accessible if user is admin
    application.add_handler(CommandHandler("add_tracked_stocks", add_tracked_stocks))
    application.add_handler(CommandHandler("remove_tracked_stocks", remove_tracked_stocks))    
    application.add_handler(CommandHandler("update_authorized", update_authorized))
    application.add_handler(CommandHandler("add_authorized", add_authorized))
    application.add_handler(CommandHandler("remove_authorized", remove_authorized))

    # on non command i.e message - echo the message on Telegram
    #application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    
    '''Enable Logging'''
    
    # Max log filesize 1 MB
    log_handler = RotatingFileHandler('receptionist.log', maxBytes=1000000, backupCount=5)

    logging.basicConfig(
        handlers = [log_handler],
        format="%(asctime)s:%(levelname)s - %(message)s", 
        level=logging.INFO
    )

    logger = logging.getLogger(__name__)

    # set higher logging level for httpx to avoid all GET and POST requests being logged
    logging.getLogger("httpx").setLevel(logging.WARNING)

    logger.info("Starting receptionist.py")
    
    
    '''Initialize Telegram Bot'''
    
    # Initialize the chat ID filter objects
    chatid_filter = filters.Chat(get_authorized_list())
    admin_chatid_filter = filters.Chat(get_admin_list())

    # Get the token for Telegram Bot
    with open('conf/telg_token', 'r') as token_file:
        telg_token = token_file.read()
        telg_token = telg_token[:-1]


    '''Main Function'''
    
    main()
