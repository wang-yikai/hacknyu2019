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
        ).strftime('%m/%d %H:%M:%S')

def logon(user, password):
    db = connect(f)
    c = db.cursor()
	try:
    	query = ("SELECT * FROM users WHERE user=?")
	except:
		db.close()
		return "Users non-existent!"
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

def get_prob_table(trend):
	semi_tr = [
		[1483228800, 1485907200, 0.1], [1485907200, 1488326400, 0], [1488326400, 1491004800, -0.3], [1491004800, 1493596800, 0.1],
		[1493596800, 1496275200, 0.1], [1496275200, 1498867200, 0.8], [1498867200, 1501545600, 0.2], [1501545600, 1504224000, 0.4],
		[1504224000, 1506816000, 0], [1506816000, 1509494400, 0], [1509494400, 1512086400, 0], [1512086400, 1514764800, -0.1],
		[1514764800, 1517443200, -0.2], [1517443200, 1519862400, 0], [1519862400, 1522540800, -0.1], [1522540800, 1525132800, 0.2],
		[1525132800, 1527811200, 0], [1527811200, 1530403200, 0.3], [1530403200, 1533081600, 0.4], [1533081600, 1535760000, -0.4],
		[1535760000, 1538352000, 1.6], [1538352000, 1541030400, -0.9], [1541030400, 1543622400, 0.1], [1543622400, 1546300800, 1.5]
	]
	probs = []
	price = trend[0][-1]
	for i in range(1, len(trend)):
		if price - trend[i][-1] >= (0.1 * price):
			percent_diff = (price - trend[i][-1])/price
			j = 0
			while j < len(semi_tr):
				if (semi_tr[j][0] <= trend[i][0] or semi_tr[j][1] >= trend[i][0]) and (semi_tr[j][-1] >= 0):
					probs.append([ int(100 * ((semi_tr[j][-1]/4 + percent_diff)/2 + abs(semi_tr[j][-1]/4 - percent_diff) ** 2)), int(price - trend[i][-1] + semi_tr[j][-1]), to_datetime(trend[i][0]), to_datetime(trend[i][1])])
					j = len(semi_tr)
				j += 1
			price = trend[i][-1]
	return probs

# sem3.offers_field("sem3_id", "7JAykYaFyiYscEmcAwYC64")
#
# offers = sem3.get_offers()
# price_history = []
#
# print("_______Price History______")
# # print(offers['results'])
# for elem in offers['results']:
#     price_history.append([ int(elem['firstrecorded_at']), int(elem['lastrecorded_at']), float(elem['price']) ])
#
# price_history = sorted(price_history)
# print(price_history)

# sem3.products_field("search", "iPhone")
#
# results = sem3.get_products()

# print("_______Product Search List_____")
# # print(results)
# for elem in results['results']:
#     print("name:", elem['name'], "sem3_id:", elem['sem3_id'])

# print("_____TREND____")
# trends = trend_median(price_history)
# print(trends)
#
# print("____PROBS____")
# print(get_prob_table(trends))

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

@app.route('/')
def homepage():
	if 'username' in session:
		return redirect(url_for('logged_on'))
	error = request.args.get('error')
	return render_template("register.html", error = error)

@app.route('/login/')
def login():
	error = request.args.get('error')
	return render_template("login.html", error = error)

@app.route("/home/")
def logged_on():
	username = reguest.args.get('username')
	if username:
		session['username'] = username
	if 'username' in session:
		return render_template("index.html")
	return redirect(url_for('homepage'))

@app.route("/logout/")
def logout():
	if 'username' in session:
		session.pop('username')
	return redirect(url_for('homepage'))

@app.route("/authenticate/", methods=['POST'])
def authenticate():
	password = request.form["password"]
	username = request.form["username"]

	text = logon(username, password)
	if len(text) < 1:
		return redirect(url_for('logged_on',username=username))
	return redirect(url_for('login',error=text))

@app.route('/register/', methods=['POST'])
def register():
	password = request.form["password"]
	username = request.form["username"]
	repeat = request.form["repeat"]#login vs. register

	if password != repeat:
		text = "Passwords do not match!"
	else:
		text = len(register(username, password))
	if len(text) < 1:
		return redirect(url_for('logged_on',username=username))
	return redirect(url_for('homepage',error=text))

if __name__ == '__main__':
    app.debug = True
    app.secret_key = '\x43\xd2\x34\x92\x5b\x4a\x80\xfc\xc6\xb0\x0e\x45\xdd\x51\x36\xc0\xd2\x3a\x85\x42\x57\xbb\x61\xf2\x7b\xb6\xfc\x17\x3b\x1a\xda\x5b\x6d\x7d\x0a\xff\xd3\x6f\xfa\x7c\x1b\xa8\x0f\x7f\x53\x18\x8d\x91\x16\x81'
    app.run()
