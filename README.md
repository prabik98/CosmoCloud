# CosmoCloud
# E-commerce Application with FastAPI and MongoDB

## Overview

This is a simple e-commerce application built using FastAPI, a modern, fast (high-performance), web framework for building APIs, and MongoDB, a NoSQL database. The application provides RESTful APIs to manage products and orders, allowing users to list products, create orders, update product quantities, and retrieve order information.

## Features

- **List Products**: Retrieve a list of available products in the system, including product name, price, and available quantity.
- **Create Product**: Add new products with details such as name, price, available quantity.
- **Create Orders**: Create new orders with details such as timestamp, purchased items, total amount, and user address.
- **Update Product Quantity**: Update the available quantity for a product when an order is placed.
- **Fetch All Orders**: Retrieve a list of all orders with optional pagination support, allowing you to specify the number of records to skip and the maximum number of records to fetch.
- **Fetch Single Order**: Fetch a single order from the system using its Order ID.

## Getting Started

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/prabik98/CosmoCloud.git
2. **Install Dependencies**:
   pip install -r requirements.txt

3. Run the Application:
   uvicorn main:app --reload

4. The application should be running at http://127.0.0.1:8000.
   To test the app, go to http://127.0.0.1:8000/docs -- swagger API

5. **Usage**
   You can interact with the APIs using tools like curl, Postman, or any REST API client.

6. **API Endpoints**
   List All Products:   GET /products
   Add New Product:   POST /products
   Create a New Order:   POST /orders
   Update Product Quantity:   PUT /products/{product_id}
   Fetch All Orders (with pagination support):   GET /orders
   Fetch Single Order by Order ID:   GET /orders/{order_id}
   
7. Acknowledgments
   FastAPI
   MongoDB
   Pydantic
   bson

