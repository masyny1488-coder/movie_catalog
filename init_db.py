import sqlite3

connection = sqlite3.connect('database.db')
cursor = connection.cursor()

# Удаляем старые таблицы, если они были
cursor.execute('DROP TABLE IF EXISTS actors')
cursor.execute('DROP TABLE IF EXISTS movies')

# 1. Создаем таблицу фильмов
cursor.execute('''
CREATE TABLE movies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    video_url TEXT NOT NULL,
    poster_url TEXT NOT NULL,
    rating REAL NOT NULL,
    genre TEXT NOT NULL
)
''')

# 2. Создаем таблицу актеров, привязанную к фильму
cursor.execute('''
CREATE TABLE actors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    movie_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    photo_url TEXT NOT NULL,
    FOREIGN KEY (movie_id) REFERENCES movies (id) ON DELETE CASCADE
)
''')

# Добавляем фильм "Интерстеллар" для теста
cursor.execute('INSERT INTO movies (title, description, video_url, poster_url, rating, genre) VALUES (?, ?, ?, ?, ?, ?)',
               ('Интерстеллар', 
                'Группа исследователей отправляется в путешествие сквозь червоточину, чтобы найти пригодную для жизни планету.', 
                'https://www.youtube.com/embed/zSWdZVtXT7E',
                'https://upload.wikimedia.org/wikipedia/ru/c/c3/Interstellar_film_poster.jpg',
                8.6,
                'Фantasтика, Драма'))

# Получаем ID только что добавленного фильма
movie_id = cursor.lastrowid

# Добавляем актеров для Интерстеллара
actors = [
    (movie_id, 'Мэттью Макконахи', 'https://upload.wikimedia.org/wikipedia/commons/b/bf/Matthew_McConaughey_2019_2.jpg'),
    (movie_id, 'Энн Хэтэуэй', 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b2/Anne_Hathaway_at_Berlinale_2023_03.jpg/440px-Anne_Hathaway_at_Berlinale_2023_03.jpg'),
    (movie_id, 'Джессика Честейн', 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/25/Jessica_Chastain_San_Sebastian_International_Film_Festival_2021.jpg/440px-Jessica_Chastain_San_Sebastian_International_Film_Festival_2021.jpg')
]

cursor.executemany('INSERT INTO actors (movie_id, name, photo_url) VALUES (?, ?, ?)', actors)

connection.commit()
connection.close()

print("База данных успешно пересоздана! Связь 'Фильмы -> Актеры' настроена.")