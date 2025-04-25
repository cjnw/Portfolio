-- name: get_user_by_email
SELECT * FROM users 
WHERE email = ?; 