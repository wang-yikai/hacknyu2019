from flask import Flask, render_template, request, session, url_for, redirect
import json
import datetime
from semantics3 import Products

sem3 = Products(
	api_key = "SEM3C4DC74D42480F5F4C1CD26C2108854E6",
	api_secret = "YmVkZGQ1YWY1NTQxOThlZTE5Y2FlMDU1Nzc2MTlmMDQ"
)

def to_datetime(d):
    return datetime.datetime.fromtimestamp(
            int(d)
        ).strftime('%Y-%m-%d %H:%M:%S')

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
