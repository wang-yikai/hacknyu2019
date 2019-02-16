from flask import Flask, render_template, request, session, url_for, redirect
import json
from semantics3 import Products

sem3 = Products(
	api_key = "SEM3C4DC74D42480F5F4C1CD26C2108854E6",
	api_secret = "YmVkZGQ1YWY1NTQxOThlZTE5Y2FlMDU1Nzc2MTlmMDQ"
)

sem3.offers_field("sem3_id", "7JAykYaFyiYscEmcAwYC64")

offers = sem3.get_offers()

print("_______Price History______")
print(offers)

# sem3.products_field("search", "iPhone")
#
# results = sem3.get_products()
#
# print("_______Product Search List_____")
# print(results)
