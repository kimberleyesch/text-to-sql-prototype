import random
import pandas as pd
from faker import Faker

CUSTOMER_COUNT = 500
PRODUCT_COUNT = 230  # max: 230
ORDERS_COUNT = 100
MAX_ITEMS_PER_ORDER= 15

INDUSTRY_SECTORS = [
    "Industrial Automation",
    "Robotics",
    "Mechanical Engineering",
    "Electrical Engineering",
    "Electronics Manufacturing",
    "Semiconductor Manufacturing",
    "Automotive Technology",
    "Electric Vehicles",
    "Aerospace and Defence",
    "Railway Technology",
    "Medical Technology",
    "Laboratory Equiptment",
    "Renewable Energy",
    "Energy Storage",
    "Telecommunications",
    "Data Center Infrastructure",
    "Building Automation",
    "Agricultural Technology",
    "Logistics Automation",
    "Advanced Manufacturing"
]

COMPANY_SIZES = ["small", "medium", "large"]

ORDER_STATUS = ["completed", "pending", "cancelled"]

LOCATION_URL = "https://raw.githubusercontent.com/datasets/world-cities/main/data/world-cities.csv"

PRODUCTS_URL = "https://huggingface.co/api/resolve-cache/datasets/crawlfeeds/HomeDepot-Smart-Home-Dataset/8d71a34c8d5f9210a0d57a3b62178072d6f069c0/crawlfeeds_homedepot__limit-2000000_category_1-smart-home_20260409_191051.csv?download=true"


# -----------------------------------------------------------------------------------------
# Read data from urls
# -----------------------------------------------------------------------------------------

def read_location_data():
    """Reads data for locations."""

    required_columns = {"name", "country"}

    try:
        location_data = pd.read_csv(LOCATION_URL)
    except Exception as error:
        raise RuntimeError("Cities and Countries could not be read from file.") from error

    if not required_columns.issubset(location_data.columns) or (len(location_data) < CUSTOMER_COUNT):
        raise ValueError("Cities and Countries file data differs from the expected.")
    
    return location_data

def read_product_data():
    """Reads data for products."""

    required_columns = {"product_name", "price", "category_4"}
    
    try:
        product_data = pd.read_csv(PRODUCTS_URL)
    except Exception as error:
        raise RuntimeError("Products could not be read from file.") from error

    if not required_columns.issubset(product_data.columns) or (len(product_data) < PRODUCT_COUNT):
        raise ValueError("Product file data differs from the expected.")

    return product_data

# -----------------------------------------------------------------------------------------
# Create test data
# -----------------------------------------------------------------------------------------

def create_customers():
    """Creates synthetic customer data."""

    fake = Faker("en_US")

    # read cities and countries
    location_data = read_location_data()

    # choose random location data
    random_locations = location_data.sample(n=CUSTOMER_COUNT)
    cities = random_locations["name"].tolist()
    countries = random_locations["country"].tolist()
    
    # create customer table
    customers = pd.DataFrame({
        "customer_id": range(1, CUSTOMER_COUNT+1),
        "company_name": [fake.unique.company() for _ in range(CUSTOMER_COUNT)],
        "industry": [random.choice(INDUSTRY_SECTORS) for _ in range(CUSTOMER_COUNT)],
        "company_size": random.choices(COMPANY_SIZES, k=CUSTOMER_COUNT),
        "country": countries,
        "city": cities,
        "acquisition_date": [fake.date_between() for _ in range(CUSTOMER_COUNT)],    # defaults between -30 years and today
        "is_active": random.choices(population=[1, 0], weights=[90, 10], k=CUSTOMER_COUNT),
    })

    return customers

def create_categories():
    """Creates synthetic category data."""

    product_data = read_product_data()

    unique_categories = (product_data["category_4"].dropna().drop_duplicates().reset_index(drop=True))

    # create categories table
    categories = pd.DataFrame({
        "category_id": range(1, len(unique_categories)+1),
        "category_name": unique_categories,
    })

    return categories

def create_products(categories):
    """Creates synthetic product data."""

    product_data = read_product_data()

    categories_mapping = dict(zip(categories["category_name"], categories["category_id"]))

    prices_cents = (pd.to_numeric(product_data["price"], errors="coerce")*100).round()

    product_prices = []
    product_costs = []

    for price in prices_cents:
        if pd.isna(price):
            price = random.randint(100, 100000)
        else:
            price = int(price)

        product_prices.append(price)

        product_costs.append(round(price*0.9))


    # create products table
    products = pd.DataFrame({
        "product_id": range(1, len(product_data)+1),
        "product_name": product_data["product_name"],
        "category_id": product_data["category_4"].map(categories_mapping),
        "current_unit_price_cents": product_prices,
        "current_unit_cost_cents": product_costs,
    })

    return products

def create_orders(customers):
    """Creates synthetic order data."""

    fake = Faker("en_US")

    selected_customer_ids = [random.choice(customers["customer_id"]) for _ in range(ORDERS_COUNT)]
    acquisition_dates = dict(zip(customers["customer_id"], customers["acquisition_date"]))

    # create orders table
    orders = pd.DataFrame({
        "order_id": range(1, ORDERS_COUNT+1),
        "customer_id": selected_customer_ids,
        "order_date": [fake.date_between(start_date=acquisition_dates[customer_id], end_date="today") for customer_id in selected_customer_ids],
        "order_status": random.choices(ORDER_STATUS, weights=[70, 10, 20], k=ORDERS_COUNT),
    })

    return orders

def create_order_items(orders, products):
    """Creates synthetic order item data."""

    order_items_data = []

    for order_id in orders["order_id"]:

        num_of_items = random.randint(1, MAX_ITEMS_PER_ORDER)

        select_products = products.sample(n=num_of_items)

        for _, product in select_products.iterrows():
            order_items_data.append({
                "order_item_id": len(order_items_data)+1,
                "order_id": order_id,
                "product_id": product["product_id"],
                "order_unit_price_cents": product["current_unit_price_cents"],
                "order_unit_cost_cents": product["current_unit_cost_cents"],
                "quantity": random.randint(1, 10),
                "discount_percent": random.choices(population=[0,5,10,15,20,30], weights=[60,15,10,5,5,5],k=1)[0],
            })

    order_items = pd.DataFrame(order_items_data)

    return order_items

def create_test_data():
    """Creates and returns all related test data."""

    customers = create_customers()
    categories = create_categories()
    products = create_products(categories)
    orders = create_orders(customers)
    order_items = create_order_items(orders, products)
    
    
    return {
        "customers": customers,
        "categories": categories,
        "products": products,
        "orders": orders,
        "order_items": order_items,
    }

def main():
    test_data = create_test_data()

    for table_name, dataframe in test_data.items():
        print(f"\n--- {table_name} ---")
        print(dataframe.head())
        print(f"Rows: {len(dataframe)}")

if __name__ == "__main__":
    main()