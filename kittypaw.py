import pandas as pd
from sqlalchemy import create_engine

# Datos de conexión
user = 'neondb_owner'
password = 'npg_haLf64lsGvBr'
host = 'ep-royal-voice-a4nxjivp.us-east-1.aws.neon.tech'
port = '5432'
dbname = 'neondb'

# Crear cadena de conexión
DATABASE_URL = f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}?sslmode=require'

# Crear motor de conexión
engine = create_engine(DATABASE_URL)

# Lista de tablas
tablas = [
    'devices',
    'mqtt_connections',
    'pet_owners',
    'pets',
    'sensor_data',
    'users'
]

# Leer y guardar cada tabla en un archivo CSV
for tabla in tablas:
    try:
        df = pd.read_sql(f'SELECT * FROM {tabla}', engine)
        df.to_csv(f'{tabla}.csv', index=False)
        print(f'Tabla "{tabla}" guardada como {tabla}.csv')
    except Exception as e:
        print(f'Error al leer o guardar la tabla "{tabla}": {e}')
