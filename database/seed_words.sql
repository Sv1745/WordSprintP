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
