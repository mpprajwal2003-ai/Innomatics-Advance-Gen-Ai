from fastapi import FastAPI, Query
from pydantic import BaseModel, Field
from typing import Optional, List
app = FastAPI()

# --- Temporary data (acting as our database for now) ---
products = [
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True},
    # --- Added Products (Task 1) ---
    {"id": 5, "name": "Laptop Stand", "price": 899, "category": "Electronics", "in_stock": True},
    {"id": 6, "name": "Mechanical Keyboard", "price": 2499, "category": "Electronics", "in_stock": True},
    {"id": 7, "name": "Webcam", "price": 1299, "category": "Electronics", "in_stock": False},
]

# --- Endpoint 0 : Home ---
@app.get("/")
def home():
    return {"message": "Welcome to our E-commerce API"}


# --- Endpoint 1 : Return all products ---
@app.get("/products")
def get_all_products():
    return {"products": products, "total": len(products)}


# --- Endpoint 2 : Filter products ---
@app.get("/products/filter")
def filter_products(
    category: str = Query(None, description="Electronics or Stationery"),
    max_price: int = Query(None, description="Maximum price"),
    in_stock: bool = Query(None, description="True = in stock only")
):

    result = products

    if category:
        result = [p for p in result if p["category"] == category]

    if max_price:
        result = [p for p in result if p["price"] <= max_price]

    if in_stock is not None:
        result = [p for p in result if p["in_stock"] == in_stock]

    return {"filtered_products": result, "count": len(result)}

# Task 2 : Category Filter Endpoint
@app.get("/products/category/{category_name}")
def get_products_by_category(category_name: str):

    result = [p for p in products if p["category"].lower() == category_name.lower()]

    if not result:
        return {"error": "No products found in this category"}

    return {"products": result, "count": len(result)}

# Task 3 : Show Only In-Stock Products
@app.get("/products/instock")
def get_instock_products():

    instock_products = [p for p in products if p["in_stock"]]

    return {
        "in_stock_products": instock_products,
        "count": len(instock_products)
    }

# Task 4 : Store Summary
@app.get("/store/summary")
def store_summary():

    total = len(products)
    instock = len([p for p in products if p["in_stock"]])
    outstock = total - instock

    categories = list(set([p["category"] for p in products]))

    return {
        "store_name": "My E-commerce Store",
        "total_products": total,
        "in_stock": instock,
        "out_of_stock": outstock,
        "categories": categories
    }

# Task 5 : Search Products
@app.get("/products/search/{keyword}")
def search_products(keyword: str):

    result = [p for p in products if keyword.lower() in p["name"].lower()]

    if not result:
        return {"message": "No products matched your search"}

    return {
        "matched_products": result,
        "count": len(result)
    }

# Bonus : Cheapest & Most Expensive Product
@app.get("/products/deals")
def product_deals():

    cheapest = min(products, key=lambda x: x["price"])
    expensive = max(products, key=lambda x: x["price"])

    return {
        "best_deal": cheapest,
        "premium_pick": expensive
    }

@app.get("/products/{product_id}")
def get_product(product_id: int):
    for product in products:
        if product["id"] == product_id:
            return {"product": product}
    return {"error": "Product not found"}

# ==================================================
# DAY 2 ASSIGNMENT STARTS HERE
# ==================================================

# Q1—Filter Products by Minimum Price
@app.get("/products/filter")
def filter_products(
        min_price: int = Query(None),
        max_price: int = Query(None),
        category: str = Query(None)
):
    result = products

    if category:
        result = [p for p in result if p["category"].lower() == category.lower()]

    if min_price:
        result = [p for p in result if p["price"] >= min_price]

    if max_price:
        result = [p for p in result if p["price"] <= max_price]

    return {"products": result, "total": len(result)}


# Q2 — Get Product Price Only
@app.get("/products/{product_id}/price")
def get_product_price(product_id: int):
    for product in products:
        if product["id"] == product_id:
            return {
                "name": product["name"],
                "price": product["price"]
            }
    return {"error": "Product not found"}


# Q3 — Customer Feedback (POST + Pydantic)
feedback = []
class CustomerFeedback(BaseModel):
    customer_name: str = Field(..., min_length=2)
    product_id: int = Field(..., gt=0)
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=300)


@app.post("/feedback")
def submit_feedback(data: CustomerFeedback):
    feedback.append(data.model_dump())

    return {
        "message": "Feedback submitted successfully",
        "feedback": data.model_dump(),
        "total_feedback": len(feedback)
    }


# Q4 — Product Summary Dashboard
@app.get("/products/summary")
def product_summary():
    in_stock = [p for p in products if p["in_stock"]]
    out_stock = [p for p in products if not p["in_stock"]]

    expensive = max(products, key=lambda p: p["price"])
    cheapest = min(products, key=lambda p: p["price"])

    categories = list(set(p["category"] for p in products))

    return {
        "total_products": len(products),
        "in_stock_count": len(in_stock),
        "out_of_stock_count": len(out_stock),
        "most_expensive": {
            "name": expensive["name"],
            "price": expensive["price"]
        },
        "cheapest": {
            "name": cheapest["name"],
            "price": cheapest["price"]
        },
        "categories": categories
    }


# Q5 — Bulk Order System
class OrderItem(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0, le=50)


class BulkOrder(BaseModel):
    company_name: str = Field(..., min_length=2)
    contact_email: str = Field(..., min_length=5)
    items: List[OrderItem]


@app.post("/orders/bulk")
def place_bulk_order(order: BulkOrder):
    confirmed = []
    failed = []
    grand_total = 0

    for item in order.items:

        product = next((p for p in products if p["id"] == item.product_id), None)

        if not product:
            failed.append({
                "product_id": item.product_id,
                "reason": "Product not found"
            })

        elif not product["in_stock"]:
            failed.append({
                "product_id": item.product_id,
                "reason": f"{product['name']} is out of stock"
            })

        else:
            subtotal = product["price"] * item.quantity
            grand_total += subtotal

            confirmed.append({
                "product": product["name"],
                "qty": item.quantity,
                "subtotal": subtotal
            })

    return {
        "company": order.company_name,
        "confirmed": confirmed,
        "failed": failed,
        "grand_total": grand_total
    }


# BONUS — Order Status System
orders = []


class OrderRequest(BaseModel):
    customer_name: str
    product_id: int
    quantity: int


@app.post("/orders")
def place_order(data: OrderRequest):
    order = {
        "order_id": len(orders) + 1,
        "customer_name": data.customer_name,
        "product_id": data.product_id,
        "quantity": data.quantity,
        "status": "pending"
    }

    orders.append(order)

    return {"order": order}


@app.get("/orders/{order_id}")
def get_order(order_id: int):
    for order in orders:
        if order["order_id"] == order_id:
            return {"order": order}

    return {"error": "Order not found"}


@app.patch("/orders/{order_id}/confirm")
def confirm_order(order_id: int):
    for order in orders:
        if order["order_id"] == order_id:
            order["status"] = "confirmed"
            return {"message": "Order confirmed", "order": order}

    return {"error": "Order not found"}


