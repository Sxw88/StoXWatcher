# Note:

1. Data source 1: Stockcodes(Cashtags) can be searched at https://www.bursamarketplace.com/mkt/themarket/stock

#Usage

##Conf folder
1. Create ./conf/ folder
2. Create telg_chatid and telg_token files under the ./conf/ folder
3. Put Telegram Chat ID and Telegram API token into the corresponding files (Both files must end with an empty line)

##RBAC
1. Edit admin.lst and authorized.lst
2. Populate both files with a list of authorized telegram user IDs / group chat IDs
3. admin.lst contains list of authorized users who can make changes to settings via receptionist script
4. authorized.lst contains list of read-only users who can request information via receptionist script

