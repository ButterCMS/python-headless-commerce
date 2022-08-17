from flask import Flask, render_template, request, session, redirect
from square.client import Client

import uuid

from butter_wrapper import *

app = Flask(__name__)

app.secret_key = "SUPER_SECRET_KEY"

@app.route("/")
@app.route("/<category>")
def main(category = None):
    butter_cms = ButterWrapper()

    # Getting product information
    products_page = butter_cms.GetProductsPage()
    data = []

    # Getting the category collection
    categories = butter_cms.GetCollection("producttypes")

    # filtering by category
    if category is not None:
        for item in products_page["data"]["fields"]["products_page"]["products"]:
            for category_type in item["product_type"]:
                if category_type["type"] == category:
                    data.append(item)
    else:
        data = products_page["data"]["fields"]["products_page"]["products"]

    return render_template("index.html", data = data, categories = categories)

@app.route("/product/<product_name>", methods = ["GET", "POST"])
def product_page(product_name):
    if request.method == "GET":
        if session["cart"] is None:
            session["cart"] = []
 
    if request.method == "POST":
        item_list = session["cart"]
        item_list.append(product_name)
        session["cart"] = item_list
      
    butter_cms = ButterWrapper()
 
    # Getting product information
    product_list = butter_cms.get_proudcts_page()
 
    data = [product for product in product_list["data"]["fields"]["products_page"]["products"] if product["product_name"] == product_name]
 
    return render_template("product.html", data = data[0])

@app.route("/cart")
def cart_page():
    if request.method == "GET":
        butter_cms = ButterWrapper()

        cart_list = butter_cms.GetCart(session["cart"])
        cart_total = 0

        if cart_list is not None:
            for item in cart_list:
                cart_total += item["product_price"]

        return render_template("cart.html", data = cart_list, total = round(cart_total, 2))


@app.route("/checkout")
def checkout_page():
    butter_cms = ButterWrapper()

    cart_list = butter_cms.GetCart(session["cart"])

    client = Client(
        access_token = "YOUR_ACCESS_TOKEN",
        environment = "sandbox"
    )

    transaction_list = []
    for item in cart_list:
        new_line_item = {
            "name": item["product_name"],
            "quantity": "1",
            "note": None,
            "base_price_money": {
                "amount": int(str(item["product_price"]).replace(".", "")),
                "currency": "USD"
            }
        }

        transaction_list.append(new_line_item)
        
    new_transaction = {
        "idempotency_key": str(uuid.uuid4()),
        "order": {
            "location_id": "LEVXRZH7FYWW0",
            "line_items": transaction_list
        }
    }

    result = client.checkout.create_payment_link(new_transaction)

    if result.is_success():
        return redirect(result.body["payment_link"]["url"])
    elif result.is_error():
        return render_template("cart.html")

app.run(host = "0.0.0.0", port = 5002, debug = True)