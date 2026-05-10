from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    # Ensure parks table exists
    parks_exists = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='parks'").fetchone()
    if not parks_exists:
        conn.execute('''
            CREATE TABLE parks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                latitude REAL,
                longitude REAL
            )
        ''')
        
    conn.execute('''
        CREATE TABLE IF NOT EXISTS rollercoasters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            park_name TEXT,
            park_id INTEGER,
            height REAL NOT NULL,
            rating INTEGER NOT NULL,
            FOREIGN KEY (park_id) REFERENCES parks (id)
        )
    ''')
    
    # Check if we need to migrate from park_name to park_id
    columns = [info['name'] for info in conn.execute('PRAGMA table_info(rollercoasters)').fetchall()]
    if 'park_name' in columns:
        if 'park_id' not in columns:
            conn.execute('ALTER TABLE rollercoasters ADD COLUMN park_id INTEGER')
            
        existing_coasters = conn.execute('SELECT id, park_name FROM rollercoasters').fetchall()
        for coaster in existing_coasters:
            if coaster['park_name']:
                conn.execute('INSERT OR IGNORE INTO parks (name, latitude, longitude) VALUES (?, ?, ?)', (coaster['park_name'], 0.0, 0.0))
                park_id = conn.execute('SELECT id FROM parks WHERE name = ?', (coaster['park_name'],)).fetchone()
                if park_id:
                    conn.execute('UPDATE rollercoasters SET park_id = ? WHERE id = ?', (park_id['id'], coaster['id']))
    
    conn.commit()
    conn.close()

# --- Rollercoaster Routes ---
@app.route('/')
def index():
    conn = get_db_connection()
    query = '''
        SELECT r.id, r.name, r.height, r.rating, p.name as park_name 
        FROM rollercoasters r 
        LEFT JOIN parks p ON r.park_id = p.id 
        ORDER BY r.id DESC
    '''
    rollercoasters = conn.execute(query).fetchall()
    
    stats = conn.execute('''
        SELECT 
            COUNT(r.id) as total_coasters,
            ROUND(AVG(r.rating), 1) as avg_rating,
            MAX(r.height) as tallest_height,
            COUNT(DISTINCT r.park_id) as unique_parks
        FROM rollercoasters r
    ''').fetchone()
    
    conn.close()
    return render_template('index.html', rollercoasters=rollercoasters, stats=stats)

@app.route('/add', methods=('GET', 'POST'))
def add():
    conn = get_db_connection()
    if request.method == 'POST':
        name = request.form['name']
        park_id = request.form['park_id']
        height = request.form['height']
        rating = request.form['rating']

        if name and park_id and height and rating:
            conn.execute('INSERT INTO rollercoasters (name, park_id, height, rating, park_name) VALUES (?, ?, ?, ?, ?)',
                         (name, park_id, height, rating, ''))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    parks = conn.execute('SELECT * FROM parks ORDER BY name').fetchall()
    conn.close()
    return render_template('add.html', parks=parks)

@app.route('/edit/<int:id>', methods=('GET', 'POST'))
def edit(id):
    conn = get_db_connection()
    coaster = conn.execute('SELECT * FROM rollercoasters WHERE id = ?', (id,)).fetchone()

    if request.method == 'POST':
        name = request.form['name']
        park_id = request.form['park_id']
        height = request.form['height']
        rating = request.form['rating']

        if name and park_id and height and rating:
            conn.execute('UPDATE rollercoasters SET name = ?, park_id = ?, height = ?, rating = ?, park_name = ? WHERE id = ?',
                         (name, park_id, height, rating, '', id))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    parks = conn.execute('SELECT * FROM parks ORDER BY name').fetchall()
    conn.close()
    return render_template('edit.html', coaster=coaster, parks=parks)

@app.route('/delete/<int:id>', methods=('POST',))
def delete(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM rollercoasters WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/coaster/<int:id>')
def coaster(id):
    conn = get_db_connection()
    query = '''
        SELECT r.*, p.name as park_name, p.latitude, p.longitude 
        FROM rollercoasters r 
        LEFT JOIN parks p ON r.park_id = p.id 
        WHERE r.id = ?
    '''
    coaster = conn.execute(query, (id,)).fetchone()
    conn.close()
    return render_template('coaster.html', coaster=coaster)


# --- Parks Management Routes ---
@app.route('/parks')
def parks():
    conn = get_db_connection()
    parks = conn.execute('SELECT * FROM parks ORDER BY name').fetchall()
    conn.close()
    return render_template('parks.html', parks=parks)

@app.route('/parks/<int:id>')
def park_detail(id):
    conn = get_db_connection()
    park = conn.execute('SELECT * FROM parks WHERE id = ?', (id,)).fetchone()
    coasters = conn.execute('SELECT * FROM rollercoasters WHERE park_id = ? ORDER BY rating DESC', (id,)).fetchall()
    stats = conn.execute('''
        SELECT COUNT(id) as total, ROUND(AVG(rating), 1) as avg_rating, MAX(height) as tallest
        FROM rollercoasters WHERE park_id = ?
    ''', (id,)).fetchone()
    conn.close()
    return render_template('park_detail.html', park=park, coasters=coasters, stats=stats)

@app.route('/parks/add', methods=('GET', 'POST'))
def park_add():
    if request.method == 'POST':
        name = request.form['name']
        latitude = request.form['latitude'] or 0.0
        longitude = request.form['longitude'] or 0.0

        if name:
            conn = get_db_connection()
            try:
                conn.execute('INSERT INTO parks (name, latitude, longitude) VALUES (?, ?, ?)',
                             (name, latitude, longitude))
                conn.commit()
            except sqlite3.IntegrityError:
                pass # Park already exists
            conn.close()
            return redirect(url_for('parks'))
            
    return render_template('park_add.html')

@app.route('/parks/edit/<int:id>', methods=('GET', 'POST'))
def park_edit(id):
    conn = get_db_connection()
    park = conn.execute('SELECT * FROM parks WHERE id = ?', (id,)).fetchone()

    if request.method == 'POST':
        name = request.form['name']
        latitude = request.form['latitude'] or 0.0
        longitude = request.form['longitude'] or 0.0

        if name:
            conn.execute('UPDATE parks SET name = ?, latitude = ?, longitude = ? WHERE id = ?',
                         (name, latitude, longitude, id))
            conn.commit()
            conn.close()
            return redirect(url_for('parks'))

    conn.close()
    return render_template('park_edit.html', park=park)

@app.route('/parks/delete/<int:id>', methods=('POST',))
def park_delete(id):
    conn = get_db_connection()
    # Check if there are coasters in this park
    coasters = conn.execute('SELECT count(id) as count FROM rollercoasters WHERE park_id = ?', (id,)).fetchone()
    if coasters['count'] == 0:
        conn.execute('DELETE FROM parks WHERE id = ?', (id,))
        conn.commit()
    conn.close()
    return redirect(url_for('parks'))

@app.route('/map')
def global_map():
    import json
    conn = get_db_connection()
    query = '''
        SELECT p.name, p.latitude, p.longitude, COUNT(r.id) as coaster_count
        FROM parks p
        LEFT JOIN rollercoasters r ON p.id = r.park_id
        WHERE p.latitude != 0 AND p.longitude != 0 AND p.latitude IS NOT NULL AND p.longitude IS NOT NULL
        GROUP BY p.id
    '''
    parks_data = conn.execute(query).fetchall()
    conn.close()
    
    parks_list = [{'name': p['name'], 'lat': p['latitude'], 'lon': p['longitude'], 'count': p['coaster_count']} for p in parks_data]
    return render_template('map.html', parks_json=json.dumps(parks_list))

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
