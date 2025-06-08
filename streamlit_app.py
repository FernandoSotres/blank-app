import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Demografía desde 1974")
st.header("Resumen de datos demográficos en el mundo desde 1974")
st.subheader("Datos de países, regiones y niveles socioeconómicos")
st.write("Datos del Banco Mundial")

# Cargar los datos
demographics = pd.read_csv("world_bank_data.csv")

# Renombrar columnas: si tienen formato 'YYYY [YRYYYY]', dejar solo el año
demographics.columns = [
    col.split(' ')[0] if ' [YR' in col else col
    for col in demographics.columns
]

# Buscar los años disponibles
year_cols = [col for col in demographics.columns if col.isdigit()]
year_cols_sorted = sorted([int(y) for y in year_cols])

# ...carga y preparación de datos...

# --- Histograma animado ---
# Prepara los datos en formato largo para animación
fertility_long = demographics[
    demographics['Series Name'] == 'Fertility rate, total (births per woman)'
].melt(
    id_vars=['Country Name'],
    value_vars=year_cols,
    var_name='Año',
    value_name='Tasa de Fertilidad'
).dropna()

fertility_long['Tasa de Fertilidad'] = pd.to_numeric(fertility_long['Tasa de Fertilidad'], errors='coerce')

def clasificar_fertilidad(x):
    if 1.05 <= x < 2.1:
        return "Bajo El Equilibrio"
    elif 2.1 <= x < 4:
        return "Equilibrio"
    elif 4 <= x < 6.3:
        return "Duplicación"
    else:
        return "Triplicación"

# ...código anterior...

orden_grupos = [
    "Triplicación",
    "Duplicación",
    "Equilibrio",
    "Bajo El Equilibrio"
]
colores = {
    "Triplicación": "green",
    "Duplicación": "blue",
    "Equilibrio": "orange",
    "Bajo El Equilibrio": "red"
}

fertility_long['Grupo Fertilidad'] = fertility_long['Tasa de Fertilidad'].apply(clasificar_fertilidad)
fertility_long['Grupo Fertilidad'] = pd.Categorical(fertility_long['Grupo Fertilidad'], categories=orden_grupos, ordered=True)

# Generar todas las combinaciones posibles de año y grupo
all_years = sorted(fertility_long['Año'].unique(), key=int)
import itertools
all_combinations = pd.DataFrame(list(itertools.product(all_years, orden_grupos)), columns=['Año', 'Grupo Fertilidad'])

conteo = fertility_long.groupby(['Año', 'Grupo Fertilidad']).size().reset_index(name='Número de Países')
conteo = pd.merge(all_combinations, conteo, on=['Año', 'Grupo Fertilidad'], how='left')
conteo['Número de Países'] = conteo['Número de Países'].fillna(0).astype(int)
conteo['Año'] = conteo['Año'].astype(str)
conteo['Grupo Fertilidad'] = pd.Categorical(conteo['Grupo Fertilidad'], categories=orden_grupos, ordered=True)

with st.expander("Ver histograma animado de tasa de fertilidad por grupo"):
    fig = px.bar(
        conteo.sort_values(['Año', 'Grupo Fertilidad']),
        x='Grupo Fertilidad',
        y='Número de Países',
        color='Grupo Fertilidad',
        animation_frame='Año',
        category_orders={'Grupo Fertilidad': orden_grupos},
        color_discrete_map=colores,
        title='Distribución de países por grupo de tasa de fertilidad a través de los años',
        labels={
            'Grupo Fertilidad': 'Grupo de Tasa de Fertilidad',
            'Número de Países': 'Número de Países',
            'Año': 'Año'
        }
    )
    fig.update_yaxes(range=[0, conteo['Número de Países'].max() * 1.35])
    st.plotly_chart(fig)

# --- Dispersión países individuales ---
with st.expander("Ver dispersión Fertilidad vs Urbanización por país"):
    year_cols_disp = [col for col in demographics.columns if col.isdigit() and int(col) >= 1974]
    to_remove = [
        'Upper middle income', 'Middle income', 'Lower middle income', 'Low income', 'High income'
    ]
    df_fertility = demographics[
        (demographics['Series Name'] == 'Fertility rate, total (births per woman)') &
        (~demographics['Country Name'].isin(to_remove))
    ]
    df_urban = demographics[
        (demographics['Series Name'] == 'Urban population') &
        (~demographics['Country Name'].isin(to_remove))
    ]
    fertility_melted = df_fertility.melt(
        id_vars=['Country Name'],
        value_vars=year_cols_disp,
        var_name='Year',
        value_name='Fertility rate, total (births per woman)'
    ).dropna()
    urban_melted = df_urban.melt(
        id_vars=['Country Name'],
        value_vars=year_cols_disp,
        var_name='Year',
        value_name='Urban population'
    ).dropna()
    # Convertir a numérico para evitar errores en el eje Y
    urban_melted['Urban population'] = pd.to_numeric(urban_melted['Urban population'], errors='coerce')
    merged = pd.merge(
        fertility_melted,
        urban_melted,
        on=['Country Name', 'Year'],
        how='inner'
    )
    merged['Urban population'] = pd.to_numeric(merged['Urban population'], errors='coerce')
    fig2 = px.scatter(
        merged,
        x='Fertility rate, total (births per woman)',
        y='Urban population',
        color='Country Name',
        animation_frame='Year',
        title='Índice De Fertilidad vs  Población Urbanizada',
        labels={
            'Fertility rate, total (births per woman)': 'Tasa De Fertilidad (Hijos Por Mujer)',
            'Urban population': 'Población Urbanizada'
        }
    )
    fig2.update_xaxes(range=[0, 7])
    fig2.update_yaxes(range=[0, merged['Urban population'].max() * 1.05])
    fig2.update_traces(marker=dict(size=12))
    for frame in fig2.frames:
        frame.name = frame.name.replace("Year=", "Año=")
    fig2.layout.sliders[0].currentvalue.prefix = "Año="
    st.plotly_chart(fig2)

# --- Dispersión por grupo de ingreso ---
with st.expander("Ver dispersión por grupo de ingreso"):
    income_groups = [
        'Upper middle income', 'Middle income', 'Lower middle income', 'Low income', 'High income'
    ]
    df_fertility_income = demographics[
        (demographics['Series Name'] == 'Fertility rate, total (births per woman)') &
        (demographics['Country Name'].isin(income_groups))
    ]
    df_urban_income = demographics[
        (demographics['Series Name'] == 'Urban population') &
        (demographics['Country Name'].isin(income_groups))
    ]
    fertility_melted_income = df_fertility_income.melt(
        id_vars=['Country Name'],
        value_vars=year_cols_disp,
        var_name='Year',
        value_name='Tasa De Fertilidad (Hijos Por Mujer)'
    ).dropna()
    urban_melted_income = df_urban_income.melt(
        id_vars=['Country Name'],
        value_vars=year_cols_disp,
        var_name='Year',
        value_name='Población Urbanizada'
    ).dropna()
    # Convertir a numérico para evitar errores en el eje Y
    urban_melted_income['Población Urbanizada'] = pd.to_numeric(urban_melted_income['Población Urbanizada'], errors='coerce')
    merged_income = pd.merge(
        fertility_melted_income,
        urban_melted_income,
        on=['Country Name', 'Year'],
        how='inner'
    )
    merged_income['Población Urbanizada'] = pd.to_numeric(merged_income['Población Urbanizada'], errors='coerce')
    fig3 = px.scatter(
        merged_income,
        x='Tasa De Fertilidad (Hijos Por Mujer)',
        y='Población Urbanizada',
        color='Country Name',
        animation_frame='Year',
        title='Índice De Fertilidad vs  Población Urbanizada (Grupos de Ingreso)',
        labels={
            'Tasa De Fertilidad (Hijos Por Mujer)': 'Tasa De Fertilidad (Hijos Por Mujer)',
            'Población Urbanizada': 'Población Urbanizada',
            'Country Name': 'Grupo de Ingreso'
        }
    )
    fig3.update_xaxes(range=[0, 7])
    fig3.update_yaxes(range=[0, merged_income['Población Urbanizada'].max() * 1.05])
    fig3.update_traces(marker=dict(size=12))
    for frame in fig3.frames:
        frame.name = frame.name.replace("Year=", "Año=")
    fig3.layout.sliders[0].currentvalue.prefix = "Año="
    st.plotly_chart(fig3)