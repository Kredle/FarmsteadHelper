-- Спочатку створюємо таблиці
-- 1. Створюємо таблицю topics (батьківська)
DROP TABLE IF EXISTS topics CASCADE;
CREATE TABLE topics (
    idTopic SERIAL PRIMARY KEY,
    Content TEXT,
    Likes INTEGER DEFAULT NULL,
    Dislikes INTEGER DEFAULT NULL,
    Category VARCHAR(45) DEFAULT NULL,
    Date DATE DEFAULT NULL,
    Time TIME DEFAULT NULL,
    Author TEXT NOT NULL,
    Title TEXT,
    Comments INTEGER DEFAULT NULL,
    Likes_list JSON,
    Dislikes_list JSON
);

-- 2. Створюємо таблицю comments (дочірня)
DROP TABLE IF EXISTS comments CASCADE;
CREATE TABLE comments (
    idComments SERIAL NOT NULL,
    Content TEXT,
    Likes INTEGER DEFAULT NULL,
    Dislikes INTEGER DEFAULT NULL,
    Author TEXT,
    Date DATE DEFAULT NULL,
    Time TIME DEFAULT NULL,
    Topics_idTopic INTEGER NOT NULL,
    Receiver TEXT,
    IsAnswer SMALLINT DEFAULT NULL,
    Comments INTEGER DEFAULT NULL,
    Likes_list JSON,
    Dislikes_list JSON,
    ParentId INTEGER DEFAULT NULL,
    PRIMARY KEY (idComments, Topics_idTopic),
    CONSTRAINT fk_Comments_Topics FOREIGN KEY (Topics_idTopic) REFERENCES topics (idTopic) ON DELETE CASCADE
);

-- Створення індексу для зовнішнього ключа
CREATE INDEX fk_Comments_Topics_idx ON comments (Topics_idTopic);