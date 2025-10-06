from flask import Flask, render_template, jsonify, request
import sqlite3
import json
import math
from pathlib import Path

app = Flask(__name__, 
            template_folder='../web/templates',
            static_folder='../web/static')

BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / "data" / "db" / "openflights.db"

def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def calculate_vector_similarity(v1, v2):
    if None in v1 or None in v2:
        return 0
    dot_product = sum(a * b for a, b in zip(v1, v2))
    mag1 = math.sqrt(sum(a * a for a in v1))
    mag2 = math.sqrt(sum(b * b for b in v2))
    if mag1 == 0 or mag2 == 0:
        return 0
    return dot_product / (mag1 * mag2)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stats')
def get_stats():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM airports')
    total_airports = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM airlines')
    total_airlines = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM routes')
    total_routes = cursor.fetchone()[0]
    
    cursor.execute('SELECT AVG(distance) FROM routes WHERE distance IS NOT NULL')
    avg_distance = cursor.fetchone()[0]
    
    conn.close()
    
    return jsonify({
        'total_airports': total_airports,
        'total_airlines': total_airlines,
        'total_routes': total_routes,
        'avg_distance': round(avg_distance, 2) if avg_distance else 0
    })

@app.route('/api/airports')
def get_airports():
    conn = get_db()
    cursor = conn.cursor()
    
    limit = request.args.get('limit', 100, type=int)
    search = request.args.get('search', '')
    
    if search:
        cursor.execute('''
            SELECT airport_id, name, city, country, iata, icao, latitude, longitude
            FROM airports
            WHERE name LIKE ? OR city LIKE ? OR country LIKE ? OR iata LIKE ?
            LIMIT ?
        ''', (f'%{search}%', f'%{search}%', f'%{search}%', f'%{search}%', limit))
    else:
        cursor.execute('''
            SELECT airport_id, name, city, country, iata, icao, latitude, longitude
            FROM airports
            LIMIT ?
        ''', (limit,))
    
    airports = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify(airports)

@app.route('/api/routes')
def get_routes():
    conn = get_db()
    cursor = conn.cursor()
    
    limit = request.args.get('limit', 100, type=int)
    
    cursor.execute('''
        SELECT r.*, 
               a1.name as source_name, a1.city as source_city, a1.country as source_country,
               a2.name as dest_name, a2.city as dest_city, a2.country as dest_country
        FROM routes r
        LEFT JOIN airports a1 ON r.source_airport_id = a1.airport_id
        LEFT JOIN airports a2 ON r.dest_airport_id = a2.airport_id
        WHERE r.distance IS NOT NULL
        ORDER BY r.distance DESC
        LIMIT ?
    ''', (limit,))
    
    routes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify(routes)

@app.route('/api/analytics/country')
def get_country_analytics():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT country, total_routes, total_airports, avg_distance, busiest_airport
        FROM route_statistics
        ORDER BY total_routes DESC
        LIMIT 20
    ''')
    
    stats = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify(stats)

@app.route('/api/vector/similar/<int:airport_id>')
def find_similar_airports(airport_id):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT vector_x, vector_y, vector_z, name, latitude, longitude
        FROM airports
        WHERE airport_id = ?
    ''', (airport_id,))
    
    target = cursor.fetchone()
    if not target:
        return jsonify({'error': 'Airport not found'}), 404
    
    target_vector = (target['vector_x'], target['vector_y'], target['vector_z'])
    
    cursor.execute('''
        SELECT airport_id, name, city, country, iata, latitude, longitude,
               vector_x, vector_y, vector_z
        FROM airports
        WHERE airport_id != ? AND vector_x IS NOT NULL
    ''', (airport_id,))
    
    similar = []
    for row in cursor.fetchall():
        airport_vector = (row['vector_x'], row['vector_y'], row['vector_z'])
        similarity = calculate_vector_similarity(target_vector, airport_vector)
        
        similar.append({
            'airport_id': row['airport_id'],
            'name': row['name'],
            'city': row['city'],
            'country': row['country'],
            'iata': row['iata'],
            'latitude': row['latitude'],
            'longitude': row['longitude'],
            'similarity': round(similarity, 4)
        })
    
    similar.sort(key=lambda x: x['similarity'], reverse=True)
    conn.close()
    
    return jsonify({
        'target': {
            'name': target['name'],
            'latitude': target['latitude'],
            'longitude': target['longitude']
        },
        'similar_airports': similar[:10]
    })

@app.route('/api/search/geohash/<geohash>')
def search_by_geohash(geohash):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT airport_id, name, city, country, iata, latitude, longitude, geohash
        FROM airports
        WHERE geohash LIKE ?
        LIMIT 50
    ''', (f'{geohash}%',))
    
    airports = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify(airports)

if __name__ == '__main__':
    print("\n" + "="*50)
    print("OpenFlights Database Platform")
    print("="*50)
    print(f"\nWeb Interface: http://localhost:8080")
    print("\nPress Ctrl+C to stop the server\n")
    app.run(host='0.0.0.0', port=8080, debug=True)
