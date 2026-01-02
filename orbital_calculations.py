import numpy as np
import math
from datetime import datetime, timedelta

# Astronomical constants
AU = 1.496e8  # Astronomical Unit in km
G = 6.67430e-20  # Gravitational constant in km^3 kg^-1 s^-2
M_SUN = 1.989e30  # Mass of Sun in kg
M_EARTH = 5.972e24  # Mass of Earth in kg
DAY_SECONDS = 86400  # Seconds in a day
YEAR_SECONDS = 365.25 * DAY_SECONDS  # Seconds in a year

class OrbitalCalculator:
    """Calculate orbital positions and velocities for celestial bodies"""
    
    @staticmethod
    def julian_date(dt):
        """Convert datetime to Julian Date"""
        a = (14 - dt.month) // 12
        y = dt.year + 4800 - a
        m = dt.month + 12 * a - 3
        
        jdn = dt.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
        jd = jdn + (dt.hour - 12) / 24 + dt.minute / 1440 + dt.second / 86400 + dt.microsecond / 86400000000
        return jd
    
    @staticmethod
    def days_since_epoch(jd):
        """Calculate days since J2000.0 epoch (January 1, 2000, 12:00 TT)"""
        jd2000 = 2451545.0
        return jd - jd2000
    
    @staticmethod
    def calculate_planet_position(orbital_elements, current_time):
        """
        Calculate planet position using orbital elements
        orbital_elements: dict with semi_major_axis, eccentricity, inclination,
                         orbital_period, mean_anomaly_0, perihelion_0, ascending_node_0
        """
        # Get orbital elements
        a = orbital_elements['semi_major_axis']  # AU
        e = orbital_elements['eccentricity']
        i = math.radians(orbital_elements['inclination'])  # Convert to radians
        period = orbital_elements['orbital_period'] * YEAR_SECONDS  # Convert to seconds
        M0 = math.radians(orbital_elements['mean_anomaly_0'])  # Mean anomaly at epoch
        w0 = math.radians(orbital_elements['perihelion_0'])  # Perihelion at epoch
        O0 = math.radians(orbital_elements['ascending_node_0'])  # Ascending node at epoch
        
        # Calculate mean motion
        n = 2 * math.pi / period
        
        # Calculate time since epoch (using J2000.0 as reference)
        jd = OrbitalCalculator.julian_date(current_time)
        days = OrbitalCalculator.days_since_epoch(jd)
        t = days * DAY_SECONDS
        
        # Calculate mean anomaly
        M = M0 + n * t
        
        # Solve Kepler's equation for eccentric anomaly (E)
        # M = E - e*sin(E)
        E = M
        for _ in range(10):  # Newton-Raphson iteration
            E = E - (E - e * math.sin(E) - M) / (1 - e * math.cos(E))
        
        # Calculate true anomaly (nu)
        nu = 2 * math.atan2(math.sqrt(1 + e) * math.sin(E/2), 
                            math.sqrt(1 - e) * math.cos(E/2))
        
        # Calculate distance from Sun (r)
        r = a * (1 - e * math.cos(E))  # in AU
        
        # Calculate position in orbital plane
        x_orbital = r * math.cos(nu)
        y_orbital = r * math.sin(nu)
        z_orbital = 0
        
        # Transform to ecliptic coordinates
        # Argument of perihelion (w) = w0 (simplified, precession ignored)
        w = w0
        
        # Rotation for inclination (i)
        x1 = x_orbital
        y1 = y_orbital * math.cos(i) - z_orbital * math.sin(i)
        z1 = y_orbital * math.sin(i) + z_orbital * math.cos(i)
        
        # Rotation for longitude of ascending node (O0)
        x_ecliptic = x1 * math.cos(O0) - y1 * math.sin(O0)
        y_ecliptic = x1 * math.sin(O0) + y1 * math.cos(O0)
        z_ecliptic = z1
        
        # Calculate velocity (simplified)
        # Vis-viva equation: v^2 = GM(2/r - 1/a)
        mu = G * M_SUN
        v_orbital = math.sqrt(mu * (2/(r*AU) - 1/(a*AU)))  # in km/s
        
        # Velocity components (simplified, directed along orbit)
        vx_orbital = -v_orbital * math.sin(nu)
        vy_orbital = v_orbital * math.sqrt(1 - e**2) * math.cos(nu)
        vz_orbital = 0
        
        # Transform velocity to ecliptic coordinates
        vx1 = vx_orbital
        vy1 = vy_orbital * math.cos(i) - vz_orbital * math.sin(i)
        vz1 = vy_orbital * math.sin(i) + vz_orbital * math.cos(i)
        
        vx_ecliptic = vx1 * math.cos(O0) - vy1 * math.sin(O0)
        vy_ecliptic = vx1 * math.sin(O0) + vy1 * math.cos(O0)
        vz_ecliptic = vz1
        
        return {
            'x': x_ecliptic,  # AU
            'y': y_ecliptic,  # AU
            'z': z_ecliptic,  # AU
            'vx': vx_ecliptic,  # km/s
            'vy': vy_ecliptic,  # km/s
            'vz': vz_ecliptic,  # km/s
            'distance_sun': r,  # AU
            'speed_sun': v_orbital  # km/s
        }
    
    @staticmethod
    def calculate_moon_position(moon_data, parent_position, current_time):
        """
        Calculate moon position relative to Sun (parent planet position + moon orbit)
        moon_data: dict with semi_major_axis, orbital_period, inclination
        parent_position: dict with x, y, z, vx, vy, vz of parent planet
        """
        a = moon_data['semi_major_axis'] / AU  # Convert km to AU
        period = moon_data['orbital_period'] * DAY_SECONDS  # Convert to seconds
        i = math.radians(moon_data['inclination'])
        
        # Simplified circular orbit for moons
        n = 2 * math.pi / period
        
        # Time since J2000.0
        jd = OrbitalCalculator.julian_date(current_time)
        days = OrbitalCalculator.days_since_epoch(jd)
        t = days * DAY_SECONDS
        
        # Mean anomaly (assuming M0 = 0 for simplicity)
        M = n * t
        
        # Position in orbital plane
        x_orbital = a * math.cos(M)
        y_orbital = a * math.sin(M)
        z_orbital = 0
        
        # Transform to ecliptic (simplified)
        x_ecliptic = x_orbital
        y_ecliptic = y_orbital * math.cos(i)
        z_ecliptic = y_orbital * math.sin(i)
        
        # Add parent planet position
        x_sun = parent_position['x'] + x_ecliptic
        y_sun = parent_position['y'] + y_ecliptic
        z_sun = parent_position['z'] + z_ecliptic
        
        # Calculate velocity relative to Sun (parent velocity + moon orbital velocity)
        # Moon orbital speed in km/s
        v_moon = 2 * math.pi * a * AU / period  # v = 2πa/T, where T is in seconds
        
        # Velocity components in orbital plane
        vx_orbital = -v_moon * math.sin(M)
        vy_orbital = v_moon * math.cos(M)
        vz_orbital = 0
        
        # Transform velocity to ecliptic
        vx_ecliptic = vx_orbital
        vy_ecliptic = vy_orbital * math.cos(i)
        vz_ecliptic = vy_orbital * math.sin(i)
        
        # Total velocity = parent velocity + moon orbital velocity
        vx_total = parent_position['vx'] + vx_ecliptic
        vy_total = parent_position['vy'] + vy_ecliptic
        vz_total = parent_position['vz'] + vz_ecliptic
        
        return {
            'x': x_sun,
            'y': y_sun,
            'z': z_sun,
            'vx': vx_total,
            'vy': vy_total,
            'vz': vz_total,
            'distance_sun': math.sqrt(x_sun**2 + y_sun**2 + z_sun**2),
            'speed_sun': math.sqrt(vx_total**2 + vy_total**2 + vz_total**2)
        }
    
    @staticmethod
    def calculate_spacecraft_position(spacecraft_data, target_position=None, earth_position=None):
        """
        Calculate approximate spacecraft position
        This is a simplified calculation - real spacecraft trajectories require ephemeris data
        """
        launch_date = datetime.strptime(spacecraft_data['launch_date'], '%Y-%m-%d')
        current_time = datetime.now()
        
        # Calculate time since launch in years
        time_since_launch = (current_time - launch_date).total_seconds() / YEAR_SECONDS
        
        status = spacecraft_data['status']
        trajectory_type = spacecraft_data['trajectory_type']
        target_body = spacecraft_data['target_body']
        name_en = spacecraft_data.get('name_en', '')
        
        # Check if spacecraft has arrived at target
        has_arrived = False
        if spacecraft_data.get('arrival_time'):
            try:
                arrival_date = datetime.strptime(spacecraft_data['arrival_time'], '%Y-%m-%d')
                has_arrived = arrival_date <= current_time
            except:
                pass
        
        if status == 'inactive':
            # For inactive spacecraft, estimate position based on last known location
            # This is a rough approximation
            if target_body == 'Jupiter':
                distance_from_sun = 5.2 + time_since_launch * 0.1
            elif target_body == 'Saturn':
                distance_from_sun = 9.5 + time_since_launch * 0.1
            elif target_body == 'Mars':
                distance_from_sun = 1.5 + time_since_launch * 0.05
            elif target_body == 'Interstellar space':
                distance_from_sun = 30 + time_since_launch * 2
            else:
                distance_from_sun = 1.0 + time_since_launch * 0.5
        else:
            # For active spacecraft
            if target_body == 'Interstellar space':
                # Voyager spacecraft - far from Sun, still moving outward
                # Estimate current distance from Sun (Voyager 1 is ~156 AU as of 2024)
                # Using launch date + constant outward velocity ~3.6 AU/year
                years_past_1977 = time_since_launch + (1977 - launch_date.year)
                distance_from_sun = 40 + years_past_1977 * 3.6
            elif target_body == 'Jupiter':
                # Juno, etc.
                if 'orbiter' in trajectory_type or has_arrived:
                    distance_from_sun = 5.2  # Jupiter's average distance
                else:
                    # En route
                    progress = min(time_since_launch / 6.0, 1.0)  # Assume 6 years to Jupiter
                    distance_from_sun = 1.0 + progress * 4.2
            elif target_body == 'Saturn':
                # Similar logic for Saturn
                if has_arrived:
                    distance_from_sun = 9.5  # Saturn's average distance
                else:
                    progress = min(time_since_launch / 7.0, 1.0)
                    distance_from_sun = 1.0 + progress * 8.5
            elif target_body == 'Mars':
                if 'rover' in trajectory_type or 'lander' in trajectory_type:
                    distance_from_sun = 1.5  # Mars' average distance
                else:
                    # En route - Mars missions typically take 6-7 months (~0.5-0.6 years)
                    progress = min(time_since_launch / 0.55, 1.0)
                    distance_from_sun = 1.0 + progress * 0.5
            elif target_body == 'Sun':
                # Parker Solar Probe
                # Highly elliptical orbit with 88-day period
                # Perihelion: 0.046 AU, Aphelion: 0.73 AU
                orbital_period = 0.24  # 88 days in years
                time_in_orbit = time_since_launch % orbital_period
                
                # Calculate position in orbit using simple approximation
                # Using cosine to simulate elliptical orbit variation
                phase = (time_in_orbit / orbital_period) * 2 * math.pi
                perihelion = 0.046  # AU
                aphelion = 0.73     # AU
                semi_major_axis = (perihelion + aphelion) / 2
                
                # Approximate distance using orbital phase
                # At phase 0 = perihelion, at phase π = aphelion
                distance_from_sun = semi_major_axis * (1 - 0.88 * math.cos(phase))
            elif target_body == 'Europa' or target_body == 'Trojan asteroids' or target_body == 'Kuiper Belt':
                # En route
                if target_body == 'Europa':
                    progress = min(time_since_launch / 6.0, 1.0)
                    distance_from_sun = 1.0 + progress * 4.2
                elif target_body == 'Trojan asteroids':
                    progress = min(time_since_launch / 12.0, 1.0)
                    distance_from_sun = 1.0 + progress * 4.2
                else:  # Kuiper Belt
                    distance_from_sun = 30 + time_since_launch * 1
            else:
                distance_from_sun = 1.0 + time_since_launch * 0.3
        
        # Calculate position (simplified, assuming radial trajectory)
        angle = (time_since_launch * 2 * math.pi) % (2 * math.pi)
        x = distance_from_sun * math.cos(angle)
        y = distance_from_sun * math.sin(angle)
        z = distance_from_sun * 0.05 * math.sin(angle)  # Slight inclination
        
        # Calculate velocity with improved accuracy
        if status == 'inactive':
            # For inactive spacecraft in interstellar space, use a decaying but still substantial speed
            if target_body == 'Interstellar space':
                # Voyager 1 and 2 are still moving at ~17 km/s and ~15 km/s respectively
                speed = spacecraft_data.get('launch_speed', 16) * 0.95  # Slight decay over time
            else:
                speed = 10 + time_since_launch * 0.1  # Slower decay for other inactive spacecraft
        else:
            if target_body == 'Sun' and name_en == 'Parker Solar Probe':
                # Parker Solar Probe's speed varies dramatically
                # At perihelion: ~194 km/s, At aphelion: ~33 km/s
                # Use vis-viva equation approximation
                orbital_period = 0.24  # 88 days in years
                time_in_orbit = time_since_launch % orbital_period
                phase = (time_in_orbit / orbital_period) * 2 * math.pi
                
                # Speed varies inversely with distance
                perihelion = 0.046  # AU
                aphelion = 0.73     # AU
                current_distance = distance_from_sun
                
                # Vis-viva approximation: v = sqrt(GM * (2/r - 1/a))
                # Need to convert everything to consistent units
                semi_major_axis = (perihelion + aphelion) / 2  # in AU
                
                # Use G in km^3 kg^-1 s^-2, M_SUN in kg, distances in km
                semi_major_axis_km = semi_major_axis * AU
                current_distance_km = current_distance * AU
                
                # Calculate speed using vis-viva equation
                mu = G * M_SUN  # in km^3/s^2
                speed = math.sqrt(mu * (2/current_distance_km - 1/semi_major_axis_km))  # in km/s
            elif target_body == 'Interstellar space' and ('Voyager' in name_en or 'Pioneer' in name_en):
                # For Voyager and Pioneer in interstellar space
                # These probes maintain high velocity due to gravitational assists
                # They haven't slowed down as much as pure escape velocity would suggest
                # Use a more realistic model: velocity decays slowly with distance
                # Based on actual data: Voyager 1 ~17 km/s, Voyager 2 ~15 km/s (as of 2024)
                # The probes maintain roughly their escape velocity from the solar system
                base_speed = spacecraft_data.get('launch_speed', 16.5)
                # Minimal decay - these probes are still moving fast due to gravity assists
                speed = base_speed * 0.95  # Slight decay from launch
            elif target_body == 'Kuiper Belt' and name_en == 'New Horizons':
                # New Horizons still moving fast in Kuiper Belt
                # Uses realistic speed ~14-15 km/s
                speed = 14.5  # Approximate current speed
            elif 'orbiter' in trajectory_type and target_position:
                # For orbiters, use target body's orbital speed
                speed = target_position.get('speed_sun', 10)
            elif 'rover' in trajectory_type or 'lander' in trajectory_type:
                # For rovers/landers, use target body's orbital speed
                if target_body == 'Mars':
                    speed = 24.1  # Mars average orbital speed in km/s
                elif target_body == 'Jupiter':
                    speed = 13.1  # Jupiter average orbital speed in km/s
                else:
                    speed = earth_position.get('speed_sun', 30) if earth_position else 30
            elif has_arrived:
                # Spacecraft has arrived at destination - use target body's speed
                if target_body == 'Jupiter':
                    speed = 13.1
                elif target_body == 'Saturn':
                    speed = 9.7
                elif target_body == 'Mars':
                    speed = 24.1
                else:
                    speed = 30  # Default fallback
            else:
                # For spacecraft en route, use vis-viva equation
                # Estimate semi-major axis based on Earth's orbit and target distance
                # Simplified: assume transfer orbit between 1 AU and target distance
                semi_major_axis = (1.0 + distance_from_sun) / 2
                semi_major_axis_km = semi_major_axis * AU
                current_distance_km = distance_from_sun * AU
                
                mu = G * M_SUN
                speed = math.sqrt(mu * (2/current_distance_km - 1/semi_major_axis_km))
        
        # Velocity components
        vx = -speed * math.sin(angle)
        vy = speed * math.cos(angle)
        vz = 0
        
        return {
            'x': x,
            'y': y,
            'z': z,
            'vx': vx,
            'vy': vy,
            'vz': vz,
            'distance_sun': distance_from_sun,
            'speed_sun': speed
        }
    
    @staticmethod
    def calculate_relative_to_earth(body_position, earth_position):
        """Calculate position and velocity relative to Earth"""
        # Distance relative to Earth
        dx = body_position['x'] - earth_position['x']
        dy = body_position['y'] - earth_position['y']
        dz = body_position['z'] - earth_position['z']
        
        distance_earth = math.sqrt(dx**2 + dy**2 + dz**2)  # in AU
        
        # Velocity relative to Earth
        dvx = body_position['vx'] - earth_position['vx']
        dvy = body_position['vy'] - earth_position['vy']
        dvz = body_position['vz'] - earth_position['vz']
        
        speed_earth = math.sqrt(dvx**2 + dvy**2 + dvz**2)  # in km/s
        
        return {
            'distance_earth': distance_earth,
            'speed_earth': speed_earth
        }
    
    @staticmethod
    def format_distance(au):
        """Format distance from AU to km"""
        km = au * AU
        return f"{km:.2f} km"
    
    @staticmethod
    def format_time_since_launch(launch_date_str):
        """Calculate time since launch and return structured data"""
        launch_date = datetime.strptime(launch_date_str, '%Y-%m-%d')
        current_date = datetime.now()
        
        delta = current_date - launch_date
        
        years = delta.days // 365
        days = delta.days % 365
        hours = delta.seconds // 3600
        
        return {
            'years': years,
            'days': days,
            'hours': hours
        }
    
    @staticmethod
    def calculate_distance_to_target(spacecraft_pos, target_pos):
        """
        Calculate distance from spacecraft to its target body
        Returns distance in AU
        """
        dx = spacecraft_pos['x'] - target_pos['x']
        dy = spacecraft_pos['y'] - target_pos['y']
        dz = spacecraft_pos['z'] - target_pos['z']
        
        distance_au = math.sqrt(dx**2 + dy**2 + dz**2)
        return distance_au
