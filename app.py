from flask import Flask, render_template, request, session, url_for, redirect
import json
import datetime
from copy import deepcopy
from sqlite3 import connect
from hashlib import sha1
from semantics3 import Products

sem3 = Products(
	api_key = "SEM3C4DC74D42480F5F4C1CD26C2108854E6",
	api_secret = "YmVkZGQ1YWY1NTQxOThlZTE5Y2FlMDU1Nzc2MTlmMDQ"
)
f = "data/database.db"
app = Flask(__name__)

@app.route('/')
def homepage():
    return render_template("index.html")

def get_median(l):
	l = sorted(l)
	if len(l) % 2 == 1:
		return l[len(l)//2]
	return (l[len(l)//2] + l[len(l)//2 - 1])/2

def insert_interval(l, interval):
	for i in range(len(l)):
		if interval[1] <= l[i][1]:
			l.insert(i, interval)
			return l
	l.append(interval)
	return l

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
        return ""
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
	return watchlistMain(user, item)#register helper

def watchlistMain(user, item):
	db = connect(f)
	c = db.cursor()
	if not in_watchlist(user, item): #if error message is blank then theres no problem, update database
		query = ("INSERT INTO watchlist VALUES (?, ?)")
		c.execute(query, (user, item))
		db.commit()
		db.close()
		return ""
	db.commit()
	db.close()
	return "Item already in watchlist!"#return error message

def in_watchlist(user, item):
	db = connect(f)
	c = db.cursor()
	query = ("SELECT item FROM watchlist WHERE user=?")
	sel = c.execute(query, (user,))
	for record in sel:
		# print(record)
		if record[0] == item:
			db.close()
			return True
	db.commit()
	db.close()
	return False

def get_watchlist(user):
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

def trend_median(price_history):
	if len(price_history) < 1:
		# print("here")
		return []

	trend = []
	curr_prices = [ price_history[0][-1] ]
	curr_intervals = [ price_history[0] ]
	last_start = price_history[0][0]
	for i in range(1, len(price_history)):
		# print(i)
		j = 0
		while j < len(curr_intervals):
			# |------|
					  # |---------|
			# |-------|
					# |-------|
			if curr_intervals[j][1] <= price_history[i][0]:
				# print("1")
				trend.append([ last_start, curr_intervals[j][1], get_median(curr_prices) ])
				last_start = price_history[i][0]
				curr_prices.remove(curr_intervals[j][-1])
				curr_intervals.pop(j)

			# |--------|
			# 	|------|
			else:
				# print("2")
				trend.append([ last_start, price_history[i][0], get_median(curr_prices)])
				last_start = price_history[i][0]
				curr_prices.append(price_history[i][-1])
				j = len(curr_intervals)

		# print("3")
		curr_intervals = insert_interval(curr_intervals, price_history[i])

		# |-----------|
		# 	|------|
	while len(curr_intervals) > 1:
		trend.append([last_start, curr_intervals[1][1], get_median(curr_prices)])
		last_start = curr_intervals[1][1]
		curr_prices.remove(curr_intervals[0][-1])
		curr_intervals.pop(0)

	trend.append([ last_start, curr_intervals[0][1], get_median(curr_prices) ])
	return sorted(trend)




sem3.offers_field("sem3_id", "7JAykYaFyiYscEmcAwYC64")

offers = sem3.get_offers()
price_history = []

print("_______Price History______")
# print(offers['results'])
for elem in offers['results']:
    price_history.append([ int(elem['firstrecorded_at']), int(elem['lastrecorded_at']), float(elem['price']) ])

price_history = sorted(price_history)
print(price_history)

# sem3.products_field("search", "iPhone")
#
# results = sem3.get_products()

# print("_______Product Search List_____")
# # print(results)
# for elem in results['results']:
#     print("name:", elem['name'], "sem3_id:", elem['sem3_id'])

print("_____TREND____")
print(trend_median(price_history))

# print("1:",register("bob", "thebuilder"))
# print("2:",login("bob", "thebuilder"))
# print("3:",login("what", "haha"))
# print("4:",register("what", "haha"))
# print("5:",register("bob", "thebuilder"))
# print("6:",add_to_watchlist("bob", "iPhone"))
# print("7:",add_to_watchlist("bob", "PC"))
# print("8:",get_watchlist("bob"))
# print("9:",add_to_watchlist("bob", "iPhone"))
# print("end:",remove_from_watchlist("bob", "iPhone"))
# print("10:",get_watchlist("bob"))
