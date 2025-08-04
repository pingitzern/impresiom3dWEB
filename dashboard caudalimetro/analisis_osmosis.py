import streamlit as st
import pandas as pd
import numpy as np

# --- Configuración de la Página ---
st.set_page_config(
    page_title="Análisis de Ósmosis",
    page_icon="💧",
    layout="wide"
)

st.title("💧 Reporte Interactivo de Producción de Ósmosis")
st.write("Sube tu archivo de Excel o CSV para analizar los ciclos de producción de tu equipo.")

# --- Funciones Principales de Análisis ---

def procesar_datos(df):
    """Limpia y prepara el DataFrame para el análisis."""
    # Renombra la columna de caudal si es necesario
    if 'L/MIN' in df.columns:
        df.rename(columns={'L/MIN': 'flowRate'}, inplace=True)
    
    # Asegura que las columnas existan
    if 'flowRate' not in df.columns or 'fecha_hora' not in df.columns:
        st.error("El archivo debe contener las columnas 'fecha_hora' y 'L/MIN' (o 'flowRate').")
        return None

    df['fecha_hora'] = pd.to_datetime(df['fecha_hora'], errors='coerce')
    df.dropna(subset=['fecha_hora', 'flowRate'], inplace=True)
    df.sort_values(by='fecha_hora', inplace=True, ascending=True)
    return df

def analizar_periodo(df, fecha_inicio, fecha_fin):
    """Aplica la lógica de negocio para analizar los datos en el rango de fechas seleccionado."""
    
    # Filtra por el rango de fechas seleccionado
    mask = (df['fecha_hora'].dt.date >= fecha_inicio) & (df['fecha_hora'].dt.date <= fecha_fin)
    df_periodo = df.loc[mask].copy()

    if df_periodo.empty:
        st.warning("No hay datos para el rango de fechas seleccionado.")
        return None, 0

    # --- Lógica de Detección de Ciclos (Regla de 10 minutos) ---
    df_periodo['time_since_last'] = df_period['fecha_hora'].diff()
    time_gap_threshold = pd.Timedelta('10 minutes')
    df_periodo['cycle_id'] = (df_periodo['time_since_last'] > time_gap_threshold).cumsum()

    all_cycles_data = []

    for cycle_id, cycle_data in df_periodo.groupby('cycle_id'):
        if cycle_data.empty:
            continue

        # Consideramos producción real si el caudal es >= 1.0 L/min
        production_data = cycle_data[cycle_data['flowRate'] >= 1.0].copy()
        if production_data.empty:
            continue

        start_time = production_data['fecha_hora'].min()
        end_time = production_data['fecha_hora'].max()
        
        # Cálculo del volumen del ciclo
        production_data['time_diff_mins'] = production_data['fecha_hora'].diff().dt.total_seconds().div(60)
        production_data['volume'] = production_data['flowRate'] * production_data['time_diff_mins']
        cycle_volume = production_data['volume'].sum()

        all_cycles_data.append({
            'start_date': start_time.date(),
            'start_time': start_time,
            'end_time': end_time,
            'cycle_volume': cycle_volume
        })
    
    if not all_cycles_data:
        st.info("No se detectaron ciclos de producción en este período.")
        return None, 0

    results_df = pd.DataFrame(all_cycles_data)
    period_total_volume = results_df['cycle_volume'].sum()
    
    return results_df, period_total_volume

# --- Interfaz de Usuario (UI) ---

# 1. Widget para subir el archivo
uploaded_file = st.file_uploader("Elige tu archivo de datos (Excel o CSV)", type=['csv', 'xlsx'])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        df_procesado = procesar_datos(df)

        if df_procesado is not None:
            st.success("Archivo cargado y procesado correctamente!")

            # 2. Widgets para filtrar por fecha
            min_date = df_procesado['fecha_hora'].min().date()
            max_date = df_procesado['fecha_hora'].max().date()
            
            st.sidebar.header("Filtros")
            fecha_inicio = st.sidebar.date_input('Fecha de Inicio', min_date, min_value=min_date, max_value=max_date)
            fecha_fin = st.sidebar.date_input('Fecha de Fin', max_date, min_value=min_date, max_value=max_date)

            if fecha_inicio > fecha_fin:
                st.sidebar.error("Error: La fecha de inicio no puede ser posterior a la fecha de fin.")
            else:
                # 3. Botón para ejecutar el análisis
                if st.sidebar.button('Generar Reporte'):
                    with st.spinner('Analizando los datos... por favor espera.'):
                        reporte_df, volumen_total = analizar_periodo(df_procesado, fecha_inicio, fecha_fin)

                    if reporte_df is not None:
                        st.header(f"Reporte del {fecha_inicio.strftime('%d/%m/%Y')} al {fecha_fin.strftime('%d/%m/%Y')}")

                        # 4. Mostrar el reporte día por día
                        for day in sorted(reporte_df['start_date'].unique()):
                            day_str = day.strftime('%d de %B de %Y')
                            st.subheader(f"🗓️ {day_str}")
                            
                            day_cycles_data = reporte_df[reporte_df['start_date'] == day]
                            daily_total_volume = day_cycles_data['cycle_volume'].sum()

                            for index, row in day_cycles_data.iterrows():
                                start_hms = row['start_time'].strftime('%H:%M:%S')
                                end_hms = row['end_time'].strftime('%H:%M:%S')
                                vol = row['cycle_volume']
                                st.write(f"  - **Ciclo:** de `{start_hms}` a `{end_hms}`  ->  **{vol:.2f} litros**")
                            
                            st.info(f"**TOTAL DEL DÍA: {daily_total_volume:.2f} litros**")

                        # 5. Mostrar el total del período y gráficos
                        st.header("Resumen del Período")
                        st.success(f"**VOLUMEN TOTAL PRODUCIDO: {volumen_total:.2f} litros**")

                        st.subheader("Gráficos del Período")
                        # Gráfico de producción diaria
                        produccion_diaria = reporte_df.groupby('start_date')['cycle_volume'].sum()
                        st.bar_chart(produccion_diaria)
                        st.caption("Gráfico 1: Total de litros producidos por día.")

    except Exception as e:
        st.error(f"Ocurrió un error al procesar el archivo: {e}")