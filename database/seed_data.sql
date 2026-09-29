-- WordSprint Seed Data (Words & Default Admin User)

-- 20 5-letter uppercase English words
INSERT INTO words (word) VALUES 
('APPLE'), 
('BRAIN'), 
('CHAIR'), 
('DREAM'), 
('EARTH'),
('FLAME'), 
('GRAPE'), 
('HEART'), 
('IMAGE'), 
('JUICE'),
('KNIFE'), 
('LIGHT'), 
('MUSIC'), 
('NIGHT'), 
('OCEAN'),
('PLANT'), 
('QUEEN'), 
('RIGHT'), 
('SMILE'), 
('TRAIN')
ON CONFLICT (word) DO NOTHING;

-- Default Admin User (username: admin, password: admin123)
INSERT INTO users (uname, pwd_hash, role) 
VALUES ('admin', '$2b$12$WrYrn08JnXmqA6MMxGRXI.57U8eEIscdFkmVF7/abnMnmPEddbtXW', 'admin')
ON CONFLICT (uname) DO NOTHING;
