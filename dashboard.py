import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import json

st.set_page_config(
    page_title="KittyPaw Dashboard",
    page_icon="🐾",
    layout="wide"
)

@st.cache_data(ttl=300)  # Cache por 5 minutos
def load_data():
    try:
        devices = pd.read_csv("devices.csv")
        mqtt = pd.read_csv("mqtt_connections.csv")
        owners = pd.read_csv("pet_owners.csv")
        pets = pd.read_csv("pets.csv")
        sensor_data = pd.read_csv("sensor_data.csv")
        users = pd.read_csv("users.csv")
    except Exception as e:
        st.error(f"Error al cargar datos: {str(e)}")
        return None, None, None, None, None, None

    if 'timestamp' in sensor_data.columns:
        sensor_data['timestamp'] = pd.to_datetime(sensor_data['timestamp'], errors='coerce')
        sensor_data['data_dict'] = sensor_data['data'].apply(lambda x: json.loads(x.replace("'", "\"")))
        sensor_data['value'] = sensor_data['data_dict'].apply(lambda x: x.get('value'))
        sensor_data['unit'] = sensor_data['data_dict'].apply(lambda x: x.get('unit'))

    if 'timestamp' in mqtt.columns:
        mqtt['timestamp'] = pd.to_datetime(mqtt['timestamp'], errors='coerce')
    if 'created_at' in users.columns:
        users['created_at'] = pd.to_datetime(users['created_at'], errors='coerce')

    return devices, mqtt, owners, pets, sensor_data, users

devices, mqtt, owners, pets, sensor_data, users = load_data()

# Inicio
def home_page():
    st.title("🐾 KittyPaw - Dashboard General")
    st.markdown("### Resumen General del Sistema")

    col1, col2, col3 = st.columns(3)
    col1.metric("🔌 Dispositivos", len(devices))
    col2.metric("🐶 Mascotas", len(pets))
    col3.metric("📈 Registros de Sensores", len(sensor_data))

    col4, col5, col6 = st.columns(3)
    col4.metric("👤 Dueños", len(owners))
    col5.metric("🧑‍💻 Usuarios", len(users))
    col6.metric("🔗 Conexiones MQTT", len(mqtt))

    st.markdown("---")
    st.subheader("🕒 Últimas Actividades")

    col1, col2, col3 = st.columns(3)
    col1.write(f"📡 Sensor: {sensor_data['timestamp'].max().strftime('%Y-%m-%d %H:%M') if 'timestamp' in sensor_data else 'N/A'}")
    col2.write(f"📶 MQTT: {mqtt['timestamp'].max().strftime('%Y-%m-%d %H:%M') if 'timestamp' in mqtt else 'N/A'}")
    col3.write(f"👥 Usuario: {users['created_at'].max().strftime('%Y-%m-%d') if 'created_at' in users else 'N/A'}")

# Visualización
def data_page():
    st.title("📊 Visualización de Datos de Sensores")
    if sensor_data.empty:
        st.warning("No hay datos de sensores disponibles.")
        return

    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("Últimos 20 registros")
        st.dataframe(
            sensor_data[['device_id', 'sensor_type', 'value', 'unit', 'timestamp']]
            .sort_values(by="timestamp", ascending=False)
            .head(20)
            .style.highlight_max(['value'], color='lightgreen')
        )
    
    with col2:
        st.subheader("Resumen Estadístico")
        st.write("Promedio por tipo de sensor:")
        stats = sensor_data.groupby('sensor_type')['value'].mean().round(2)
        st.table(stats)

    sensor_type = st.selectbox("Filtrar por tipo de sensor:", sensor_data['sensor_type'].dropna().unique())
    filtered = sensor_data[sensor_data['sensor_type'] == sensor_type]

    if not filtered.empty:
        st.line_chart(filtered.set_index('timestamp')['value'])

# Dispositivos
def devices_page():
    st.title("📱 Dispositivos Registrados")
    st.dataframe(devices)

    if 'battery_level' in devices.columns:
        st.bar_chart(devices.set_index('name')['battery_level'])

# Mascotas
def pets_page():
    st.title("🐕 Información de Mascotas")
    st.dataframe(pets)

    if 'species' in pets.columns:
        species_count = pets['species'].value_counts()
        st.write("Distribución por especie:")
        fig, ax = plt.subplots()
        ax.pie(species_count, labels=species_count.index, autopct="%1.1f%%")
        st.pyplot(fig)

# Usuarios
def users_page():
    st.title("👥 Usuarios y Dueños")

    st.subheader("🧑‍💻 Usuarios del Sistema")
    if not users.empty:
        user_cols = ['username', 'email', 'password', 'is_admin'] if all(col in users.columns for col in ['username', 'email', 'password', 'is_admin']) else users.columns
        st.dataframe(users[user_cols])

    st.subheader("👤 Dueños Registrados")
    if not owners.empty:
        owner_cols = ['name', 'email', 'password'] if all(col in owners.columns for col in ['name', 'email', 'password']) else owners.columns
        st.dataframe(owners[owner_cols])

# Navegación
st.sidebar.title("📁 Menú de Navegación")
page = st.sidebar.radio("Selecciona una opción:", [
    "Inicio",
    "Visualización de Datos",
    "Dispositivos",
    "Mascotas",
    "Usuarios"
])

if page == "Inicio":
    home_page()
elif page == "Visualización de Datos":
    data_page()
elif page == "Dispositivos":
    devices_page()
elif page == "Mascotas":
    pets_page()
elif page == "Usuarios":
    users_page()


