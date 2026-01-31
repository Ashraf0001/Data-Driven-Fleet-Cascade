"""
Fleet Decision Platform - Streamlit Dashboard

A beautiful interactive dashboard for testing the Fleet Decision Platform.
"""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st


# ==============================================================================
# Configuration
# ==============================================================================

st.set_page_config(
    page_title="Fleet Decision Platform",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for styling
st.markdown(
    """
<style>
    /* Main container styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Card styling */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }

    .metric-card h3 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }

    .metric-card p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
        font-size: 0.9rem;
    }

    /* Status badges */
    .status-optimal {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
    }

    .status-infeasible {
        background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
    }

    /* Risk badges */
    .risk-high { background: #ff4757; color: white; }
    .risk-medium { background: #ffa502; color: white; }
    .risk-low { background: #2ed573; color: white; }

    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }

    /* Headers */
    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }

    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e8eb 100%);
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        font-weight: 600;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
</style>
""",
    unsafe_allow_html=True,
)

API_BASE_URL = "http://127.0.0.1:8000"


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
    np.random.seed(42)
    statuses = ["operational"] * 8 + ["maintenance"] * 2
    return [
        {
            "vehicle_id": f"V{i:03d}",
            "current_zone": int(np.random.randint(0, n_zones)),
            "capacity": 1,
            "status": np.random.choice(statuses),
            "mileage_km": int(np.random.randint(10000, 100000)),
            "age_months": int(np.random.randint(6, 60)),
        }
        for i in range(1, n_vehicles + 1)
    ]


def create_zone_heatmap(demand: np.ndarray, n_zones: int):
    """Create a heatmap of demand per zone."""
    grid_size = int(np.sqrt(n_zones))
    demand_grid = demand.reshape(grid_size, grid_size)

    fig = go.Figure(
        data=go.Heatmap(
            z=demand_grid,
            colorscale="Viridis",
            showscale=True,
            colorbar=dict(title="Demand"),
        )
    )

    fig.update_layout(
        title="Demand by Zone",
        xaxis_title="Zone X",
        yaxis_title="Zone Y",
        height=400,
    )

    return fig


def create_allocation_sankey(allocations: list, n_zones: int):
    """Create a Sankey diagram of allocations."""
    if not allocations:
        return None

    # Count flows
    flows = {}
    for alloc in allocations:
        key = (alloc["from_zone"], alloc["to_zone"])
        flows[key] = flows.get(key, 0) + 1

    if not flows:
        return None

    source = []
    target = []
    value = []
    labels = [f"Zone {i}" for i in range(n_zones)] + [f"Zone {i} (dest)" for i in range(n_zones)]

    for (src, tgt), count in flows.items():
        source.append(src)
        target.append(tgt + n_zones)
        value.append(count)

    fig = go.Figure(
        data=[
            go.Sankey(
                node=dict(pad=15, thickness=20, line=dict(color="black", width=0.5), label=labels),
                link=dict(source=source, target=target, value=value),
            )
        ]
    )

    fig.update_layout(title="Vehicle Allocation Flow", height=500)
    return fig


# ==============================================================================
# Sidebar
# ==============================================================================

with st.sidebar:
    st.image(
        "https://img.icons8.com/fluency/96/delivery.png",
        width=80,
    )
    st.title("Fleet Decision Platform")
    st.markdown("---")

    # API Status
    api_status = check_api_health()
    if api_status:
        st.success("✅ API Connected")
    else:
        st.error("❌ API Offline")
        st.info("Start the API with:\n`uv run uvicorn src.api.main:app --reload`")

    st.markdown("---")

    # Navigation
    page = st.radio(
        "Navigation",
        ["🏠 Dashboard", "🚗 Fleet Optimization", "📊 Demand Forecast", "⚠️ Risk Analysis"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown(
        """
    ### Quick Links
    - [API Docs](/docs)
    - [GitHub](https://github.com/Ashraf0001/Data-Driven-Fleet-Cascade)
    """
    )

# ==============================================================================
# Main Content
# ==============================================================================

if page == "🏠 Dashboard":
    st.title("🚗 Fleet Decision Platform")
    st.markdown("### Enterprise-grade Decision Intelligence for Fleet Operations")

    # Hero metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            """
        <div class="metric-card">
            <h3>50</h3>
            <p>Vehicles</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
        <div class="metric-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
            <h3>25</h3>
            <p>Service Zones</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            """
        <div class="metric-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
            <h3>98%</h3>
            <p>Coverage</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            """
        <div class="metric-card" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
            <h3>$1.2K</h3>
            <p>Daily Cost</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # Features
    st.subheader("✨ Platform Capabilities")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
        #### 📈 Demand Forecasting
        - XGBoost-based predictions
        - Multi-zone forecasting
        - Time-series features
        - Historical pattern learning

        #### 🚚 Fleet Optimization
        - Min-cost flow allocation
        - OR-Tools solver
        - Real-time rebalancing
        - Constraint-aware planning
        """
        )

    with col2:
        st.markdown(
            """
        #### ⚠️ Risk Prediction
        - Remaining Useful Life (RUL)
        - Heuristic risk scoring
        - Maintenance scheduling
        - Asset health monitoring

        #### 🔍 Explainability
        - Feature importance
        - Allocation reasoning
        - KPI dashboards
        - Cost breakdown
        """
        )

    st.markdown("---")

    # Quick Test
    st.subheader("🚀 Quick Test")

    if st.button("Run Simulation", type="primary", use_container_width=True):
        if api_status:
            with st.spinner("Running optimization..."):
                result = call_api("/api/v1/optimize/simulate", method="POST")

                if result:
                    st.success(f"✅ Optimization {result['status'].upper()}")

                    col1, col2, col3 = st.columns(3)
                    col1.metric("Total Cost", f"${result['total_cost']:.2f}")
                    col2.metric("Vehicles Allocated", result["num_allocations"])
                    col3.metric("Coverage", f"{result['coverage'] * 100:.0f}%")
        else:
            st.warning("Please start the API server first!")


elif page == "🚗 Fleet Optimization":
    st.title("🚗 Fleet Optimization")
    st.markdown("Allocate vehicles to zones using min-cost flow optimization")

    # Configuration
    st.subheader("⚙️ Configuration")

    col1, col2, col3 = st.columns(3)

    with col1:
        n_vehicles = st.slider("Number of Vehicles", 10, 100, 50, step=10)
    with col2:
        n_zones = st.selectbox("Number of Zones", [9, 16, 25, 36, 49], index=2)
    with col3:
        max_cost = st.slider("Max Cost per Vehicle ($)", 10, 100, 50, step=5)

    col1, col2 = st.columns(2)
    with col1:
        hour = st.slider("Hour of Day", 0, 23, 18)
    with col2:
        day = st.selectbox(
            "Day of Week",
            ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            index=4,
        )
        day_of_week = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ].index(day)

    st.markdown("---")

    # Run Optimization
    if st.button("🚀 Run Optimization", type="primary", use_container_width=True):
        if not api_status:
            st.error("API is not available. Please start the server.")
        else:
            # Generate fleet
            fleet_data = generate_fleet_data(n_vehicles, n_zones)

            # Generate demand
            np.random.seed(hour + day_of_week)
            grid_size = int(np.sqrt(n_zones))
            demand = []
            for z in range(n_zones):
                row, col = z // grid_size, z % grid_size
                center_dist = np.sqrt((row - grid_size / 2) ** 2 + (col - grid_size / 2) ** 2)
                base = max(5, 15 - center_dist * 2) + np.random.randint(0, 5)
                if 17 <= hour <= 19:
                    base *= 1.5
                demand.append(int(base))

            # Prepare request
            request_data = {
                "demand_forecast": {str(i): [d] for i, d in enumerate(demand)},
                "fleet_state": {"vehicles": fleet_data},
                "constraints": {"max_cost_per_vehicle": max_cost},
            }

            with st.spinner("Running optimization..."):
                result = call_api("/api/v1/optimize", method="POST", data=request_data)

            if result:
                # Status
                status_class = (
                    "status-optimal" if result["status"] == "optimal" else "status-infeasible"
                )
                st.markdown(
                    f'<span class="{status_class}">{result["status"].upper()}</span>',
                    unsafe_allow_html=True,
                )

                # KPIs
                st.subheader("📊 Key Performance Indicators")

                kpis = result["kpis"]
                col1, col2, col3, col4 = st.columns(4)

                col1.metric("Total Cost", f"${result['total_cost']:.2f}")
                col2.metric("Vehicles Allocated", kpis["vehicles_allocated"])
                col3.metric("Zones Served", f"{kpis['zones_served']}/{kpis['total_zones']}")
                col4.metric("Utilization", f"{kpis['utilization'] * 100:.0f}%")

                # Visualizations
                st.subheader("📈 Visualizations")

                col1, col2 = st.columns(2)

                with col1:
                    # Demand heatmap
                    fig = create_zone_heatmap(np.array(demand), n_zones)
                    st.plotly_chart(fig, use_container_width=True)

                with col2:
                    # Allocation pie chart
                    allocs = result["allocations"]
                    rebalanced = sum(1 for a in allocs if a["rebalanced"])
                    stayed = len(allocs) - rebalanced

                    fig = px.pie(
                        values=[stayed, rebalanced],
                        names=["Stayed in Zone", "Rebalanced"],
                        title="Vehicle Movement",
                        color_discrete_sequence=["#2ed573", "#ffa502"],
                    )
                    st.plotly_chart(fig, use_container_width=True)

                # Allocation table
                st.subheader("📋 Allocation Details")
                if allocs:
                    df = pd.DataFrame(allocs)
                    df["cost"] = df["cost"].round(2)
                    st.dataframe(df, use_container_width=True, hide_index=True)


elif page == "📊 Demand Forecast":
    st.title("📊 Demand Forecasting")
    st.markdown("Predict ride demand per zone using ML models")

    # Configuration
    st.subheader("⚙️ Forecast Parameters")

    col1, col2, col3 = st.columns(3)

    with col1:
        hour = st.slider("Hour", 0, 23, 18)
    with col2:
        day = st.selectbox(
            "Day",
            ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            index=4,
        )
        day_of_week = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ].index(day)
    with col3:
        month = st.selectbox("Month", list(range(1, 13)), index=5)

    n_zones = st.selectbox("Number of Zones", [9, 16, 25], index=2)
    horizon = st.slider("Forecast Horizon (hours)", 1, 24, 6)

    st.markdown("---")

    if st.button("📈 Generate Forecast", type="primary", use_container_width=True):
        if not api_status:
            st.error("API is not available. Please start the server.")
        else:
            request_data = {
                "zone_ids": list(range(n_zones)),
                "hour": hour,
                "day_of_week": day_of_week,
                "month": month,
                "horizon_hours": horizon,
            }

            with st.spinner("Generating forecast..."):
                result = call_api("/api/v1/forecast", method="POST", data=request_data)

            if result:
                st.success(
                    f"✅ Forecast generated using **{result['metadata'].get('model', 'heuristic')}** model"
                )

                forecasts = result["forecasts"]

                # Aggregate demand
                total_demand = sum(v[0] for v in forecasts.values())
                avg_demand = total_demand / len(forecasts) if forecasts else 0

                col1, col2, col3 = st.columns(3)
                col1.metric("Total Demand", int(total_demand))
                col2.metric("Avg per Zone", f"{avg_demand:.1f}")
                col3.metric("Peak Zone", max(forecasts.keys(), key=lambda k: forecasts[k][0]))

                # Visualizations
                col1, col2 = st.columns(2)

                with col1:
                    # Bar chart
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
                        color_continuous_scale="Viridis",
                    )
                    st.plotly_chart(fig, use_container_width=True)

                with col2:
                    # Heatmap
                    demand_arr = np.array([v[0] for v in forecasts.values()])
                    fig = create_zone_heatmap(demand_arr, n_zones)
                    st.plotly_chart(fig, use_container_width=True)


elif page == "⚠️ Risk Analysis":
    st.title("⚠️ Risk Analysis")
    st.markdown("Assess vehicle health and predict maintenance needs")

    # Configuration
    st.subheader("🚗 Fleet Configuration")

    n_vehicles = st.slider("Number of Vehicles to Analyze", 5, 50, 20)

    st.markdown("---")

    if st.button("🔍 Analyze Risk", type="primary", use_container_width=True):
        if not api_status:
            st.error("API is not available. Please start the server.")
        else:
            # Generate fleet with varied risk profiles
            np.random.seed(42)
            vehicles = []
            for i in range(1, n_vehicles + 1):
                vehicles.append(
                    {
                        "vehicle_id": f"V{i:03d}",
                        "current_zone": int(np.random.randint(0, 25)),
                        "status": np.random.choice(
                            ["operational", "operational", "operational", "maintenance"]
                        ),
                        "mileage_km": int(np.random.randint(10000, 150000)),
                        "age_months": int(np.random.randint(3, 72)),
                    }
                )

            request_data = {"vehicles": vehicles}

            with st.spinner("Analyzing risk..."):
                result = call_api("/api/v1/risk/score", method="POST", data=request_data)

            if result:
                st.success("✅ Risk analysis complete")

                # Summary
                summary = result["summary"]
                col1, col2, col3 = st.columns(3)

                col1.metric("🔴 High Risk", summary.get("high", 0))
                col2.metric("🟡 Medium Risk", summary.get("medium", 0))
                col3.metric("🟢 Low Risk", summary.get("low", 0))

                # Visualizations
                col1, col2 = st.columns(2)

                with col1:
                    # Pie chart
                    fig = px.pie(
                        values=list(summary.values()),
                        names=list(summary.keys()),
                        title="Risk Distribution",
                        color=list(summary.keys()),
                        color_discrete_map={
                            "high": "#ff4757",
                            "medium": "#ffa502",
                            "low": "#2ed573",
                        },
                    )
                    st.plotly_chart(fig, use_container_width=True)

                with col2:
                    # Risk scores bar
                    scores = result["risk_scores"]
                    df = pd.DataFrame(scores)

                    fig = px.bar(
                        df,
                        x="vehicle_id",
                        y="risk_score",
                        color="risk_category",
                        title="Risk Score by Vehicle",
                        color_discrete_map={
                            "high": "#ff4757",
                            "medium": "#ffa502",
                            "low": "#2ed573",
                        },
                    )
                    fig.update_layout(xaxis_tickangle=-45)
                    st.plotly_chart(fig, use_container_width=True)

                # Detailed table
                st.subheader("📋 Detailed Risk Scores")

                df = pd.DataFrame(scores)
                df["risk_score"] = df["risk_score"].round(3)

                # Style the dataframe
                def color_risk(val):
                    if val == "high":
                        return "background-color: #ff4757; color: white"
                    if val == "medium":
                        return "background-color: #ffa502; color: white"
                    return "background-color: #2ed573; color: white"

                styled_df = df.style.map(color_risk, subset=["risk_category"])
                st.dataframe(styled_df, use_container_width=True, hide_index=True)

                # High risk vehicles
                high_risk = [s for s in scores if s["risk_category"] == "high"]
                if high_risk:
                    st.warning(f"⚠️ {len(high_risk)} vehicles require immediate attention!")
                    for v in high_risk:
                        st.markdown(f"- **{v['vehicle_id']}**: Risk Score {v['risk_score']:.2f}")

# ==============================================================================
# Footer
# ==============================================================================

st.markdown("---")
st.markdown(
    """
<div style="text-align: center; color: #888; padding: 1rem;">
    <p>Fleet Decision Platform v0.1.0 | Built with ❤️ using Streamlit & FastAPI</p>
</div>
""",
    unsafe_allow_html=True,
)
