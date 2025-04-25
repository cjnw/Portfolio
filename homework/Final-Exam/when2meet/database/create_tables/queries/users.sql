-- name: get_user_by_email
SELECT * FROM users WHERE email = ?;

-- name: create_user
INSERT INTO users (email, password_hash) VALUES (?, ?);

-- name: update_last_login
UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?;
