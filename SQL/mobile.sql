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
    iphone_price int,
    iphone_imei int,
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


CREATE TABLE company_settings (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(255),
  address TEXT,
  phone VARCHAR(50),
  email VARCHAR(100),
  terms TEXT
);

CREATE TABLE bill_header (
  bill_id INT PRIMARY KEY AUTO_INCREMENT,
  customer_name VARCHAR(255),
  customer_mobile VARCHAR(50),
  customer_contact VARCHAR(100),
  customer_address TEXT,
  bill_date DATETIME DEFAULT CURRENT_TIMESTAMP,
  subtotal DECIMAL(12,2),
  discount DECIMAL(12,2) DEFAULT 0,
  tax DECIMAL(12,2) DEFAULT 0,
  net_total DECIMAL(12,2),
  payment_status VARCHAR(20) DEFAULT 'Unpaid'
);


CREATE TABLE bill_detail (
  detail_id INT PRIMARY KEY AUTO_INCREMENT,
  bill_id INT,
  product_name VARCHAR(255),
  price DECIMAL(12,2),
  quantity DECIMAL(12,3),
  imei int,
  serial_number VARCHAR(100),
  storage varchar(100),
  line_total DECIMAL(12,2)
);


