import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Demografía desde 1974")
st.header("Resumen da datos demográficos en el mundo desde 1974")
st.subheader("Datos de paìses, regiones y niveles socioeconómicos")
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

# --- Histograma interactivo ---
with st.expander("Ver histograma de tasa de fertilidad por grupo"):
    selected_year = st.slider(
        "Selecciona el año para el histograma:",
        min_value=min(year_cols_sorted),
        max_value=max(year_cols_sorted),
        value=max(year_cols_sorted),
        step=1,
        key="hist_slider"
    )
    selected_year = str(selected_year)

    fertility_year = demographics[
        demographics['Series Name'] == 'Fertility rate, total (births per woman)'
    ][['Country Name', selected_year]].dropna()

    fertility_year[selected_year] = pd.to_numeric(fertility_year[selected_year], errors='coerce')

    def clasificar_fertilidad(x):
        if x < 2.1:
            return "Bajo del límite de equilibrio"
        elif 2.1 <= x < 4:
            return "Sobre el límite del equilibrio"
        elif 4 <= x < 6.3:
            return "Duplicación"
        else:
            return "Triplicación"

    fertility_year['Grupo Fertilidad'] = fertility_year[selected_year].apply(clasificar_fertilidad)

    orden_grupos = [
        "Triplicación",
        "Duplicación",
        "Sobre el límite del equilibrio",
        "Bajo del límite de equilibrio"
    ]
    colores = {
        "Triplicación": "green",
        "Duplicación": "blue",
        "Sobre el límite del equilibrio": "orange",
        "Bajo del límite de equilibrio": "red"
    }

    conteo = fertility_year['Grupo Fertilidad'].value_counts().reindex(orden_grupos).reset_index()
    conteo.columns = ['Grupo Fertilidad', 'Número de Países']

    fig = px.bar(
        conteo,
        x='Grupo Fertilidad',
        y='Número de Países',
        color='Grupo Fertilidad',
        color_discrete_map=colores,
        title=f'Distribución de países por grupo de tasa de fertilidad ({selected_year})',
        labels={
            'Grupo Fertilidad': 'Grupo de Tasa de Fertilidad',
            'Número de Países': 'Número de Países'
        }
    )
    st.plotly_chart(fig)
    st.success("¡Visualización generada correctamente! Puedes interactuar con el control para explorar los datos demográficos.")

# --- Dispersión interactiva ---
with st.expander("Ver gráficos de dispersión Fertilidad vs Urbanización"):
    year_cols_disp = [col for col in demographics.columns if col.isdigit() and int(col) >= 1974]
    year_cols_disp_sorted = sorted([int(y) for y in year_cols_disp])
    selected_year_disp = st.slider(
        "Selecciona el año para los gráficos de dispersión:",
        min_value=min(year_cols_disp_sorted),
        max_value=max(year_cols_disp_sorted),
        value=max(year_cols_disp_sorted),
        step=1,
        key="dispersion_slider"
    )
    selected_year_disp = str(selected_year_disp)

    # --- Dispersión por país ---
    income_groups = [
        'Upper middle income', 'Middle income', 'Lower middle income', 'Low income', 'High income'
    ]
    df_fertility = demographics[
        (demographics['Series Name'] == 'Fertility rate, total (births per woman)') &
        (~demographics['Country Name'].isin(income_groups))
    ][['Country Name', selected_year_disp]].rename(columns={selected_year_disp: 'Fertility'})
    df_urban = demographics[
        (demographics['Series Name'] == 'Urban population') &
        (~demographics['Country Name'].isin(income_groups))
    ][['Country Name', selected_year_disp]].rename(columns={selected_year_disp: 'Urban'})

    merged = pd.merge(df_fertility, df_urban, on='Country Name').dropna()
    merged['Fertility'] = pd.to_numeric(merged['Fertility'], errors='coerce')
    merged['Urban'] = pd.to_numeric(merged['Urban'], errors='coerce')

    fig_disp = px.scatter(
        merged,
        x='Fertility',
        y='Urban',
        color='Country Name',
        title=f'Índice De Fertilidad vs Población Urbanizada por país ({selected_year_disp})',
        labels={
            'Fertility': 'Tasa De Fertilidad (Hijos Por Mujer)',
            'Urban': 'Población Urbanizada',
            'Country Name': 'País'
        }
    )
    fig_disp.update_traces(marker=dict(size=12))
    fig_disp.update_xaxes(range=[0, 7])
    fig_disp.update_yaxes(range=[0, merged['Urban'].max() * 1.05])
    st.plotly_chart(fig_disp)

    # --- Dispersión por grupo de ingreso ---
    df_fertility_income = demographics[
        (demographics['Series Name'] == 'Fertility rate, total (births per woman)') &
        (demographics['Country Name'].isin(income_groups))
    ][['Country Name', selected_year_disp]].rename(columns={selected_year_disp: 'Fertility'})
    df_urban_income = demographics[
        (demographics['Series Name'] == 'Urban population') &
        (demographics['Country Name'].isin(income_groups))
    ][['Country Name', selected_year_disp]].rename(columns={selected_year_disp: 'Urban'})

    merged_income = pd.merge(df_fertility_income, df_urban_income, on='Country Name').dropna()
    merged_income['Fertility'] = pd.to_numeric(merged_income['Fertility'], errors='coerce')
    merged_income['Urban'] = pd.to_numeric(merged_income['Urban'], errors='coerce')

    fig_disp_income = px.scatter(
        merged_income,
        x='Fertility',
        y='Urban',
        color='Country Name',
        title=f'Índice De Fertilidad vs Población Urbanizada por grupo de ingreso ({selected_year_disp})',
        labels={
            'Fertility': 'Tasa De Fertilidad (Hijos Por Mujer)',
            'Urban': 'Población Urbanizada',
            'Country Name': 'Grupo de Ingreso'
        }
    )
    fig_disp_income.update_traces(marker=dict(size=18))
    fig_disp_income.update_xaxes(range=[0, 7])
    fig_disp_income.update_yaxes(range=[0, merged_income['Urban'].max() * 1.05])
    st.plotly_chart(fig_disp_income)

    st.success("¡Visualización generada correctamente! Puedes interactuar con los controles para explorar los datos demográficos.")