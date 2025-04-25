SELECT * FROM events 
WHERE creator_id = ? 
ORDER BY id DESC 
LIMIT 1; 