-- name: create_event
INSERT INTO events (name, creator_id, start_date, end_date, start_time, end_time)
VALUES (?, ?, ?, ?, ?, ?);

-- name: get_event_by_id
SELECT * FROM events WHERE id = ?;

-- name: get_user_created_events
SELECT e.*, COUNT(ei.id) as participant_count
FROM events e
LEFT JOIN event_invites ei ON e.id = ei.event_id
WHERE e.creator_id = ?
GROUP BY e.id
ORDER BY e.start_date DESC;

-- name: get_user_invited_events
SELECT e.*, u.email as creator_email, ei.status as invite_status
FROM events e
JOIN event_invites ei ON e.id = ei.event_id
JOIN users u ON e.creator_id = u.id
WHERE ei.user_id = ?
ORDER BY e.start_date DESC;

-- name: create_event_invite
INSERT INTO event_invites (event_id, user_id) VALUES (?, ?);

-- name: update_invite_status
UPDATE event_invites SET status = ? WHERE event_id = ? AND user_id = ?;

-- name: get_invite
SELECT ei.*, u.email as user_email
FROM event_invites ei
JOIN users u ON ei.user_id = u.id
WHERE ei.event_id = ? AND ei.user_id = ?;
