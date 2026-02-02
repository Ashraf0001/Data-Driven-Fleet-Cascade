"""
Fleet Decision Platform - Streamlit Dashboard
"""

import os

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st

from src.data.loader import generate_demand_forecast, generate_fleet_state


# ==============================================================================
# Configuration
# ==============================================================================

st.set_page_config(
    page_title="Fleet Decision Platform",
    page_icon="F",
    layout="wide",
)

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")


# ==============================================================================
# Helper Functions
# ==============================================================================


def check_api_health():
    """Check if the API is running."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=2)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


def call_api(endpoint: str, method: str = "GET", data: dict = None, params: dict = None):
    """Make API call and return response."""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        if method == "GET":
            response = requests.get(url, params=params, timeout=10)
        else:
            response = requests.post(url, json=data, params=params, timeout=30)
        return response.json() if response.status_code == 200 else None
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {e}")
        return None


def generate_fleet_data(n_vehicles: int, n_zones: int) -> list:
    """Generate sample fleet data."""
    fleet_df = generate_fleet_state(n_vehicles=n_vehicles, n_zones=n_zones, seed=42)
    return fleet_df[
        ["vehicle_id", "current_zone", "capacity", "status", "mileage_km", "age_months"]
    ].to_dict("records")


def create_zone_heatmap(demand: np.ndarray, n_zones: int):
    """Create a heatmap of demand per zone."""
    grid_size = int(np.sqrt(n_zones))
    demand_grid = demand.reshape(grid_size, grid_size)

    fig = go.Figure(
        data=go.Heatmap(
            z=demand_grid,
            colorscale="Blues",
            showscale=True,
        )
    )

    fig.update_layout(
        title="Demand by Zone",
        xaxis_title="X",
        yaxis_title="Y",
        height=350,
        margin=dict(l=40, r=40, t=40, b=40),
    )

    return fig


# ==============================================================================
# Sidebar
# ==============================================================================

with st.sidebar:
    st.title("Fleet Platform")
    st.caption("Decision Intelligence for Fleet Operations")
    st.caption(f"API Base: {API_BASE_URL}")

    st.divider()

    # API Status
    if check_api_health():
        st.success("API Connected")
    else:
        st.error("API Offline")
        st.caption("Run: `make run`")

    st.divider()

    page = st.radio(
        "Navigate",
        ["Overview", "Optimization", "Forecasting", "Risk"],
    )

# ==============================================================================
# Pages
# ==============================================================================

if page == "Overview":
    st.title("Fleet Decision Platform")
    st.caption("Enterprise-grade decision intelligence for fleet operations")

    st.divider()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Vehicles", "50")
    col2.metric("Zones", "25")
    col3.metric("Coverage", "98%")
    col4.metric("Daily Cost", "$1.2K")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Capabilities")
        st.markdown("""
        - **Demand Forecasting** - XGBoost predictions by zone
        - **Fleet Optimization** - Min-cost flow allocation
        - **Risk Prediction** - RUL and health scoring
        - **Explainability** - Feature importance & KPIs
        """)

    with col2:
        st.subheader("Quick Test")
        if st.button("Run Simulation", use_container_width=True):
            if check_api_health():
                with st.spinner("Running..."):
                    result = call_api("/api/v1/optimize/simulate", method="POST")
                if result:
                    st.success(f"Status: {result['status']}")
                    st.metric("Total Cost", f"${result['total_cost']:.2f}")
                    st.metric("Allocations", result["num_allocations"])
            else:
                st.warning("Start the API server first")


elif page == "Optimization":
    st.title("Fleet Optimization")
    st.caption("Allocate vehicles to zones using min-cost flow")

    st.divider()

    # Config
    col1, col2, col3 = st.columns(3)
    with col1:
        n_vehicles = st.slider("Vehicles", 10, 100, 50, step=10)
    with col2:
        n_zones = st.selectbox("Zones", [9, 16, 25, 36], index=2)
    with col3:
        max_cost = st.slider("Max Cost ($)", 10, 100, 50, step=5)

    col1, col2 = st.columns(2)
    with col1:
        hour = st.slider("Hour", 0, 23, 18)
    with col2:
        day_of_week = st.selectbox(
            "Day",
            options=range(7),
            format_func=lambda x: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][x],
            index=4,
        )

    st.divider()

    if st.button("Run Optimization", type="primary", use_container_width=True):
        if not check_api_health():
            st.error("API not available")
        else:
            # Generate data
            fleet_data = generate_fleet_data(n_vehicles, n_zones)

            demand = generate_demand_forecast(
                n_zones=n_zones, hour=hour, day_of_week=day_of_week, seed=hour + day_of_week
            )

            request_data = {
                "demand_forecast": {str(i): [int(d)] for i, d in enumerate(demand)},
                "fleet_state": {"vehicles": fleet_data},
                "constraints": {"max_cost_per_vehicle": max_cost},
            }

            with st.spinner("Optimizing..."):
                result = call_api("/api/v1/optimize", method="POST", data=request_data)

            if result:
                # Status
                if result["status"] == "optimal":
                    st.success(f"Status: {result['status'].upper()}")
                else:
                    st.error(f"Status: {result['status'].upper()}")

                # KPIs
                kpis = result["kpis"]
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Cost", f"${result['total_cost']:.2f}")
                col2.metric("Allocated", kpis["vehicles_allocated"])
                col3.metric("Zones", f"{kpis['zones_served']}/{kpis['total_zones']}")
                col4.metric("Utilization", f"{kpis['utilization'] * 100:.0f}%")

                st.divider()

                # Charts
                col1, col2 = st.columns(2)

                with col1:
                    fig = create_zone_heatmap(np.array(demand), n_zones)
                    st.plotly_chart(fig, use_container_width=True)

                with col2:
                    allocs = result["allocations"]
                    rebalanced = sum(1 for a in allocs if a["rebalanced"])
                    stayed = len(allocs) - rebalanced

                    fig = px.pie(
                        values=[stayed, rebalanced],
                        names=["Stayed", "Rebalanced"],
                        title="Vehicle Movement",
                        color_discrete_sequence=["#4A90A4", "#E8927C"],
                    )
                    fig.update_layout(height=350, margin=dict(l=40, r=40, t=40, b=40))
                    st.plotly_chart(fig, use_container_width=True)

                # Table
                st.subheader("Allocations")
                if allocs:
                    df = pd.DataFrame(allocs)
                    df["cost"] = df["cost"].round(2)
                    st.dataframe(df, use_container_width=True, hide_index=True)


elif page == "Forecasting":
    st.title("Demand Forecasting")
    st.caption("Predict ride demand by zone")

    st.divider()

    col1, col2, col3 = st.columns(3)
    with col1:
        hour = st.slider("Hour", 0, 23, 18)
    with col2:
        day_of_week = st.selectbox(
            "Day",
            options=range(7),
            format_func=lambda x: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][x],
            index=4,
        )
    with col3:
        month = st.selectbox("Month", list(range(1, 13)), index=5)

    n_zones = st.selectbox("Zones", [9, 16, 25], index=2)

    st.divider()

    if st.button("Generate Forecast", type="primary", use_container_width=True):
        if not check_api_health():
            st.error("API not available")
        else:
            request_data = {
                "zone_ids": list(range(n_zones)),
                "hour": hour,
                "day_of_week": day_of_week,
                "month": month,
                "horizon_hours": 1,
            }

            with st.spinner("Forecasting..."):
                result = call_api("/api/v1/forecast", method="POST", data=request_data)

            if result:
                model = result["metadata"].get("model", "heuristic")
                st.success(f"Model: {model}")

                forecasts = result["forecasts"]
                total = sum(v[0] for v in forecasts.values())
                avg = total / len(forecasts) if forecasts else 0

                col1, col2, col3 = st.columns(3)
                col1.metric("Total Demand", int(total))
                col2.metric("Avg per Zone", f"{avg:.1f}")
                col3.metric("Peak Zone", max(forecasts.keys(), key=lambda k: forecasts[k][0]))

                st.divider()

                col1, col2 = st.columns(2)

                with col1:
                    df = pd.DataFrame(
                        {
                            "Zone": list(forecasts.keys()),
                            "Demand": [v[0] for v in forecasts.values()],
                        }
                    )
                    fig = px.bar(
                        df,
                        x="Zone",
                        y="Demand",
                        title="Demand by Zone",
                        color="Demand",
                        color_continuous_scale="Blues",
                    )
                    fig.update_layout(height=350, margin=dict(l=40, r=40, t=40, b=40))
                    st.plotly_chart(fig, use_container_width=True)

                with col2:
                    demand_arr = np.array([v[0] for v in forecasts.values()])
                    fig = create_zone_heatmap(demand_arr, n_zones)
                    st.plotly_chart(fig, use_container_width=True)


elif page == "Risk":
    st.title("Risk Analysis")
    st.caption("Vehicle health and maintenance prediction")

    st.divider()

    n_vehicles = st.slider("Vehicles to Analyze", 5, 50, 20)

    st.divider()

    if st.button("Analyze Risk", type="primary", use_container_width=True):
        if not check_api_health():
            st.error("API not available")
        else:
            np.random.seed(42)
            vehicles = [
                {
                    "vehicle_id": f"V{i:03d}",
                    "current_zone": int(np.random.randint(0, 25)),
                    "status": np.random.choice(
                        ["operational", "operational", "operational", "maintenance"]
                    ),
                    "mileage_km": int(np.random.randint(10000, 150000)),
                    "age_months": int(np.random.randint(3, 72)),
                }
                for i in range(1, n_vehicles + 1)
            ]

            with st.spinner("Analyzing..."):
                result = call_api("/api/v1/risk/score", method="POST", data={"vehicles": vehicles})

            if result:
                st.success("Analysis complete")

                summary = result["summary"]
                col1, col2, col3 = st.columns(3)
                col1.metric("High Risk", summary.get("high", 0))
                col2.metric("Medium Risk", summary.get("medium", 0))
                col3.metric("Low Risk", summary.get("low", 0))

                st.divider()

                col1, col2 = st.columns(2)

                with col1:
                    fig = px.pie(
                        values=list(summary.values()),
                        names=list(summary.keys()),
                        title="Risk Distribution",
                        color=list(summary.keys()),
                        color_discrete_map={
                            "high": "#D64045",
                            "medium": "#E8B44C",
                            "low": "#5B9279",
                        },
                    )
                    fig.update_layout(height=350, margin=dict(l=40, r=40, t=40, b=40))
                    st.plotly_chart(fig, use_container_width=True)

                with col2:
                    scores = result["risk_scores"]
                    df = pd.DataFrame(scores)
                    fig = px.bar(
                        df,
                        x="vehicle_id",
                        y="risk_score",
                        color="risk_category",
                        title="Risk by Vehicle",
                        color_discrete_map={
                            "high": "#D64045",
                            "medium": "#E8B44C",
                            "low": "#5B9279",
                        },
                    )
                    fig.update_layout(
                        height=350,
                        margin=dict(l=40, r=40, t=40, b=40),
                        xaxis_tickangle=-45,
                    )
                    st.plotly_chart(fig, use_container_width=True)

                # Table
                st.subheader("Details")
                df = pd.DataFrame(scores)
                df["risk_score"] = df["risk_score"].round(3)
                st.dataframe(df, use_container_width=True, hide_index=True)

                # Warnings
                high_risk = [s for s in scores if s["risk_category"] == "high"]
                if high_risk:
                    st.warning(f"{len(high_risk)} vehicles need immediate attention")

# ==============================================================================
# Footer
# ==============================================================================

st.divider()
st.caption("Fleet Decision Platform v0.1.0")
