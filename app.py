import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Marketing SmartMarket", layout="wide")

# -------------------------------------------------------------
# Chargement des données
# -------------------------------------------------------------
df = pd.read_csv('df_extended.csv')# -------------------------------------------------------------
# Calcul des KPI (avec sécurisation)
# -------------------------------------------------------------
df["CTR"] = df["clicks"] / df["impressions"]
df["CVR"] = df["conversions"] / df["clicks"].replace(0, pd.NA)
df["CPC"] = df["cost"] / df["clicks"].replace(0, pd.NA)
df["CPA"] = df["cost"] / df["conversions"].replace(0, pd.NA)

# -------------------------------------------------------------
# Filtres
# -------------------------------------------------------------
st.sidebar.header("Filtres")

channel_f = st.sidebar.selectbox(
    "Canal", ["Tous"] + sorted(df["channel"].dropna().unique())
)
device_f = st.sidebar.selectbox(
    "Device", ["Tous"] + sorted(df["device"].dropna().unique())
)
status_f = st.sidebar.selectbox(
    "Statut", ["Tous"] + sorted(df["status"].dropna().unique())
)

df_f = df.copy()

if channel_f != "Tous":
    df_f = df_f[df_f["channel"] == channel_f]
if device_f != "Tous":
    df_f = df_f[df_f["device"] == device_f]
if status_f != "Tous":
    df_f = df_f[df_f["status"] == status_f]

st.subheader("Nombre d’enregistrements filtrés")
st.write(len(df_f))

# -------------------------------------------------------------
# KPI Cards
# -------------------------------------------------------------
st.subheader("KPI Clés")

col1, col2, col3, col4 = st.columns(4)

col1.metric("CTR Moyen", f"{df_f['CTR'].mean():.2%}")
col2.metric("CVR Moyen", f"{df_f['CVR'].mean():.2%}")
col3.metric("CPC Moyen (€)", f"{df_f['CPC'].mean():.2f}")
col4.metric("CPA Moyen (€)", f"{df_f['CPA'].mean():.2f}")

# -------------------------------------------------------------
# Performance par canal
# -------------------------------------------------------------
st.subheader("Performance par Canal")

kpi_by_channel = (
    df_f.groupby("channel")[["CTR", "CVR", "CPC", "CPA"]]
    .mean()
    .reset_index()
)

fig1 = px.bar(
    kpi_by_channel,
    x="channel",
    y=["CTR", "CVR"],
    barmode="group",
    title="CTR & CVR par Canal"
)
st.plotly_chart(fig1, use_container_width=True)

fig2 = px.bar(
    kpi_by_channel,
    x="channel",
    y=["CPC", "CPA"],
    barmode="group",
    title="CPC & CPA par Canal"
)
st.plotly_chart(fig2, use_container_width=True)

# -------------------------------------------------------------
# Funnel Marketing
# -------------------------------------------------------------
st.subheader(" Entonnoir Marketing")

df_funnel = (
    df_f.groupby("channel")[["impressions", "clicks", "conversions"]]
    .sum()
    .reset_index()
)

df_funnel_long = df_funnel.melt(
    id_vars="channel",
    value_vars=["impressions", "clicks", "conversions"],
    var_name="Étape",
    value_name="Volume"
)

fig3 = px.funnel(
    df_funnel_long,
    x="Volume",
    y="Étape",
    color="channel",
    title="Funnel Marketing par Canal"
)
st.plotly_chart(fig3, use_container_width=True)

# -------------------------------------------------------------
# Performance par Device
# -------------------------------------------------------------
st.subheader("Performance par Device")

kpi_by_device = (
    df_f.groupby("device")[["CTR", "CVR", "CPC", "CPA"]]
    .mean()
    .reset_index()
)

fig4 = px.bar(
    kpi_by_device,
    x="device",
    y=["CTR", "CVR", "CPC", "CPA"],
    barmode="group",
    title="KPI par Device"
)
st.plotly_chart(fig4, use_container_width=True)

# -------------------------------------------------------------
# Heatmap Canal x Device
# -------------------------------------------------------------
st.subheader("Heatmap Conversions : Canal × Device")

pivot = df_f.pivot_table(
    index="channel",
    columns="device",
    values="conversions",
    aggfunc="sum",
    fill_value=0
)

fig5 = px.imshow(
    pivot,
    text_auto=True,
    color_continuous_scale="Blues",
    title="Conversions par Canal et Device"
)
st.plotly_chart(fig5, use_container_width=True)
