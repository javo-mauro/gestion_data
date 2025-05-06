import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import json
import plotly.express as px
import plotly.graph_objects as go
from twilio.rest import Client
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

st.set_page_config(
    page_title="KittyPaw Analytics",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Twilio configuration
TWILIO_ACCOUNT_SID = 'YOUR_TWILIO_SID'  # Add to environment variables
TWILIO_AUTH_TOKEN = 'YOUR_TWILIO_TOKEN'  # Add to environment variables
WHATSAPP_NUMBERS = ['+56979099687', '+56990819190']

# SendGrid configuration
SENDGRID_API_KEY = 'YOUR_SENDGRID_API_KEY'  # Add to environment variables
EMAIL_TO = 'javomauro.contacto@gmail.com'

def send_whatsapp_message(message):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    for number in WHATSAPP_NUMBERS:
        try:
            client.messages.create(
                body=message,
                from_='whatsapp:+14155238886',  # Your Twilio WhatsApp number
                to=f'whatsapp:{number}'
            )
        except Exception as e:
            st.error(f"Error sending WhatsApp to {number}: {str(e)}")

def send_email(message):
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        email = Mail(
            from_email='your-verified-sender@domain.com',
            to_emails=EMAIL_TO,
            subject='Dashboard Report Summary',
            plain_text_content=message
        )
        sg.send(email)
    except Exception as e:
        st.error(f"Error sending email: {str(e)}")


# Configuración personalizada
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #FFFFFF;
        border-radius: 4px;
        color: #000000;
        font-size: 14px;
        font-weight: 400;
        align-items: center;
        justify-content: center;
        border: none;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        background-color: #4CAF50;
        color: white;
    }
    .metric-container {
        background-color: white;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .dataframe {
        font-size: 12px;
    }
    </style>
""", unsafe_allow_html=True)

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
    data = {}
    required_files = {
        'devices': "devices.csv",
        'mqtt': "mqtt_connections.csv",
        'owners': "pet_owners.csv",
        'pets': "pets.csv",
        'sensor_data': "sensor_data.csv",
        'users': "users.csv"
    }
    
    try:
        for key, file in required_files.items():
            if not os.path.exists(file):
                st.error(f"Archivo no encontrado: {file}")
                return None, None, None, None, None, None
            data[key] = pd.read_csv(file)
            
        # Process timestamps and data
        if 'timestamp' in data['sensor_data'].columns:
            data['sensor_data']['timestamp'] = pd.to_datetime(data['sensor_data']['timestamp'])
        if 'data' in data['sensor_data'].columns:
            data['sensor_data']['data_dict'] = data['sensor_data']['data'].apply(lambda x: json.loads(x.replace("'", "\"")))
            data['sensor_data']['value'] = data['sensor_data']['data_dict'].apply(lambda x: x.get('value'))
            data['sensor_data']['unit'] = data['sensor_data']['data_dict'].apply(lambda x: x.get('unit'))
            
        return data['devices'], data['mqtt'], data['owners'], data['pets'], data['sensor_data'], data['users']
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

    # Imagen del resumen del dashboard
    st.image("https://raw.githubusercontent.com/your-repo/dashboard-summary.png", 
             caption="Resumen del Dashboard")

    # Sección de envío de mensajes
    st.header("📱 Enviar Resumen")

    # Campo de comentarios
    message = st.text_area(
        "Comentarios adicionales",
        height=150,
        placeholder="Ingrese sus comentarios aquí..."
    )

    # Generar resumen automático
    dashboard_summary = f"""
    🐾 KittyPaw Dashboard - Resumen

    Dispositivos Activos: {len(devices[devices['status'] == 'online'])}
    Total Mascotas: {len(pets)}
    Últimas Mediciones: {len(sensor_data)}

    Comentarios: {message}
    """

    # Botón de envío
    if st.button('📲 Enviar Resumen a WhatsApp y Email'):
        with st.spinner('Enviando mensajes...'):
            send_whatsapp_message(dashboard_summary)
            send_email(dashboard_summary)
            st.success('✅ Resumen enviado exitosamente!')

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
    st.title("📊 Panel de Análisis de Datos")

    # Tabs para diferentes tipos de análisis
    tab1, tab2, tab3, tab4 = st.tabs(["📱 Dispositivos", "🐾 Mascotas", "📊 Sensores", "📈 Tendencias"])

    with tab1:
        st.subheader("Análisis de Dispositivos")

        # KPIs de dispositivos
        cols = st.columns(4)
        cols[0].metric("Dispositivos Totales", len(devices))
        cols[1].metric("Dispositivos Online", len(devices[devices['status'] == 'online']))
        cols[2].metric("Batería Promedio", f"{devices['battery_level'].mean():.1f}%")
        cols[3].metric("Dispositivos Críticos", len(devices[devices['battery_level'] < 20]))

        # Tabla interactiva de dispositivos
        st.dataframe(
            devices[['name', 'device_id', 'status', 'battery_level', 'type']],
            use_container_width=True,
            hide_index=True
        )

    with tab2:
        st.subheader("Análisis de Mascotas")

        # Filtros de mascotas
        species_filter = st.multiselect("Filtrar por Especie", pets['species'].unique())
        filtered_pets = pets if not species_filter else pets[pets['species'].isin(species_filter)]

        # Estadísticas de mascotas
        cols = st.columns(3)
        cols[0].metric("Total Mascotas", len(filtered_pets))
        cols[1].metric("Con Vacunas", len(filtered_pets[filtered_pets['has_vaccinations']]))
        cols[2].metric("Con Enfermedades", len(filtered_pets[filtered_pets['has_diseases']]))

        # Tabla detallada de mascotas
        st.dataframe(
            filtered_pets[['name', 'species', 'breed', 'birth_date', 'has_vaccinations']],
            use_container_width=True,
            hide_index=True
        )

    with tab3:
        st.subheader("Análisis de Sensores")

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

        # Datos filtrados
        filtered_data = sensor_data[
            (sensor_data['device_id'] == selected_device) &
            (sensor_data['sensor_type'] == sensor_type)
        ].copy()
        filtered_data['timestamp'] = pd.to_datetime(filtered_data['timestamp'])

        # Estadísticas del sensor
        if not filtered_data.empty:
            stats = filtered_data['value'].describe()
            cols = st.columns(4)
            cols[0].metric("Promedio", f"{stats['mean']:.2f}")
            cols[1].metric("Mínimo", f"{stats['min']:.2f}")
            cols[2].metric("Máximo", f"{stats['max']:.2f}")
            cols[3].metric("Mediciones", int(stats['count']))

            # Gráfico temporal
            st.line_chart(
                filtered_data.set_index('timestamp')['value'],
                use_container_width=True
            )

    with tab4:
        st.subheader("Análisis de Tendencias")

        # Selección de período
        period = st.selectbox(
            "Seleccionar Período",
            ["Última Hora", "Último Día", "Última Semana", "Último Mes"]
        )

        # Análisis de tendencias por tipo de sensor
        trends = sensor_data.groupby('sensor_type').agg({
            'value': ['mean', 'min', 'max', 'count']
        }).round(2)

        st.dataframe(
            trends,
            use_container_width=True
        )

        # Exportar datos
        if st.button("📥 Exportar Análisis"):
            trends.to_csv("analisis_tendencias.csv")
            st.success("Análisis exportado exitosamente!")



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
                    
    # Gráfico de línea temporal
    filtered_data = sensor_data[sensor_data['device_id'] == selected_device]
    fig = px.line(
        filtered_data,
        x='timestamp',
        y='value',
        title=f"Mediciones del dispositivo {selected_device}"
    )
    st.plotly_chart(fig)

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