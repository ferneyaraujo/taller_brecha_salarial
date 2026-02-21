"""
Dashboard: Brecha Salarial de Género en Colombia
Herramienta de análisis para analistas de RRHH y líderes organizacionales
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# ─────────────────────────────────────────────
# CONFIGURACIÓN DE PÁGINA
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Brecha Salarial de Género",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# PALETA DE COLORES Y CSS PERSONALIZADO
# ─────────────────────────────────────────────
COLOR_FEMALE = "#D63384"   # rosa magenta
COLOR_MALE   = "#2563EB"   # azul vivo
COLOR_BG     = "#F5F7FB"
COLOR_CARD   = "#FFFFFF"
COLOR_BORDER = "#DDE3F0"
COLOR_TEXT   = "#1E2340"
COLOR_ACCENT = "#5B5EF4"

PALETTE = {
    "Female": COLOR_FEMALE,
    "Male":   COLOR_MALE,
}

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

* {{ font-family: 'Inter', sans-serif; }}

/* Fondo general */
[data-testid="stAppViewContainer"] {{
    background-color: {COLOR_BG};
    color: {COLOR_TEXT};
}}
[data-testid="stHeader"] {{
    background-color: {COLOR_BG};
}}
[data-testid="stSidebar"] {{
    background-color: {COLOR_CARD};
    border-right: 1px solid {COLOR_BORDER};
    box-shadow: 2px 0 12px rgba(0,0,0,0.06);
}}
[data-testid="stSidebar"] .stMarkdown p {{
    color: #4A5270;
}}

/* Tarjetas KPI */
.kpi-card {{
    background: {COLOR_CARD};
    border: 1px solid {COLOR_BORDER};
    border-radius: 14px;
    padding: 20px 24px;
    text-align: center;
    box-shadow: 0 2px 14px rgba(91,94,244,0.08);
    margin-bottom: 8px;
    transition: box-shadow 0.2s;
}}
.kpi-card:hover {{
    box-shadow: 0 4px 24px rgba(91,94,244,0.16);
}}
.kpi-label {{
    font-size: 0.72rem;
    color: #7480A0;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 6px;
    font-weight: 600;
}}
.kpi-value {{
    font-size: 1.9rem;
    font-weight: 800;
    color: {COLOR_ACCENT};
    line-height: 1.2;
}}
.kpi-sub {{
    font-size: 0.76rem;
    color: #9BA8C0;
    margin-top: 4px;
}}

/* Encabezado */
.main-title {{
    font-size: 2.4rem;
    font-weight: 800;
    background: linear-gradient(90deg, {COLOR_FEMALE}, {COLOR_ACCENT}, {COLOR_MALE});
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 4px;
}}
.main-subtitle {{
    color: #5A6480;
    font-size: 1.0rem;
    margin-bottom: 28px;
}}

/* Separador de sección */
.section-title {{
    font-size: 0.88rem;
    font-weight: 700;
    color: {COLOR_ACCENT};
    text-transform: uppercase;
    letter-spacing: 1.2px;
    border-left: 3px solid {COLOR_ACCENT};
    padding-left: 10px;
    margin: 28px 0 6px 0;
    background: linear-gradient(90deg, rgba(91,94,244,0.07) 0%, transparent 80%);
    padding-top: 6px;
    padding-bottom: 6px;
    border-radius: 0 6px 6px 0;
}}
.question-tag {{
    font-size: 0.81rem;
    color: #7480A0;
    font-style: italic;
    margin-bottom: 12px;
}}

/* Gráficos */
.stPlotlyChart {{
    border-radius: 12px;
    overflow: hidden;
    background: {COLOR_CARD};
    border: 1px solid {COLOR_BORDER};
    box-shadow: 0 1px 8px rgba(0,0,0,0.05);
    padding: 4px;
}}

/* Sidebar labels */
[data-testid="stSidebar"] label {{
    color: #4A5270 !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
}}
[data-testid="stSidebar"] .stSlider label {{
    color: #4A5270 !important;
}}

/* Divisor */
hr {{
    border-color: {COLOR_BORDER} !important;
}}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CARGA DE DATOS
# ─────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("colombia_salary_gap_analysis.csv")
    df["has_sons"] = df["has_sons"].astype(str)
    df["job_level_label"] = "Nivel " + df["job_level"].astype(str)
    # Mapa de educación para ordenar
    edu_order = {"High School": 1, "Bachelor": 2, "Master": 3, "PhD": 4}
    df["edu_order"] = df["education_level"].map(edu_order)
    return df

df_raw = load_data()

# ─────────────────────────────────────────────
# SIDEBAR – FILTROS INTERACTIVOS
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## Filtros")
    st.markdown("---")

    # Departamento
    depts = sorted(df_raw["department"].unique().tolist())
    selected_depts = st.multiselect(
        "Departamento",
        options=depts,
        default=depts,
    )

    # Nivel educativo
    edu_levels = ["High School", "Bachelor", "Master", "PhD"]
    selected_edu = st.multiselect(
        "Nivel educativo",
        options=edu_levels,
        default=edu_levels,
    )

    # Rango de experiencia
    exp_min, exp_max = int(df_raw["years_of_experience"].min()), int(df_raw["years_of_experience"].max())
    exp_range = st.slider(
        "Años de experiencia",
        min_value=exp_min,
        max_value=exp_max,
        value=(exp_min, exp_max),
    )

    # Rango de edad
    age_min, age_max = int(df_raw["age"].min()), int(df_raw["age"].max())
    age_range = st.slider(
        "Rango de edad",
        min_value=age_min,
        max_value=age_max,
        value=(age_min, age_max),
    )

    # Nivel de cargo
    job_levels = sorted(df_raw["job_level"].unique().tolist())
    selected_levels = st.multiselect(
        "Nivel de cargo (1=Junior … 5=Senior)",
        options=job_levels,
        default=job_levels,
        format_func=lambda x: f"Nivel {x}",
    )

    # Métrica principal a visualizar
    st.markdown("---")
    metric_choice = st.radio(
        "Métrica principal",
        options=["Salario mensual", "Compensación total"],
        index=0,
    )

    st.markdown("---")
    st.markdown(
        "<div style='color:#8892b0;font-size:0.75rem;text-align:center'>"
        "Datos: colombia_salary_gap_analysis.csv<br>"
        "551 registros · 10 variables</div>",
        unsafe_allow_html=True,
    )

# Columna de métrica seleccionada
metric_col = "monthly_salary" if metric_choice == "Salario mensual" else "total_compensation"
metric_label = "Salario Mensual (COP)" if metric_choice == "Salario mensual" else "Compensación Total (COP)"

# ─────────────────────────────────────────────
# FILTRAR DATOS
# ─────────────────────────────────────────────
df = df_raw[
    df_raw["department"].isin(selected_depts) &
    df_raw["education_level"].isin(selected_edu) &
    df_raw["years_of_experience"].between(exp_range[0], exp_range[1]) &
    df_raw["age"].between(age_range[0], age_range[1]) &
    df_raw["job_level"].isin(selected_levels)
].copy()

# ─────────────────────────────────────────────
# ENCABEZADO
# ─────────────────────────────────────────────
st.markdown('<div class="main-title">Brecha Salarial de Género</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="main-subtitle">Herramienta para analistas de RRHH y líderes organizacionales que responde: '
    '¿Qué tan grande es la brecha salarial entre hombres y mujeres, y qué factores la explican?</div>',
    unsafe_allow_html=True,
)

if df.empty:
    st.error("⚠️ No hay datos con los filtros seleccionados. Por favor ajusta los filtros en el panel lateral.")
    st.stop()

# ─────────────────────────────────────────────
# KPIs
# ─────────────────────────────────────────────
g_male   = df[df["gender"] == "Male"]
g_female = df[df["gender"] == "Female"]

avg_male   = g_male[metric_col].mean()
avg_female = g_female[metric_col].mean()
gap_pct    = (avg_male - avg_female) / avg_male * 100 if avg_male > 0 else 0
n_total    = len(df)
prom_male  = g_male["promotion_history"].mean()
prom_female= g_female["promotion_history"].mean()

def fmt_cop(val):
    if val >= 1_000_000:
        return f"${val/1_000_000:.1f}M"
    return f"${val/1_000:.0f}K"

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-label">Salario promedio Hombre</div>
        <div class="kpi-value">{fmt_cop(avg_male)}</div>
        <div class="kpi-sub">{len(g_male)} registros</div>
    </div>""", unsafe_allow_html=True)

with col2:
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-label">Salario promedio Mujer</div>
        <div class="kpi-value">{fmt_cop(avg_female)}</div>
        <div class="kpi-sub">{len(g_female)} registros</div>
    </div>""", unsafe_allow_html=True)

with col3:
    color_gap = "#FF6B6B" if gap_pct > 5 else "#FFD166" if gap_pct > 0 else "#06D6A0"
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-label">Brecha salarial</div>
        <div class="kpi-value" style="color:{color_gap}">{gap_pct:.1f}%</div>
        <div class="kpi-sub">Hombres ganan más</div>
    </div>""", unsafe_allow_html=True)

with col4:
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-label">Promociones promedio H/M</div>
        <div class="kpi-value">{prom_male:.1f} / {prom_female:.1f}</div>
        <div class="kpi-sub">Historial de ascensos</div>
    </div>""", unsafe_allow_html=True)

with col5:
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-label">Total registros</div>
        <div class="kpi-value">{n_total}</div>
        <div class="kpi-sub">con filtros aplicados</div>
    </div>""", unsafe_allow_html=True)

# Configuración de tema Plotly compartida
PLOT_THEME = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color=COLOR_TEXT, size=12),
    legend=dict(bgcolor="rgba(255,255,255,0.85)", bordercolor=COLOR_BORDER, borderwidth=1),
    margin=dict(t=50, b=40, l=40, r=20),
    xaxis=dict(gridcolor="#E8EDF6", zerolinecolor="#C8D0E0", linecolor="#C8D0E0"),
    yaxis=dict(gridcolor="#E8EDF6", zerolinecolor="#C8D0E0", linecolor="#C8D0E0"),
)

# ─────────────────────────────────────────────
# FILA 1: Gráfico 1 + Gráfico 2
# ─────────────────────────────────────────────
st.markdown('<div class="section-title">Análisis por Departamento y Distribución Salarial</div>', unsafe_allow_html=True)
row1_col1, row1_col2 = st.columns([1.3, 1], gap="medium")

# ── GRÁFICO 1: Barras agrupadas por departamento ──
with row1_col1:
    st.markdown('<div class="question-tag">¿En qué departamentos es mayor la brecha salarial entre hombres y mujeres?</div>', unsafe_allow_html=True)

    dept_salary = (
        df.groupby(["department", "gender"])[metric_col]
        .mean()
        .reset_index()
        .rename(columns={metric_col: "avg_salary"})
    )
    dept_salary["avg_salary_M"] = dept_salary["avg_salary"] / 1_000_000

    fig1 = px.bar(
        dept_salary,
        x="department",
        y="avg_salary_M",
        color="gender",
        barmode="group",
        color_discrete_map=PALETTE,
        labels={"avg_salary_M": "Salario promedio (millones COP)", "department": "Departamento", "gender": "Género"},
        title=f"<b>{metric_label.split(' (')[0]} promedio por departamento</b>",
    )
    fig1.update_layout(**PLOT_THEME)
    fig1.update_traces(
        marker_line_width=0,
        hovertemplate="<b>%{x}</b><br>%{y:.1f}M COP<extra></extra>",
    )
    st.plotly_chart(fig1, use_container_width=True)

# ── GRÁFICO 2: Violin plot de distribución salarial ──
with row1_col2:
    st.markdown('<div class="question-tag">¿Cuánto varía la distribución salarial entre hombres y mujeres?</div>', unsafe_allow_html=True)

    df_plot2 = df.copy()
    df_plot2["salary_M"] = df_plot2[metric_col] / 1_000_000

    fig2 = px.violin(
        df_plot2,
        y="salary_M",
        x="gender",
        color="gender",
        box=True,
        points="outliers",
        color_discrete_map=PALETTE,
        labels={"salary_M": "Salario (millones COP)", "gender": "Género"},
        title="<b>Distribución salarial por género</b>",
    )
    fig2.update_layout(**PLOT_THEME)
    fig2.update_traces(
        meanline_visible=True,
        hovertemplate="%{y:.1f}M COP<extra></extra>",
    )
    st.plotly_chart(fig2, use_container_width=True)

# ─────────────────────────────────────────────
# FILA 2: Gráfico 3 + Gráfico 4
# ─────────────────────────────────────────────
st.markdown('<div class="section-title">Educación, Experiencia y Brecha Salarial</div>', unsafe_allow_html=True)
row2_col1, row2_col2 = st.columns([1, 1.3], gap="medium")

# ── GRÁFICO 3: Brecha por nivel educativo ──
with row2_col1:
    st.markdown('<div class="question-tag">¿Un mayor nivel educativo reduce la brecha salarial entre géneros?</div>', unsafe_allow_html=True)

    edu_salary = (
        df.groupby(["education_level", "gender"])[metric_col]
        .mean()
        .reset_index()
    )
    edu_pivot = edu_salary.pivot(index="education_level", columns="gender", values=metric_col).reset_index()
    edu_pivot = edu_pivot.merge(
        df[["education_level", "edu_order"]].drop_duplicates(), on="education_level"
    ).sort_values("edu_order")

    if "Male" in edu_pivot.columns and "Female" in edu_pivot.columns:
        edu_pivot["gap_pct"] = (edu_pivot["Male"] - edu_pivot["Female"]) / edu_pivot["Male"] * 100
        edu_pivot["Male_M"] = edu_pivot["Male"] / 1_000_000
        edu_pivot["Female_M"] = edu_pivot["Female"] / 1_000_000

        fig3 = go.Figure()
        fig3.add_trace(go.Bar(
            y=edu_pivot["education_level"],
            x=edu_pivot["Male_M"],
            name="Hombre",
            orientation="h",
            marker_color=COLOR_MALE,
            hovertemplate="Hombre: %{x:.1f}M COP<extra></extra>",
        ))
        fig3.add_trace(go.Bar(
            y=edu_pivot["education_level"],
            x=edu_pivot["Female_M"],
            name="Mujer",
            orientation="h",
            marker_color=COLOR_FEMALE,
            hovertemplate="Mujer: %{x:.1f}M COP<extra></extra>",
        ))
        # Anotaciones de brecha
        for _, row_e in edu_pivot.iterrows():
            fig3.add_annotation(
                x=max(row_e.get("Male_M", 0), row_e.get("Female_M", 0)) + 0.3,
                y=row_e["education_level"],
                text=f"Brecha: {row_e['gap_pct']:.1f}%",
                showarrow=False,
                font=dict(color="#D97706", size=11, family="Inter"),
            )
        fig3.update_layout(
            **PLOT_THEME,
            barmode="group",
            title="<b>Salario promedio por nivel educativo</b>",
            xaxis_title="Salario promedio (millones COP)",
            yaxis_title="",
        )
        st.plotly_chart(fig3, use_container_width=True)

# ── GRÁFICO 4: Scatter salario vs experiencia ──
with row2_col2:
    st.markdown('<div class="question-tag">¿La experiencia laboral beneficia económicamente a hombres y mujeres por igual?</div>', unsafe_allow_html=True)

    df_scatter = df.copy()
    df_scatter["salary_M"] = df_scatter[metric_col] / 1_000_000

    fig4 = px.scatter(
        df_scatter,
        x="years_of_experience",
        y="salary_M",
        color="gender",
        color_discrete_map=PALETTE,
        opacity=0.65,
        trendline="ols",
        trendline_scope="trace",
        labels={
            "years_of_experience": "Años de experiencia",
            "salary_M": "Salario (millones COP)",
            "gender": "Género",
        },
        title="<b>Salario vs. Años de experiencia</b>",
        hover_data={"department": True, "education_level": True},
    )
    fig4.update_layout(**PLOT_THEME)
    fig4.update_traces(marker=dict(size=7, line=dict(width=0)))
    st.plotly_chart(fig4, use_container_width=True)

# ─────────────────────────────────────────────
# FILA 3: Gráfico 5 (heatmap) + Gráfico 6 (barras brecha por nivel de cargo)
# ─────────────────────────────────────────────
st.markdown('<div class="section-title">Nivel de Cargo y Promociones</div>', unsafe_allow_html=True)
row3_col1, row3_col2 = st.columns([1.1, 1], gap="medium")

# ── GRÁFICO 5: Heatmap de salario promedio por nivel de cargo y género ──
with row3_col1:
    st.markdown('<div class="question-tag">¿Existe brecha salarial en todos los niveles jerárquicos de la empresa?</div>', unsafe_allow_html=True)

    heat_data = (
        df.groupby(["job_level", "gender"])[metric_col]
        .mean()
        .reset_index()
    )
    heat_pivot = heat_data.pivot(index="job_level", columns="gender", values=metric_col)
    heat_pivot_M = heat_pivot / 1_000_000

    # Calcular porcentaje de brecha por nivel
    if "Male" in heat_pivot_M.columns and "Female" in heat_pivot_M.columns:
        gap_matrix = ((heat_pivot_M["Male"] - heat_pivot_M["Female"]) / heat_pivot_M["Male"] * 100)

        fig5 = go.Figure()

        # Barras apiladas por género mostrando brecha relativa
        fig5 = px.bar(
            heat_data.assign(salary_M=lambda x: x[metric_col] / 1_000_000),
            x="job_level",
            y="salary_M",
            color="gender",
            barmode="group",
            color_discrete_map=PALETTE,
            labels={
                "job_level": "Nivel de cargo",
                "salary_M": "Salario promedio (millones COP)",
                "gender": "Género",
            },
            title="<b>Salario promedio por nivel de cargo</b>",
            text_auto=".1f",
        )
        # Agregar anotaciones de brecha
        for lvl, gap in gap_matrix.items():
            fig5.add_annotation(
                x=lvl,
                y=heat_pivot_M.loc[lvl].max() + 1,
                text=f"Δ {gap:.1f}%",
                showarrow=False,
                font=dict(color="#D97706", size=11, family="Inter"),
            )
        fig5.update_layout(**PLOT_THEME)
        fig5.update_traces(
            textfont_size=10,
            textangle=0,
            cliponaxis=False,
            marker_line_width=0,
        )
        st.plotly_chart(fig5, use_container_width=True)

# ── GRÁFICO 6: Historial de promociones por género y nivel educativo ──
with row3_col2:
    st.markdown('<div class="question-tag">¿Las mujeres reciben menos ascensos que los hombres independientemente del nivel educativo?</div>', unsafe_allow_html=True)

    prom_data = (
        df.groupby(["education_level", "gender"])["promotion_history"]
        .mean()
        .reset_index()
        .merge(df[["education_level", "edu_order"]].drop_duplicates(), on="education_level")
        .sort_values("edu_order")
    )

    fig6 = px.line(
        prom_data,
        x="education_level",
        y="promotion_history",
        color="gender",
        markers=True,
        color_discrete_map=PALETTE,
        labels={
            "education_level": "Nivel educativo",
            "promotion_history": "Promedio de ascensos",
            "gender": "Género",
        },
        title="<b>Historial de ascensos por nivel educativo</b>",
    )
    fig6.update_layout(**PLOT_THEME)
    fig6.update_traces(line_width=3, marker_size=9)
    st.plotly_chart(fig6, use_container_width=True)

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#9BA8C0;font-size:0.78rem;padding:8px 0'>"
    "Dashboard de Brecha Salarial · Maestría en Analítica de Datos · "
    "Valentina Torres - Mario Orozco - David Merlano - Angie De Alba - Ferney Araujo · "
    "Modelos Analíticos – Daniel Romero · 2025"
    "</div>",
    unsafe_allow_html=True,
)
