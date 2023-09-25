from fastapi import FastAPI, HTTPException, Query, Path, Body, status
from fastapi.responses import Response, JSONResponse
from fastapi.encoders import jsonable_encoder
from pymongo import MongoClient
from pymongo.collection import Collection
from typing import List
from models.product import Product, Order, UpdateProduct
from bson import ObjectId
from bson.errors import InvalidId

app = FastAPI()

#Database connection
client = MongoClient("mongodb+srv://bikash:incorrect@cloud.jwcitcy.mongodb.net/")
db = client["ecommerce"]
products_collection: Collection = db["products"]
orders_collection: Collection = db["orders"]


@app.get("/products", response_model=List[Product])
def list_products():
    products = list(products_collection.find())
    get_products = [product for product in products]
    return get_products

@app.post("/products", response_model=Product)
def create_product(product: Product):
    product = jsonable_encoder(product)
    del product['_id']
    new_product = products_collection.insert_one(product)
    product_added = products_collection.find_one({"_id":new_product.inserted_id})
    product_added['_id']=str(product_added['_id'])
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=product_added)

@app.put("/products/{product_id}", response_model=Product, response_model_exclude_unset=True)
def update_product(product_id: str, product: UpdateProduct):
    #product_id is valid ObjectId
    try:
        product_id_obj = ObjectId(product_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid product ID")

    #Find product in database
    existing_product = products_collection.find_one({"_id": product_id_obj})

    if not existing_product:
        raise HTTPException(status_code=404, detail="Product not found")

    #Update available quantity
    product={key: value for key, value in product.dict().items() if value is not None}
    products_collection.update_one(
        {"_id": product_id_obj},
        {"$set": product}
    )
    #Return updated product
    updated_product = products_collection.find_one({"_id":product_id_obj})
    updated_product["_id"] = str(updated_product["_id"])
    return updated_product

@app.get("/orders", response_model=List[Order])
def get_orders(skip: int = Query(0, description="Number of records to skip"),
               limit: int = Query(3, description="Number of records to fetch")):
    #validation
    if skip < 0 or limit < 0:
        raise HTTPException(status_code=400, detail="Skip and limit must be non-negative")

    #Fetch orders with pagination
    orders = list(orders_collection.find().skip(skip).limit(limit))

    if not orders:
        raise HTTPException(status_code=404, detail="No orders found")
    return orders

@app.get("/orders/{order_id}", response_model=Order)
def get_order(order_id: str = Path(..., description="Order ID")):
    #valid ObjectId
    try:
        order_id_obj = ObjectId(order_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid order ID")

    #Find order by id
    order_by_id = orders_collection.find_one({"_id": order_id_obj})

    if not order_by_id:
        raise HTTPException(status_code=404, detail="Order not found")
    return order_by_id

@app.post("/orders", response_model=Order)
async def create_order(order: Order):
    order = jsonable_encoder(order)
    del order['_id']
    #Calculate total amount for order
    total_amount = 0
    # counter=-1
    for count, item in enumerate(order['items']):
        try:
            product_id = ObjectId(item['product_id'])
        except InvalidId:
            raise HTTPException(status_code=400, detail="Invalid product_id")
        
        product = products_collection.find_one({"_id": product_id})
        
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        available_quantity = product["available_quantity"]

        bought_quantity = 0
        if((available_quantity - item['bought_quantity']) >= 0):
            bought_quantity = item['bought_quantity']
        else:
            bought_quantity = available_quantity
        
        total_amount += product["price"] * bought_quantity

        #available_quantity updation
        updated_quantity = product["available_quantity"] - bought_quantity
        products_collection.update_one(
            {"_id": product_id},
            {"$set": {"available_quantity": updated_quantity}}
        )
        order['items'][count]['bought_quantity'] = bought_quantity
        
    order["total_amount"] = total_amount

    #order inserted into MongoDB collection
    new_order = orders_collection.insert_one(order)

    #order returned
    created_order = orders_collection.find_one({"_id":new_order.inserted_id})
    created_order['_id'] = created_order['_id']
    return created_order