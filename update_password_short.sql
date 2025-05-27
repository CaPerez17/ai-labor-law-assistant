-- Archivo para actualizar la contraseña del admin con un hash más corto
UPDATE usuarios 
SET password_hash = '$2b$04$.F1WiI7XCewCBThXeI58EuV2q9Jevuyn5V7ljkjRI.DKAh9njaSi6'
WHERE email = 'admin@legalassista.com'; 