-- Archivo para actualizar la contraseña del admin
UPDATE usuarios 
SET password_hash = '$2b$12$KlzXEK2MHcnQTQnMnQT/ZOwOFwXFCVSy5lJ5hVReuHj1J3MPQKtKa'
WHERE email = 'admin@legalassista.com'; 