CREATE TABLE IF NOT EXISTS phone(
  id INT UNSIGNED AUTO_INCREMENT,
  model VARCHAR(30),
  brand VARCHAR(30),
  size VARCHAR(10),
  carrier VARCHAR(30),
  cond ENUM("Used", "New", "New other", "For parts"),
  PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS averagesale(
  id INT UNSIGNED,
  price FLOAT(6,2),
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (id) REFERENCES phone(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS sale(
  id INT UNSIGNED,
  price FLOAT(6,2),
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (id) REFERENCES phone(id) ON DELETE CASCADE
);