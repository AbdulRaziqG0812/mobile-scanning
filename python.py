from flask import Flask, flash, request, render_template, redirect, url_for
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

# route for homepage    
@app.route('/homepage' , methods=['GET', 'POST'])
def homepage(): 
    return render_template('homepage.html')

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
                flash("Login successful!", "success")
                return redirect(url_for('homepage'))
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

@app.route('/product', methods=['GET', 'POST'])
def product():
    conn = None
    cursor = None
    categories = []

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Fetch categories for dropdown
        cursor.execute("SELECT category_name FROM categories")
        categories = cursor.fetchall()

        if request.method == "POST":
            category = request.form.get('category')

            # Fetch all form fields
            iphone_model = request.form.get('iphone_model')
            iphone_storage = request.form.get('iphone_storage')
            iphone_price = request.form.get('iphone_price')
            iphone_imei = request.form.get('iphone_imei')
            iphone_color = request.form.get('iphone_color')
            iphone_stock = request.form.get('iphone_stock')
            iphone_battery_health = request.form.get('iphone_battery_health')
            iphone_serial = request.form.get('iphone_serial')
            iphone_display_size = request.form.get('iphone_display_size')

            # Insert into products table
            cursor.execute("""
                INSERT INTO iphone_products (
                    category, iphone_model, iphone_storage, iphone_price,
                    iphone_imei, iphone_color, iphone_stock, iphone_battery_health,
                    iphone_serial, iphone_display_size
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                category, iphone_model, iphone_storage, iphone_price,
                iphone_imei, iphone_color, iphone_stock, iphone_battery_health,
                iphone_serial, iphone_display_size
            ))

            conn.commit()
            flash(f" product added successfully!", "success")
            return redirect(url_for('product'))  # ✅ Redirect after submit

    except Exception as e:
        flash(f"An error occurred: {e}", "error")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template('product.html', categories=categories)


# Product list route
@app.route('/product_list')
def product_list():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM iphone_products ORDER BY product_id DESC")
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('product_list.html', products=products)

# ✅ Edit Product

@app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    conn = None
    cursor = None
    categories = []

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Fetch categories for dropdown
        cursor.execute("SELECT category_name FROM categories")
        categories = cursor.fetchall()

        # Fetch product details
        cursor.execute("SELECT * FROM iphone_products WHERE product_id=%s", (product_id,))
        product = cursor.fetchone()

        if request.method == "POST":
            category = request.form.get('category')
            iphone_model = request.form.get('iphone_model')
            iphone_storage = request.form.get('iphone_storage')
            iphone_price = request.form.get('iphone_price')
            iphone_imei = request.form.get('iphone_imei')
            iphone_color = request.form.get('iphone_color')
            iphone_stock = request.form.get('iphone_stock')
            iphone_battery_health = request.form.get('iphone_battery_health')
            iphone_serial = request.form.get('iphone_serial')
            iphone_display_size = request.form.get('iphone_display_size')

            # Update product in database
            cursor.execute("""
                UPDATE iphone_products SET
                    category=%s, iphone_model=%s, iphone_storage=%s, iphone_price=%s,
                    iphone_imei=%s, iphone_color=%s, iphone_stock=%s, iphone_battery_health=%s,
                    iphone_serial=%s, iphone_display_size=%s
                WHERE product_id=%s
            """, (
                category, iphone_model, iphone_storage, iphone_price,
                iphone_imei, iphone_color, iphone_stock, iphone_battery_health,
                iphone_serial, iphone_display_size, product_id
            ))

            conn.commit()
            flash("✅ Product updated successfully!", "success")
            return redirect(url_for('product_list'))  # Redirect to product list/add page

    except Exception as e:
        flash(f"An error occurred: {e}", "error")

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
        query += " AND (category LIKE %s OR iphone_model LIKE %s)"
        params.extend([f"%{keyword}%", f"%{keyword}%"])

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

if __name__ == '__main__':
    app.run(host="192.168.100.23", debug=True, port=5500)
    # app.run(debug=True)