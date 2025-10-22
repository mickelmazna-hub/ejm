import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

# --- Configuración de la Página de Streamlit ---
# (Esto reemplaza a fig.update_layout)
st.set_page_config(layout="wide")
st.title("Dashboard de Rendimiento Estudiantil")

# --- 1. Preparar los Datos (Igual que antes) ---
# Usamos @st.cache_data para que los datos no se recarguen cada vez
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

# --- 2. Crear el Widget de Filtro (Reemplaza a ipywidgets) ---
# Esto crea el menú de selección múltiple en una barra lateral
st.sidebar.header("Filtros del Dashboard")
selected_schools = st.sidebar.multiselect(
    'Seleccione las escuelas:',
    options=all_schools,
    default=all_schools # Por defecto, muestra todas
)

# --- 3. Filtrar los Datos ---
if not selected_schools:
    dff = df
else:
    dff = df[df['Escuela'].isin(selected_schools)]

# --- 4. Crear la Figura de Plotly (Igual que antes) ---
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

# --- 5. Mostrar el Gráfico en Streamlit ---
st.plotly_chart(fig, use_container_width=True)