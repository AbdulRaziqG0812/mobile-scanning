CREATE DATABASE  mobile_scanning;
USE mobile_scanning;


CREATE TABLE login(
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE register(
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    confirm_password VARCHAR(255) NOT NULL
);

CREATE TABLE  categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL UNIQUE
);


CREATE TABLE iphone_products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    category VARCHAR(100) NOT NULL,
    iphone_model VARCHAR(100) NOT NULL,
    iphone_storage VARCHAR(50),
    iphone_purchase_price DECIMAL(12,2) NOT NULL DEFAULT 0,
    iphone_sale_price DECIMAL(12,2) NOT NULL DEFAULT 0,
    iphone_imei VARCHAR(20),
    iphone_color VARCHAR(50),
    iphone_stock INT,
    iphone_battery_health VARCHAR(10),
    iphone_serial VARCHAR(100),
    iphone_display_size VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE  customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    mobile VARCHAR(20) NOT NULL,
    Contact VARCHAR(100),
    address VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE bills (
    bill_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    customer_name VARCHAR(255),
    customer_mobile VARCHAR(50),
    customer_contact VARCHAR(100),
    customer_address TEXT,
    bill_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    subtotal DECIMAL(12,2) DEFAULT 0,
    discount DECIMAL(12,2) DEFAULT 0,
    net_total DECIMAL(12,2) DEFAULT 0
);


CREATE TABLE bill_items (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    bill_id INT,
    product_id INT,
    product_model VARCHAR(255),
    product_storage VARCHAR(50),
    product_price DECIMAL(12,2) NOT NULL DEFAULT 0,
    product_serial VARCHAR(100),
    product_imei VARCHAR(100),
    product_color VARCHAR(50),
    purchase_price DECIMAL(12,2) DEFAULT 0,
    qty INT NOT NULL DEFAULT 1,
    amount DECIMAL(12,2) NOT NULL DEFAULT 0
);


CREATE TABLE company_settings (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    name_ar VARCHAR(255),
    vat_no VARCHAR(100),
    cr_no VARCHAR(100),
    po_box VARCHAR(100),
    postal_code VARCHAR(50),
    country VARCHAR(100),
    phone VARCHAR(50),
    email VARCHAR(150),
    instagram VARCHAR(255),
    facebook VARCHAR(255),
    snapchat VARCHAR(255),
    address TEXT,
    terms TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
