import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parent
DATA_DIR = ROOT_DIR / "data"
MODELS_DIR = ROOT_DIR / "models"

st.set_page_config(
    page_title="GetAround — tableau de décision",
    layout="wide",
    page_icon="🚗",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
.block-container {padding-top: 1.2rem; padding-bottom: 2rem;}
[data-testid="stMetricValue"] {font-size: 1.7rem;}
.hero-card {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    color: white;
    padding: 1.2rem 1.35rem;
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,0.08);
    margin-bottom: 0.8rem;
}
.soft-card {
    background: #f8fafc;
    color: #0f172a;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 1rem 1.1rem;
    margin-bottom: 0.8rem;
}
.soft-card h4 {color: #0f172a;}
.soft-card code {background: #e2e8f0; color: #0f172a; padding: 0.1rem 0.35rem; border-radius: 4px;}
.small-note {color: #475569; font-size: 0.92rem;}
.badge {
    display: inline-block;
    background: #dcfce7;
    color: #166534;
    font-weight: 600;
    padding: 0.22rem 0.55rem;
    border-radius: 999px;
    margin-right: 0.35rem;
    margin-bottom: 0.35rem;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


@st.cache_data
def load_delay_data():
    return pd.read_excel(DATA_DIR / "get_around_delay_analysis.xlsx", sheet_name="rentals_data")


@st.cache_data
def load_thresholds():
    return pd.read_csv(DATA_DIR / "threshold_simulation.csv")


@st.cache_data
def load_summary():
    return json.loads((DATA_DIR / "business_summary.json").read_text(encoding="utf-8"))


@st.cache_data
def load_pricing_metrics():
    return json.loads((MODELS_DIR / "pricing_metrics.json").read_text(encoding="utf-8"))


summary = load_summary()
threshold_df = load_thresholds()
delay_df = load_delay_data()
pricing_metrics = load_pricing_metrics()
rec = summary["recommendation"]
fallback = summary["conservative_fallback"]

scenario_candidates = threshold_df[
    (threshold_df["scope"].isin(["all", "connect"]))
    & (threshold_df["threshold_min"].isin([30, 60, 90, 120, 150, 180]))
].copy()
scenario_candidates["decision_score"] = (
    scenario_candidates["solved_share_of_all_problematic_cases"]
    - 0.5 * scenario_candidates["affected_share_of_all_rentals"]
)

st.sidebar.title("GetAround — tableau de bord")
st.sidebar.markdown(
    "<span class='badge'>Décision</span><span class='badge'>API</span><span class='badge'>Déploiement</span>",
    unsafe_allow_html=True,
)
st.sidebar.write("Cette application est pensée comme un outil d’aide à la décision, et non comme une simple restitution de notebook.")
section = st.sidebar.radio(
    "Navigation",
    ["Synthèse", "Simulateur", "Analyse du risque", "API de prix", "Déploiement"],
)
st.sidebar.markdown("---")
st.sidebar.metric("Recommandation principale", f"{rec['threshold_min']} min · ALL")
st.sidebar.metric("Option prudente", f"{fallback['threshold_min']} min · CONNECT")
st.sidebar.metric("Cas problématiques", f"{summary['operational_risk']['problematic_cases']:,}")
st.sidebar.caption("Le jeu de données ne contient pas de chiffre d’affaires : l’impact commercial est donc approché par le nombre de locations affectées.")

st.title("🚗 GetAround — tableau de décision")
st.caption("Tableau de bord dédié à l’analyse des retards, complété par une synthèse du volet API de prédiction de prix.")

hero_left, hero_right = st.columns([1.35, 1])

with hero_left:
    st.markdown(
        f"""
        <div class="hero-card">
            <h3 style="margin-top:0;">Décision recommandée</h3>
            <p style="font-size:1.07rem; line-height:1.55;">
                Activer un délai minimal de <b>{rec['threshold_min']} minutes sur l’ensemble du parc</b>.
                C’est le premier seuil qui dépasse <b>80 % de protection</b> tout en conservant un impact commercial limité.
            </p>
            <p style="margin-bottom:0;">
                <b>{rec['solved_problematic_cases']}</b> cas problématiques résolus
                ({rec['solved_share_of_all_problematic_cases']*100:.1f} %) pour seulement
                <b>{rec['affected_rentals']}</b> locations affectées
                ({rec['affected_share_of_all_rentals']*100:.1f} % du total).
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with hero_right:
    st.markdown(
        """
        <div class="soft-card">
            <h4 style="margin-top:0;">Contenu du projet</h4>
            <ul>
                <li>Recommandation claire et chiffrée</li>
                <li>Simulateur de scénarios</li>
                <li>Synthèse du volet API</li>
                <li>Structure orientée déploiement</li>
                <li>Documentation d’exploitation</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

k1, k2, k3, k4 = st.columns(4)
k1.metric("Locations totales", f"{summary['dataset']['all_rentals']:,}")
k2.metric("Locations liées", f"{summary['dataset']['linked_rentals']:,}", f"{summary['dataset']['linked_rentals_share']*100:.1f} % du total")
k3.metric("Cas problématiques", f"{summary['operational_risk']['problematic_cases']:,}", f"{summary['operational_risk']['problematic_share_of_all_rentals']*100:.1f} % du total")
k4.metric("Modèle de prix", pricing_metrics["best_model"], f"MAE {pricing_metrics['chosen_model_metrics']['MAE']:.2f} €/jour")

if section == "Synthèse":
    st.subheader("Tableau de synthèse")
    scorecard = scenario_candidates[
        [
            "scope",
            "threshold_min",
            "affected_rentals",
            "affected_share_of_all_rentals",
            "solved_problematic_cases",
            "solved_share_of_all_problematic_cases",
            "efficiency_solved_per_affected",
            "decision_score",
        ]
    ].sort_values("decision_score", ascending=False).copy()

    for col in [
        "affected_share_of_all_rentals",
        "solved_share_of_all_problematic_cases",
        "efficiency_solved_per_affected",
        "decision_score",
    ]:
        scorecard[col] = (scorecard[col] * 100).round(1)

    scorecard = scorecard.rename(
        columns={
            "scope": "Périmètre",
            "threshold_min": "Seuil (min)",
            "affected_rentals": "Locations affectées",
            "affected_share_of_all_rentals": "Part des locations affectées (%)",
            "solved_problematic_cases": "Cas problématiques résolus",
            "solved_share_of_all_problematic_cases": "Part des cas résolus (%)",
            "efficiency_solved_per_affected": "Cas résolus / locations affectées (%)",
            "decision_score": "Score interne de décision",
        }
    )
    st.dataframe(scorecard, use_container_width=True, hide_index=True)

    c1, c2 = st.columns([1.15, 1])
    with c1:
        fig = go.Figure()
        for scope, label in [("all", "Tout le parc"), ("connect", "Connect uniquement")]:
            sub = threshold_df[threshold_df["scope"] == scope]
            fig.add_trace(
                go.Scatter(
                    x=sub["affected_share_of_all_rentals"] * 100,
                    y=sub["solved_share_of_all_problematic_cases"] * 100,
                    mode="lines+markers",
                    name=label,
                    text=sub["threshold_min"].astype(str) + " min",
                    hovertemplate="Seuil %{text}<br>Locations affectées : %{x:.1f}%<br>Cas résolus : %{y:.1f}%<extra></extra>",
                )
            )
        fig.add_hline(y=80, line_dash="dot")
        fig.update_layout(
            title="Protection opérationnelle vs impact global",
            xaxis_title="Part des locations affectées (%)",
            yaxis_title="Part des cas problématiques résolus (%)",
            height=450,
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        delta_solved = rec["solved_problematic_cases"] - fallback["solved_problematic_cases"]
        delta_affected = rec["affected_rentals"] - fallback["affected_rentals"]
        st.markdown(
            f"""
            <div class="soft-card">
                <h4 style="margin-top:0;">Lecture de la recommandation</h4>
                <p><b>Pourquoi ne pas s’arrêter à Connect uniquement ?</b></p>
                <p>
                    L’option prudente protège moins le fonctionnement global.
                    Passer de <b>Connect uniquement</b> à <b>tout le parc</b> à 120 minutes permet de résoudre <b>{delta_solved}</b> cas problématiques supplémentaires
                    pour <b>{delta_affected}</b> locations affectées supplémentaires.
                </p>
                <p class="small-note">Le score interne sert uniquement à ordonner les scénarios entre eux.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div class="soft-card">
                <h4 style="margin-top:0;">Point de décision</h4>
                <p>120 minutes constitue ici le premier seuil réellement efficace. En dessous, trop d’incidents restent non résolus. Au-dessus, les gains deviennent plus marginaux alors que l’impact commercial continue d’augmenter.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

elif section == "Simulateur":
    st.subheader("Simulateur de scénarios")
    left, right = st.columns([0.95, 1.35])
    with left:
        scope = st.selectbox("Périmètre", ["all", "connect", "mobile"], index=0)
        threshold = st.slider("Seuil (minutes)", min_value=0, max_value=1440, value=120, step=30)
        row = threshold_df.query("scope == @scope and threshold_min == @threshold").iloc[0]
        st.metric("Locations affectées", int(row["affected_rentals"]))
        st.metric("Part des locations affectées", f"{row['affected_share_of_all_rentals']*100:.1f}%")
        st.metric("Cas problématiques résolus", int(row["solved_problematic_cases"]))
        st.metric("Part des cas résolus", f"{row['solved_share_of_all_problematic_cases']*100:.1f}%")
        stance = "protection forte" if row["solved_share_of_all_problematic_cases"] >= 0.8 else "protection partielle"
        st.info(f"Lecture du scénario : {stance}.")
    with right:
        fig = px.line(
            threshold_df[threshold_df["scope"].isin(["all", "connect", "mobile"])],
            x="threshold_min",
            y="solved_share_of_all_problematic_cases",
            color="scope",
            markers=True,
            title="Part des cas problématiques résolus selon le seuil",
            labels={"threshold_min": "Seuil (minutes)", "solved_share_of_all_problematic_cases": "Part résolue", "scope": "Périmètre"},
        )
        fig.update_layout(yaxis_tickformat=".0%")
        st.plotly_chart(fig, use_container_width=True)

        fig2 = px.line(
            threshold_df[threshold_df["scope"].isin(["all", "connect", "mobile"])],
            x="threshold_min",
            y="affected_share_of_all_rentals",
            color="scope",
            markers=True,
            title="Impact global selon le seuil",
            labels={"threshold_min": "Seuil (minutes)", "affected_share_of_all_rentals": "Part affectée", "scope": "Périmètre"},
        )
        fig2.update_layout(yaxis_tickformat=".0%")
        st.plotly_chart(fig2, use_container_width=True)

elif section == "Analyse du risque":
    st.subheader("Analyse du risque")
    ended = delay_df[(delay_df["state"] == "ended") & delay_df["delay_at_checkout_in_minutes"].notna()].copy()
    low = ended["delay_at_checkout_in_minutes"].quantile(0.01)
    high = ended["delay_at_checkout_in_minutes"].quantile(0.99)
    ended["delay_winsorized"] = ended["delay_at_checkout_in_minutes"].clip(lower=low, upper=high)

    c1, c2 = st.columns(2)
    with c1:
        fig_hist = px.histogram(
            ended,
            x="delay_winsorized",
            color="checkin_type",
            nbins=60,
            opacity=0.7,
            barmode="overlay",
            title="Distribution des retards de restitution (winsorisée)",
            labels={"delay_winsorized": "Retard de restitution (minutes)"},
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    with c2:
        behavior_df = pd.DataFrame(summary["checkout_behavior_by_checkin_type"]).T.reset_index().rename(columns={"index": "checkin_type"})
        for col in ["late_gt_0_share", "late_gt_15_share", "late_gt_60_share"]:
            behavior_df[col] = behavior_df[col] * 100
        fig_bar = px.bar(
            behavior_df.melt(id_vars=["checkin_type"], value_vars=["late_gt_0_share", "late_gt_15_share", "late_gt_60_share"]),
            x="checkin_type",
            y="value",
            color="variable",
            barmode="group",
            title="Intensité des retours tardifs par type de check-in",
            labels={"value": "Part (%)", "variable": "Indicateur", "checkin_type": "Type de check-in"},
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown(
        f"""
        <div class="soft-card">
            <h4 style="margin-top:0;">Lecture opérationnelle</h4>
            <p>
                Les locations Connect sont globalement moins exposées que les locations mobile.
                Le retard médian est de <b>{summary['checkout_behavior_by_checkin_type']['connect']['median_delay_min']:.0f} min</b> pour Connect contre
                <b>{summary['checkout_behavior_by_checkin_type']['mobile']['median_delay_min']:.0f} min</b> pour mobile.
            </p>
            <p>
                Les retours tardifs de plus de 60 minutes concernent <b>{summary['checkout_behavior_by_checkin_type']['connect']['late_gt_60_share']*100:.1f} %</b> des locations Connect,
                contre <b>{summary['checkout_behavior_by_checkin_type']['mobile']['late_gt_60_share']*100:.1f} %</b> des locations mobile.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

elif section == "API de prix":
    st.subheader("API de prix et synthèse du modèle")
    chosen = pricing_metrics["chosen_model_metrics"]
    p1, p2, p3, p4 = st.columns(4)
    p1.metric("Modèle retenu", pricing_metrics["best_model"])
    p2.metric("MAE", f"{chosen['MAE']:.2f} €/jour")
    p3.metric("RMSE", f"{chosen['RMSE']:.2f}")
    p4.metric("R²", f"{chosen['R2']:.3f}")

    left, right = st.columns([1.05, 1.15])
    with left:
        metrics_df = pd.DataFrame(pricing_metrics["holdout_metrics"]).sort_values(["RMSE", "MAE"])
        st.dataframe(metrics_df, use_container_width=True, hide_index=True)
    with right:
        fi = pd.DataFrame(pricing_metrics["top_features"]).sort_values("importance", ascending=True)
        fig = px.bar(
            fi,
            x="importance",
            y="feature",
            orientation="h",
            title="Variables les plus influentes pour le prix",
            labels={"importance": "Importance agrégée", "feature": "Variable"},
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        """
        <div class="soft-card">
            <h4 style="margin-top:0;">Contenu du volet API</h4>
            <p>Le dépôt contient une application FastAPI séparée avec :</p>
            <ul>
                <li><code>POST /predict</code> pour l’inférence</li>
                <li><code>/docs</code> pour la documentation interactive</li>
                <li><code>/metadata</code> et <code>/health</code> pour l’exploitation</li>
                <li>Dockerfiles cohérents avec le cours de déploiement</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

elif section == "Déploiement":
    st.subheader("Déploiement")
    d1, d2 = st.columns(2)
    with d1:
        st.markdown(
            """
            <div class="soft-card">
                <h4 style="margin-top:0;">Répartition conseillée du déploiement</h4>
                <ol>
                    <li>Déployer le tableau de bord Streamlit comme une application</li>
                    <li>Déployer FastAPI comme un service API séparé</li>
                    <li>Conserver les deux services dans le même dépôt GitHub</li>
                    <li>Utiliser la page <code>/docs</code> pour la démonstration</li>
                </ol>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with d2:
        st.markdown(
            """
            <div class="soft-card">
                <h4 style="margin-top:0;">Intérêt de cette structure</h4>
                <ul>
                    <li>Elle répond à la fois à la question produit et à la question machine learning</li>
                    <li>Elle est déjà organisée pour GitHub et le déploiement</li>
                    <li>Elle inclut une API documentée, des tests et des commandes d’exécution</li>
                    <li>Elle ressemble à un projet finalisé et non à un simple brouillon de travail</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.code("make dashboard\nmake api\nmake test\nmake train\nmake analyze", language="bash")
