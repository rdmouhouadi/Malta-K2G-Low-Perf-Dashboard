import streamlit as st
import pandas as pd
import math
import altair as alt
import plotly.graph_objects as go
from pathlib import Path

# Set title and favicon
st.set_page_config(
    page_title='Daily Frames Dashboard - MALTA K2G',
    page_icon = None,
    layout = 'wide',
)

alt.themes.enable("dark") ##new

# -----------------------------------------------------------------------------
# Load the Excel data (with caching)

@st.cache_data
def load_equipment_data():
    """Load daily frames data from an Excel file."""
    DATA_FILENAME = 'data/daily_frames.xlsx'
    df = pd.read_excel(DATA_FILENAME, index_col=0, parse_dates=True)
    return df

final_df = load_equipment_data()

# -----------------------------------------------------------------------------
# Build the Streamlit page

'''
# :bar_chart: Low Performance MALTA K2G Dashboard


'''

''
equipments = final_df.columns.tolist()

if not equipments:
    st.warning("No equipment data found.")
else:
    with st.sidebar:

        selected_equipments = st.multiselect(
            "Equipment Serial NB",
            options=equipments,
            default=[equipments[0]]
            )
        
        date_range = st.slider(
            "Select the date range:",
            min_value=final_df.index.min().to_pydatetime(),
            max_value=final_df.index.max().to_pydatetime(),
            value=(final_df.index.min().to_pydatetime(), final_df.index.max().to_pydatetime())
            )

        filtered_df = final_df.loc[date_range[0]:date_range[1], selected_equipments]

    # Tabs for separating visualizations
    tab1, tab2 = st.tabs(["Per Equipment", "Overall Aggregation"])


    with tab1:
        # Plotly chart
        st.title("📈 Daily Frames Over Time")

        fig = go.Figure()

        for equip in selected_equipments:
            fig.add_trace(go.Scatter(
                x=filtered_df.index,
                y=filtered_df[equip],
                mode='lines+markers',
                name=equip
            ))

        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Daily Frames",
            template="plotly_white",
            legend_title="Equipment"
        )

        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.title("📊 Aggregate Frames ")

        # Initialize session state for granularity if not set
        if 'granularity' not in st.session_state:
            st.session_state.granularity = 'Daily'

        # Resample data
        daily_total = filtered_df.sum(axis=1)
        weekly_total = daily_total.resample('W').sum()
        monthly_total = daily_total.resample('ME').sum()

        # Map granularity to visibility array
        visibility_map = {
            'Daily': [True, False, False],
            'Weekly': [False, True, False],
            'Monthly': [False, False, True]
        }

        # Plotly figure
        fig = go.Figure()

        # Add traces
        fig.add_trace(go.Scatter(x=daily_total.index, y=daily_total.values, mode='lines+markers', name='Daily'))
        fig.add_trace(go.Scatter(x=weekly_total.index, y=weekly_total.values, mode='lines+markers', name='Weekly'))
        fig.add_trace(go.Scatter(x=monthly_total.index, y=monthly_total.values, mode='lines+markers', name='Monthly'))

        # Update visibility based on session state
        fig.update_traces(visible=False)
        for i, visible in enumerate(visibility_map[st.session_state.granularity]):
            fig.data[i].visible = visible

        # Add dropdown that updates session state using a callback
        def set_granularity(gran):
            st.session_state.granularity = gran

        fig.update_layout(
            updatemenus=[
                dict(
                    buttons=[
                        dict(label="Daily", method="update", args=[{"visible": visibility_map["Daily"]}], args2=None),
                        dict(label="Weekly", method="update", args=[{"visible": visibility_map["Weekly"]}], args2=None),
                        dict(label="Monthly", method="update", args=[{"visible": visibility_map["Monthly"]}], args2=None),
                    ],
                    direction="down",
                    showactive=True,
                    x=0.0,
                    xanchor="left",
                    y=1.15,
                    yanchor="top"
                ),
            ],
            xaxis_title="Date",
            yaxis_title="Total Frames",
            title=f"{st.session_state.granularity} Total Frames",
            template="plotly_white",
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True)
