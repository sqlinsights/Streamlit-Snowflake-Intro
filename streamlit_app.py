from sqlite3 import Row
import streamlit as st
import pandas as pd
import snowflake.connector
import altair as alt

st.set_page_config(layout='wide')
sidebar = st.sidebar

def connect_to_snowflake_up(acct, usr, pwd, rl, db, wh):
    ctx = snowflake.connector.connect(user=usr,
                                      account=acct,
                                      warehouse=wh,
                                      role=rl,
                                      database=db,
                                      password=pwd
                                      )
    cs = ctx.cursor()
    st.session_state['snow_conn'] = cs
    st.session_state['connected'] = True
@st.cache(suppress_st_warning=True, show_spinner=False)
def get_sensor_data():
    with open('queries/read_data.sql','r') as qry:
        sensor_qry = qry.readline()
    q_query = str(sensor_qry)
    q_results = st.session_state['snow_conn'].execute(q_query)
    q_results = st.session_state['snow_conn'].fetch_pandas_all()
    return q_results

if 'connected' not in st.session_state:
    conn_expanded = True
    st.session_state['connected'] = False
else:
    conn_expanded = False

with sidebar:
    with st.expander("Connect to Snowflake", expanded=conn_expanded):
        acct = st.text_input("Account")
        usr = st.text_input("Username")
        pwd = st.text_input("Password", type='password')
        role = st.text_input("Role",)
        db = st.text_input("Database")
        wh = st.text_input("WH")
        login_btn = st.button("Login", on_click=connect_to_snowflake_up, args=[
                        acct, usr, pwd, role, db, wh])

if st.session_state['connected'] == True:
    
    sensors_data = get_sensor_data()
    #st.table(sensors_data.head(10))


    selected_sensor = sidebar.multiselect("Sensors", options = sensors_data['SENSOR_ID'].unique())
    
    min_r = sidebar.select_slider("Seleccione valor menor",options=range(1,51),value=sensors_data['READING_VALUE'].min())

    max_r = sidebar.select_slider("Seleccione valor mayor",options=range(1,51), value=sensors_data['READING_VALUE'].max())
    

    st.subheader("Graficos")

    if len(selected_sensor) > 0:
        normal, altair_c, generados, csv = st.tabs(["Normales", "Altair", "Generados","CSV"])
        
        with normal:
            st.line_chart(sensors_data[['READING_DATE', 'READING_VALUE']].loc[(sensors_data['SENSOR_ID'].isin(selected_sensor)) & \
                                                                        (sensors_data['READING_VALUE'] >= min_r) & \
                                                                        (sensors_data['READING_VALUE'] <= max_r)],
            x='READING_DATE', y='READING_VALUE')
        
            
        with altair_c:
            line_chart = alt.Chart(sensors_data[['READING_DATE', 'READING_VALUE','SENSOR_ID']].loc[(sensors_data['SENSOR_ID'].isin(selected_sensor)) & \
                                                                            (sensors_data['READING_VALUE'] >= min_r) & \
                                                                            (sensors_data['READING_VALUE'] <= max_r)]).mark_line().encode(
                x=alt.X('dayhours(READING_DATE):T'),
                y = alt.Y('mean(READING_VALUE):Q'),
                color = alt.Color('SENSOR_ID:N'),
                row = alt.Row('SENSOR_ID:N')
                ).properties(width=800, height=150)
                
            st.altair_chart(line_chart)
            selection = alt.selection_interval()
            base = alt.Chart(sensors_data[['READING_DATE', 'READING_VALUE','SENSOR_ID']].loc[(sensors_data['SENSOR_ID'].isin(selected_sensor)) & \
                                                                            (sensors_data['READING_VALUE'] >= min_r) & \
                                                                            (sensors_data['READING_VALUE'] <= max_r)]).mark_bar().encode(
                x=alt.X('day(READING_DATE):T'),
                y = alt.Y('mean(READING_VALUE):Q'),
                color = alt.condition(selection, 'SENSOR_ID:N', alt.value('lightgray'))
                ).add_selection(selection).properties(width=1200, height=150)
            timeline = alt.Chart(sensors_data[['READING_DATE', 'READING_VALUE','SENSOR_ID']].loc[(sensors_data['SENSOR_ID'].isin(selected_sensor)) & \
                                                                            (sensors_data['READING_VALUE'] >= min_r) & \
                                                                            (sensors_data['READING_VALUE'] <= max_r)]).mark_line().encode(
                x=alt.X('READING_DATE:T'),
                y = alt.Y('READING_VALUE:Q'),
                color = alt.Color('SENSOR_ID:N')
                ).transform_filter(selection).properties(width=1200, height=150)    
            st.altair_chart(alt.vconcat(base,timeline))
        with generados:
            for i in selected_sensor:
                with st.expander(f"Datos para: {i}", expanded=False):
                    st.line_chart(sensors_data[['READING_DATE', 'READING_VALUE']].loc[(sensors_data['SENSOR_ID'] == i) & \
                                                                                (sensors_data['READING_VALUE'] >= min_r) & \
                                                                                (sensors_data['READING_VALUE'] <= max_r)],
                                                                                x='READING_DATE', y='READING_VALUE')
    
        with csv:
            columns_a, columns_b = st.columns(2)
            with columns_a:
                imported = st.file_uploader("Cargar Archivos")
            if imported != None:
                with columns_b:
                    data = pd.read_csv(imported)
                    st.table(data)