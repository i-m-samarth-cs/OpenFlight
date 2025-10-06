# OpenFlights Advanced MariaDB Database Platform

## 🚀 Features

This platform demonstrates advanced database concepts using the OpenFlights dataset:

### 1. **High Availability (Simulated Galera Cluster)**
- Multi-node database architecture simulation
- Fault-tolerant design principles
- Load balancing concepts

### 2. **ColumnStore Analytics**
- Optimized analytical queries
- Fast aggregations on large datasets
- Country-level route statistics
- Performance metrics

### 3. **Vector Search**
- Geospatial similarity search
- 3D vector representations of coordinates
- Find airports in similar geographic locations
- Cosine similarity calculations

### 4. **Geohash Indexing**
- Efficient spatial indexing
- Quick proximity searches
- Geographic clustering

## 📊 Database Schema

### Airports Table
- Airport details with geolocation
- Vector representations (x, y, z)
- Geohash encoding for spatial queries

### Airlines Table
- Airline information
- Active/inactive status
- IATA/ICAO codes

### Routes Table
- Flight route connections
- Distance calculations
- Equipment information

### Route Statistics Table
- Country-level analytics
- Pre-computed aggregations
- Performance optimization

## 🌐 Web Interface

The platform includes a beautiful, modern web interface with:

- **Real-time Statistics Dashboard**
  - Total airports, airlines, and routes
  - Average route distances
  
- **Airport Search**
  - Full-text search across multiple fields
  - IATA/ICAO code lookup
  - Geographic coordinates display

- **Flight Routes Explorer**
  - Longest routes visualization
  - Distance calculations
  - Route details

- **Country Analytics**
  - Top countries by routes
  - Average distances per country
  - Busiest airports

- **Vector Similarity Search**
  - Find geographically similar airports
  - Similarity scoring
  - Visual comparison

## 🎯 Usage

### Starting the Application

**Windows:**
```bash
# Double-click start.bat OR run:
start.bat
```

**Linux/Mac:**
```bash
./start.sh
```

### Accessing the Interface

Open your browser and navigate to:
```
http://localhost:8080
```

### API Endpoints

- `GET /api/stats` - Database statistics
- `GET /api/airports?limit=N&search=TERM` - Search airports
- `GET /api/routes?limit=N` - Get flight routes
- `GET /api/analytics/country` - Country-level statistics
- `GET /api/vector/similar/:id` - Find similar airports
- `GET /api/search/geohash/:hash` - Geohash proximity search

## 🔧 Technical Details

### Vector Search Algorithm

The platform uses 3D vector representation for geospatial similarity:

1. Convert latitude/longitude to 3D coordinates (x, y, z)
2. Calculate cosine similarity between vectors
3. Rank airports by similarity score

### Distance Calculation

Uses the Haversine formula for great-circle distances:
```
distance = 2 * R * arcsin(sqrt(sin²(Δlat/2) + cos(lat1) * cos(lat2) * sin²(Δlon/2)))
```

### Geohash Encoding

Implements geohash for efficient spatial indexing:
- Variable precision (default: 6 characters)
- Hierarchical geographic clustering
- Fast proximity searches

## 📈 Performance Features

1. **Indexing Strategy**
   - Primary keys on all tables
   - Spatial indexes (geohash)
   - Vector columns for similarity

2. **Query Optimization**
   - Pre-computed statistics
   - Limited result sets
   - Efficient JOIN operations

3. **Caching**
   - In-memory data structures
   - Reduced database calls
   - Fast response times

## 🔮 Future Enhancements

- Real-time flight data integration
- Interactive map visualization
- Advanced route planning algorithms
- Multi-node cluster deployment
- Real-time analytics dashboard
- Machine learning predictions

## 📚 Dataset

Data source: [OpenFlights](https://openflights.org/data.html)

- **Airports**: 7,698+ airports worldwide
- **Airlines**: 6,000+ airlines
- **Routes**: 67,000+ flight routes

## 🛠️ Technology Stack

- **Database**: SQLite (MariaDB simulation)
- **Backend**: Python Flask
- **Frontend**: HTML5, CSS3, JavaScript
- **Data Processing**: Python CSV, Math libraries

## 📝 License

This project uses data from OpenFlights, which is made available under the Open Database License.

---

**Built with ❤️ for learning advanced database concepts**
