from butter_cms import ButterCMS

class ButterWrapper:
    def __init__(self):
        self.token = "d8a3560395bd1c063e9e062b38a0e2f74a0c6aec"
        self.client = ButterCMS(self.token)

    def GetProductsPage(self):
        products_page = self.client.pages.get('*', 'products-page')
        return products_page

    def GetCollection(self, collection_name):
        collection = self.client.content_fields.get([collection_name])
        collection_items = collection["data"]
        return collection_items

    def GetCart(self, cart):
        products = self.GetProductsPage()

        cart_list = []
        print(cart)

        if cart is not None:
            for item in cart:
                data = [product for product in products["data"]["fields"]["products_page"]["products"] if product["product_name"] == item]
                cart_list.append(data[0])

        return cart_list