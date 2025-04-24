'''import streamlit as st
import pandas as pd
import math
from pathlib import Path

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='Low Performance MALTA K2G Dashboard',
    page_icon=':earth_americas:', # This is an emoji shortcode. Could be a URL too.
)

# -----------------------------------------------------------------------------
# Declare some useful functions.

@st.cache_data
def get_gdp_data():
    """Grab GDP data from a CSV file.

    This uses caching to avoid having to read the file every time. If we were
    reading from an HTTP endpoint instead of a file, it's a good idea to set
    a maximum age to the cache with the TTL argument: @st.cache_data(ttl='1d')
    """

    # Instead of a CSV on disk, you could read from an HTTP endpoint here too.
    DATA_FILENAME = Path(__file__).parent/'data/gdp_data.csv'
    raw_gdp_df = pd.read_csv(DATA_FILENAME)

    MIN_YEAR = 1960
    MAX_YEAR = 2022

    # The data above has columns like:
    # - Country Name
    # - Country Code
    # - [Stuff I don't care about]
    # - GDP for 1960
    # - GDP for 1961
    # - GDP for 1962
    # - ...
    # - GDP for 2022
    #
    # ...but I want this instead:
    # - Country Name
    # - Country Code
    # - Year
    # - GDP
    #
    # So let's pivot all those year-columns into two: Year and GDP
    gdp_df = raw_gdp_df.melt(
        ['Country Code'],
        [str(x) for x in range(MIN_YEAR, MAX_YEAR + 1)],
        'Year',
        'GDP',
    )

    # Convert years from string to integers
    gdp_df['Year'] = pd.to_numeric(gdp_df['Year'])

    return gdp_df

gdp_df = get_gdp_data()

# -----------------------------------------------------------------------------
# Draw the actual page

# Set the title that appears at the top of the page.
'''
'''# :earth_americas: GDP dashboard

Browse GDP data from the [World Bank Open Data](https://data.worldbank.org/) website. As you'll
notice, the data only goes to 2022 right now, and datapoints for certain years are often missing.
But it's otherwise a great (and did I mention _free_?) source of data.
'''

'''# Add some spacing
''
''

min_value = gdp_df['Year'].min()
max_value = gdp_df['Year'].max()

from_year, to_year = st.slider(
    'Which years are you interested in?',
    min_value=min_value,
    max_value=max_value,
    value=[min_value, max_value])

countries = gdp_df['Country Code'].unique()

if not len(countries):
    st.warning("Select at least one country")

selected_countries = st.multiselect(
    'Which countries would you like to view?',
    countries,
    ['DEU', 'FRA', 'GBR', 'BRA', 'MEX', 'JPN'])

''
''
''

# Filter the data
filtered_gdp_df = gdp_df[
    (gdp_df['Country Code'].isin(selected_countries))
    & (gdp_df['Year'] <= to_year)
    & (from_year <= gdp_df['Year'])
]

st.header('GDP over time', divider='gray')

''

st.line_chart(
    filtered_gdp_df,
    x='Year',
    y='GDP',
    color='Country Code',
)

''
''


first_year = gdp_df[gdp_df['Year'] == from_year]
last_year = gdp_df[gdp_df['Year'] == to_year]

st.header(f'GDP in {to_year}', divider='gray')

''

cols = st.columns(4)

for i, country in enumerate(selected_countries):
    col = cols[i % len(cols)]

    with col:
        first_gdp = first_year[first_year['Country Code'] == country]['GDP'].iat[0] / 1000000000
        last_gdp = last_year[last_year['Country Code'] == country]['GDP'].iat[0] / 1000000000

        if math.isnan(first_gdp):
            growth = 'n/a'
            delta_color = 'off'
        else:
            growth = f'{last_gdp / first_gdp:,.2f}x'
            delta_color = 'normal'

        st.metric(
            label=f'{country} GDP',
            value=f'{last_gdp:,.0f}B',
            delta=growth,
            delta_color=delta_color
        )
'''

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
