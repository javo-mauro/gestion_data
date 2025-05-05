
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import json
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="KittyPaw Dashboard",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuración de tema personalizado
st.markdown("""
    <style>
    .stApp {
        background-color: #f5f7f9;
    }
    .css-1d391kg {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .metric-card {
        background-color: white;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

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

def update_data():
    try:
        import subprocess
        subprocess.run(['python', 'kittypaw.py'], check=True)
        st.success('¡Datos actualizados exitosamente!')
        st.rerun()
    except Exception as e:
        st.error(f'Error al actualizar datos: {str(e)}')

def home_page():
    st.title("🐾 KittyPaw - Panel de Control")
    
    # Botón de actualización
    if st.button('🔄 Actualizar Datos'):
        update_data()
    
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
        device_status = devices['status'].value_counts().reset_index()
        device_status.columns = ['Estado', 'Cantidad']
        st.dataframe(device_status)
        st.caption(f"Total dispositivos: {len(devices)}")

    with col2:
        st.subheader("Nivel de Batería por Dispositivo")
        battery_data = devices[['name', 'battery_level']].sort_values('battery_level', ascending=False)
        battery_data.columns = ['Dispositivo', 'Nivel de Batería']
        st.dataframe(battery_data)
        st.caption(f"Promedio de batería: {battery_data['Nivel de Batería'].mean():.1f}%")

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
        status_data = devices['status'].value_counts().reset_index()
        status_data.columns = ['Estado', 'Cantidad']
        st.dataframe(status_data)

    with col2:
        st.subheader("Nivel de Batería")
        battery_stats = devices.agg({
            'battery_level': ['min', 'max', 'mean']
        }).round(2)
        battery_stats.columns = ['Valor']
        battery_stats.index = ['Mínimo', 'Máximo', 'Promedio']
        st.dataframe(battery_stats)

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
        species_data = pets['species'].value_counts().reset_index()
        species_data.columns = ['Especie', 'Cantidad']
        st.dataframe(species_data)
        st.caption(f"Total mascotas: {len(pets)}")
    
    with col2:
        st.subheader("Top 10 Razas")
        breed_data = pets['breed'].value_counts().head(10).reset_index()
        breed_data.columns = ['Raza', 'Cantidad']
        st.dataframe(breed_data)
        st.caption(f"Total razas únicas: {len(pets['breed'].unique())}")

    # Lista de mascotas
    st.subheader("Lista de Mascotas")
    for _, pet in pets.iterrows():
        with st.expander(f"🐾 {pet['name']}"):
            col1, col2, col3 = st.columns(3)
            col1.write(f"**Especie:** {pet['species']}")
            col2.write(f"**Raza:** {pet['breed']}")
            col3.write(f"**Edad:** {pet['age']} años")

def scrum_board():
    st.title("📋 Scrum Board")
    
    # Épicas del proyecto
    st.header("📌 Épicas del Proyecto")
    epicas = {
        "Monitoreo de Mascotas": "Implementación del sistema de seguimiento y monitoreo de mascotas",
        "Gestión de Dispositivos": "Sistema de administración de dispositivos IoT",
        "Análisis de Datos": "Procesamiento y visualización de datos de sensores",
        "Experiencia de Usuario": "Mejora continua de la interfaz y experiencia de usuario"
    }
    
    for epic, desc in epicas.items():
        with st.expander(f"🎯 {epic}"):
            st.write(desc)
            
    # Sprint actual
    st.header("🏃‍♂️ Sprint Actual")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Sprint Progress")
        sprint_progress = st.progress(0.65)
        st.caption("Sprint 3: 65% Completado")
        
    with col2:
        st.subheader("⏱️ Timeframe")
        st.info("Sprint 3: 1 Mayo - 15 Mayo 2025")
    
    # Tablero Kanban
    st.header("📌 Tablero Kanban")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("### 📝 To Do")
        tasks_todo = [
            "Implementar alertas de batería baja",
            "Diseñar dashboard de análisis avanzado",
            "Optimizar consumo de datos"
        ]
        for task in tasks_todo:
            st.warning(task)
            
    with col2:
        st.markdown("### 🔄 In Progress")
        tasks_progress = [
            "Mejorar UX del dashboard",
            "Implementar filtros avanzados"
        ]
        for task in tasks_progress:
            st.info(task)
            
    with col3:
        st.markdown("### 👀 Review")
        tasks_review = [
            "API de notificaciones",
            "Sistema de autenticación"
        ]
        for task in tasks_review:
            st.success(task)
            
    with col4:
        st.markdown("### ✅ Done")
        tasks_done = [
            "Conexión con base de datos",
            "Sistema básico de monitoreo",
            "Registro de dispositivos"
        ]
        for task in tasks_done:
            st.success(task)
            
    # Burndown Chart
    st.header("📉 Burndown Chart")
    burndown_data = pd.DataFrame({
        'Día': range(1, 11),
        'Ideal': [20, 18, 16, 14, 12, 10, 8, 6, 4, 2],
        'Real': [20, 19, 17, 15, 14, 13, 11, 10, 8, 7]
    })
    
    fig = px.line(burndown_data, x='Día', y=['Ideal', 'Real'],
                  title='Sprint Burndown Chart')
    st.plotly_chart(fig)
    
    # Retrospectiva
    st.header("🔄 Retrospectiva del Sprint Anterior")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("✨ Lo que funcionó bien")
        st.write("- Implementación del sistema base")
        st.write("- Colaboración del equipo")
        st.write("- Calidad del código")
        
    with col2:
        st.subheader("🎯 Áreas de mejora")
        st.write("- Tiempo de respuesta del servidor")
        st.write("- Documentación del código")
        st.write("- Pruebas automatizadas")

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
pages = {
    "🏠 Inicio": home_page,
    "📊 Visualización de Datos": data_page,
    "📱 Dispositivos": devices_page,
    "🐾 Mascotas": pets_page,
    "👥 Usuarios": users_page,
    "📋 Scrum Board": scrum_board
}

page = st.sidebar.radio("Selecciona una página:", list(pages.keys()))
pages[page]()
