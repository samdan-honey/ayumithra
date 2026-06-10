import sqlite3
import os

def init_database():
    """Initialize SQLite database with tables and data"""
   
    # Remove existing database if present
    db_path = 'database/health_app.db'
    if os.path.exists(db_path):
        os.remove(db_path)
   
    # Create database directory if it doesn't exist
    os.makedirs('database', exist_ok=True)
   
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
   
    # Create tables
    cursor.execute('''
        CREATE TABLE diseases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            precautions TEXT,
            severity_level TEXT,
            recommended_action TEXT
        )
    ''')
   
    cursor.execute('''
        CREATE TABLE symptoms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')
   
    cursor.execute('''
        CREATE TABLE disease_symptoms (
            disease_id INTEGER,
            symptom_id INTEGER,
            FOREIGN KEY (disease_id) REFERENCES diseases(id),
            FOREIGN KEY (symptom_id) REFERENCES symptoms(id),
            PRIMARY KEY (disease_id, symptom_id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (username) REFERENCES users(username)
        )
    ''')
    
    # Hash default password "admin123" using SHA-256
    import hashlib
    default_password_hash = hashlib.sha256(b"admin123").hexdigest()
    cursor.execute('''
        INSERT OR IGNORE INTO users (username, password)
        VALUES (?, ?)
    ''', ('admin', default_password_hash))
   
    # Insert diseases
    diseases_data = [
        ('Flu',
         'Influenza is a viral infection that attacks your respiratory system.',
         'Rest, stay hydrated, take fever reducers, avoid contact with others, get vaccinated annually',
         'Moderate',
         'Rest at home, monitor symptoms. Seek medical care if symptoms worsen or persist beyond 7 days.'),
       
        ('Common Cold',
         'A viral infection of your nose and throat (upper respiratory tract).',
         'Rest, drink fluids, gargle salt water, use humidifier, take vitamin C',
         'Mild',
         'Self-care at home. See doctor if symptoms last more than 10 days or worsen.'),
       
        ('Migraine',
         'A headache of varying intensity, often accompanied by nausea and sensitivity to light and sound.',
         'Rest in dark quiet room, apply cold compress, avoid triggers, stay hydrated, manage stress',
         'Moderate',
         'Take pain relievers early. Consult neurologist if migraines are frequent or severe.'),
       
        ('Food Poisoning',
         'Illness caused by eating contaminated food, usually by bacteria, viruses, or parasites.',
         'Stay hydrated, eat bland foods, avoid dairy and fatty foods, wash hands frequently',
         'Moderate',
         'Rest and hydrate. Seek immediate care if severe dehydration, bloody stools, or high fever occur.'),
       
        ('COVID-19',
         'Coronavirus disease caused by SARS-CoV-2 virus affecting the respiratory system.',
         'Isolate, rest, stay hydrated, monitor oxygen levels, take prescribed medications, get vaccinated',
         'High',
         'Isolate immediately. Monitor symptoms closely. Seek emergency care if breathing difficulty, chest pain, or confusion occur.'),
       
        ('Dengue',
         'Mosquito-borne viral infection causing flu-like illness, can develop into severe dengue.',
         'Rest, drink plenty of fluids, take paracetamol for fever, avoid aspirin, use mosquito nets',
         'High',
         'Hospitalization may be required. Seek immediate medical attention if severe abdominal pain, persistent vomiting, or bleeding occurs.'),
       
        ('Malaria',
         'Mosquito-borne disease caused by Plasmodium parasites.',
         'Complete full course of antimalarial medication, rest, stay hydrated, use mosquito nets, take preventive medication in endemic areas',
         'High',
         'Seek immediate medical treatment. Malaria requires prescription antimalarial drugs and medical monitoring.')
    ]
   
    cursor.executemany('''
        INSERT INTO diseases (name, description, precautions, severity_level, recommended_action)
        VALUES (?, ?, ?, ?, ?)
    ''', diseases_data)
   
    # Insert symptoms
    symptoms_list = [
        'Fever', 'Cough', 'Sore Throat', 'Runny Nose', 'Sneezing',
        'Body Aches', 'Fatigue', 'Headache', 'Chills', 'Nausea',
        'Vomiting', 'Diarrhea', 'Abdominal Pain', 'Loss of Taste',
        'Loss of Smell', 'Shortness of Breath', 'Chest Pain',
        'Sensitivity to Light', 'Sensitivity to Sound', 'Dizziness',
        'Rash', 'Joint Pain', 'Muscle Pain', 'Sweating', 'Loss of Appetite'
    ]
   
    cursor.executemany('INSERT INTO symptoms (name) VALUES (?)',
                      [(symptom,) for symptom in symptoms_list])
   
    # Map symptoms to diseases (disease_id, symptom_id)
    # Flu: 1
    flu_symptoms = [1, 2, 3, 6, 7, 8, 9, 23]
   
    # Common Cold: 2
    cold_symptoms = [2, 3, 4, 5, 7, 8, 10]
   
    # Migraine: 3
    migraine_symptoms = [8, 10, 18, 19, 20, 17]
   
    # Food Poisoning: 4
    food_poisoning_symptoms = [10, 11, 12, 13, 1, 6, 25]
   
    # COVID-19: 5
    covid_symptoms = [1, 2, 7, 14, 15, 16, 8, 3, 6, 23]
   
    # Dengue: 6
    dengue_symptoms = [1, 8, 6, 21, 22, 10, 7, 13, 17]
   
    # Malaria: 7
    malaria_symptoms = [1, 9, 24, 8, 6, 10, 11, 7, 25, 22]
   
    # Insert disease-symptom mappings
    all_mappings = []
    all_mappings.extend([(1, s) for s in flu_symptoms])
    all_mappings.extend([(2, s) for s in cold_symptoms])
    all_mappings.extend([(3, s) for s in migraine_symptoms])
    all_mappings.extend([(4, s) for s in food_poisoning_symptoms])
    all_mappings.extend([(5, s) for s in covid_symptoms])
    all_mappings.extend([(6, s) for s in dengue_symptoms])
    all_mappings.extend([(7, s) for s in malaria_symptoms])
   
    cursor.executemany('''
        INSERT INTO disease_symptoms (disease_id, symptom_id)
        VALUES (?, ?)
    ''', all_mappings)
   
    conn.commit()
    conn.close()
   
    print("Database initialized successfully!")
    print(f"Created {len(diseases_data)} diseases")
    print(f"Created {len(symptoms_list)} symptoms")
    print(f"Created {len(all_mappings)} disease-symptom mappings")

if __name__ == '__main__':
    init_database()
