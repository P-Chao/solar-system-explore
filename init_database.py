import sqlite3
from datetime import datetime

def init_database():
    """Initialize the solar system database with tables and initial data"""
    
    conn = sqlite3.connect('solar_system.db')
    cursor = conn.cursor()
    
    # Drop existing tables to recreate with new schema
    cursor.execute('DROP TABLE IF EXISTS spacecraft')
    cursor.execute('DROP TABLE IF EXISTS moons')
    cursor.execute('DROP TABLE IF EXISTS planets')
    
    # Create planets table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS planets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            name_en TEXT NOT NULL,
            wikipedia_url TEXT NOT NULL,
            wikipedia_url_en TEXT NOT NULL,
            semi_major_axis REAL NOT NULL,  -- in AU
            eccentricity REAL NOT NULL,
            inclination REAL NOT NULL,      -- in degrees
            orbital_period REAL NOT NULL,   -- in Earth years
            mean_anomaly_0 REAL NOT NULL,  -- mean anomaly at epoch
            perihelion_0 REAL NOT NULL,    -- perihelion at epoch in degrees
            ascending_node_0 REAL NOT NULL, -- ascending node at epoch in degrees
            radius REAL NOT NULL,          -- in km
            mass REAL NOT NULL,             -- in kg
            type TEXT NOT NULL,             -- planet type in Chinese
            type_en TEXT NOT NULL,         -- planet type in English
            rotation_period REAL,          -- in Earth hours
            density REAL,                   -- in g/cm³
            equatorial_radius REAL,         -- in km
            polar_radius REAL,             -- in km
            magnetic_field REAL,           -- in µT (microtesla), NULL if none
            atmospheric_pressure REAL      -- in Pa (Pascals), NULL if no atmosphere
        )
    ''')
    
    # Create moons table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS moons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            name_en TEXT NOT NULL,
            wikipedia_url TEXT NOT NULL,
            wikipedia_url_en TEXT NOT NULL,
            parent_planet_id INTEGER NOT NULL,
            semi_major_axis REAL NOT NULL,
            orbital_period REAL NOT NULL,
            inclination REAL NOT NULL,
            radius REAL NOT NULL,
            mass REAL NOT NULL,
            type TEXT,                      -- moon type in Chinese
            type_en TEXT,                   -- moon type in English
            rotation_period REAL,
            density REAL,
            surface_temperature REAL,
            atmosphere TEXT,                -- atmosphere description in Chinese
            atmosphere_en TEXT,             -- atmosphere description in English
            atmospheric_pressure REAL,      -- in Pa (Pascals), NULL if no atmosphere
            magnetic_field REAL
        )
    ''')
    
    # Create spacecraft table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS spacecraft (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            name_en TEXT NOT NULL,
            wikipedia_url TEXT NOT NULL,
            wikipedia_url_en TEXT NOT NULL,
            launch_date TEXT NOT NULL,      -- YYYY-MM-DD format
            target_body TEXT,               -- target planet/body
            status TEXT NOT NULL,           -- 'active' or 'inactive'
            trajectory_type TEXT NOT NULL,  -- e.g., 'flyby', 'orbiter', 'lander', 'rover'
            launch_speed REAL,              -- relative to Earth in km/s
            current_phase TEXT,             -- current mission phase
            arrival_time TEXT,              -- arrival time or expected arrival time (YYYY-MM-DD format)
            last_update TEXT                -- timestamp of last status update
        )
    ''')
    
    # Insert planet data with comprehensive information
    planets_data = [
        ('水星', 'Mercury', 'https://zh.wikipedia.org/wiki/%E6%B0%B4%E6%98%9F', 'https://en.wikipedia.org/wiki/Mercury_(planet)',
         0.387098, 0.205630, 7.005, 0.240846, 174.796, 29.124, 48.331, 2439.7, 3.3011e23,
         '类地行星', 'Terrestrial Planet', 1407.6, 5.427, 2439.7, 2439.7, 0.011, None),  # No significant atmosphere
        ('金星', 'Venus', 'https://zh.wikipedia.org/wiki/%E9%87%91%E6%98%9F', 'https://en.wikipedia.org/wiki/Venus',
         0.723332, 0.006772, 3.39458, 0.615198, 50.115, 76.680, 131.533, 6051.8, 4.8675e24,
         '类地行星', 'Terrestrial Planet', 5832.5, 5.243, 6051.8, 6051.8, None, 9.2e6),  # 9.2 MPa at surface
        ('地球', 'Earth', 'https://zh.wikipedia.org/wiki/%E5%9C%B0%E7%90%83', 'https://en.wikipedia.org/wiki/Earth',
         1.000000, 0.0167086, 0.00005, 1.000017, 358.617, 102.947, 0.0, 6371.0, 5.97237e24,
         '类地行星', 'Terrestrial Planet', 23.9345, 5.514, 6378.1, 6356.8, 31.0, 101325),  # 1 atm = 101325 Pa
        ('火星', 'Mars', 'https://zh.wikipedia.org/wiki/%E7%81%AB%E6%98%9F', 'https://en.wikipedia.org/wiki/Mars',
         1.523679, 0.0934123, 1.85061, 1.8808158, 19.412, 336.040, 49.578, 3389.5, 6.4171e23,
         '类地行星', 'Terrestrial Planet', 24.6229, 3.933, 3396.2, 3376.2, 0.021, 600),  # ~600 Pa average
        ('木星', 'Jupiter', 'https://zh.wikipedia.org/wiki/%E6%9C%A8%E6%98%9F', 'https://en.wikipedia.org/wiki/Jupiter',
         5.20260, 0.048498, 1.30530, 11.862615, 20.020, 14.753, 100.556, 69911, 1.8982e27,
         '气态巨行星', 'Gas Giant', 9.925, 1.326, 71492, 66854, 417.0, 2e5),  # ~200 kPa at cloud level
        ('土星', 'Saturn', 'https://zh.wikipedia.org/wiki/%E5%9C%9F%E6%98%9F', 'https://en.wikipedia.org/wiki/Saturn',
         9.55491, 0.055546, 2.48446, 29.4571, 317.020, 92.431, 113.715, 58232, 5.6834e26,
         '气态巨行星', 'Gas Giant', 10.656, 0.687, 60268, 54364, 21.8, 1.4e5),  # ~140 kPa at cloud level
        ('天王星', 'Uranus', 'https://zh.wikipedia.org/wiki/%E5%A4%A9%E7%8E%8B%E6%98%9F', 'https://en.wikipedia.org/wiki/Uranus',
         19.2184, 0.047168, 0.772556, 84.0205, 142.590, 170.964, 74.006, 25362, 8.6810e25,
         '冰巨星', 'Ice Giant', 17.24, 1.271, 25559, 24973, 23.0, 1.2e5),  # ~120 kPa at cloud level
        ('海王星', 'Neptune', 'https://zh.wikipedia.org/wiki/%E6%B5%B7%E7%8E%8B%E6%98%9F', 'https://en.wikipedia.org/wiki/Neptune',
         30.0709, 0.008586, 1.76917, 164.7913, 256.228, 44.971, 131.784, 24622, 1.0241e26,
         '冰巨星', 'Ice Giant', 16.11, 1.638, 24764, 24341, 13.0, 1.0e5)  # ~100 kPa at cloud level
    ]
    
    cursor.executemany('''
        INSERT OR REPLACE INTO planets 
        (name, name_en, wikipedia_url, wikipedia_url_en, semi_major_axis, eccentricity, inclination, 
         orbital_period, mean_anomaly_0, perihelion_0, ascending_node_0, radius, mass,
         type, type_en, rotation_period, density, equatorial_radius, polar_radius, magnetic_field, atmospheric_pressure)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', planets_data)
    
    # Insert moon data (major moons)
    # Get planet IDs
    earth_id = cursor.execute('SELECT id FROM planets WHERE name_en = "Earth"').fetchone()[0]
    mars_id = cursor.execute('SELECT id FROM planets WHERE name_en = "Mars"').fetchone()[0]
    jupiter_id = cursor.execute('SELECT id FROM planets WHERE name_en = "Jupiter"').fetchone()[0]
    saturn_id = cursor.execute('SELECT id FROM planets WHERE name_en = "Saturn"').fetchone()[0]
    
    moons_data = [
        ('月球', 'Moon', 'https://zh.wikipedia.org/wiki/%E6%9C%88%E7%90%83', 'https://en.wikipedia.org/wiki/Moon', earth_id,
         384400, 27.321582, 5.145, 1737.4, 7.342e22, '规则卫星', 'Regular Satellite', 655.72, 3.344, 250, '稀薄大气层', 'Exosphere', 1e-9, 120.0),  # ~1 nPa
        ('火卫一', 'Phobos', 'https://zh.wikipedia.org/wiki/%E7%81%AB%E5%8D%AB%E4%B8%80', 'https://en.wikipedia.org/wiki/Phobos_(moon)', mars_id,
         9376, 0.31891023, 1.093, 11.1, 1.0659e16, '不规则卫星', 'Irregular Satellite', 7.66, 1.876, 200, '无大气层', 'No Atmosphere', None, None),
        ('火卫二', 'Deimos', 'https://zh.wikipedia.org/wiki/%E7%81%AB%E5%8D%AB%E4%BA%8C', 'https://en.wikipedia.org/wiki/Deimos_(moon)', mars_id,
         23463, 1.26244, 1.793, 6.2, 1.4762e15, '不规则卫星', 'Irregular Satellite', 30.3, 1.471, 234, '无大气层', 'No Atmosphere', None, None),
        ('木卫一', 'Io', 'https://zh.wikipedia.org/wiki/%E6%9C%A8%E5%8D%AB%E4%B8%80', 'https://en.wikipedia.org/wiki/Io_(moon)', jupiter_id,
         421700, 1.769137786, 0.05, 1821.6, 8.9319e22, '规则卫星', 'Regular Satellite', 42.46, 3.528, 110, '含硫大气层', 'Sulfur-rich Atmosphere', 0.01, 2000.0),  # ~10 mPa
        ('木卫二', 'Europa', 'https://zh.wikipedia.org/wiki/%E6%9C%A8%E5%8D%AB%E4%BA%8C', 'https://en.wikipedia.org/wiki/Europa_(moon)', jupiter_id,
         671100, 3.551181041, 0.47, 1560.8, 4.7998e22, '规则卫星', 'Regular Satellite', 85.23, 3.013, 102, '含氧大气层', 'Oxygen-rich Atmosphere', 1e-6, 240.0),  # ~1 µPa
        ('木卫三', 'Ganymede', 'https://zh.wikipedia.org/wiki/%E6%9C%A8%E5%8D%AB%E4%B8%89', 'https://en.wikipedia.org/wiki/Ganymede_(moon)', jupiter_id,
         1070400, 7.15455296, 0.20, 2634.1, 1.4819e23, '规则卫星', 'Regular Satellite', 171.69, 1.936, 110, '含氧大气层', 'Oxygen-rich Atmosphere', 1e-6, 719.0),  # ~1 µPa
        ('木卫四', 'Callisto', 'https://zh.wikipedia.org/wiki/%E6%9C%A8%E5%8D%AB%E5%9B%9B', 'https://en.wikipedia.org/wiki/Callisto_(moon)', jupiter_id,
         1882700, 16.6890184, 0.192, 2410.3, 1.0759e23, '规则卫星', 'Regular Satellite', 400.54, 1.834, 134, '含氧大气层', 'Oxygen-rich Atmosphere', 1e-9, 417.0),  # ~1 nPa
        ('土卫六', 'Titan', 'https://zh.wikipedia.org/wiki/%E5%9C%9F%E5%8D%AB%E5%85%AD', 'https://en.wikipedia.org/wiki/Titan_(moon)', saturn_id,
         1221870, 15.945, 0.34854, 2574, 1.3452e23, '规则卫星', 'Regular Satellite', 382.68, 1.880, 94, '富含氮大气层', 'Nitrogen-rich Atmosphere', 146700, 21.0),  # 146.7 kPa surface pressure
        ('土卫二', 'Enceladus', 'https://zh.wikipedia.org/wiki/%E5%9C%9F%E5%8D%AB%E4%BA%8C', 'https://en.wikipedia.org/wiki/Enceladus_(moon)', saturn_id,
         238020, 1.370218, 0.009, 252.1, 1.08e20, '规则卫星', 'Regular Satellite', 32.89, 1.609, 75, '水蒸气大气层', 'Water Vapor Atmosphere', 0.01, None)  # ~10 mPa
    ]
    
    cursor.executemany('''
        INSERT OR REPLACE INTO moons 
        (name, name_en, wikipedia_url, wikipedia_url_en, parent_planet_id, semi_major_axis, 
         orbital_period, inclination, radius, mass, type, type_en, rotation_period, density,
         surface_temperature, atmosphere, atmosphere_en, atmospheric_pressure, magnetic_field)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', moons_data)
    
    # Insert spacecraft data (successful missions that left Earth-Moon system)
    current_time = datetime.now().isoformat()
    spacecraft_data = [
        ('旅行者1号', 'Voyager 1', 'https://zh.wikipedia.org/wiki/%E6%97%85%E8%A1%8C%E8%80%85%E5%8F%B7%E6%8E%A2%E6%B5%8B%E5%99%A8', 'https://en.wikipedia.org/wiki/Voyager_1',
         '1977-09-05', 'Interstellar space', 'active', 'flyby', 16.6, 'Interstellar', None, current_time),
        ('旅行者2号', 'Voyager 2', 'https://zh.wikipedia.org/wiki/%E6%97%85%E8%A1%8C%E8%80%85%E5%8F%B7%E6%8E%A2%E6%B5%8B%E5%99%A8', 'https://en.wikipedia.org/wiki/Voyager_2',
         '1977-08-20', 'Interstellar space', 'active', 'flyby', 16.3, 'Interstellar', '1989-08-25', current_time),
        ('先驱者10号', 'Pioneer 10', 'https://zh.wikipedia.org/wiki/%E5%85%88%E9%A9%B1%E8%80%85%E5%8F%B7%E6%8E%A2%E6%B5%8B%E5%99%A8', 'https://en.wikipedia.org/wiki/Pioneer_10',
         '1972-03-02', 'Interstellar space', 'inactive', 'flyby', 14.3, 'Lost contact 2003', '1983-06-13', current_time),
        ('先驱者11号', 'Pioneer 11', 'https://zh.wikipedia.org/wiki/%E5%85%88%E9%A9%B1%E8%80%85%E5%8F%B7%E6%8E%A2%E6%B5%8B%E5%99%A8', 'https://en.wikipedia.org/wiki/Pioneer_11',
         '1973-04-06', 'Interstellar space', 'inactive', 'flyby', 14.5, 'Lost contact 1995', '1979-09-01', current_time),
        ('伽利略号', 'Galileo', 'https://zh.wikipedia.org/wiki/%E4%BC%BD%E5%88%A9%E7%95%A5%E5%8F%B7%E6%8E%A2%E6%B5%8B%E5%99%A8', 'https://en.wikipedia.org/wiki/Galileo_(spacecraft)',
         '1989-10-18', 'Jupiter', 'inactive', 'orbiter', 13.6, 'Deorbited 2003', '1995-12-07', current_time),
        ('卡西尼-惠更斯号', 'Cassini-Huygens', 'https://zh.wikipedia.org/wiki/%E5%8D%A1%E8%A5%BF%E5%B0%BC-%E6%83%A0%E6%9B%B4%E6%96%AF%E5%8F%B7', 'https://en.wikipedia.org/wiki/Cassini%E2%80%93Huygens',
         '1997-10-15', 'Saturn', 'inactive', 'orbiter', 13.4, 'Ended mission 2017', '2004-07-01', current_time),
        ('新视野号', 'New Horizons', 'https://zh.wikipedia.org/wiki/%E6%96%B0%E8%A7%86%E9%87%8E%E5%8F%B7', 'https://en.wikipedia.org/wiki/New_Horizons',
         '2006-01-19', 'Kuiper Belt', 'active', 'flyby', 16.3, 'Kuiper Belt exploration', '2015-07-14', current_time),
        ('朱诺号', 'Juno', 'https://zh.wikipedia.org/wiki/%E6%9C%B1%E8%AF%BA%E5%8F%B7', 'https://en.wikipedia.org/wiki/Juno_(spacecraft)',
         '2011-08-05', 'Jupiter', 'active', 'orbiter', 13.1, 'Orbital operations', '2016-07-04', current_time),
        ('好奇号', 'Curiosity', 'https://zh.wikipedia.org/wiki/%E5%A5%BD%E5%A5%87%E5%8F%B7', 'https://en.wikipedia.org/wiki/Curiosity_(rover)',
         '2011-11-26', 'Mars', 'active', 'rover', 5.8, 'Surface operations', '2012-08-06', current_time),
        ('毅力号', 'Perseverance', 'https://zh.wikipedia.org/wiki/%E6%AF%85%E5%8A%9B%E5%8F%B7', 'https://en.wikipedia.org/wiki/Perseverance_(rover)',
         '2020-07-30', 'Mars', 'active', 'rover', 5.9, 'Surface operations', '2021-02-18', current_time),
        ('祝融号', 'Zhurong', 'https://zh.wikipedia.org/wiki/%E7%A5%9D%E8%9E%8D%E5%8F%B7', 'https://en.wikipedia.org/wiki/Zhurong_(rover)',
         '2020-07-23', 'Mars', 'inactive', 'rover', 4.1, 'Hibernated since May 2022', '2021-05-15', current_time),
        ('天问一号', 'Tianwen-1', 'https://zh.wikipedia.org/wiki/%E5%A4%A9%E9%97%AE%E4%B8%80%E5%8F%B7', 'https://en.wikipedia.org/wiki/Tianwen-1',
         '2020-07-23', 'Mars', 'active', 'orbiter', 11.2, 'Orbital operations', '2021-02-10', current_time),
        ('露西号', 'Lucy', 'https://zh.wikipedia.org/wiki/%E9%9C%B2%E8%A5%BF%E5%8F%B7%E6%8E%A2%E6%B5%8B%E5%99%A8', 'https://en.wikipedia.org/wiki/Lucy_(spacecraft)',
         '2021-10-16', 'Trojan asteroids', 'active', 'flyby', 12.9, 'En route to Jupiter Trojans', '2033-03-03', current_time),
        ('欧罗巴快船', 'Europa Clipper', 'https://zh.wikipedia.org/wiki/%E6%AC%A7%E7%BD%97%E5%B7%B4%E5%BF%AB%E8%88%B9', 'https://en.wikipedia.org/wiki/Europa_Clipper',
         '2024-10-14', 'Europa', 'active', 'orbiter', 13.0, 'En route to Jupiter', '2030-04-11', current_time),
        ('帕克太阳探测器', 'Parker Solar Probe', 'https://zh.wikipedia.org/wiki/%E5%B8%95%E5%85%8B%E5%A4%AA%E9%98%B3%E6%8E%A2%E6%B5%8B%E5%99%A8', 'https://en.wikipedia.org/wiki/Parker_Solar_Probe',
         '2018-08-12', 'Sun', 'active', 'flyby', 12.0, 'Solar observation', None, current_time)
    ]
    
    cursor.executemany('''
        INSERT OR REPLACE INTO spacecraft 
        (name, name_en, wikipedia_url, wikipedia_url_en, launch_date, target_body, status, 
         trajectory_type, launch_speed, current_phase, arrival_time, last_update)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', spacecraft_data)
    
    conn.commit()
    conn.close()
    
    print("Database initialized successfully!")
    print("Tables created: planets, moons, spacecraft")
    print(f"Planets: {len(planets_data)}")
    print(f"Moons: {len(moons_data)}")
    print(f"Spacecraft: {len(spacecraft_data)}")

if __name__ == '__main__':
    init_database()
