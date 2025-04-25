-- name: create_user
INSERT INTO users (email, password_hash)
VALUES (?, ?); 