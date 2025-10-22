import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

# --- Configuración de la Página de Streamlit ---
st.set_page_config(layout="wide")
st.title("Dashboard de Rendimiento Estudiantil")

# --- 1. Preparar los Datos (Función de caché igual) ---
@st.cache_data
def load_data():
    x_labels = [
        'Ciencias Adminitrativas', 'Ciencias Biológicas', 'Ciencias Contables', 'Ciencias Económicas',
        'Ciencias Físicas','Ciencias Matemáticas','Ciencias Sociales','Derecho y Ciencia Política',
        'Educación','Farmacia y Bioquímica','Ingenierías de\nSistemas y Informática',
        'Ingeniería\nElectrónica y Eléctrica','Ingeniería Geológica, Minera,\n Metalúrgica y Geográfica',
        'Ingeniería Industrial','Letras y Ciencias Humanas','Medicina','Medicina Veterinaria',
        'Odontología','Psicología','Química e Ingeniería Química'
    ]
    grupo3 = [2606, 571, 2011, 1248, 290, 466, 1315, 1343, 1496, 513, 1059, 1189, 913, 937, 444, 902, 325, 328, 1044, 575]  # Invictos
    grupo2 = [438, 331, 1465, 960, 609, 834, 620, 580, 598, 212, 622, 968, 898, 690, 794, 559, 106, 94, 141, 755]      # Desaprobados
    grupo1 = [inv + des for inv, des in zip(grupo3, grupo2)] # Matriculados
    porcentaje_lineaA = [round(inv / total * 100, 1) if total > 0 else 0 for inv, total in zip(grupo3, grupo1)]
    porcentaje_lineaB = [round(des / total * 100, 1) if total > 0 else 0 for des, total in zip(grupo2, grupo1)]

    df = pd.DataFrame({
        'Escuela': x_labels,
        'Matriculados': grupo1,
        'Desaprobados': grupo2,
        'Invictos': grupo3,
        '% Invictos': porcentaje_lineaA,
        '% Desaprobados': porcentaje_lineaB
    })
    return df

df = load_data()
all_schools = df['Escuela'].unique()

# --- 2. Crear los Widgets de Filtro en la Barra Lateral ---
st.sidebar.header("Filtros del Dashboard")

# Filtro 1: Selección de Escuelas (Igual que antes)
selected_schools = st.sidebar.multiselect(
    'Seleccione las escuelas:',
    options=all_schools,
    default=all_schools
)

# <-- NUEVO: Filtro 2: Ordenar el gráfico -->
sort_by = st.sidebar.selectbox(
    'Ordenar por:',
    options=['Matriculados', 'Invictos', 'Desaprobados', '% Invictos', '% Desaprobados'],
    index=0 # Por defecto, ordena por 'Matriculados'
)

# <-- NUEVO: Filtro 3: Mostrar/Ocultar Tabla -->
show_table = st.sidebar.checkbox('Mostrar tabla de datos', value=False)


# --- 3. Filtrar y Ordenar los Datos ---
if not selected_schools:
    dff = df.copy() # Si no hay selección, usa todos los datos
else:
    dff = df[df['Escuela'].isin(selected_schools)].copy()

# Aplica el orden
dff = dff.sort_values(by=sort_by, ascending=False)


# --- 4. <-- NUEVO: Mostrar KPIs (Métricas Clave) ---
st.subheader("Métricas Totales (Según Filtro)")

# Calcular totales
total_matriculados = dff['Matriculados'].sum()
total_invictos = dff['Invictos'].sum()
total_desaprobados = dff['Desaprobados'].sum()

# Usar columnas para poner las métricas una al lado de la otra
col1, col2, col3 = st.columns(3)
col1.metric("Total Matriculados", f"{total_matriculados:,}")
col2.metric("Total Invictos", f"{total_invictos:,}")
col3.metric("Total Desaprobados", f"{total_desaprobados:,}")

st.markdown("---") # Línea divisoria

# --- 5. Crear la Figura de Plotly (El código del gráfico es el mismo) ---
# (Ahora usa 'dff' que está filtrado Y ordenado)
st.subheader("Gráfico Comparativo por Escuela")

fig = make_subplots(specs=[[{"secondary_y": True}]])

# Barras
fig.add_trace(
    go.Bar(
        x=dff['Escuela'], y=dff['Matriculados'], name='Matriculados', 
        marker_color='blue', text=dff['Matriculados'], textposition='outside'
    ), secondary_y=False)
fig.add_trace(
    go.Bar(x=dff['Escuela'], y=dff['Desaprobados'], name='Desaprobados', marker_color='red'),
    secondary_y=False)
fig.add_trace(
    go.Bar(x=dff['Escuela'], y=dff['Invictos'], name='Invictos', marker_color='green'),
    secondary_y=False)

# Líneas
fig.add_trace(
    go.Scatter(
        x=dff['Escuela'], y=dff['% Invictos'], name='% Invictos', 
        mode='lines+markers+text', line=dict(color='orange', width=1.5),
        text=dff['% Invictos'].apply(lambda x: f'{x}%'), textposition='top center'
    ), secondary_y=True)
fig.add_trace(
    go.Scatter(
        x=dff['Escuela'], y=dff['% Desaprobados'], name='% Desaprobados', 
        mode='lines+markers+text', line=dict(color='purple', width=1.5, dash='dash'),
        text=dff['% Desaprobados'].apply(lambda x: f'{x}%'), textposition='bottom center'
    ), secondary_y=True)

# Layout del gráfico
fig.update_layout(
    barmode='group',
    height=700,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    xaxis_tickangle=-45
)
fig.update_yaxes(title_text="Estudiantes", secondary_y=False)
fig.update_yaxes(title_text="%Porcentajes", range=[0, 100], secondary_y=True)

# --- 6. Mostrar el Gráfico en Streamlit ---
st.plotly_chart(fig, use_container_width=True)

# --- 7. <-- NUEVO: Mostrar la Tabla de Datos (si está activado) ---
if show_table:
    st.markdown("---")
    st.subheader("Datos Filtrados y Ordenados")
    # Mostramos el dataframe, usando 'Escuela' como el índice para que se vea más limpio
    st.dataframe(dff.set_index('Escuela'))
