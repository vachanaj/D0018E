CREATE TABLE reviews (
    review_id INT AUTO_INCREMENT PRIMARY KEY,
    review_login_id INT,
    review_asset_id INT,
    review_asset_rating INT,
    review_asset_comments TEXT,
    FOREIGN KEY (review_login_id) REFERENCES login(login_id), 
    FOREIGN KEY (review_asset_id) REFERENCES assets(assets_id) 
);

ALTER TABLE reviews
ADD COLUMN parent_review_id INT NULL,  -- Allows replies by linking to another review
ADD COLUMN author_role ENUM('customer', 'admin') NOT NULL DEFAULT 'customer',  -- Specifies whether the review is from a user or admin
ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Stores the timestamp of the review
ADD FOREIGN KEY (parent_review_id) REFERENCES reviews(review_id);  -- Links replies to original reviews




