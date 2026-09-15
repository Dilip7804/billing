import sqlite3
import os
import csv
from datetime import datetime

def init_db():
    conn = sqlite3.connect('store_billing.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bills (
            bill_no INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_mobile TEXT,
            grand_total REAL,
            payment_mode TEXT DEFAULT 'CASH',
            date_time TEXT
        )
    ''')
    
    try:
        cursor.execute("ALTER TABLE bills ADD COLUMN payment_mode TEXT DEFAULT 'CASH'")
    except:
        pass
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            barcode TEXT UNIQUE,
            rate REAL,
            stock REAL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bill_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bill_no INTEGER,
            item_name TEXT,
            qty REAL,
            rate REAL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT
        )
    ''')
    cursor.execute("INSERT OR IGNORE INTO users (username, password) VALUES ('admin', '1234')")
    
    conn.commit()
    conn.close()

def check_login(username, password):
    conn = sqlite3.connect('store_billing.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user is not None

def import_vrs_csv(filename):
    if not os.path.exists(filename):
        return False, "File nahi mili!"
    
    try:
        conn = sqlite3.connect('store_billing.db')
        cursor = conn.cursor()
        
        with open(filename, mode='r', encoding='utf-8', errors='ignore') as f:
            reader = csv.reader(f)
            header = next(reader, None)
            
            count = 0
            for row in reader:
                if len(row) >= 4:
                    name = row[0].strip()
                    barcode = row[1].strip()
                    
                    try:
                        rate = float(row[2].strip())
                    except:
                        rate = 0.0
                        
                    try:
                        stock = float(row[3].strip())
                    except:
                        stock = 0.0
                    
                    # Yahan stock = items.stock + excluded.stock kar diya hai taaki quantity jud jaye
                    cursor.execute('''
                        INSERT INTO items (name, barcode, rate, stock) 
                        VALUES (?, ?, ?, ?)
                        ON CONFLICT(barcode) DO UPDATE SET 
                        name = excluded.name,
                        rate = excluded.rate,
                        stock = items.stock + excluded.stock
                    ''', (name, barcode, rate, stock))
                    count += 1
                    
        conn.commit()
        conn.close()
        return True, f"Success! {count} items sync ho gaye aur stock update ho gaya."
    except Exception as e:
        try:
            conn = sqlite3.connect('store_billing.db')
            cursor = conn.cursor()
            cursor.execute("DROP TABLE IF EXISTS items")
            cursor.execute('''
                CREATE TABLE items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    barcode TEXT UNIQUE,
                    rate REAL,
                    stock REAL
                )
            ''')
            conn.commit()
            conn.close()
            return import_vrs_csv(filename)
        except Exception as inner_e:
            return False, f"Sync Error: {str(inner_e)}"

def update_item_stock(barcode, new_stock):
    """Opening Stock screen se individual item ki stock quantity update karne ke liye"""
    try:
        conn = sqlite3.connect('store_billing.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE items SET stock = ? WHERE barcode = ?", (new_stock, barcode))
        conn.commit()
        conn.close()
        return True, "Stock successfully updated!"
    except Exception as e:
        return False, str(e)

def search_item(query):
    conn = sqlite3.connect('store_billing.db')
    cursor = conn.cursor()
    query_str = f"%{query.strip()}%"
    cursor.execute("SELECT name, rate, stock FROM items WHERE barcode = ? OR LOWER(name) LIKE LOWER(?)", (query.strip(), query_str))
    item = cursor.fetchone()
    conn.close()
    return item

def search_items_suggestions(query):
    if not query.strip():
        return []
    conn = sqlite3.connect('store_billing.db')
    cursor = conn.cursor()
    query_str = f"%{query.strip()}%"
    cursor.execute("SELECT name, rate, stock FROM items WHERE barcode LIKE ? OR LOWER(name) LIKE LOWER(?) LIMIT 6", (query_str, query_str))
    items = cursor.fetchall()
    conn.close()
    return items

def save_bill_to_db(customer_mobile, cart_items, grand_total, payment_mode="CASH"):
    try:
        conn = sqlite3.connect('store_billing.db')
        cursor = conn.cursor()
        
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute("INSERT INTO bills (customer_mobile, grand_total, payment_mode, date_time) VALUES (?, ?, ?, ?)", 
                       (customer_mobile, grand_total, payment_mode, date_str))
        bill_no = cursor.lastrowid
        
        for item in cart_items:
            name = item['name']
            qty = float(item['qty'])
            rate = float(item.get('rate', 0.0))
            
            # Save individual bill items for stock tracking
            cursor.execute("INSERT INTO bill_items (bill_no, item_name, qty, rate) VALUES (?, ?, ?, ?)",
                           (bill_no, name, qty, rate))
            
            # Deduct stock from items table
            cursor.execute("UPDATE items SET stock = stock - ? WHERE name = ?", (qty, name))
            
        conn.commit()
        conn.close()
        print("Bill successfully saved to DB!")
        return True, "Bill successfully saved!"
    except Exception as e:
        print("Error saving bill:", e)
        return False, str(e)

def get_sales_reports():
    """Sales report screen ke liye saare bills fetch karne ka function"""
    try:
        conn = sqlite3.connect('store_billing.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bills ORDER BY bill_no DESC")
        rows = cursor.fetchall()
        print("DEBUG - Fetched Bills from database:", rows)
        conn.close()
        return rows
    except Exception as e:
        print("DEBUG - DB Fetch Error:", e)
        return []

def get_stock_inventory():
    """
    Inventory screen ke liye: Total Aaya, Total Bika aur Balance stock calculate karta hai.
    Returns: list of tuples -> (item_name, total_in, total_sold, balance_stock)
    """
    try:
        conn = sqlite3.connect('store_billing.db')
        cursor = conn.cursor()
        
        # Get total sold quantity per item from bill_items table
        cursor.execute("SELECT item_name, SUM(qty) FROM bill_items GROUP BY item_name")
        sold_dict = {row[0]: float(row[1]) for row in cursor.fetchall()}
        
        # Get current balance stock and items from items table
        cursor.execute("SELECT name, stock FROM items")
        items_rows = cursor.fetchall()
        
        stock_list = []
        for name, current_stock in items_rows:
            sold = sold_dict.get(name, 0.0)
            balance = float(current_stock) if current_stock is not None else 0.0
            total_in = balance + sold
            stock_list.append((name, total_in, sold, balance))
            
        conn.close()
        return stock_list
    except Exception as e:
        print("DEBUG - Stock Fetch Error:", e)
        return []