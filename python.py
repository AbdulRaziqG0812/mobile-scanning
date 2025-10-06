from datetime import datetime
from flask import Flask, flash, jsonify, request, render_template, redirect, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from werkzeug import Response

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

@app.route('/dashboard', methods=['GET'])
def dashboard():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    # ✅ Total Products
    cursor.execute("SELECT COUNT(*) AS total_products FROM iphone_products")
    total_products = cursor.fetchone()['total_products'] or 0

    # ✅ Total Customers
    cursor.execute("SELECT COUNT(*) AS total_customers FROM customers")
    total_customers = cursor.fetchone()['total_customers'] or 0

    # ✅ Monthly Sales and Revenue
    now = datetime.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    cursor.execute("""
        SELECT COUNT(*) AS monthly_sales, IFNULL(SUM(net_total), 0) AS monthly_revenue
        FROM bills
        WHERE bill_date >= %s
    """, (month_start,))

    sales_data = cursor.fetchone() or {'monthly_sales': 0, 'monthly_revenue': 0}
    monthly_sales = sales_data['monthly_sales']
    monthly_revenue = sales_data['monthly_revenue']

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
            cursor = conn.cursor(dictionary=True)

            # 1️⃣ Get user by username only
            cursor.execute("SELECT * FROM login WHERE username = %s", (username,))
            user = cursor.fetchone()

            # 2️⃣ Check if user exists and password matches
            if user and check_password_hash(user['password'], password):
                # 3️⃣ Save session (login success)
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['role'] = user.get('role', 'user')  # optional, if you use roles

                return redirect(url_for('dashboard'))
            else:
                flash("Invalid username or password!", "error")
                return redirect(url_for('loginpage'))

        except Exception as e:
            flash(f"Error: {e}", "error")
            return redirect(url_for('loginpage'))
        finally:
            cursor.close()
            conn.close()

    return render_template('loginpage.html')

# register route

# Secret registration key (sirf authorized logon ko dena)
REGISTER_KEY = "MAT_OMAN"

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('fullname')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        entered_key = request.form.get('register_key')

        # 1️⃣ Check registration key
        if entered_key != REGISTER_KEY:
            flash("Invalid registration key!", "error")
            return redirect(url_for('register'))

        # 2️⃣ Check password match
        if password != confirm:
            flash("Passwords do not match!", "error")
            return redirect(url_for('register'))

        # 3️⃣ Check password strength
        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "error")
            return redirect(url_for('register'))

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)

            # 4️⃣ Check duplicate username
            cursor.execute("SELECT * FROM login WHERE username = %s", (username,))
            existing_user = cursor.fetchone()
            if existing_user:
                flash("Username already exists. Please choose another.", "error")
                return redirect(url_for('register'))

            # 5️⃣ Hash password securely
            hashed_pw = generate_password_hash(password)

            # 6️⃣ Insert into register table
            cursor.execute(
                "INSERT INTO register (username, email, password, confirm_password) VALUES (%s, %s, %s, %s)",
                (username, email, hashed_pw, hashed_pw)
            )

            # 7️⃣ Insert into login table
            cursor.execute(
                "INSERT INTO login (username, password) VALUES (%s, %s)",
                (username, hashed_pw)
            )

            conn.commit()
 
            return redirect(url_for('loginpage'))

        except Exception as e:
            flash(f"Error: {e}", "error")
            return redirect(url_for('register'))

        finally:
            cursor.close()
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

            # ✅ Success message + redirect (prevents double entry)
            flash("✅ Product added successfully!", "success")
            return redirect(url_for('product'))  # 🔥 This stops duplicate on refresh

    except Exception as e:
        flash(f"⚠️ Error adding product: {e}", "danger")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    # ✅ Render form page
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
            iphone_sale_price = request.form.get('iphone_sale_price')
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

        # ✅ Fetch customer info
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

        # ✅ Insert into bills
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

        # ✅ Insert items
        product_ids = request.form.getlist("product_id[]")
        qtys = request.form.getlist("qty[]")
        amounts = request.form.getlist("amount[]")

        for i in range(len(product_ids)):
            pid = int(product_ids[i])
            qty = int(qtys[i])
            amount = float(amounts[i])

            # ✅ Insert item including purchase price
            cursor.execute("""
                INSERT INTO bill_items (
                    bill_id, product_id, product_model, product_storage,
                    product_price, product_serial, product_imei,
                    product_color, purchase_price, qty, amount
                )
                SELECT %s, product_id, iphone_model, iphone_storage,
                       iphone_sale_price, iphone_serial, iphone_imei,
                       iphone_color, iphone_purchase_price, %s, %s
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

    # ✅ Calculate totals
    cursor.execute("""
        SELECT 
            IFNULL(SUM(subtotal), 0) AS sub_total,
            IFNULL(SUM(net_total), 0) AS net_total
        FROM bills
    """)
    totals = cursor.fetchone()
    sub_total = totals["sub_total"]
    net_total = totals["net_total"]

    # ✅ Fetch bills with customer info
    cursor.execute("""
        SELECT 
            b.bill_id, 
            b.bill_date,
            c.name AS customer_name,
            c.mobile AS customer_mobile,
            c.Contact AS customer_contact,
            c.address AS customer_address,
            b.subtotal, 
            b.discount, 
            b.net_total
        FROM bills b
        JOIN customers c ON b.customer_id = c.customer_id
        ORDER BY b.bill_date DESC
        LIMIT 100
    """)
    bills = cursor.fetchall()

    # ✅ Fetch related items for each bill (now includes purchase_price)
    bill_items = {}
    for bill in bills:
        cursor.execute("""
            SELECT 
                bi.qty, 
                bi.product_price AS sale_price, 
                bi.purchase_price, 
                bi.amount,
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

    # ✅ Pass totals to template also
    return render_template(
        "billing_list.html", 
        bills=bills, 
        bill_items=bill_items, 
        sub_total=sub_total, 
        net_total=net_total
    )


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

        # ✅ Get company info (only one active record)
    cursor.execute("SELECT * FROM company_settings ORDER BY id DESC LIMIT 1")
    company = cursor.fetchone()

    # Get bill info
    cursor.execute("""
        SELECT 
            b.bill_id, 
            b.bill_date,
            b.customer_name, 
            b.customer_mobile,
            b.customer_contact,
            b.customer_address,
            b.subtotal,
            b.discount,
            b.net_total
        FROM bills b
        WHERE b.bill_id = %s
    """, (bill_id,))
    bill = cursor.fetchone()

    if not bill:
        return "Bill not found", 404

    # Get bill items
    cursor.execute("""
        SELECT 
            bi.item_id,
            bi.product_id,
            bi.product_model,
            bi.product_storage,
            bi.product_price,
            bi.product_serial,
            bi.product_imei,
            bi.product_color,
            bi.qty,
            bi.amount
        FROM bill_items bi
        WHERE bi.bill_id = %s
    """, (bill_id,))
    items = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("invoice.html", bill=bill, items=items,company=company)



# create company route
@app.route("/company", methods=["GET", "POST"])
def company():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    # 🔹 Check if company settings already exist (only one record expected)
    cursor.execute("SELECT * FROM company_settings LIMIT 1")
    company = cursor.fetchone()

    if request.method == "POST":
        # 🔹 Get all form fields
        name = request.form.get("name", "")
        name_ar = request.form.get("name_ar", "")
        vat_no = request.form.get("vat_no", "")
        cr_no = request.form.get("cr_no", "")
        po_box = request.form.get("po_box", "")
        postal_code = request.form.get("postal_code", "")
        country = request.form.get("country", "")
        phone = request.form.get("phone", "")
        email = request.form.get("email", "")
        instagram = request.form.get("instagram", "")
        facebook = request.form.get("facebook", "")
        snapchat = request.form.get("snapchat", "")
        address = request.form.get("address", "")
        terms = request.form.get("terms", "")

        # 🔹 If record exists → UPDATE
        if company:
            cursor.execute("""
                UPDATE company_settings
                SET 
                    name = %s,
                    name_ar = %s,
                    vat_no = %s,
                    cr_no = %s,
                    po_box = %s,
                    postal_code = %s,
                    country = %s,
                    phone = %s,
                    email = %s,
                    instagram = %s,
                    facebook = %s,
                    snapchat = %s,
                    address = %s,
                    terms = %s,
                    updated_at = NOW()
                WHERE id = %s
            """, (
                name, name_ar, vat_no, cr_no, po_box, postal_code, country,
                phone, email, instagram, facebook, snapchat,
                address, terms, company["id"]
            ))
            flash("Company settings updated successfully!", "success")

        # 🔹 Else → INSERT
        else:
            cursor.execute("""
                INSERT INTO company_settings (
                    name, name_ar, vat_no, cr_no, po_box, postal_code, country,
                    phone, email, instagram, facebook, snapchat,
                    address, terms
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                name, name_ar, vat_no, cr_no, po_box, postal_code, country,
                phone, email, instagram, facebook, snapchat,
                address, terms
            ))
            flash("Company settings saved successfully!", "success")

        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for("company"))

    # 🔹 Render form with existing data (if any)
    cursor.close()
    conn.close()
    return render_template("company.html", company=company or {})

# report route
@app.route('/reports', methods=['GET', 'POST'])
def reports():
    selected_month = request.form.get("month")  # format: YYYY-MM

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    # 🧾 Pick last month with data if none selected
    if not selected_month:
        cursor.execute("SELECT DATE_FORMAT(MAX(bill_date), '%Y-%m') AS last_month FROM bills")
        result = cursor.fetchone()
        selected_month = result['last_month'] if result['last_month'] else None

    # ✅ Main Query — use purchase_price from bill_items
    query = """
        SELECT 
            DATE_FORMAT(b.bill_date, '%Y-%m') AS month,
            SUM(IFNULL(bi.qty, 0)) AS total_units,

            -- 💰 Total Sales
            SUM(IFNULL(bi.qty * bi.product_price, 0)) AS total_sales,

            -- 🛒 Total Purchase (from bill_items.purchase_price)
            SUM(IFNULL(bi.qty * bi.purchase_price, 0)) AS total_purchase,

            -- 📈 Total Profit
            SUM(
                IFNULL(bi.qty * (bi.product_price - bi.purchase_price), 0)
            ) AS total_profit

        FROM bills b
        LEFT JOIN bill_items bi ON b.bill_id = bi.bill_id
        WHERE bi.product_id IS NOT NULL
    """

    # 📅 Month filter
    params = []
    if selected_month:
        query += " AND DATE_FORMAT(b.bill_date, '%Y-%m') = %s"
        params.append(selected_month)

    query += " GROUP BY DATE_FORMAT(b.bill_date, '%Y-%m') ORDER BY DATE_FORMAT(b.bill_date, '%Y-%m') DESC"

    # 🔍 Execute query
    cursor.execute(query, params)
    data = cursor.fetchall()

    cursor.close()
    conn.close()

    # ✅ Prepare chart data
    chart_labels, sales_data, purchase_data, profit_data, units_data = [], [], [], [], []

    if data:
        for row in data:
            chart_labels.append(row.get('month', 'N/A'))
            sales_data.append(float(row.get('total_sales') or 0))
            purchase_data.append(float(row.get('total_purchase') or 0))
            profit_data.append(float(row.get('total_profit') or 0))
            units_data.append(int(row.get('total_units') or 0))
    else:
        chart_labels = [selected_month or 'No Data']
        sales_data = [0]
        purchase_data = [0]
        profit_data = [0]
        units_data = [0]

    # 🧮 Totals
    total_sales = sum(sales_data)
    total_purchase = sum(purchase_data)
    total_profit = sum(profit_data)
    total_units = sum(units_data)

    # 🖼️ Render report template
    return render_template(
        "reports.html",
        selected_month=selected_month,
        chart_labels=chart_labels,
        sales_data=sales_data,
        purchase_data=purchase_data,
        profit_data=profit_data,
        units_data=units_data,
        total_sales=total_sales,
        total_purchase=total_purchase,
        total_profit=total_profit,
        total_units=total_units
    )



if __name__ == '__main__':
    app.run(host="192.168.100.23", debug=True, port=5500)
    # app.run(debug=True)