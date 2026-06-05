#!/usr/bin/env python
# coding: utf-8

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.io as pio
import streamlit as st


# =========================================
# CONFIGURACIÓN GENERAL
# =========================================
BASE_DIR = Path(__file__).resolve().parent
pio.templates.default = "plotly_white"


# =========================================
# PATHS
# =========================================
path_energy_gdp = BASE_DIR / "energy-use-per-person-vs-gdp-per-capita.csv"
path_energy_mix = BASE_DIR / "global-energy-substitution.csv"
path_oil_consumption = BASE_DIR / "oil-consumption-by-country.csv"
path_baci = BASE_DIR / "BACI_HS22_Y2024_V202601.csv"
path_country_codes = BASE_DIR / "country_codes.csv"
path_product_codes = BASE_DIR / "product_codes.csv"
path_energy_mix_country = BASE_DIR / "energy-consumption-by-source-and-country.csv"


# =========================================
# CARGA DE DATOS
# =========================================
df_energy_gdp = pd.read_csv(path_energy_gdp)
df_energy_mix = pd.read_csv(path_energy_mix)
df_oil_consumption = pd.read_csv(path_oil_consumption)
df_baci = pd.read_csv(path_baci)
df_country_codes = pd.read_csv(path_country_codes)
df_product_codes = pd.read_csv(path_product_codes)
df_energy_mix_country = pd.read_csv(path_energy_mix_country)


# =========================================
# FUNCIÓN 1: SCATTER ENERGÍA VS PIB
# =========================================
def create_energy_gdp_scatter(df):
    df_plot = df[
        df["GDP per capita"].notna()
        & df["Per capita energy consumption"].notna()
        & df["World region according to OWID"].notna()
    ].copy()

    fig = px.scatter(
        df_plot,
        x="GDP per capita",
        y="Per capita energy consumption",
        color="World region according to OWID",
        hover_name="Entity",
        hover_data={
            "Code": True,
            "Year": True,
            "GDP per capita": ":,.0f",
            "Per capita energy consumption": ":,.0f",
            "World region according to OWID": False,
        },
        title="Consumo de energía per cápita vs PIB per cápita por país",
        labels={
            "GDP per capita": "PIB per cápita",
            "Per capita energy consumption": "Consumo de energía per cápita",
            "World region according to OWID": "Región",
        },
    )

    fig.update_xaxes(type="log")
    fig.update_yaxes(type="log")
    fig.update_traces(marker=dict(size=9, opacity=0.75))
    fig.update_layout(template="plotly_white", legend_title_text="Región")

    return fig


# =========================================
# FUNCIÓN 2: SUNBURST MIX ENERGÉTICO GLOBAL
# =========================================
def create_global_energy_mix_sunburst(df_energy_mix):
    df_energy_mix_2024 = df_energy_mix[
        (df_energy_mix["Entity"] == "World") & (df_energy_mix["Year"] == 2024)
    ].copy()

    row = df_energy_mix_2024.iloc[0]

    df_sunburst = pd.DataFrame(
        {
            "level_1": [
                "Renovables",
                "Renovables",
                "Renovables",
                "Renovables",
                "Renovables",
                "Renovables",
                "Nuclear",
                "Hidrocarburos",
                "Hidrocarburos",
                "Hidrocarburos",
            ],
            "level_2": [
                "Other renewables",
                "Modern biofuels",
                "Solar",
                "Wind",
                "Hydropower",
                "Traditional biomass",
                "Nuclear",
                "Natural gas",
                "Oil",
                "Coal",
            ],
            "value": [
                row["Other renewables"],
                row["Modern biofuels"],
                row["Solar"],
                row["Wind"],
                row["Hydropower"],
                row["Traditional biomass"],
                row["Nuclear"],
                row["Natural gas"],
                row["Oil"],
                row["Coal"],
            ],
        }
    )

    fig = px.sunburst(
        df_sunburst,
        path=["level_1", "level_2"],
        values="value",
        title="Mix energético global (2024)",
    )

    fig.update_layout(template="plotly_white")

    return fig


# =========================================
# FUNCIÓN 3: LÍNEA CONSUMO DE PETRÓLEO
# =========================================
def create_oil_consumption_line_chart(df_oil_consumption):
    fig = px.line(
        df_oil_consumption,
        x="Year",
        y="Oil",
        color="Entity",
        title="Evolución del consumo de petróleo",
        labels={
            "Year": "Año",
            "Oil": "Consumo de petróleo",
            "Entity": "Entidad",
        },
    )

    fig.update_layout(template="plotly_white")

    return fig


# =========================================
# PREPARACIÓN BACI OIL
# =========================================
def prepare_baci_oil(df_baci, df_country_codes, df_energy_gdp):
    

    # Filtrar petróleo: crudo y refinado
    df_baci_oil = df_baci[df_baci["k"].isin([270900, 271000])].copy()

    df_baci_oil["product_type"] = df_baci_oil["k"].map(
        {
            270900: "Crudo",
            271000: "Refinado",
        }
    )

    # Dummy Hormuz
    hormuz_exporters = [
        "Saudi Arabia",
        "Iraq",
        "Kuwait",
        "United Arab Emirates",
        "Oman",
        "Iran",
        "Qatar",
        "Bahrain",
    ]

    df_baci_oil["via_hormuz"] = (
        df_baci_oil["exporter_name"].isin(hormuz_exporters).astype(int)
    )

    df_baci_oil["hormuz_label"] = df_baci_oil["via_hormuz"].map(
        {
            1: "Hormuz",
            0: "No Hormuz",
        }
    )

    # Corrección de nombres
    name_corrections = {
        "USA": "United States",
        "Russian Federation": "Russia",
        "Rep. of Korea": "South Korea",
        "TÃ¼rkiye": "Turkey",
        "CÃ´te d'Ivoire": "Cote d'Ivoire",
        "CuraÃ§ao": "Curacao",
        "United Rep. of Tanzania": "Tanzania",
        "Dem. Rep. of the Congo": "Democratic Republic of Congo",
        "Viet Nam": "Vietnam",
        "Rep. of Moldova": "Moldova",
        "Dominican Rep.": "Dominican Republic",
        "Lao People's Dem. Rep.": "Laos",
        "Dem. People's Rep. of Korea": "North Korea",
        "Cabo Verde": "Cape Verde",
        "Bolivia (Plurinational State of)": "Bolivia",
        "Brunei Darussalam": "Brunei",
        "China, Hong Kong SAR": "Hong Kong",
        "China, Macao SAR": "Macao",
    }

    df_baci_oil["exporter_name"] = df_baci_oil["exporter_name"].replace(name_corrections)
    df_baci_oil["importer_name"] = df_baci_oil["importer_name"].replace(name_corrections)

    # Tablas auxiliares de región
    df_exporter_region = df_energy_gdp[
        ["Entity", "World region according to OWID"]
    ].dropna().drop_duplicates().rename(
        columns={
            "Entity": "exporter_name",
            "World region according to OWID": "exporter_region",
        }
    )

    df_importer_region = df_energy_gdp[
        ["Entity", "World region according to OWID"]
    ].dropna().drop_duplicates().rename(
        columns={
            "Entity": "importer_name",
            "World region according to OWID": "importer_region",
        }
    )

    df_baci_oil = df_baci_oil.merge(df_exporter_region, on="exporter_name", how="left")
    df_baci_oil = df_baci_oil.merge(df_importer_region, on="importer_name", how="left")

    # Imputación manual exportadores
    region_manual_map_exporter = {
        "Venezuela": "South America",
        "Other Asia, nes": "Asia",
        "South Sudan": "Africa",
        "Marshall Isds": "Oceania",
        "Gibraltar": "Europe",
        "Timor-Leste": "Asia",
        "Bosnia Herzegovina": "Europe",
        "Cayman Isds": "North America",
        "Br. Virgin Isds": "North America",
        "Curacao": "North America",
        "Cuba": "North America",
        "Turks and Caicos Isds": "North America",
        "Andorra": "Europe",
        "Anguilla": "North America",
        "American Samoa": "Oceania",
        "Saint Helena": "Africa",
        "Guam": "Oceania",
        "Saint Pierre and Miquelon": "North America",
        "FS Micronesia": "Oceania",
        "French Polynesia": "Oceania",
        "New Caledonia": "Oceania",
        "Eritrea": "Africa",
        "Central African Rep.": "Africa",
        "San Marino": "Europe",
        "North Korea": "Asia",
        "Pitcairn": "Oceania",
        "Saint BarthÃ©lemy": "North America",
        "Br. Indian Ocean Terr.": "Asia",
        "Solomon Isds": "Oceania",
        "Tuvalu": "Oceania",
        "Saint Maarten": "North America",
        "Bonaire": "North America",
        "Christmas Isds": "Oceania",
        "Cook Isds": "Oceania",
        "Wallis and Futuna Isds": "Oceania",
        "Falkland Isds (Malvinas)": "South America",
        "Palau": "Oceania",
    }

    df_baci_oil["exporter_region"] = df_baci_oil["exporter_region"].fillna(
        df_baci_oil["exporter_name"].map(region_manual_map_exporter)
    )

    # Imputación manual importadores
    region_manual_map_importer = {
        "Other Asia, nes": "Asia",
        "Gibraltar": "Europe",
        "Marshall Isds": "Oceania",
        "Venezuela": "South America",
        "Bosnia Herzegovina": "Europe",
        "Bonaire": "North America",
        "Curacao": "North America",
        "Guam": "Oceania",
        "New Caledonia": "Oceania",
        "Cayman Isds": "North America",
        "Central African Rep.": "Africa",
        "French Polynesia": "Oceania",
        "American Samoa": "Oceania",
        "Andorra": "Europe",
        "Timor-Leste": "Asia",
        "Solomon Isds": "Oceania",
        "Saint Maarten": "North America",
        "N. Mariana Isds": "Oceania",
        "Cuba": "North America",
        "Br. Virgin Isds": "North America",
        "Turks and Caicos Isds": "North America",
        "Cook Isds": "Oceania",
        "Palau": "Oceania",
        "Br. Indian Ocean Terr.": "Asia",
        "FS Micronesia": "Oceania",
        "Falkland Isds (Malvinas)": "South America",
        "State of Palestine": "Asia",
        "Yemen": "Asia",
        "Saint Pierre and Miquelon": "North America",
        "Christmas Isds": "Oceania",
        "Tuvalu": "Oceania",
        "Saint BarthÃ©lemy": "North America",
        "South Sudan": "Africa",
        "Wallis and Futuna Isds": "Oceania",
        "Anguilla": "North America",
        "Saint Helena": "Africa",
        "North Korea": "Asia",
        "Niue": "Oceania",
        "Norfolk Isds": "Oceania",
        "Eritrea": "Africa",
        "San Marino": "Europe",
        "Pitcairn": "Oceania",
        "Fr. South Antarctic Terr.": "Oceania",
        "Cocos Isds": "Oceania",
        "Montserrat": "North America",
    }

    df_baci_oil["importer_region"] = df_baci_oil["importer_region"].fillna(
        df_baci_oil["importer_name"].map(region_manual_map_importer)
    )

    return df_baci_oil


# =========================================
# FUNCIÓN 4: TREEMAP DESTINOS HORMUZ
# =========================================
def create_hormuz_destinations_treemap_by_region(df_baci_oil):
    df_hormuz_destinations = (
        df_baci_oil[df_baci_oil["via_hormuz"] == 1]
        .groupby(["importer_region", "importer_name"], as_index=False)["v"]
        .sum()
        .rename(columns={"v": "total_imports_hormuz"})
        .sort_values(["importer_region", "total_imports_hormuz"], ascending=[True, False])
    )

    fig = px.treemap(
        df_hormuz_destinations,
        path=[px.Constant("Hormuz"), "importer_region", "importer_name"],
        values="total_imports_hormuz",
        color="importer_region",
        title="Destinos del petróleo exportado potencialmente vía Hormuz",
        labels={
            "total_imports_hormuz": "Importaciones",
            "importer_region": "Región",
            "importer_name": "País destino",
        },
    )

    fig.update_layout(template="plotly_white")
    fig.update_traces(root_color="white")

    return fig


# =========================================
# PREPARAR ENERGY MIX COUNTRY 2024
# =========================================
def prepare_energy_mix_country_2024(df_energy_mix_country):
    df_2024 = df_energy_mix_country[
        df_energy_mix_country["Year"] == 2024
    ].copy().reset_index(drop=True)

    energy_cols_required = [
        "Oil",
        "Gas",
        "Coal",
        "Nuclear",
        "Hydropower",
        "Solar",
        "Wind",
        "Biofuels",
        "Other renewables",
    ]

    df_2024 = (
        df_2024[
            ~df_2024["Code"].str.startswith("OWID", na=False)
        ]
        .dropna(subset=energy_cols_required)
        .copy()
    )

    energy_cols_total = [
        "Oil",
        "Gas",
        "Coal",
        "Nuclear",
        "Hydropower",
        "Solar",
        "Wind",
        "Biofuels",
        "Other renewables",
    ]

    energy_cols_hydrocarbons = [
        "Oil",
        "Gas",
        "Coal",
    ]

    df_2024["energy_total"] = df_2024[energy_cols_total].sum(axis=1)
    df_2024["hydrocarbons_total"] = df_2024[energy_cols_hydrocarbons].sum(axis=1)
    df_2024["hydrocarbons_share"] = (
        df_2024["hydrocarbons_total"] / df_2024["energy_total"]
    )
    df_2024["hydrocarbons_share_pct"] = df_2024["hydrocarbons_share"] * 100

    return df_2024


# =========================================
# PREPARAR DATAFRAME DE VULNERABILIDAD
# =========================================
def prepare_vulnerability_scatter(df_baci_oil, df_energy_mix_country_2024):
    df_imports_total = (
        df_baci_oil.groupby("importer_name", as_index=False)["v"]
        .sum()
        .rename(columns={"v": "imports_total"})
    )

    df_imports_hormuz = (
        df_baci_oil[df_baci_oil["via_hormuz"] == 1]
        .groupby("importer_name", as_index=False)["v"]
        .sum()
        .rename(columns={"v": "imports_hormuz"})
    )

    df_importer_region_unique = (
        df_baci_oil[["importer_name", "importer_region"]]
        .drop_duplicates()
        .copy()
    )

    df_vulnerability_baci = df_imports_total.merge(
        df_imports_hormuz,
        on="importer_name",
        how="left",
    )

    df_vulnerability_baci["imports_hormuz"] = df_vulnerability_baci["imports_hormuz"].fillna(0)
    df_vulnerability_baci["imports_hormuz_pct"] = (
        df_vulnerability_baci["imports_hormuz"] / df_vulnerability_baci["imports_total"]
    )

    df_vulnerability_baci = df_vulnerability_baci.merge(
        df_importer_region_unique,
        on="importer_name",
        how="left",
    )

    df_energy_mix_scatter = df_energy_mix_country_2024[
        [
            "Entity",
            "Code",
            "energy_total",
            "hydrocarbons_total",
            "hydrocarbons_share",
            "hydrocarbons_share_pct",
        ]
    ].copy()

    df_vulnerability_scatter = df_vulnerability_baci.merge(
        df_energy_mix_scatter,
        left_on="importer_name",
        right_on="Entity",
        how="inner",
    )

    df_vulnerability_scatter = df_vulnerability_scatter.drop(columns=["Entity"])
    df_vulnerability_scatter = df_vulnerability_scatter.sort_values(
        "imports_hormuz",
        ascending=False,
    ).reset_index(drop=True)

    return df_vulnerability_scatter


# =========================================
# FUNCIÓN 5: SCATTER DE VULNERABILIDAD
# =========================================
def create_vulnerability_scatter(df_vulnerability_scatter):
    fig = px.scatter(
        df_vulnerability_scatter,
        x="imports_hormuz_pct",
        y="hydrocarbons_share_pct",
        size="imports_total",
        color="importer_region",
        hover_name="importer_name",
        hover_data={
            "imports_total": ":,.0f",
            "imports_hormuz": ":,.0f",
            "imports_hormuz_pct": ":.1%",
            "hydrocarbons_share_pct": ":.1f",
            "importer_region": True,
            "Code": True,
        },
        title="Vulnerabilidad de países ante un cierre potencial de Hormuz",
        labels={
            "imports_hormuz_pct": "% importaciones potencialmente vía Hormuz",
            "hydrocarbons_share_pct": "% del mix energético que son hidrocarburos",
            "imports_total": "Importaciones totales",
            "importer_region": "Región",
        },
    )

    fig.update_layout(template="plotly_white")

    return fig


# =========================================
# PREPARACIÓN DE DATAFRAMES DERIVADOS
# =========================================
df_baci_oil = prepare_baci_oil(df_baci, df_country_codes, df_energy_gdp)
df_energy_mix_country_2024 = prepare_energy_mix_country_2024(df_energy_mix_country)
df_vulnerability_scatter = prepare_vulnerability_scatter(
    df_baci_oil, df_energy_mix_country_2024
)


# =========================================
# GENERAR FIGURAS
# =========================================
fig_energy_gdp = create_energy_gdp_scatter(df_energy_gdp)
fig_energy_mix = create_global_energy_mix_sunburst(df_energy_mix)
fig_oil_consumption = create_oil_consumption_line_chart(df_oil_consumption)
fig_hormuz_destinations = create_hormuz_destinations_treemap_by_region(df_baci_oil)
fig_vulnerability = create_vulnerability_scatter(df_vulnerability_scatter)


# =========================================
# STREAMLIT APP
# =========================================
st.set_page_config(
    page_title="Impacto potencial del cierre de Hormuz",
    layout="wide",
)

st.title("Impacto potencial del cierre del estrecho de Hormuz")
st.markdown(
    """
    Este dashboard explora la relación entre energía, dependencia del petróleo
    y vulnerabilidad de los países ante una posible interrupción del tránsito por Hormuz.
    """
)

st.subheader("Resumen clave")

col1, col2, col3 = st.columns(3)

col1.metric("Petróleo mundial vía Hormuz", "~20%")
col2.metric("Hidrocarburos", "~75% consumo energético")
col3.metric("Destino principal", "~70% Asia")

st.markdown("---")

st.subheader("1. Energía y desarrollo")
st.plotly_chart(fig_energy_gdp, use_container_width=True)

st.markdown("---")

st.subheader("2. Mix energético global")
st.plotly_chart(fig_energy_mix, use_container_width=True)

st.markdown("---")

st.subheader("3. Evolución del consumo de petróleo")
st.plotly_chart(fig_oil_consumption, use_container_width=True)

st.markdown("---")

st.subheader("4. Destinos del petróleo potencialmente vía Hormuz")
st.plotly_chart(fig_hormuz_destinations, use_container_width=True)

st.markdown("---")

st.subheader("5. Vulnerabilidad de los países")
st.plotly_chart(fig_vulnerability, use_container_width=True)

st.markdown(
    """
    **Lectura del gráfico de vulnerabilidad**  
    - **Eje X**: porcentaje de importaciones potencialmente vía Hormuz  
    - **Eje Y**: porcentaje del mix energético que son hidrocarburos  
    - **Tamaño**: importaciones totales de petróleo  
    - **Color**: región del importador
    """
)
