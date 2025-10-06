import sqlite3
import csv
import os
import math
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "db" / "openflights.db"

def create_connection():
    conn = sqlite3.connect(str(DB_PATH))
    return conn

def create_tables(conn):
    cursor = conn.cursor()
    
    # Airports table with vector support
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS airports (
            airport_id INTEGER PRIMARY KEY,
            name TEXT,
            city TEXT,
            country TEXT,
            iata TEXT,
            icao TEXT,
            latitude REAL,
            longitude REAL,
            altitude INTEGER,
            timezone REAL,
            dst TEXT,
            tz_database TEXT,
            type TEXT,
            source TEXT,
            geohash TEXT,
            vector_x REAL,
            vector_y REAL,
            vector_z REAL
        )
    ''')
    
    # Airlines table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS airlines (
            airline_id INTEGER PRIMARY KEY,
            name TEXT,
            alias TEXT,
            iata TEXT,
            icao TEXT,
            callsign TEXT,
            country TEXT,
            active TEXT
        )
    ''')
    
    # Routes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS routes (
            route_id INTEGER PRIMARY KEY AUTOINCREMENT,
            airline TEXT,
            airline_id INTEGER,
            source_airport TEXT,
            source_airport_id INTEGER,
            dest_airport TEXT,
            dest_airport_id INTEGER,
            codeshare TEXT,
            stops INTEGER,
            equipment TEXT,
            distance REAL
        )
    ''')
    
    # Analytics tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS route_statistics (
            stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
            country TEXT,
            total_routes INTEGER,
            total_airports INTEGER,
            avg_distance REAL,
            busiest_airport TEXT,
            calculation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    print("✓ Tables created successfully")

def calculate_distance(lat1, lon1, lat2, lon2):
    if None in [lat1, lon1, lat2, lon2]:
        return None
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

def lat_lon_to_vector(lat, lon):
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    x = math.cos(lat_rad) * math.cos(lon_rad)
    y = math.cos(lat_rad) * math.sin(lon_rad)
    z = math.sin(lat_rad)
    return x, y, z

def geohash_encode(lat, lon, precision=6):
    base32 = '0123456789bcdefghjkmnpqrstuvwxyz'
    lat_range = [-90.0, 90.0]
    lon_range = [-180.0, 180.0]
    geohash = []
    bits = 0
    bit = 0
    even_bit = True
    
    while len(geohash) < precision:
        if even_bit:
            mid = (lon_range[0] + lon_range[1]) / 2
            if lon > mid:
                bit |= (1 << (4 - bits))
                lon_range[0] = mid
            else:
                lon_range[1] = mid
        else:
            mid = (lat_range[0] + lat_range[1]) / 2
            if lat > mid:
                bit |= (1 << (4 - bits))
                lat_range[0] = mid
            else:
                lat_range[1] = mid
        
        even_bit = not even_bit
        bits += 1
        
        if bits == 5:
            geohash.append(base32[bit])
            bits = 0
            bit = 0
    
    return ''.join(geohash)

def import_airports(conn):
    cursor = conn.cursor()
    airports_file = DATA_DIR / "raw" / "airports.dat"
    
    with open(airports_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        count = 0
        for row in reader:
            try:
                airport_id = int(row[0]) if row[0] != '\\N' else None
                name = row[1] if row[1] != '\\N' else None
                city = row[2] if row[2] != '\\N' else None
                country = row[3] if row[3] != '\\N' else None
                iata = row[4] if row[4] != '\\N' else None
                icao = row[5] if row[5] != '\\N' else None
                lat = float(row[6]) if row[6] != '\\N' else None
                lon = float(row[7]) if row[7] != '\\N' else None
                altitude = int(row[8]) if row[8] != '\\N' else None
                timezone = float(row[9]) if row[9] != '\\N' else None
                dst = row[10] if row[10] != '\\N' else None
                tz = row[11] if row[11] != '\\N' else None
                type_val = row[12] if len(row) > 12 and row[12] != '\\N' else 'airport'
                source = row[13] if len(row) > 13 and row[13] != '\\N' else 'OurAirports'
                
                geohash = None
                vec_x, vec_y, vec_z = None, None, None
                
                if lat is not None and lon is not None:
                    geohash = geohash_encode(lat, lon)
                    vec_x, vec_y, vec_z = lat_lon_to_vector(lat, lon)
                
                cursor.execute('''
                    INSERT INTO airports VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (airport_id, name, city, country, iata, icao, lat, lon, altitude, 
                      timezone, dst, tz, type_val, source, geohash, vec_x, vec_y, vec_z))
                count += 1
            except Exception as e:
                pass
    
    conn.commit()
    print(f"✓ Imported {count} airports")

def import_airlines(conn):
    cursor = conn.cursor()
    airlines_file = DATA_DIR / "raw" / "airlines.dat"
    
    with open(airlines_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        count = 0
        for row in reader:
            try:
                airline_id = int(row[0]) if row[0] != '\\N' else None
                name = row[1] if row[1] != '\\N' else None
                alias = row[2] if row[2] != '\\N' else None
                iata = row[3] if row[3] != '\\N' else None
                icao = row[4] if row[4] != '\\N' else None
                callsign = row[5] if row[5] != '\\N' else None
                country = row[6] if row[6] != '\\N' else None
                active = row[7] if row[7] != '\\N' else 'Y'
                
                cursor.execute('''
                    INSERT INTO airlines VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (airline_id, name, alias, iata, icao, callsign, country, active))
                count += 1
            except Exception as e:
                pass
    
    conn.commit()
    print(f"✓ Imported {count} airlines")

def import_routes(conn):
    cursor = conn.cursor()
    routes_file = DATA_DIR / "raw" / "routes.dat"
    
    # Get airport coordinates for distance calculation
    cursor.execute('SELECT airport_id, latitude, longitude FROM airports')
    airport_coords = {row[0]: (row[1], row[2]) for row in cursor.fetchall()}
    
    with open(routes_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        count = 0
        for row in reader:
            try:
                airline = row[0] if row[0] != '\\N' else None
                airline_id = int(row[1]) if row[1] != '\\N' else None
                src_airport = row[2] if row[2] != '\\N' else None
                src_id = int(row[3]) if row[3] != '\\N' else None
                dest_airport = row[4] if row[4] != '\\N' else None
                dest_id = int(row[5]) if row[5] != '\\N' else None
                codeshare = row[6] if row[6] != '\\N' else None
                stops = int(row[7]) if row[7] != '\\N' else 0
                equipment = row[8] if row[8] != '\\N' else None
                
                distance = None
                if src_id in airport_coords and dest_id in airport_coords:
                    src_coords = airport_coords[src_id]
                    dest_coords = airport_coords[dest_id]
                    if all(coord is not None for coord in src_coords + dest_coords):
                        distance = calculate_distance(*src_coords, *dest_coords)
                
                cursor.execute('''
                    INSERT INTO routes (airline, airline_id, source_airport, source_airport_id,
                                      dest_airport, dest_airport_id, codeshare, stops, equipment, distance)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (airline, airline_id, src_airport, src_id, dest_airport, dest_id, 
                      codeshare, stops, equipment, distance))
                count += 1
            except Exception as e:
                pass
    
    conn.commit()
    print(f"✓ Imported {count} routes")

def generate_statistics(conn):
    cursor = conn.cursor()
    print("Generating statistics (this may take a moment)...")
    
    # Simplified and faster query
    cursor.execute('''
        INSERT INTO route_statistics (country, total_routes, total_airports, avg_distance, busiest_airport)
        SELECT 
            a.country,
            COUNT(DISTINCT r.route_id) as total_routes,
            COUNT(DISTINCT a.airport_id) as total_airports,
            ROUND(AVG(r.distance), 2) as avg_distance,
            'Calculating...' as busiest_airport
        FROM airports a
        LEFT JOIN routes r ON a.airport_id = r.source_airport_id
        WHERE a.country IS NOT NULL AND a.country != ''
        GROUP BY a.country
        HAVING total_routes > 0
        ORDER BY total_routes DESC
        LIMIT 50
    ''')
    
    conn.commit()
    print("✓ Generated route statistics for top 50 countries")

def main():
    print("Starting database setup...")
    conn = create_connection()
    create_tables(conn)
    import_airports(conn)
    import_airlines(conn)
    import_routes(conn)
    generate_statistics(conn)
    conn.close()
    print("\n✓ Database setup completed successfully!")

if __name__ == "__main__":
    main()
