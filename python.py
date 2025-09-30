from datetime import datetime
from flask import Flask, flash, jsonify, request, render_template, redirect, url_for
import mysql.connector
# from werkzeug import Response

app = Flask(__name__)
app.secret_key = "112233"  # kuch bhi random strong string daal do

db_config= {
    'host':'localhost',
    'user':'root',
    'password':'raziq12@',
    'database':'mobile_scanning'
}
# route for home page

@app.route('/')
def home():
    return render_template('loginpage.html')

# route for dashboard    

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard(): 
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    # Total Products
    cursor.execute("SELECT COUNT(*) AS total_products FROM iphone_products")
    total_products = cursor.fetchone()['total_products']

    # Total Customers
    cursor.execute("SELECT COUNT(*) AS total_customers FROM customers")
    total_customers = cursor.fetchone()['total_customers']

    # Monthly Sales and Revenue
    now = datetime.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    cursor.execute("""
        SELECT COUNT(*) AS monthly_sales, IFNULL(SUM(net_total),0) AS monthly_revenue
        FROM bills
        WHERE bill_date >= %s
    """, (month_start,))
    sales_data = cursor.fetchone()
    monthly_sales = sales_data['monthly_sales'] or 0
    monthly_revenue = sales_data['monthly_revenue'] or 0

    cursor.close()
    conn.close()

    return render_template(
        "dashboard.html",
        total_products=total_products,
        total_customers=total_customers,
        monthly_sales=monthly_sales,
        monthly_revenue=monthly_revenue
    )

# route for loginpage

@app.route('/loginpage', methods=['GET', 'POST'])
def loginpage():
    if request.method == 'POST':
        username = request.form.get('id')
        password = request.form.get('password')

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True, buffered=True)

            cursor.execute(
                "SELECT * FROM login WHERE username = %s AND password = %s",
                (username, password)
            )
            existing_user = cursor.fetchone()

            if existing_user:
                return redirect(url_for('dashboard'))
            else:
                flash("Invalid username or password!", "error")
                return redirect(url_for('loginpage'))

        except Exception as e:
            flash(f"Error: {e}", "error")
            return redirect(url_for('loginpage'))
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    return render_template('loginpage.html')

# route for Register

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('fullname')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm')

        if password != confirm:
            flash("Passwords do not match!", "error")
            return redirect(url_for('register'))

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            # Insert into register table
            cursor.execute(
                "INSERT INTO register (username, email, password, confirm_password) VALUES (%s, %s, %s, %s)",
                (username, email, password, confirm)
            )

            # Also insert into login table
            cursor.execute(
                "INSERT INTO login (username, password) VALUES (%s, %s)",
                (username, password)
            )

            conn.commit()
            flash("Registration successful! Please login.", "success")

        except Exception as e:
            flash(f"Error: {e}", "error")
            return redirect(url_for('register'))
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    return render_template("register.html")

# ✅ Add Category
@app.route("/category", methods=["GET", "POST"])
def category():
    if request.method == "POST":
        category_name = request.form["category_name"]

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO categories (category_name) VALUES (%s)", (category_name,))
        conn.commit()
        conn.close()

        flash("✅ Category added successfully!", "success")

        # ✅ Redirect back to form (allow multiple entries)
        return redirect(url_for("category"))

    return render_template("category.html")



# ✅ Category List
@app.route("/category_list")
def category_list():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM categories ORDER BY category_id DESC")
    categories = cursor.fetchall()
    conn.close()
    return render_template("category_list.html", categories=categories)

# ✅ Edit category
@app.route("/edit_category/<int:id>", methods=["GET", "POST"])
def edit_category(id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        new_name = request.form["category_name"]
        cursor.execute("UPDATE categories SET category_name=%s WHERE category_id=%s", (new_name, id))
        conn.commit()
        conn.close()
        flash("✅ Category updated successfully!", "success")
        return redirect(url_for("category_list"))

    cursor.execute("SELECT * FROM categories WHERE category_id=%s", (id,))
    category = cursor.fetchone()
    conn.close()
    return render_template("edit_category.html", category=category)


# ✅ Delete category
@app.route("/delete_category/<int:id>", methods=["POST"])
def delete_category(id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM categories WHERE category_id=%s", (id,))
    conn.commit()
    conn.close()
    flash("🗑️ Category deleted successfully!", "success")
    return redirect(url_for("category_list"))


# ✅ Full Product Add Route (All Categories)

# ✅ Product Add Route
@app.route('/product', methods=['GET', 'POST'])
def product():
    conn = None
    cursor = None
    categories = []

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # ✅ Fetch categories for dropdown
        cursor.execute("SELECT category_name FROM categories")
        categories = cursor.fetchall()

        # ✅ Handle product form submission
        if request.method == "POST":
            category = request.form.get('category')
            iphone_model = request.form.get('iphone_model')
            iphone_storage = request.form.get('iphone_storage')
            iphone_purchase_price = request.form.get('iphone_purchase_price')
            iphone_sale_price = request.form.get('iphone_sale_price')
            iphone_imei = request.form.get('iphone_imei')
            iphone_color = request.form.get('iphone_color')
            iphone_stock = request.form.get('iphone_stock')
            iphone_battery_health = request.form.get('iphone_battery_health')
            iphone_serial = request.form.get('iphone_serial')
            iphone_display_size = request.form.get('iphone_display_size')

            # ✅ Insert data into table
            cursor.execute("""
                INSERT INTO iphone_products (
                    category, iphone_model, iphone_storage, 
                    iphone_purchase_price, iphone_sale_price,
                    iphone_imei, iphone_color, iphone_stock, 
                    iphone_battery_health, iphone_serial, iphone_display_size
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                category, iphone_model, iphone_storage,
                iphone_purchase_price, iphone_sale_price,
                iphone_imei, iphone_color, iphone_stock,
                iphone_battery_health, iphone_serial, iphone_display_size
            ))

            conn.commit()
            flash("✅ Product added successfully!", "success")
            return redirect(url_for('product'))  # ✅ Redirect to product list

    except Exception as e:
        flash(f"⚠️ Error adding product: {e}", "error")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template('product.html', categories=categories)


# ✅ Product List Route
@app.route('/product_list')
def product_list():
    conn = None
    cursor = None
    products = []
    total_purchase = 0
    total_sale = 0

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # ✅ Auto delete products with zero or negative stock
        cursor.execute("DELETE FROM iphone_products WHERE iphone_stock <= 0")
        conn.commit()

        # ✅ Fetch all products
        cursor.execute("SELECT * FROM iphone_products ORDER BY product_id DESC")
        products = cursor.fetchall()

        # ✅ Calculate totals
        cursor.execute("""
            SELECT 
                IFNULL(SUM(iphone_purchase_price), 0) AS total_purchase,
                IFNULL(SUM(iphone_sale_price), 0) AS total_sale
            FROM iphone_products
        """)
        totals = cursor.fetchone()
        total_purchase = totals["total_purchase"]
        total_sale = totals["total_sale"]

    except Exception as e:
        flash(f"⚠️ Error loading product list: {e}", "error")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template(
        'product_list.html',
        products=products,
        total_purchase=total_purchase,
        total_sale=total_sale
    )

# ✅ Edit Product

@app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    conn = None
    cursor = None
    categories = []

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # ✅ Fetch categories for dropdown
        cursor.execute("SELECT category_name FROM categories")
        categories = cursor.fetchall()

        # ✅ Fetch product details
        cursor.execute("SELECT * FROM iphone_products WHERE product_id=%s", (product_id,))
        product = cursor.fetchone()

        if not product:
            flash("⚠️ Product not found!", "error")
            return redirect(url_for('product'))

        if request.method == "POST":
            category = request.form.get('category')
            iphone_model = request.form.get('iphone_model')
            iphone_storage = request.form.get('iphone_storage')
            iphone_purchase_price = request.form.get('iphone_purchase_price')
            iphone_sale_price = request.form.get('iphone_price')
            iphone_imei = request.form.get('iphone_imei')
            iphone_color = request.form.get('iphone_color')
            iphone_stock = request.form.get('iphone_stock')
            iphone_battery_health = request.form.get('iphone_battery_health')
            iphone_serial = request.form.get('iphone_serial')
            iphone_display_size = request.form.get('iphone_display_size')

            # ✅ Update product in database
            cursor.execute("""
                UPDATE iphone_products SET
                    category=%s, iphone_model=%s, iphone_storage=%s,
                    iphone_purchase_price=%s, iphone_sale_price=%s,
                    iphone_imei=%s, iphone_color=%s, iphone_stock=%s,
                    iphone_battery_health=%s, iphone_serial=%s, iphone_display_size=%s
                WHERE product_id=%s
            """, (
                category, iphone_model, iphone_storage,
                iphone_purchase_price, iphone_sale_price,
                iphone_imei, iphone_color, iphone_stock,
                iphone_battery_health, iphone_serial, iphone_display_size,
                product_id
            ))

            conn.commit()
            flash("✅ Product updated successfully!", "success")
            return redirect(url_for('product_list'))  # Go back to product page

    except Exception as e:
        flash(f"⚠️ An error occurred: {e}", "error")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template('edit_product.html', product=product, categories=categories)


# ✅ Delete Product
@app.route('/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM iphone_products WHERE product_id=%s", (product_id,))
        conn.commit()
        flash("🗑️ Product deleted successfully!", "success")
    except Exception as e:
        flash(f"An error occurred: {e}", "error")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return redirect(url_for('product_list'))  # Redirect to product list/add page

# serchh route

@app.route("/search", methods=["GET"])
def search():
    keyword = request.args.get("q", "").strip()

    query = "SELECT * FROM iphone_products WHERE 1=1"
    params = []

    if keyword:
        # ✅ Search by Category, Model, or IMEI
        query += " AND (category LIKE %s OR iphone_model LIKE %s OR iphone_imei LIKE %s)"
        params.extend([f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"])

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, params)
    products = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("product_list.html", products=products, keyword=keyword)


# ✅ Customer Add Route
@app.route("/customer", methods=["GET", "POST"])
def customer():
    if request.method == "POST":
        name = request.form["name"]
        mobile = request.form["mobile"]
        Contact = request.form.get("Contact", "")
        address = request.form.get("address", "")

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO customers (name, mobile, Contact, address) VALUES (%s, %s, %s, %s)",
                       (name, mobile, Contact, address))
        conn.commit()
        cursor.close()
        conn.close()

        flash("Customer added successfully!", "success")
                # 🚀 Redirect after POST to avoid resubmission
        return redirect(url_for("customer"))

    return render_template("customer.html")

# ✅ Show Customer List
@app.route("/customer_list")
def customer_list():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM customers ORDER BY customer_id DESC")
    customers = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("customer_list.html", customers=customers)

# ✅ Edit Customer
@app.route("/edit_customer/<int:id>", methods=["GET", "POST"])
def edit_customer(id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        name = request.form["name"]
        mobile = request.form["mobile"]
        Contact = request.form.get("contact")  # ✅ correct
        address = request.form.get("address")

        cursor.execute(
            "UPDATE customers SET name=%s, mobile=%s, Contact=%s, address=%s WHERE customer_id=%s",
            (name, mobile, Contact, address, id)
        )
        conn.commit()
        cursor.close()
        conn.close()

        flash("Customer updated successfully!", "success")
        return redirect(url_for("customer_list"))

    cursor.execute("SELECT * FROM customers WHERE customer_id=%s", (id,))
    customer = cursor.fetchone()
    cursor.close()
    conn.close()

    return render_template("edit_customer.html", customer=customer)


# ✅ Delete Customer
@app.route("/delete_customer/<int:id>", methods=["POST"])
def delete_customer(id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM customers WHERE customer_id=%s", (id,))
    conn.commit()
    cursor.close()
    conn.close()

    flash("Customer deleted successfully!", "success")
    return redirect(url_for("customer_list"))

# ✅ Search Customer by Mobile or Contact
@app.route('/search_customer', methods=['GET'])
def search_customer():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    
    search = request.args.get('search', '').strip()
    
    if search:
        query = """
            SELECT * FROM customers
            WHERE mobile LIKE %s OR Contact LIKE %s
            ORDER BY customer_id DESC
        """
        like_search = f"%{search}%"
        cursor.execute(query, (like_search, like_search))
    else:
        query = "SELECT * FROM customers ORDER BY customer_id DESC"
        cursor.execute(query)
    
    customers = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('customer_list.html', customers=customers)

# ---------- GET CUSTOMER ----------
@app.route("/get_customer/<int:id>")
def get_customer(id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT customer_id, name, mobile, Contact, address FROM customers WHERE customer_id=%s", (id,))
    customer = cursor.fetchone()
    cursor.close()
    conn.close()
    return jsonify(customer)

# ---------- GET PRODUCT ----------
@app.route("/get_product/<int:id>")
def get_product(id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT product_id, iphone_model, iphone_storage, iphone_sale_price, iphone_imei,
               iphone_color, iphone_stock, iphone_serial
        FROM iphone_products
        WHERE product_id=%s
    """, (id,))
    product = cursor.fetchone()
    cursor.close()
    conn.close()
    return jsonify(product)

# ---------- BILLING FORM ----------
@app.route("/billing", methods=["GET", "POST"])
def billing():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    # ✅ Fetch customers and available products
    cursor.execute("SELECT * FROM customers")
    customers = cursor.fetchall()

    cursor.execute("SELECT * FROM iphone_products WHERE iphone_stock > 0")
    products = cursor.fetchall()

    if request.method == "POST":
        customer_id = request.form["customer_id"]
        subtotal = request.form["subtotal"]
        discount = request.form["discount"]
        net_total = request.form["net_total"]

        # ✅ Fetch full customer info (with aliases for consistency)
        cursor.execute("""
            SELECT 
                name AS customer_name, 
                mobile AS customer_mobile, 
                Contact AS customer_contact, 
                address AS customer_address 
            FROM customers 
            WHERE customer_id = %s
        """, (customer_id,))
        customer = cursor.fetchone()

        if not customer:
            flash("Invalid customer selected!", "danger")
            cursor.close()
            conn.close()
            return redirect(url_for("billing"))

        # ✅ Insert into bills with all details
        cursor.execute("""
            INSERT INTO bills (
                customer_id, customer_name, customer_mobile,
                customer_contact, customer_address,
                subtotal, discount, net_total
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            customer_id,
            customer["customer_name"],
            customer["customer_mobile"],
            customer["customer_contact"],
            customer["customer_address"],
            subtotal,
            discount,
            net_total
        ))

        bill_id = cursor.lastrowid

        # ✅ Insert all items into bill_items
        product_ids = request.form.getlist("product_id[]")
        qtys = request.form.getlist("qty[]")
        amounts = request.form.getlist("amount[]")

        for i in range(len(product_ids)):
            pid = int(product_ids[i])
            qty = int(qtys[i])
            amount = float(amounts[i])

            cursor.execute("""
                INSERT INTO bill_items (
                    bill_id, product_id, product_model, product_storage,
                    product_price, product_serial, product_imei,
                    product_color, qty, amount
                )
                SELECT %s, product_id, iphone_model, iphone_storage,
                       iphone_sale_price, iphone_serial, iphone_imei,
                       iphone_color, %s, %s
                FROM iphone_products
                WHERE product_id = %s
            """, (bill_id, qty, amount, pid))

            # ✅ Update stock
            cursor.execute("""
                UPDATE iphone_products
                SET iphone_stock = GREATEST(iphone_stock - %s, 0)
                WHERE product_id = %s
            """, (qty, pid))

        conn.commit()
        cursor.close()
        conn.close()

        flash("Bill created successfully! You can now print the invoice.", "success")
        return redirect(url_for("invoice", bill_id=bill_id))

    cursor.close()
    conn.close()
    return render_template("billing.html", customers=customers, products=products)


# ---------- BILLING LIST ----------
@app.route("/billing_list")
def billing_list():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    # Fetch bills with customer info
    cursor.execute("""
        SELECT b.bill_id, b.bill_date,
               c.name AS customer_name,
               c.mobile AS customer_mobile,
               c.Contact AS customer_contact,
               c.address AS customer_address,
               b.subtotal, b.discount, b.net_total
        FROM bills b
        JOIN customers c ON b.customer_id = c.customer_id
        ORDER BY b.bill_date DESC
        LIMIT 100
    """)
    bills = cursor.fetchall()

    # Fetch related items for each bill
    bill_items = {}
    for bill in bills:
        cursor.execute("""
            SELECT bi.qty, bi.product_price AS price, bi.amount,
                   bi.product_model,
                   bi.product_storage,
                   bi.product_color,
                   bi.product_imei,
                   bi.product_serial
            FROM bill_items bi
            WHERE bi.bill_id = %s
        """, (bill['bill_id'],))
        bill_items[bill['bill_id']] = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template("billing_list.html", bills=bills, bill_items=bill_items)


# ---------- DELETE BILL ----------
@app.route('/delete_bill/<int:bill_id>', methods=['GET'])
def delete_bill(bill_id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    # Delete bill items first
    cursor.execute("DELETE FROM bill_items WHERE bill_id=%s", (bill_id,))
    # Then delete the bill
    cursor.execute("DELETE FROM bills WHERE bill_id=%s", (bill_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Bill deleted successfully!", "success")
    return redirect(url_for('billing_list'))

# ---------- SEARCH BILL ----------
@app.route("/search_bill")
def search_bill():
    keyword = request.args.get("q", "").strip()
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    bills = []
    bill_items = {}

    # ✅ Step 1: Search filter (correct JOIN order)
    if keyword:
        cursor.execute("""
            SELECT DISTINCT b.bill_id
            FROM bills b
            JOIN customers c ON b.customer_id = c.customer_id
            JOIN bill_items bi ON bi.bill_id = b.bill_id
            WHERE bi.product_model LIKE %s 
               OR bi.product_imei LIKE %s
               OR bi.product_serial LIKE %s
               OR c.name LIKE %s
               OR c.mobile LIKE %s
        """, (
            f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", 
            f"%{keyword}%", f"%{keyword}%"
        ))
        bill_ids = [row["bill_id"] for row in cursor.fetchall()]
    else:
        bill_ids = []

    # ✅ Step 2: Fetch bills (filtered or all)
    if bill_ids:
        format_ids = ",".join(["%s"] * len(bill_ids))
        cursor.execute(f"""
            SELECT b.*, c.name AS customer_name, c.mobile AS customer_mobile,
                   c.Contact AS customer_contact, c.address AS customer_address
            FROM bills b
            JOIN customers c ON b.customer_id = c.customer_id
            WHERE b.bill_id IN ({format_ids})
            ORDER BY b.bill_date DESC
        """, bill_ids)
    else:
        cursor.execute("""
            SELECT b.*, c.name AS customer_name, c.mobile AS customer_mobile,
                   c.Contact AS customer_contact, c.address AS customer_address
            FROM bills b
            JOIN customers c ON b.customer_id = c.customer_id
            ORDER BY b.bill_date DESC
        """)
    bills = cursor.fetchall()

    # ✅ Step 3: Fetch all bill_items for these bills
    if bills:
        bill_ids = [bill["bill_id"] for bill in bills]
        format_ids = ",".join(["%s"] * len(bill_ids))
        cursor.execute(f"SELECT * FROM bill_items WHERE bill_id IN ({format_ids})", bill_ids)
        all_items = cursor.fetchall()

        for item in all_items:
            bid = item["bill_id"]
            bill_items.setdefault(bid, []).append(item)

    cursor.close()
    conn.close()

    return render_template("billing_list.html", bills=bills, bill_items=bill_items, keyword=keyword)


# ---------- INVOICE ----------
@app.route("/invoice/<int:bill_id>")
def invoice(bill_id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    # Get bill info
    cursor.execute("SELECT * FROM bills WHERE bill_id=%s", (bill_id,))
    bill = cursor.fetchone()

    # Get customer info
    cursor.execute("""
        SELECT c.name AS customer_name, c.mobile AS customer_mobile, c.contact AS customer_contact, c.address AS customer_address
        FROM bills b
        JOIN customers c ON b.customer_id = c.customer_id
        WHERE b.bill_id=%s
    """, (bill_id,))
    customer = cursor.fetchone()

    # Get bill items
    cursor.execute("SELECT * FROM bill_items WHERE bill_id=%s", (bill_id,))
    items = cursor.fetchall()

    # Get company info
    cursor.execute("SELECT * FROM company_settings LIMIT 1")
    company = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template("invoice.html", bill=bill, customer=customer, items=items, company=company)



# create company route

@app.route("/company", methods=["GET", "POST"])
def company():
    if request.method == "POST":
        # Get form data
        name = request.form.get("name", "")
        address = request.form.get("address", "")
        phone = request.form.get("phone", "")
        email = request.form.get("email", "")
        terms = request.form.get("terms", "")

        # Connect to DB
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Insert new company settings
        cursor.execute("""
            INSERT INTO company_settings (name, address, phone, email, terms)
            VALUES (%s, %s, %s, %s, %s)
        """, (name, address, phone, email, terms))

        conn.commit()
        cursor.close()
        conn.close()

        flash("Company settings saved successfully!", "success")
        return redirect(url_for("company"))

    # For GET request, just show empty form
    return render_template("company.html", company={})

if __name__ == '__main__':
    app.run(host="192.168.100.23", debug=True, port=5600)
    # app.run(debug=True)