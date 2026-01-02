from flask import Flask, jsonify, render_template
import sqlite3
from datetime import datetime
from orbital_calculations import OrbitalCalculator

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # Support Chinese characters in JSON

def get_db_connection():
    """Create database connection"""
    conn = sqlite3.connect('solar_system.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/api/solar-system-data')
def get_solar_system_data():
    """
    API endpoint to get real-time solar system data
    Returns planets, moons, and spacecraft with their current positions
    """
    current_time = datetime.now()
    conn = get_db_connection()
    
    # Get all planets
    planets = conn.execute('SELECT * FROM planets ORDER BY semi_major_axis').fetchall()
    
    result = {
        'timestamp': current_time.isoformat(),
        'planets': []
    }
    
    # Store Earth position for relative calculations
    earth_position = None
    
    # Calculate planet positions
    for planet in planets:
        planet_data = dict(planet)
        
        # Calculate orbital position
        orbital_elements = {
            'semi_major_axis': planet['semi_major_axis'],
            'eccentricity': planet['eccentricity'],
            'inclination': planet['inclination'],
            'orbital_period': planet['orbital_period'],
            'mean_anomaly_0': planet['mean_anomaly_0'],
            'perihelion_0': planet['perihelion_0'],
            'ascending_node_0': planet['ascending_node_0']
        }
        
        position = OrbitalCalculator.calculate_planet_position(orbital_elements, current_time)
        
        # Store Earth position
        if planet['name_en'] == 'Earth':
            earth_position = position
        
        planet_info = {
            'id': planet['id'],
            'name': planet['name'],
            'name_en': planet['name_en'],
            'wikipedia_url': planet['wikipedia_url'],
            'wikipedia_url_en': planet['wikipedia_url_en'],
            'type': 'planet',
            'planet_type': planet['type'],  # Planet type in Chinese
            'planet_type_en': planet['type_en'],  # Planet type in English
            'position': {
                'x': position['x'],
                'y': position['y'],
                'z': position['z']
            },
            'distance_sun': OrbitalCalculator.format_distance(position['distance_sun']),
            'distance_sun_au': position['distance_sun'],
            'speed_sun': f"{position['speed_sun']:.2f} km/s",
            'distance_earth': 'N/A',
            'speed_earth': 'N/A',
            'moons': [],
            'extra_info': {
                'mass': f"{planet['mass']:.4e} kg",
                'rotation_period': f"{planet['rotation_period']:.2f} hours",
                'orbital_period': f"{planet['orbital_period']:.4f} Earth years",
                'density': f"{planet['density']:.3f} g/cm³",
                'radius': f"{planet['radius']:.1f} km",
                'equatorial_radius': f"{planet['equatorial_radius']:.1f} km",
                'polar_radius': f"{planet['polar_radius']:.1f} km",
                'magnetic_field': f"{planet['magnetic_field']:.3f} µT" if planet['magnetic_field'] is not None else '无',
                'atmospheric_pressure': format_atmospheric_pressure(planet['atmospheric_pressure'])
            }
        }
        
        result['planets'].append(planet_info)
    
    # Calculate moon positions
    for i, planet in enumerate(result['planets']):
        moons = conn.execute('SELECT * FROM moons WHERE parent_planet_id = ? ORDER BY semi_major_axis', 
                            (planet['id'],)).fetchall()
        
        for moon in moons:
            moon_data = dict(moon)
            
            # Get parent planet position
            parent_pos = {
                'x': planet['position']['x'],
                'y': planet['position']['y'],
                'z': planet['position']['z'],
                'vx': 0,  # Will be updated from planet
                'vy': 0,
                'vz': 0
            }
            
            # Get planet velocity from calculation
            planet_record = planets[i]
            orbital_elements = {
                'semi_major_axis': planet_record['semi_major_axis'],
                'eccentricity': planet_record['eccentricity'],
                'inclination': planet_record['inclination'],
                'orbital_period': planet_record['orbital_period'],
                'mean_anomaly_0': planet_record['mean_anomaly_0'],
                'perihelion_0': planet_record['perihelion_0'],
                'ascending_node_0': planet_record['ascending_node_0']
            }
            planet_position = OrbitalCalculator.calculate_planet_position(orbital_elements, current_time)
            parent_pos['vx'] = planet_position['vx']
            parent_pos['vy'] = planet_position['vy']
            parent_pos['vz'] = planet_position['vz']
            
            # Calculate moon position
            moon_data_calc = {
                'semi_major_axis': moon['semi_major_axis'],
                'orbital_period': moon['orbital_period'],
                'inclination': moon['inclination']
            }
            
            position = OrbitalCalculator.calculate_moon_position(moon_data_calc, parent_pos, current_time)
            
            moon_info = {
                'id': moon['id'],
                'name': moon['name'],
                'name_en': moon['name_en'],
                'wikipedia_url': moon['wikipedia_url'],
                'wikipedia_url_en': moon['wikipedia_url_en'],
                'type': 'moon',
                'moon_type': moon['type'],  # Moon type in Chinese
                'moon_type_en': moon['type_en'],  # Moon type in English
                'position': {
                    'x': position['x'],
                    'y': position['y'],
                    'z': position['z']
                },
                'distance_sun': OrbitalCalculator.format_distance(position['distance_sun']),
                'distance_sun_au': position['distance_sun'],
                'speed_sun': f"{position['speed_sun']:.2f} km/s",
                'extra_info': {
                    'mass': f"{moon['mass']:.4e} kg",
                    'rotation_period': f"{moon['rotation_period']:.2f} hours",
                    'orbital_period': f"{moon['orbital_period']:.4f} Earth days",
                    'density': f"{moon['density']:.3f} g/cm³",
                    'radius': f"{moon['radius']:.1f} km",
                    'surface_temperature': f"{moon['surface_temperature']:.0f} K" if moon['surface_temperature'] else 'N/A',
                    'atmosphere': moon['atmosphere'] if moon['atmosphere'] else 'N/A',
                    'atmosphere_en': moon['atmosphere_en'] if moon['atmosphere_en'] else 'N/A',
                    'magnetic_field': f"{moon['magnetic_field']:.1f} nT" if moon['magnetic_field'] is not None else '无',
                    'atmospheric_pressure': format_atmospheric_pressure(moon['atmospheric_pressure'])
                }
            }
            
            planet['moons'].append(moon_info)
    
    # Calculate relative positions for planets and moons
    if earth_position:
        for planet in result['planets']:
            planet_pos = {
                'x': planet['position']['x'],
                'y': planet['position']['y'],
                'z': planet['position']['z'],
                'vx': planet.get('vx', 0),
                'vy': planet.get('vy', 0),
                'vz': planet.get('vz', 0)
            }
            
            # Get actual velocity from calculation
            planet_record = next(p for p in planets if p['id'] == planet['id'])
            orbital_elements = {
                'semi_major_axis': planet_record['semi_major_axis'],
                'eccentricity': planet_record['eccentricity'],
                'inclination': planet_record['inclination'],
                'orbital_period': planet_record['orbital_period'],
                'mean_anomaly_0': planet_record['mean_anomaly_0'],
                'perihelion_0': planet_record['perihelion_0'],
                'ascending_node_0': planet_record['ascending_node_0']
            }
            planet_position = OrbitalCalculator.calculate_planet_position(orbital_elements, current_time)
            planet_pos['vx'] = planet_position['vx']
            planet_pos['vy'] = planet_position['vy']
            planet_pos['vz'] = planet_position['vz']
            
            relative = OrbitalCalculator.calculate_relative_to_earth(planet_pos, earth_position)
            planet['distance_earth'] = OrbitalCalculator.format_distance(relative['distance_earth'])
            planet['speed_earth'] = f"{relative['speed_earth']:.2f} km/s"
            
            # Calculate relative positions for moons
            for moon in planet['moons']:
                moon_pos = {
                    'x': moon['position']['x'],
                    'y': moon['position']['y'],
                    'z': moon['position']['z'],
                    'vx': 0,  # Simplified
                    'vy': 0,
                    'vz': 0
                }
                relative = OrbitalCalculator.calculate_relative_to_earth(moon_pos, earth_position)
                moon['distance_earth'] = OrbitalCalculator.format_distance(relative['distance_earth'])
                moon['speed_earth'] = f"{relative['speed_earth']:.2f} km/s"
    
    # Get spacecraft
    spacecraft = conn.execute('SELECT * FROM spacecraft ORDER BY launch_date').fetchall()
    result['spacecraft'] = []
    
    # Separate active and inactive spacecraft
    active_spacecraft = []
    inactive_spacecraft = []
    
    for sc in spacecraft:
        sc_data = dict(sc)
        
        # Calculate spacecraft position
        spacecraft_info = {
            'id': sc['id'],
            'name': sc['name'],
            'name_en': sc['name_en'],
            'wikipedia_url': sc['wikipedia_url'],
            'wikipedia_url_en': sc['wikipedia_url_en'],
            'type': 'spacecraft',
            'launch_date': sc['launch_date'],
            'time_since_launch': OrbitalCalculator.format_time_since_launch(sc['launch_date']),
            'target_body': sc['target_body'],
            'status': sc['status'],
            'trajectory_type': sc['trajectory_type'],
            'current_phase': sc['current_phase'],
            'arrival_time': sc['arrival_time']
        }
        
        # Get target position if available
        target_position = None
        if sc['target_body'] in ['Jupiter', 'Saturn', 'Mars']:
            target_planet = next((p for p in result['planets'] if p['name_en'] == sc['target_body']), None)
            if target_planet:
                target_position = {
                    'speed_sun': 30.0  # Approximate
                }
        
        position = OrbitalCalculator.calculate_spacecraft_position(
            sc_data, target_position, earth_position
        )
        
        spacecraft_info.update({
            'position': {
                'x': position['x'],
                'y': position['y'],
                'z': position['z']
            },
            'distance_sun': OrbitalCalculator.format_distance(position['distance_sun']),
            'distance_sun_au': position['distance_sun'],
            'speed_sun': f"{position['speed_sun']:.2f} km/s"
        })
        
        # Calculate relative to Earth
        if earth_position:
            sc_pos = {
                'x': position['x'],
                'y': position['y'],
                'z': position['z'],
                'vx': position['vx'],
                'vy': position['vy'],
                'vz': position['vz']
            }
            relative = OrbitalCalculator.calculate_relative_to_earth(sc_pos, earth_position)
            spacecraft_info['distance_earth'] = OrbitalCalculator.format_distance(relative['distance_earth'])
            spacecraft_info['speed_earth'] = f"{relative['speed_earth']:.2f} km/s"
        
        # Calculate distance to target body for active spacecraft
        # Only for probes that haven't arrived yet (no arrival_time or arrival_time is in future)
        if sc['status'] == 'active':
            spacecraft_info['target_distance'] = None
            spacecraft_info['target_position_known'] = False
            
            # Check if spacecraft has arrived
            has_arrived = False
            if sc['arrival_time']:
                try:
                    arrival_date = datetime.strptime(sc['arrival_time'], '%Y-%m-%d')
                    has_arrived = arrival_date <= current_time
                except:
                    pass
            
            # Only calculate target distance if not arrived and target is a known planet
            if not has_arrived and sc['target_body']:
                target_planet = None
                
                # Map target body to planet name_en
                target_mapping = {
                    'Jupiter': 'Jupiter',
                    'Saturn': 'Saturn',
                    'Mars': 'Mars',
                    'Sun': None,  # Sun is not in planets table
                    'Europa': 'Jupiter',  # Europa orbits Jupiter
                    'Interstellar space': None,
                    'Trojan asteroids': None,
                    'Kuiper Belt': None
                }
                
                planet_name_en = target_mapping.get(sc['target_body'])
                
                if planet_name_en:
                    target_planet = next((p for p in result['planets'] if p['name_en'] == planet_name_en), None)
                
                if target_planet:
                    target_pos = {
                        'x': target_planet['position']['x'],
                        'y': target_planet['position']['y'],
                        'z': target_planet['position']['z']
                    }
                    
                    distance_to_target_au = OrbitalCalculator.calculate_distance_to_target(
                        {'x': position['x'], 'y': position['y'], 'z': position['z']},
                        target_pos
                    )
                    
                    spacecraft_info['target_distance'] = distance_to_target_au
                    spacecraft_info['target_position_known'] = True
        
        # Sort into active/inactive (maintaining launch_date order)
        if sc['status'] == 'active':
            active_spacecraft.append(spacecraft_info)
        else:
            inactive_spacecraft.append(spacecraft_info)
    
    # Combine: active first, then inactive (both in launch_date order)
    result['spacecraft'] = active_spacecraft + inactive_spacecraft
    result['inactive_count'] = len(inactive_spacecraft)
    
    conn.close()
    
    return jsonify(result)

def format_atmospheric_pressure(pressure):
    """Format atmospheric pressure in human-readable format"""
    if pressure is None:
        return '无大气层'
    
    # Define thresholds for different units
    ATM = 101325  # 1 atm in Pa
    KPA = 1000    # 1 kPa in Pa
    HPA = 100     # 1 hPa in Pa
    MPA = 1e6     # 1 MPa in Pa
    
    # Choose appropriate unit based on magnitude
    if pressure >= MPA:
        return f"{pressure/MPA:.2f} MPa"
    elif pressure >= ATM:
        return f"{pressure/ATM:.2f} atm"
    elif pressure >= KPA:
        return f"{pressure/KPA:.2f} kPa"
    elif pressure >= HPA:
        return f"{pressure/HPA:.1f} hPa"
    elif pressure >= 1:
        return f"{pressure:.2f} Pa"
    elif pressure >= 1e-3:
        return f"{pressure*1e3:.2f} mPa"
    elif pressure >= 1e-6:
        return f"{pressure*1e6:.2f} µPa"
    elif pressure >= 1e-9:
        return f"{pressure*1e9:.2f} nPa"
    else:
        return f"{pressure:.2e} Pa"

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
