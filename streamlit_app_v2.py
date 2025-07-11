import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# Set title and favicon
st.set_page_config(
    page_title='Daily Frames Dashboard - MALTA K2G',
    page_icon=None,
    layout='wide',
)

# Load the Excel data (with caching)
@st.cache_data
def load_equipment_data():
    """Load daily frames data from an Excel file."""
    DATA_FILENAME = 'data/daily_frames.xlsx'
    df = pd.read_excel(DATA_FILENAME, index_col=0, parse_dates=True)
    return df

@st.cache_data
def load_noise_equipment_data():
    """Load daily Noise data from an Excel file."""
    NOISE_DATA_FILENAME = 'data/daily_noise.xlsx'
    df = pd.read_excel(NOISE_DATA_FILENAME, index_col=0, parse_dates=True)
    return df

# Load the data
final_df = load_equipment_data()
noise_final_df = load_noise_equipment_data()

# --------------------------------------------------------------------------
# Build the Streamlit page
'''
# :bar_chart: Low Performance MALTA K2G Dashboard
'''
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
        filtered_noise_df = noise_final_df.loc[date_range[0]:date_range[1], selected_equipments]

    # Tabs for separating visualizations
    tab1, tab2 = st.tabs(["Per Equipment", "Overall Aggregation"])

    with tab1:
        # Title and graph for daily frames
        st.title("📈 Daily Frames Over Time")

        # --- fig_1: Pre-existing graph displaying frames for selected equipment ---
        fig_1 = go.Figure()

        for equip in selected_equipments:
            fig_1.add_trace(go.Scatter(
                x=filtered_df.index,
                y=filtered_df[equip],
                mode='lines+markers',
                name=f"Frames - {equip}",
                yaxis='y1'
            ))

        fig_1.update_layout(
            xaxis_title="Date",
            yaxis_title="Daily Frames",
            template="plotly_white",
            legend_title="Equipment"
        )

        st.plotly_chart(fig_1, use_container_width=True)

        # --- fig_2: New graph displaying frames and noise (sum of frames and avg noise) ---
        st.title("📊 Frames & Noise (Sum & Average)")

        # Create a new figure for the second graph
        fig_2 = go.Figure()

        if len(selected_equipments) == 1:
            # Case 1: Only one equipment selected - plot frames and noise for that equipment
            equip = selected_equipments[0]
            
            # Plot frames for that equipment
            fig_2.add_trace(go.Scatter(
                x=filtered_df.index,
                y=filtered_df[equip],
                mode='lines+markers',
                name=f"Frames - {equip}",
                yaxis='y1'
            ))

            # Plot noise for that equipment
            fig_2.add_trace(go.Scatter(
                x=filtered_noise_df.index,
                y=filtered_noise_df[equip],
                mode='lines+markers',
                name=f"Noise - {equip}",
                yaxis='y2'
            ))

        elif len(selected_equipments) > 1:
            # Case 2: Multiple equipment selected - plot sum of frames and avg noise

            # Sum of frames for selected equipment(s)
            frame_sum_all = filtered_df.sum(axis=1)

            # Average of noise for selected equipment(s)
            noise_avg_all = filtered_noise_df.mean(axis=1)

            # Plot the sum of frames for all selected equipment
            fig_2.add_trace(go.Scatter(
                x=filtered_df.index,
                y=frame_sum_all,
                mode='lines+markers',
                #name="Sum of Frames - All Equipments",
                name="Sum of Frames",
                yaxis='y1',
                line=dict(dash='dash')  # Dash line for aggregated data
            ))

            # Plot the average noise for all selected equipment
            fig_2.add_trace(go.Scatter(
                x=filtered_noise_df.index,
                y=noise_avg_all,
                mode='lines+markers',
                #name="Avg Noise - All Equipments",
                name="Total Avg Noise",
                yaxis='y2',
                line=dict(dash='dash')  # Dash line for aggregated data
            ))

        # Update layout with dual y-axes
        fig_2.update_layout(
            xaxis_title="Date",
            yaxis_title="Daily Frames",
            yaxis=dict(title="Daily Frames", side="left"),
            yaxis2=dict(title="Daily Noise", side="right", overlaying='y'),
            template="plotly_white",
            title="Frames & Noise (Sum & Average)"
        )

        # Display the second plot
        st.plotly_chart(fig_2, use_container_width=True)


    with tab2:
        st.title("📊 Aggregate Frames & Noise")

        # Initialize session state for granularity if not set
        if 'granularity' not in st.session_state:
            st.session_state.granularity = 'Daily'

        # Resample data for frames (daily, weekly, monthly)
        daily_total = filtered_df.sum(axis=1)
        weekly_total = daily_total.resample('W').sum()
        monthly_total = daily_total.resample('ME').sum()

        # Resample noise data (daily, weekly, monthly)
        daily_noise_avg = filtered_noise_df.mean(axis=1)
        weekly_noise_avg = daily_noise_avg.resample('W').mean()
        monthly_noise_avg = daily_noise_avg.resample('ME').mean()

        # Map granularity to visibility array for frames and noise
        visibility_map = {
            'Daily': [True, False, False, True, False, False],
            'Weekly': [False, True, False, False, True, False],
            'Monthly': [False, False, True, False, False, True]
        }

        # Plotly figure for aggregated data
        fig = go.Figure()

        # Add traces for frames aggregation
        fig.add_trace(go.Scatter(x=daily_total.index, y=daily_total.values, mode='lines+markers', name='Frames - Daily', yaxis='y1'))
        fig.add_trace(go.Scatter(x=weekly_total.index, y=weekly_total.values, mode='lines+markers', name='Frames - Weekly', yaxis='y1'))
        fig.add_trace(go.Scatter(x=monthly_total.index, y=monthly_total.values, mode='lines+markers', name='Frames - Monthly', yaxis='y1'))

        # Add traces for noise aggregation
        fig.add_trace(go.Scatter(x=daily_noise_avg.index, y=daily_noise_avg.values, mode='lines+markers', name='Noise - Daily', yaxis='y2'))
        fig.add_trace(go.Scatter(x=weekly_noise_avg.index, y=weekly_noise_avg.values, mode='lines+markers', name='Noise - Weekly', yaxis='y2'))
        fig.add_trace(go.Scatter(x=monthly_noise_avg.index, y=monthly_noise_avg.values, mode='lines+markers', name='Noise - Monthly', yaxis='y2'))

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
            yaxis=dict(title="Total Frames", side="left"),
            yaxis2=dict(title="Total Noise", side="right", overlaying='y'),
            title=f"{st.session_state.granularity} Total Frames & Noise",
            template="plotly_white",
            showlegend=True
        )

        # Display the plot
        st.plotly_chart(fig, use_container_width=True)
