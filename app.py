import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

def make_embed_url(url):
    if 'watch?v=' in url:
        video_id = url.split('watch?v=')[1].split('&')[0]
        return f'https://www.youtube.com/embed/{video_id}'
    elif 'youtu.be/' in url:
        video_id = url.split('youtu.be/')[1].split('?')[0]
        return f'https://www.youtube.com/embed/{video_id}'
    return url

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row 
    conn.execute('PRAGMA foreign_keys = ON')
    return conn

# Главная страница
@app.route('/')
def home():
    conn = get_db_connection()
    movies = conn.execute('SELECT * FROM movies').fetchall()
    conn.close()
    return render_template('index.html', movies=movies)

# НОВЫЙ МАРШРУТ: Страница отдельного фильма
@app.route('/movie/<int:id>')
def movie_detail(id):
    conn = get_db_connection()
    # Берем сам фильм
    movie = conn.execute('SELECT * FROM movies WHERE id = ?', (id,)).fetchone()
    # Берем всех актеров, привязанных к этому фильму
    actors = conn.execute('SELECT * FROM actors WHERE movie_id = ?', (id,)).fetchall()
    conn.close()
    
    if movie is None:
        return "Фильм не найден", 404
        
    return render_template('movie_detail.html', movie=movie, actors=actors)

# Добавление фильма и его актеров
@app.route('/add', methods=('GET', 'POST'))
def add_movie():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        video_url = make_embed_url(request.form['video_url'])
        poster_url = request.form['poster_url']
        rating = request.form['rating']
        genre = request.form['genre']

        conn = get_db_connection()
        cursor = conn.execute('INSERT INTO movies (title, description, video_url, poster_url, rating, genre) VALUES (?, ?, ?, ?, ?, ?)',
                     (title, description, video_url, poster_url, rating, genre))
        movie_id = cursor.lastrowid # Получаем ID созданного фильма

        # Сохраняем трех актеров из формы
        for i in range(1, 4):
            actor_name = request.form.get(f'actor{i}_name')
            actor_photo = request.form.get(f'actor{i}_photo')
            if actor_name and actor_photo: # Если поля заполнены
                conn.execute('INSERT INTO actors (movie_id, name, photo_url) VALUES (?, ?, ?)', 
                             (movie_id, actor_name, actor_photo))

        conn.commit()
        conn.close()
        return redirect(url_for('home'))

    return render_template('add_movie.html')

# Редактирование фильма и актеров
@app.route('/edit/<int:id>', methods=('GET', 'POST'))
def edit_movie(id):
    conn = get_db_connection()
    movie = conn.execute('SELECT * FROM movies WHERE id = ?', (id,)).fetchone()
    # Получаем текущих актеров для предзаполнения формы
    actors = conn.execute('SELECT * FROM actors WHERE movie_id = ?', (id,)).fetchall()

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        video_url = make_embed_url(request.form['video_url'])
        poster_url = request.form['poster_url']
        rating = request.form['rating']
        genre = request.form['genre']

        # Обновляем инфо о фильме
        conn.execute('UPDATE movies SET title = ?, description = ?, video_url = ?, poster_url = ?, rating = ?, genre = ? WHERE id = ?',
                     (title, description, video_url, poster_url, rating, genre, id))
        
        # Перезаписываем актеров: проще сначала удалить старых, а потом вставить новых
        conn.execute('DELETE FROM actors WHERE movie_id = ?', (id,))
        for i in range(1, 4):
            actor_name = request.form.get(f'actor{i}_name')
            actor_photo = request.form.get(f'actor{i}_photo')
            if actor_name and actor_photo:
                conn.execute('INSERT INTO actors (movie_id, name, photo_url) VALUES (?, ?, ?)', 
                             (id, actor_name, actor_photo))

        conn.commit()
        conn.close()
        return redirect(url_for('movie_detail', id=id))

    conn.close()
    return render_template('edit_movie.html', movie=movie, actors=actors)

@app.route('/delete/<int:id>', methods=('POST',))
def delete_movie(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM movies WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)