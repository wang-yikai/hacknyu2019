from flask import Flask, render_template, request, session, url_for, redirect
import json
import datetime
from sqlite3 import connect
from hashlib import sha1
from semantics3 import Products

sem3 = Products(
	api_key = "SEM3C4DC74D42480F5F4C1CD26C2108854E6",
	api_secret = "YmVkZGQ1YWY1NTQxOThlZTE5Y2FlMDU1Nzc2MTlmMDQ"
)
f = "data/database.db"

def to_datetime(d):
    return datetime.datetime.fromtimestamp(
            int(d)
        ).strftime('%Y-%m-%d %H:%M:%S')

def login(user, password):
    db = connect(f)
    c = db.cursor()
    query = ("SELECT * FROM users WHERE user=?")
    sel = c.execute(query,(user,));

    #records with this username
    #so should be at most one record (in theory)

    for record in sel:
        password = sha1(password.encode('utf-8')).hexdigest()
        if (password==record[1]):
            return "" #no error message because it will be rerouted to mainpage
        else:
            return "Invalid password"#error message
    db.close()
    return "User does not exist"#error message

def register(user, password):
    db = connect(f)
    c = db.cursor()
    try: #does table already exist?
        c.execute("SELECT * FROM users")
    except: #if not, this is the first user!
        c.execute("CREATE TABLE users (user TEXT, password TEXT)")
    db.commit()
    db.close()
    return regMain(user, password)#register helper

def regMain(user, password):#register helper
    db = connect(f)
    c = db.cursor()
    reg = regReqs(user, password)
    if reg == "": #if error message is blank then theres no problem, update database
        query = ("INSERT INTO users VALUES (?, ?)")
        password = sha1(password.encode('utf-8')).hexdigest()
        c.execute(query, (user, password))
        db.commit()
        db.close()
        return 1
    db.commit()
    db.close()
    return reg#return error message

def regReqs(user, password):      #error message generator
    if duplicate_user(user):          #checks if username already exists
        return "Username already exists"
    if " " in user:
        return "Spaces not allowed in username"
    return ""

def duplicate_user(user):#checks if username already exists
    db = connect(f)
    c = db.cursor()
    query = ("SELECT * FROM users WHERE user=?")
    sel = c.execute(query, (user,))
    retVal = False
    for record in sel:
        retVal = True
    db.commit()
    db.close()
    return retVal

def add_to_watchlist(user, item):
	db = connect(f)
    c = db.cursor()
    try: #does table already exist?
        c.execute("SELECT * FROM watchlist")
    except: #if not, this is the first user!
        c.execute("CREATE TABLE watchlist (user TEXT, item TEXT)")
    db.commit()
    db.close()
    return watchlistMain(user, password)#register helper

def watchlistMain(user, item):
	db = connect(f)
    c = db.cursor()
    if not in_watchlist(user, item): #if error message is blank then theres no problem, update database
        query = ("INSERT INTO watchlist VALUES (?, ?)")
        c.execute(query, (user, item))
        db.commit()
        db.close()
        return 1
    db.commit()
    db.close()
    return "Item already in watchlist!"#return error message

def in_watchlist(user, item):
	db = connect(f)
    c = db.cursor()
    query = ("SELECT * FROM watchlist WHERE user=?")
    sel = c.execute(query, (user,))
    for record in sel:
        if record == item:
			return True
    db.commit()
    db.close()
    return False

def get_watchlist(user, item):
	db = connect(f)
    c = db.cursor()
    query = ("SELECT * FROM watchlist WHERE user=?")
    sel = c.execute(query, (user,))
    results = []
    for record in sel:
        results.append(record)
    db.commit()
    db.close()
    return results

def remove_from_watchlist(user, item):
	db = connect(f)
    c = db.cursor()
    data = c.execute("DELETE FROM watchlist WHERE user=? AND item=?",(user,item,))
    db.commit()
    db.close()


sem3.offers_field("sem3_id", "7JAykYaFyiYscEmcAwYC64")

offers = sem3.get_offers()
price_history = []

print("_______Price History______")
# print(offers['results'])
for elem in offers['results']:
    price_history.append([ to_datetime(elem['lastrecorded_at']), to_datetime(elem['firstrecorded_at']), elem['price'] ])

sorted(price_history)
print(price_history)

sem3.products_field("search", "iPhone")

results = sem3.get_products()

print("_______Product Search List_____")
# print(results)
for elem in results['results']:
    print("name:", elem['name'], "sem3_id:", elem['sem3_id'])
