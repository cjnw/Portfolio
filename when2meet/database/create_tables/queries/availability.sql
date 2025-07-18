-- name: set_availability
INSERT INTO availability (event_id, user_id, date, time_slot, status)
VALUES (?, ?, ?, ?, ?)
ON CONFLICT(event_id, user_id, date, time_slot)
DO UPDATE SET status = excluded.status, updated_at = CURRENT_TIMESTAMP;

-- name: get_event_availability
SELECT a.*, u.email
FROM availability a
JOIN users u ON a.user_id = u.id
WHERE a.event_id = ?
ORDER BY a.date, a.time_slot;

-- name: get_best_time
SELECT date, time_slot,
       COUNT(CASE WHEN status = 'available' THEN 1 END) as available_count,
       COUNT(CASE WHEN status = 'unavailable' THEN 1 END) as unavailable_count
FROM availability
WHERE event_id = ?
GROUP BY date, time_slot
ORDER BY available_count DESC, unavailable_count ASC
LIMIT 1;
