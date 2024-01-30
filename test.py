#!/usr/bin/python3

def check_authorized(chatid):
    str_chatid = str(chatid)

    # Read file which contains a list of authorized users
    authorized_ids = []

    with open('authorized.lst') as readfile:
        authorized_ids = [line.rstrip() for line in readfile]

    if str_chatid in authorized_ids:
        return True
    else:
        return False


print(check_authorized('-100210185610'))
