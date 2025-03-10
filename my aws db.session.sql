ALTER TABLE cart
ADD CONSTRAINT fk_cart_login_id
FOREIGN KEY (cart_login_id) REFERENCES login(login_id);