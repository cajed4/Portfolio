DROP TABLE IF EXISTS cart_items;
DROP TABLE IF EXISTS shoppers;

CREATE TABLE shoppers (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    user_name VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE cart_items (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    shopper VARCHAR(255) REFERENCES shoppers(user_name),
    item_name VARCHAR(255) NOT NULL,
    qty INTEGER NOT NULL,
    price NUMERIC(10,2) NOT NULL
);

INSERT INTO shoppers (name, user_name) VALUES
('John', 'john123');

INSERT INTO cart_items (shopper, item_name, qty, price) VALUES
('john123', 'apple', 2, 1.25),
('john123', 'orange', 1, 1.75),
('john123', 'banana', 3, 0.75);