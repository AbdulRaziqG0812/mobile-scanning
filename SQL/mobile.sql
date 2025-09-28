CREATE database mobile_scanning;
USE mobile_scanning;

create table login(
id int auto_increment primary key,
username varchar(255),
password varchar(255) 
);

create table register(
id int auto_increment primary key,
username varchar(255),
email varchar(255) unique,
password varchar(255),
confirm_password varchar(255) 
);

CREATE TABLE categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE iphone_products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    category VARCHAR(100) NOT NULL,
    iphone_model VARCHAR(100) NOT NULL,
    iphone_storage VARCHAR(50),
    iphone_purchase_price VARCHAR(100) DEFAULT 0,
    iphone_sale_price VARCHAR(100) DEFAULT 0,
    iphone_imei INT,
    iphone_color VARCHAR(50),
    iphone_stock INT,
    iphone_battery_health VARCHAR(10),
    iphone_serial VARCHAR(100),
    iphone_display_size VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE customers (
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
    subtotal DECIMAL(12,2),
    discount DECIMAL(12,2),
    net_total DECIMAL(12,2)
);

CREATE TABLE bill_items (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    bill_id INT,
    product_id INT,
    product_model VARCHAR(255),
    product_storage VARCHAR(50),
    product_price DECIMAL(12,2),
    product_serial VARCHAR(100),
    product_imei VARCHAR(100),
    product_color VARCHAR(50),
    qty INT,
    amount DECIMAL(12,2)
);

CREATE TABLE company_settings (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(255) NOT NULL,
  address TEXT,
  phone VARCHAR(50),
  email VARCHAR(100),
  terms TEXT
);

