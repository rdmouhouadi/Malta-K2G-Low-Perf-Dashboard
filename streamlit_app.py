import streamlit as st
import pandas as pd
import math
import plotly.graph_objects as go
from pathlib import Path

# Set the title and favicon
st.set_page_config(
    page_title='Daily Frames Dashboard - MALTA K2G',
    page_icon=':bar_chart:',
)

# -----------------------------------------------------------------------------
# Load the data (with caching)

@st.cache_data
def load_equipment_data():
    """Load daily frames data from a CSV."""
    DATA_FILENAME = Path(__file__).parent / 'data/daily_frames.xlsx'
    df = pd.read_excel(DATA_FILENAME, index_col=0, parse_dates=True)
    return df

final_df = load_equipment_data()

# -----------------------------------------------------------------------------
# Draw the page

'''
# :bar_chart: Low Performance MALTA K2G Dashboard

Visualize daily frame counts for each equipment over time.
'''

''

# Equipment selection
equipments = final_df.columns.tolist()

if not equipments:
    st.warning("No equipment data found.")
else:
    selected_equipments = st.multiselect(
        "Which equipments would you like to view?",
        options=equipments,
        default=[equipments[0]]
    )

    # Date range selection
    date_range = st.slider(
        "Select the date range:",
        min_value=final_df.index.min().to_pydatetime(),
        max_value=final_df.index.max().to_pydatetime(),
        value=(final_df.index.min().to_pydatetime(), final_df.index.max().to_pydatetime())
    )

    filtered_df = final_df.loc[date_range[0]:date_range[1], selected_equipments]

    # Line chart with Plotly
    st.header("📈 Daily Frames Over Time", divider='gray')

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

    # Metrics display
    st.header(f"📊 Equipment Summary ({date_range[0].date()} to {date_range[1].date()})", divider='gray')
    cols = st.columns(min(len(selected_equipments), 4))

    for i, equip in enumerate(selected_equipments):
        col = cols[i % len(cols)]
        with col:
            start_val = filtered_df[equip].iloc[0]
            end_val = filtered_df[equip].iloc[-1]
            growth = f"{end_val / start_val:.2f}x" if start_val else 'n/a'
            st.metric(
                label=f"{equip}",
                value=f"{end_val:.0f} frames",
                delta=growth
            )
