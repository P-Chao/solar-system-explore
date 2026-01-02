import sqlite3
from datetime import datetime

def update_spacecraft_status():
    """
    Update spacecraft status and information in the database.
    This script can be used to:
    - Update spacecraft status (active/inactive)
    - Update current mission phase
    - Add new spacecraft
    - Update last_update timestamp
    """
    
    conn = sqlite3.connect('solar_system.db')
    cursor = conn.cursor()
    
    print("Updating spacecraft data...")
    
    # Example: Update spacecraft status (modify as needed)
    updates = [
        # Update status for specific spacecraft
        # ('active', 'Orbital operations extended', '祝融号'),
        # ('inactive', 'Mission completed', '伽利略号'),
    ]
    
    for status, phase, name in updates:
        cursor.execute('''
            UPDATE spacecraft 
            SET status = ?, current_phase = ?, last_update = ?
            WHERE name = ?
        ''', (status, phase, datetime.now().isoformat(), name))
        print(f"Updated {name}: {status} - {phase}")
    
    # Example: Add new spacecraft (modify as needed)
    # new_spacecraft = [
    #     ('新探测器', 'New Probe', 'https://zh.wikipedia.org/wiki/example', 
    #      'https://en.wikipedia.org/wiki/example', '2025-01-01', 'Mars', 
    #      'active', 'flyby', 15.0, 'En route', '2026-06-01', 
    #      datetime.now().isoformat())
    # ]
    
    # cursor.executemany('''
    #     INSERT INTO spacecraft 
    #     (name, name_en, wikipedia_url, wikipedia_url_en, launch_date, 
    #      target_body, status, trajectory_type, launch_speed, current_phase, 
    #      arrival_time, last_update)
    #     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    # ''', new_spacecraft)
    
    # Display current spacecraft status
    print("\nCurrent Spacecraft Status:")
    print("-" * 100)
    cursor.execute('SELECT name, name_en, status, current_phase, launch_date FROM spacecraft ORDER BY launch_date')
    spacecraft = cursor.fetchall()
    
    for sc in spacecraft:
        print(f"{sc[0]} ({sc[1]}): {sc[2]} | {sc[3]} | Launched: {sc[4]}")
    
    conn.commit()
    conn.close()
    
    print("\nDatabase update completed!")

def update_mission_phases():
    """
    Update mission phases based on current date.
    This function can be extended to automatically update phases
    based on arrival times and current dates.
    """
    conn = sqlite3.connect('solar_system.db')
    cursor = conn.cursor()
    
    current_date = datetime.now()
    
    print("Checking mission phases...")
    
    # Get spacecraft with arrival times
    cursor.execute('''
        SELECT id, name, arrival_time, current_phase, status
        FROM spacecraft
        WHERE arrival_time IS NOT NULL AND status = 'active'
    ''')
    
    spacecraft = cursor.fetchall()
    
    for sc in spacecraft:
        sc_id, name, arrival_str, current_phase, status = sc
        if arrival_str:
            try:
                arrival_date = datetime.strptime(arrival_str, '%Y-%m-%d')
                
                if current_date >= arrival_date:
                    # Spacecraft has arrived
                    if current_phase == 'En route':
                        new_phase = 'Arrived'
                        cursor.execute('''
                            UPDATE spacecraft
                            SET current_phase = ?, last_update = ?
                            WHERE id = ?
                        ''', (new_phase, current_date.isoformat(), sc_id))
                        print(f"Updated {name}: {new_phase}")
                
            except ValueError as e:
                print(f"Error parsing arrival date for {name}: {e}")
    
    conn.commit()
    conn.close()
    
    print("Mission phase update completed!")

def add_new_spacecraft(name, name_en, wikipedia_url, wikipedia_url_en, 
                       launch_date, target_body, status, trajectory_type,
                       launch_speed, current_phase, arrival_time=None):
    """
    Add a new spacecraft to the database.
    
    Parameters:
    - name: Spacecraft name in Chinese
    - name_en: Spacecraft name in English
    - wikipedia_url: Chinese Wikipedia URL
    - wikipedia_url_en: English Wikipedia URL
    - launch_date: Launch date in YYYY-MM-DD format
    - target_body: Target planet/body
    - status: 'active' or 'inactive'
    - trajectory_type: e.g., 'flyby', 'orbiter', 'lander', 'rover'
    - launch_speed: Launch speed relative to Earth in km/s
    - current_phase: Current mission phase
    - arrival_time: Arrival time in YYYY-MM-DD format (optional)
    """
    
    conn = sqlite3.connect('solar_system.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO spacecraft 
        (name, name_en, wikipedia_url, wikipedia_url_en, launch_date, 
         target_body, status, trajectory_type, launch_speed, current_phase, 
         arrival_time, last_update)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, name_en, wikipedia_url, wikipedia_url_en, launch_date, 
          target_body, status, trajectory_type, launch_speed, current_phase, 
          arrival_time, datetime.now().isoformat()))
    
    conn.commit()
    conn.close()
    
    print(f"Successfully added spacecraft: {name} ({name_en})")

if __name__ == '__main__':
    print("Solar System Database Update Tool")
    print("=" * 50)
    print("\nOptions:")
    print("1. Update spacecraft status (edit the script first)")
    print("2. Update mission phases automatically")
    print("3. Display current spacecraft list")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == '1':
        print("\nTo update spacecraft status, edit the 'updates' list in this script")
        print("and run it again.")
        update_spacecraft_status()
    elif choice == '2':
        update_mission_phases()
    elif choice == '3':
        conn = sqlite3.connect('solar_system.db')
        cursor = conn.cursor()
        cursor.execute('SELECT name, name_en, status, current_phase, launch_date FROM spacecraft ORDER BY launch_date')
        spacecraft = cursor.fetchall()
        
        print("\nCurrent Spacecraft List:")
        print("-" * 100)
        for sc in spacecraft:
            print(f"{sc[0]} ({sc[1]}): {sc[2]} | {sc[3]} | Launched: {sc[4]}")
        
        conn.close()
    else:
        print("Invalid choice. Exiting.")
