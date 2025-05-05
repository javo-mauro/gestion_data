
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import json
import plotly.express as px
import plotly.graph_objects as go

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

def get_device_stats(device_id):
    device_data = sensor_data[sensor_data['device_id'] == device_id]
    stats = {}
    for sensor_type in device_data['sensor_type'].unique():
        type_data = device_data[device_data['sensor_type'] == sensor_type]['value']
        stats[sensor_type] = {
            'min': type_data.min(),
            'max': type_data.max(),
            'avg': type_data.mean(),
            'count': len(type_data)
        }
    return stats

def home_page():
    st.title("🐾 KittyPaw - Panel de Control")
    
    # Enlaces externos
    st.markdown("### 🔗 Enlaces Importantes")
    col1, col2 = st.columns(2)
    with col1:
        st.link_button("📋 Ver Diagrama en Miro", "https://miro.com/app/board/uXjVI-oKwLk=/", use_container_width=True)
    with col2:
        st.link_button("📁 Acceder a Google Drive", "https://drive.google.com/drive/home", use_container_width=True)
    
    st.markdown("---")
    
    # Primera fila - Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🔌 Dispositivos Activos", len(devices[devices['status'] == 'online']))
    col2.metric("🐶 Mascotas Registradas", len(pets))
    col3.metric("👤 Dueños", len(owners))
    col4.metric("📊 Total Mediciones", len(sensor_data))

    # Segunda fila - Gráficos resumen
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Estado de Dispositivos")
        device_status = devices['status'].value_counts()
        fig = go.Figure(data=[go.Pie(labels=device_status.index, values=device_status.values)])
        st.plotly_chart(fig)

    with col2:
        st.subheader("Nivel de Batería por Dispositivo")
        fig = px.bar(devices, x='name', y='battery_level', title="Nivel de Batería")
        st.plotly_chart(fig)

    # Tercera fila - Últimas mediciones
    st.subheader("📊 Últimas Mediciones por Tipo de Sensor")
    latest_readings = sensor_data.groupby('sensor_type').agg({
        'value': ['mean', 'min', 'max', 'count']
    }).round(2)
    latest_readings.columns = ['Promedio', 'Mínimo', 'Máximo', 'Total Mediciones']
    st.dataframe(latest_readings)

def data_page():
    st.title("📊 Visualización de Datos de Sensores")

    # Filtros
    col1, col2 = st.columns(2)
    with col1:
        selected_device = st.selectbox(
            "Seleccionar Dispositivo",
            devices['device_id'].unique()
        )
    with col2:
        sensor_type = st.selectbox(
            "Tipo de Sensor",
            sensor_data['sensor_type'].unique()
        )

    filtered_data = sensor_data[
        (sensor_data['device_id'] == selected_device) &
        (sensor_data['sensor_type'] == sensor_type)
    ]

    # Mostrar estadísticas
    col1, col2, col3, col4 = st.columns(4)
    stats = filtered_data['value'].describe()
    col1.metric("Promedio", f"{stats['mean']:.2f}")
    col2.metric("Mínimo", f"{stats['min']:.2f}")
    col3.metric("Máximo", f"{stats['max']:.2f}")
    col4.metric("Total Mediciones", int(stats['count']))

    # Gráfico de línea temporal
    fig = px.line(
        filtered_data,
        x='timestamp',
        y='value',
        title=f"Mediciones de {sensor_type} - {selected_device}"
    )
    st.plotly_chart(fig)

    # Tabla de datos
    st.subheader("Últimas Mediciones")
    st.dataframe(
        filtered_data[['timestamp', 'value', 'unit']]
        .sort_values('timestamp', ascending=False)
        .head(20)
    )

def devices_page():
    st.title("📱 Dispositivos")
    
    # Resumen de dispositivos
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Estado de Dispositivos")
        status_counts = devices['status'].value_counts()
        fig = px.pie(names=status_counts.index, values=status_counts.values)
        st.plotly_chart(fig)

    with col2:
        st.subheader("Nivel de Batería")
        fig = px.bar(devices, x='name', y='battery_level')
        st.plotly_chart(fig)

    # Detalles por dispositivo
    st.subheader("Detalles de Dispositivos")
    for _, device in devices.iterrows():
        with st.expander(f"📱 {device['name']} ({device['device_id']})"):
            col1, col2, col3 = st.columns(3)
            col1.metric("Estado", device['status'])
            col2.metric("Batería", f"{device['battery_level']}%")
            col3.metric("Tipo", device['type'])
            
            # Estadísticas de sensores
            stats = get_device_stats(device['device_id'])
            if stats:
                st.subheader("Estadísticas de Sensores")
                for sensor_type, stat in stats.items():
                    st.write(f"**{sensor_type}**")
                    st.write(f"- Promedio: {stat['avg']:.2f}")
                    st.write(f"- Mín: {stat['min']:.2f}")
                    st.write(f"- Máx: {stat['max']:.2f}")
                    st.write(f"- Total mediciones: {stat['count']}")

def pets_page():
    st.title("🐕 Mascotas")
    
    # Resumen de mascotas
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Distribución por Especie")
        species_count = pets['species'].value_counts()
        fig = px.pie(names=species_count.index, values=species_count.values)
        st.plotly_chart(fig)
    
    with col2:
        st.subheader("Distribución por Raza")
        breed_count = pets['breed'].value_counts().head(10)
        fig = px.bar(x=breed_count.index, y=breed_count.values)
        st.plotly_chart(fig)

    # Lista de mascotas
    st.subheader("Lista de Mascotas")
    for _, pet in pets.iterrows():
        with st.expander(f"🐾 {pet['name']}"):
            col1, col2, col3 = st.columns(3)
            col1.write(f"**Especie:** {pet['species']}")
            col2.write(f"**Raza:** {pet['breed']}")
            col3.write(f"**Edad:** {pet['age']} años")

def users_page():
    st.title("👥 Usuarios y Dueños")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🧑‍💻 Usuarios del Sistema")
        admin_count = users['is_admin'].value_counts()
        fig = px.pie(
            names=['Administradores', 'Usuarios Normales'],
            values=[admin_count.get(True, 0), admin_count.get(False, 0)]
        )
        st.plotly_chart(fig)
        st.dataframe(users[['username', 'email', 'is_admin']])
    
    with col2:
        st.subheader("👤 Dueños de Mascotas")
        st.metric("Total Dueños", len(owners))
        st.dataframe(owners[['name', 'email']])

# Navegación
st.sidebar.title("📁 Menú de Navegación")
language = st.sidebar.selectbox("Idioma / Language", ["Español", "English"])

if language == "Español":
    pages = {
        "Inicio": home_page,
        "Visualización de Datos": data_page,
        "Dispositivos": devices_page,
        "Mascotas": pets_page,
        "Usuarios": users_page
    }
else:
    pages = {
        "Home": home_page,
        "Data Visualization": data_page,
        "Devices": devices_page,
        "Pets": pets_page,
        "Users": users_page
    }

page = st.sidebar.radio("Selecciona una página:", list(pages.keys()))
pages[page]()
