#TODO
1. (DONE) Implement a list to read from and iterate through all items in the list
2. (DONE) Create and integrate Telegram Bot for sending alerts
3. (DONE) Implement threshold based notifications
4. Ideas for interactive components for the Telegram Bot
	4a. Do an ad-hoc check on followed companies
	4b. Pull data for specific company
	4c. Add company cashtag to followed companies
5. (DONE) Access Control List - a simple authorizzed/unauthorizzed will do ;]
6. Logging
7. Headless browser interaction to pull up fancy charts from Bursa?

# Note:

1. Data source 1: Stockcodes(Cashtags) can be searched at https://www.bursamarketplace.com/mkt/themarket/stock

#Usage

##Conf folder
1. Create ./conf/ folder
2. Create telg_chatid and telg_token files under the ./conf/ folder
3. Put Telegram Chat ID and Telegram API token into the corresponding file
* Both files must end with an empty line

##RBAC
1. Edit admin.lst and authorized.lst
2. Populate both files with a list of authorized telegram user IDs / group chat IDs
3. admin.lst contains list of authorized users who can make changes to settings via receptionist script
4. authorized.lst contains list of read-only users who can request information via receptionist script

