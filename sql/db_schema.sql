DROP TABLE IF EXISTS averagesale;
DROP TABLE IF EXISTS sale;
DROP TABLE IF EXISTS phone;

CREATE TABLE phone(
  id INT UNSIGNED AUTO_INCREMENT,
  model VARCHAR(30) NOT NULL,
  brand VARCHAR(30) NOT NULL,
  cond ENUM("n/a", "New", "New other", "Manufacturer refurbished", "Seller refurbished", "Used", "For parts") NOT NULL,
  carrier VARCHAR(30) NOT NULL,
  storage_capacity VARCHAR(10),
  color VARCHAR(20),
  PRIMARY KEY (id),
  UNIQUE(model, brand, cond, carrier, storage_capacity, color)
);

CREATE TABLE averagesale(
  id INT UNSIGNED,
  price FLOAT(6,2) NOT NULL,
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (id) REFERENCES phone(id) ON DELETE CASCADE,
  INDEX(id),
  INDEX(timestamp)
);

CREATE TABLE sale(
  id INT UNSIGNED,
  price FLOAT(6,2) NOT NULL,
  date DATE NOT NULL,
  FOREIGN KEY (id) REFERENCES phone(id) ON DELETE CASCADE,
  INDEX(id),
  INDEX(date)
);
