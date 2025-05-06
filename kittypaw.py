
import pandas as pd
from sqlalchemy import create_engine
import logging
import os
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Datos de conexión
user = 'neondb_owner'
password = 'npg_haLf64lsGvBr'
host = 'ep-royal-voice-a4nxjivp.us-east-1.aws.neon.tech'
port = '5432'
dbname = 'neondb'

def connect_to_db():
    try:
        DATABASE_URL = f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}?sslmode=require'
        engine = create_engine(DATABASE_URL)
        return engine
    except Exception as e:
        logging.error(f"Error connecting to database: {e}")
        return None

def validate_and_save_data(df, tabla):
    try:
        # Validate data is not empty
        if df.empty:
            logging.warning(f"No data found for table {tabla}")
            return False
            
        # Save data
        csv_path = f'{tabla}.csv'
        df.to_csv(csv_path, index=False)
        logging.info(f'Tabla "{tabla}" guardada como {csv_path}')
        return True
    except Exception as e:
        logging.error(f'Error saving table {tabla}: {e}')
        return False

def main():
    # Create backup of existing files
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    for file in os.listdir('.'):
        if file.endswith('.csv'):
            try:
                os.rename(file, f'backup_{timestamp}_{file}')
            except Exception as e:
                logging.warning(f"Could not backup {file}: {e}")

    # Connect to database
    engine = connect_to_db()
    if not engine:
        logging.error("Could not connect to database. Exiting.")
        return

    # Lista de tablas
    tablas = [
        'devices',
        'mqtt_connections',
        'pet_owners',
        'pets',
        'sensor_data',
        'users'
    ]

    success_count = 0
    for tabla in tablas:
        try:
            df = pd.read_sql(f'SELECT * FROM {tabla}', engine)
            if validate_and_save_data(df, tabla):
                success_count += 1
        except Exception as e:
            logging.error(f'Error processing table "{tabla}": {e}')

    logging.info(f"Update completed. {success_count}/{len(tablas)} tables updated successfully.")

if __name__ == "__main__":
    main()
