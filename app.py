import streamlit as st
import plotly.express as px
import pandas as pd

# --- Configuración de la Página de Streamlit ---
st.set_page_config(layout="wide")
st.title("Dashboard de Repitencia Estudiantil")

# --- 1. Preparar los Datos (Tu código original) ---
# Usamos @st.cache_data para que los datos no se recarguen
@st.cache_data
def load_data():
    data = []
    x_labels = ['Contabilidad', 'Ingeniería\nIndustrial', 'Derecho', 'Economía\nPública', 'Educación\nFísica']
    valores = [
        [548, 33, 3, 0],
        [412, 14, 3, 0],
        [376, 22, 0, 0],
        [348, 10, 1, 0],
        [334, 14, 2, 0]
    ]

    for fac, vals in zip(x_labels, valores):
        for i, v in enumerate(vals):
            # Añadimos un filtro para no incluir datos con 0 estudiantes
            if v > 0: 
                data.append({'Escuela': fac, 'Repitencia': f'{i+1}°', 'Estudiantes': v})
    
    df = pd.DataFrame(data)
    return df

df = load_data()
all_schools = df['Escuela'].unique()
all_repitencias = sorted(df['Repitencia'].unique())

# --- 2. Crear los Widgets de Filtro en la Barra Lateral ---
st.sidebar.header("Filtros del Dashboard")

# Filtro 1: Selección de Escuelas
selected_schools = st.sidebar.multiselect(
    'Seleccione las escuelas:',
    options=all_schools,
    default=all_schools
)

# Filtro 2: Selección de Nivel de Repitencia
selected_repitencias = st.sidebar.multiselect(
    'Seleccione nivel de repitencia:',
    options=all_repitencias,
    default=all_repitencias
)

# Filtro 3: Ordenar el gráfico
sort_order = st.sidebar.radio(
    'Ordenar por total de estudiantes:',
    options=['Descendente', 'Ascendente'],
    index=0 # Por defecto, Descendente
)

# Filtro 4: Mostrar/Ocultar Tabla
show_table = st.sidebar.checkbox('Mostrar tabla de datos', value=False)


# --- 3. Filtrar los Datos ---
# Filtramos el DataFrame basado en las selecciones
dff = df[
    df['Escuela'].isin(selected_schools) &
    df['Repitencia'].isin(selected_repitencias)
]

# --- 4. Mostrar KPIs (Métricas Clave) ---
st.subheader("Métricas Totales (Según Filtro)")

total_estudiantes = dff['Estudiantes'].sum()
num_escuelas = len(dff['Escuela'].unique())

col1, col2 = st.columns(2)
col1.metric("Escuelas Seleccionadas", f"{num_escuelas}")
col2.metric("Total Estudiantes (con repitencia)", f"{total_estudiantes:,}")

st.markdown("---") # Línea divisoria

# --- 5. Preparar y Mostrar el Gráfico ---
st.subheader("Gráfico Comparativo de Repitencias")

# Si no hay datos, muestra un mensaje
if dff.empty:
    st.warning("No hay datos para mostrar con los filtros seleccionados.")
else:
    # Lógica para ordenar el eje X del gráfico
    # 1. Agrupamos por escuela y sumamos los estudiantes
    df_agg = dff.groupby('Escuela')['Estudiantes'].sum().reset_index()
    
    # 2. Ordenamos
    sort_asc = (sort_order == 'Ascendente')
    df_agg = df_agg.sort_values(by='Estudiantes', ascending=sort_asc)
    
    # 3. Creamos una lista con el orden de las escuelas
    sorted_schools_list = df_agg['Escuela'].tolist()

    # 4. Creamos el gráfico con Plotly Express (tu código)
    fig = px.bar(
        dff, 
        x='Escuela', 
        y='Estudiantes', 
        color='Repitencia', 
        barmode='group',
        title='Estudiantes por Repitencia y Escuela Profesional',
        text='Estudiantes' # Añade el valor sobre la barra
    )

    # 5. Aplicamos el orden al eje X
    fig.update_layout(
        xaxis_title='Escuela Profesional', 
        yaxis_title='Estudiantes',
        height=600,
        # Aquí le decimos a Plotly el orden exacto del eje X
        xaxis={'categoryorder':'array', 'categoryarray': sorted_schools_list} 
    )
    fig.update_traces(textposition='outside') # Pone el texto fuera de la barra

    # 6. Mostrar el Gráfico
    st.plotly_chart(fig, use_container_width=True)

# --- 6. Mostrar la Tabla de Datos (si está activado) ---
if show_table:
    st.markdown("---")
    st.subheader("Datos Filtrados y Ordenados")
    # Mostramos el dataframe filtrado
    st.dataframe(dff)
