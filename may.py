import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Dashboard de Logins - Academia", layout="wide")

uploaded_file = st.sidebar.file_uploader("📄 Envie o arquivo de logins (CSV)", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df = df.dropna(subset=['timestamp'])
    df['timestamp'] = df['timestamp'].dt.tz_localize(None)
    df['date'] = df['timestamp'].dt.date
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.day_name()
    df['week'] = df['timestamp'].dt.isocalendar().week

    st.sidebar.subheader("🔍 Filtros")
    date_range = st.sidebar.date_input("Período", [df['date'].min(), df['date'].max()])
    selected_users = st.sidebar.multiselect("Usuários", df['user_id'].unique(), default=df['user_id'].unique())
    
    ...

    st.title(f"🏋️‍♂️ Logins Semanais ({date_range[0]} até {date_range[1]})")

    start_date = pd.Timestamp(date_range[0]).date()
    end_date = pd.Timestamp(date_range[1]).date()


    df_filtered = df[
        (df['date'] >= start_date) &
        (df['date'] <= end_date) &
        (df['user_id'].isin(selected_users))
    ]

    col1, col2, col3 = st.columns(3)
    col1.metric("👥 Usuários únicos", df_filtered['user_id'].nunique())
    col2.metric("🔢 Logins totais", len(df_filtered))
    col3.metric("📊 Média por usuário", round(len(df_filtered) / max(df_filtered['user_id'].nunique(), 1), 2))

    st.markdown("---")

    st.subheader("📅 Logins por Dia")
    daily_counts = df_filtered.groupby('date').size().reset_index(name='logins')
    fig1 = px.line(daily_counts, x='date', y='logins', title='Logins por Dia')
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("⏰ Heatmap de Horários")
    heatmap_data = df_filtered.groupby(['day_of_week', 'hour']).size().unstack().fillna(0)
    st.dataframe(heatmap_data.style.background_gradient(cmap='Blues'), height=300)

    st.subheader("📈 Logins Semanais")
    weekly_counts = df_filtered.groupby('week').size().reset_index(name='logins')
    fig2 = px.bar(weekly_counts, x='week', y='logins', title='Total de Logins por Semana')
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("📋 Tabela de Logins")
    st.dataframe(df_filtered.sort_values(by="timestamp", ascending=False), height=300)

else:
    st.warning("⚠️ Faça upload de um arquivo CSV com colunas user_id e timestamp.")
