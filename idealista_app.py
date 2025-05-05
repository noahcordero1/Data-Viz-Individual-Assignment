import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Set page configuration
st.set_page_config(page_title="Madrid Real Estate Dashboard",
                   page_icon="🏢",
                   layout="wide",
                   initial_sidebar_state="expanded")

# Add custom CSS to improve appearance
st.markdown("""
<style>
    .main {
        background-color: #f5f7f9;
    }
    h1, h2, h3 {
        color: #2c3e50;
    }
    .metric-card {
        border: 1px solid #e6e9ef;
        border-radius: 5px;
        padding: 15px;
        background-color: white;
        box-shadow: 0 0 8px rgba(0,0,0,0.1);
        text-align: center;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4e89ae;
        color: white;
    }
    .st-emotion-cache-16txtl3 {
        padding: 3rem 1rem;
    }
    div[data-testid="stSidebarNav"] {
        background-color: rgba(245, 247, 249, 0.9);
        padding-top: 2rem;
    }
    .st-emotion-cache-16idsys p {
        font-size: 1.05rem;
        line-height: 1.5;
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.title("Madrid Real Estate Analysis Dashboard")
st.write("""
This dashboard provides insights into the Madrid real estate market to support investment and property purchase decisions.
Explore the data through interactive visualizations and filters to identify market trends, property characteristics, and value opportunities.
""")


# Load the data
@st.cache_data
def load_data():
    df = pd.read_csv('idealista_madrid.csv')

    # Add calculated columns
    df['price_per_sqft'] = df['price'] / df['sqft']
    df['price_per_room'] = df['price'] / df['rooms'].replace(0, 1)  # Avoid division by zero

    # Extract neighborhoods from address
    df['neighborhood'] = df['address'].str.split(',').str[0]

    return df


df = load_data()

# Sidebar filters
st.sidebar.header("Filters")
st.sidebar.markdown("---")

# Price range filter
price_min = int(df['price'].min())
price_max = int(df['price'].max())
price_range = st.sidebar.slider(
    "Price Range (€)",
    min_value=price_min,
    max_value=price_max,
    value=(price_min, 3000000),  # Default upper limit to 3M for better usability
    step=50000
)

# Area range filter
area_min = int(df['sqft'].min())
area_max = int(df['sqft'].max())
area_range = st.sidebar.slider(
    "Area Range (sqft)",
    min_value=area_min,
    max_value=area_max,
    value=(area_min, area_max),
    step=10
)

st.sidebar.markdown("---")

# Number of rooms filter
room_counts = sorted(df['rooms'].unique())
selected_rooms = st.sidebar.multiselect(
    "Number of Rooms",
    options=room_counts,
    default=room_counts
)

# Number of bathrooms filter
bath_counts = sorted(df['baths'].unique())
selected_baths = st.sidebar.multiselect(
    "Number of Bathrooms",
    options=bath_counts,
    default=bath_counts
)

st.sidebar.markdown("---")

# Property type filter
property_types = df['typology'].unique()
selected_types = st.sidebar.multiselect(
    "Property Type",
    options=property_types,
    default=property_types
)

# Neighborhood filter
neighborhoods = sorted(df['neighborhood'].unique())
selected_neighborhoods = st.sidebar.multiselect(
    "Neighborhoods",
    options=neighborhoods,
    default=[]  # Default to no filter
)

# Apply filters
filtered_df = df.copy()
filtered_df = filtered_df[
    (filtered_df['price'] >= price_range[0]) &
    (filtered_df['price'] <= price_range[1]) &
    (filtered_df['sqft'] >= area_range[0]) &
    (filtered_df['sqft'] <= area_range[1]) &
    (filtered_df['rooms'].isin(selected_rooms)) &
    (filtered_df['baths'].isin(selected_baths)) &
    (filtered_df['typology'].isin(selected_types))
    ]

# Apply neighborhood filter only if neighborhoods are selected
if selected_neighborhoods:
    filtered_df = filtered_df[filtered_df['neighborhood'].isin(selected_neighborhoods)]

# Check if filtered dataframe is empty and show warning
if filtered_df.empty:
    st.warning("No properties match your filter criteria. Please adjust your filters.")

# Dashboard Metrics
st.header("Key Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Properties", f"{len(filtered_df)}")
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    avg_price = filtered_df['price'].mean()
    # Check if avg_price is NaN or if filtered_df is empty
    if pd.isna(avg_price) or filtered_df.empty:
        st.metric("Avg. Price", "N/A")
    else:
        st.metric("Avg. Price", f"€{int(avg_price):,}")
    st.markdown("</div>", unsafe_allow_html=True)

with col3:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    avg_price_sqft = filtered_df['price_per_sqft'].mean()
    # Check if avg_price_sqft is NaN or if filtered_df is empty
    if pd.isna(avg_price_sqft) or filtered_df.empty:
        st.metric("Avg. €/sqft", "N/A")
    else:
        st.metric("Avg. €/sqft", f"€{int(avg_price_sqft):,}")
    st.markdown("</div>", unsafe_allow_html=True)

with col4:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    avg_area = filtered_df['sqft'].mean()
    # Check if avg_area is NaN or if filtered_df is empty
    if pd.isna(avg_area) or filtered_df.empty:
        st.metric("Avg. Area", "N/A")
    else:
        st.metric("Avg. Area", f"{int(avg_area)} sqft")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# Create tabs for different analysis views
tab1, tab2, tab3 = st.tabs(["Market Overview", "Property Analysis", "Value Analysis"])

# Tab 1: Market Overview
with tab1:
    st.header("Market Overview")

    if filtered_df.empty:
        st.warning("No properties match your filter criteria. Please adjust your filters to see visualizations.")
    else:
        col1, col2 = st.columns(2)

        with col1:
            # Price distribution histogram
            fig_price_dist = px.histogram(
                filtered_df,
                x="price",
                nbins=30,
                title="Price Distribution",
                labels={"price": "Price (€)", "count": "Number of Properties"},
                color_discrete_sequence=['#4e89ae']
            )
            fig_price_dist.update_layout(
                bargap=0.1,
                plot_bgcolor='rgba(255, 255, 255, 0.9)',
                paper_bgcolor='rgba(255, 255, 255, 0.0)',
                title_font=dict(size=18),
                margin=dict(l=40, r=40, t=50, b=40)
            )
            st.plotly_chart(fig_price_dist, use_container_width=True)

        with col2:
            # Property types pie chart
            typology_counts = filtered_df['typology'].value_counts().reset_index()
            typology_counts.columns = ['typology', 'count']

            fig_typology = px.pie(
                typology_counts,
                values='count',
                names='typology',
                title='Property Types',
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig_typology.update_traces(textposition='inside', textinfo='percent+label')
            fig_typology.update_layout(
                plot_bgcolor='rgba(255, 255, 255, 0.9)',
                paper_bgcolor='rgba(255, 255, 255, 0.0)',
                title_font=dict(size=18),
                margin=dict(l=40, r=40, t=50, b=40)
            )
            st.plotly_chart(fig_typology, use_container_width=True)

        # Top neighborhoods by average price
        if len(filtered_df['neighborhood'].unique()) > 1:
            top_neighborhoods = filtered_df.groupby('neighborhood')['price'].mean().reset_index()
            top_neighborhoods = top_neighborhoods.sort_values('price', ascending=False).head(10)

            fig_top_neighborhoods = px.bar(
                top_neighborhoods,
                x='neighborhood',
                y='price',
                title='Top 10 Neighborhoods by Average Price',
                labels={'price': 'Average Price (€)', 'neighborhood': 'Neighborhood'},
                color_discrete_sequence=['#4e89ae']
            )
            fig_top_neighborhoods.update_layout(
                xaxis_tickangle=-45,
                plot_bgcolor='rgba(255, 255, 255, 0.9)',
                paper_bgcolor='rgba(255, 255, 255, 0.0)',
                title_font=dict(size=18),
                margin=dict(l=40, r=40, t=50, b=40)
            )
            st.plotly_chart(fig_top_neighborhoods, use_container_width=True)
        else:
            st.info("Select more than one neighborhood to see neighborhood comparison charts.")

# Tab 2: Property Analysis
with tab2:
    st.header("Property Analysis")

    if filtered_df.empty:
        st.warning("No properties match your filter criteria. Please adjust your filters to see visualizations.")
    else:
        col1, col2 = st.columns(2)

        with col1:
            # Area vs Price scatterplot
            fig_area_price = px.scatter(
                filtered_df,
                x='sqft',
                y='price',
                color='typology',
                size='rooms',
                hover_name='neighborhood',
                hover_data=['baths', 'price_per_sqft'],
                title='Property Area vs Price',
                labels={'sqft': 'Area (sqft)', 'price': 'Price (€)', 'typology': 'Property Type', 'rooms': 'Rooms'},
                color_discrete_sequence=px.colors.qualitative.Safe
            )
            fig_area_price.update_layout(
                plot_bgcolor='rgba(255, 255, 255, 0.9)',
                paper_bgcolor='rgba(255, 255, 255, 0.0)',
                title_font=dict(size=18),
                margin=dict(l=40, r=40, t=50, b=40)
            )
            st.plotly_chart(fig_area_price, use_container_width=True)

        with col2:
            # Distribution of rooms
            fig_rooms = px.histogram(
                filtered_df,
                x='rooms',
                color='typology',
                barmode='group',
                title='Distribution of Rooms by Property Type',
                labels={'rooms': 'Number of Rooms', 'count': 'Number of Properties', 'typology': 'Property Type'},
                color_discrete_sequence=px.colors.qualitative.Safe
            )
            fig_rooms.update_layout(
                plot_bgcolor='rgba(255, 255, 255, 0.9)',
                paper_bgcolor='rgba(255, 255, 255, 0.0)',
                title_font=dict(size=18),
                margin=dict(l=40, r=40, t=50, b=40)
            )
            st.plotly_chart(fig_rooms, use_container_width=True)

        # Distribution of bathrooms
        fig_baths = px.histogram(
            filtered_df,
            x='baths',
            color='typology',
            barmode='group',
            title='Distribution of Bathrooms by Property Type',
            labels={'baths': 'Number of Bathrooms', 'count': 'Number of Properties', 'typology': 'Property Type'},
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        fig_baths.update_layout(
            plot_bgcolor='rgba(255, 255, 255, 0.9)',
            paper_bgcolor='rgba(255, 255, 255, 0.0)',
            title_font=dict(size=18),
            margin=dict(l=40, r=40, t=50, b=40)
        )
        st.plotly_chart(fig_baths, use_container_width=True)

# Tab 3: Value Analysis
with tab3:
    st.header("Value Analysis")

    if filtered_df.empty:
        st.warning("No properties match your filter criteria. Please adjust your filters to see visualizations.")
    else:
        col1, col2 = st.columns(2)

        with col1:
            # Price per square foot by neighborhood
            if len(filtered_df['neighborhood'].unique()) > 1:
                price_sqft_neighborhood = filtered_df.groupby('neighborhood')['price_per_sqft'].mean().reset_index()
                price_sqft_neighborhood = price_sqft_neighborhood.sort_values('price_per_sqft', ascending=False).head(
                    10)

                fig_price_sqft = px.bar(
                    price_sqft_neighborhood,
                    x='neighborhood',
                    y='price_per_sqft',
                    title='Top 10 Neighborhoods by Price per Square Foot',
                    labels={'price_per_sqft': 'Average Price per Square Foot (€)', 'neighborhood': 'Neighborhood'},
                    color_discrete_sequence=['#43a2ca']
                )
                fig_price_sqft.update_layout(
                    xaxis_tickangle=-45,
                    plot_bgcolor='rgba(255, 255, 255, 0.9)',
                    paper_bgcolor='rgba(255, 255, 255, 0.0)',
                    title_font=dict(size=18),
                    margin=dict(l=40, r=40, t=50, b=40)
                )
                st.plotly_chart(fig_price_sqft, use_container_width=True)
            else:
                st.info("Select more than one neighborhood to see neighborhood comparison charts.")

        with col2:
            # Price per room analysis
            if len(filtered_df['rooms'].unique()) > 1:
                price_room_df = filtered_df.groupby(['rooms', 'typology'])['price'].mean().reset_index()

                fig_price_room = px.bar(
                    price_room_df,
                    x='rooms',
                    y='price',
                    color='typology',
                    barmode='group',
                    title='Average Price by Number of Rooms and Property Type',
                    labels={'rooms': 'Number of Rooms', 'price': 'Average Price (€)', 'typology': 'Property Type'},
                    color_discrete_sequence=px.colors.qualitative.Safe
                )
                fig_price_room.update_layout(
                    plot_bgcolor='rgba(255, 255, 255, 0.9)',
                    paper_bgcolor='rgba(255, 255, 255, 0.0)',
                    title_font=dict(size=18),
                    margin=dict(l=40, r=40, t=50, b=40)
                )
                st.plotly_chart(fig_price_room, use_container_width=True)
            else:
                st.info("Select more than one room configuration to see room comparison charts.")

        # Value opportunity analysis
        st.subheader("Value Opportunities")

        # Check if we have enough data for value analysis
        if len(filtered_df['neighborhood'].unique()) > 1:
            # Calculate neighborhood average prices
            neighborhood_avg = filtered_df.groupby('neighborhood')['price_per_sqft'].mean().reset_index()
            neighborhood_avg.columns = ['neighborhood', 'avg_price_per_sqft']

            # Find properties with good value (price per sqft below neighborhood average)
            value_df = filtered_df.merge(neighborhood_avg, on='neighborhood')
            value_df['value_ratio'] = value_df['price_per_sqft'] / value_df['avg_price_per_sqft']
            value_df['value_opportunity'] = 2 - value_df['value_ratio']  # Higher score = better value

            # Price per sqft vs property size - with trendline
            try:
                fig_value_size = px.scatter(
                    filtered_df,
                    x='sqft',
                    y='price_per_sqft',
                    color='typology',
                    size='rooms',
                    hover_name='neighborhood',
                    hover_data=['price', 'baths'],
                    title='Price per Square Foot vs Property Size',
                    labels={'sqft': 'Area (sqft)', 'price_per_sqft': 'Price per Square Foot (€)',
                            'typology': 'Property Type'},
                    color_discrete_sequence=px.colors.qualitative.Safe,
                    trendline='ols'  # Add trendline - now safe since statsmodels is installed
                )
                fig_value_size.update_layout(
                    plot_bgcolor='rgba(255, 255, 255, 0.9)',
                    paper_bgcolor='rgba(255, 255, 255, 0.0)',
                    title_font=dict(size=18),
                    margin=dict(l=40, r=40, t=50, b=40)
                )
                st.plotly_chart(fig_value_size, use_container_width=True)
            except Exception as e:
                # Fallback without trendline if error occurs
                fig_value_size = px.scatter(
                    filtered_df,
                    x='sqft',
                    y='price_per_sqft',
                    color='typology',
                    size='rooms',
                    hover_name='neighborhood',
                    hover_data=['price', 'baths'],
                    title='Price per Square Foot vs Property Size',
                    labels={'sqft': 'Area (sqft)', 'price_per_sqft': 'Price per Square Foot (€)',
                            'typology': 'Property Type'},
                    color_discrete_sequence=px.colors.qualitative.Safe
                )
                fig_value_size.update_layout(
                    plot_bgcolor='rgba(255, 255, 255, 0.9)',
                    paper_bgcolor='rgba(255, 255, 255, 0.0)',
                    title_font=dict(size=18),
                    margin=dict(l=40, r=40, t=50, b=40)
                )
                st.plotly_chart(fig_value_size, use_container_width=True)
                st.info("Trendline could not be displayed due to limited data. More diverse data points are needed.")
        else:
            st.info("Select more than one neighborhood to see value opportunity analysis.")

        # Property data table
        st.subheader("Property Data")

        # Select columns to display
        display_columns = ['title', 'price', 'rooms', 'baths', 'sqft', 'price_per_sqft', 'neighborhood', 'typology']

        # Format the display dataframe
        formatted_df = filtered_df[display_columns].copy()
        if not formatted_df.empty:
            formatted_df['price'] = formatted_df['price'].apply(lambda x: f"€{int(x):,}")
            formatted_df['price_per_sqft'] = formatted_df['price_per_sqft'].apply(lambda x: f"€{int(x):,}")

        # Display the dataframe with pagination
        st.dataframe(formatted_df, height=300, use_container_width=True)

        # Add a download button for the filtered data
        if not filtered_df.empty:
            st.download_button(
                label="Download filtered data as CSV",
                data=filtered_df.to_csv(index=False).encode('utf-8'),
                file_name='madrid_real_estate_filtered.csv',
                mime='text/csv',
            )

# Footer with design rationale
st.markdown("---")
st.header("Design Rationale")
st.markdown("""
### Dashboard Design Principles
This dashboard was designed based on the following data visualization principles and cognitive factors:
# Dashboard Design Principles
---------------------------
This dashboard was designed following established cognitive principles and data visualization best practices to support effective decision-making when exploring Madrid's real estate market.

## Cognitive Principles Applied
-----------------------------
### Cognitive Load Management
- Information Chunking: Related metrics and visualizations are grouped into logical sections (Market Overview, Property Analysis, Value Analysis)
- Progressive Disclosure: Information is revealed through tabs, moving from overview to detailed analysis
- Working Memory Optimization: Limited to 5-7 key metrics in each section to prevent cognitive overload

### Decision Support
-----------------
- Decision Hierarchy: Dashboard follows a natural decision flow from situation awareness (Key Metrics) to exception identification (visualizations highlighting outliers) to comparative analysis (neighborhood comparisons)
- Comparative Analysis: Consistent scales and visual encoding allow direct comparison between neighborhoods, property types, and other dimensions
- Pattern Recognition: Visualizations are designed to highlight trends, correlations, and anomalies that might be invisible in raw data

### Bias Mitigation
-----------------
- Confirmation Bias Mitigation: Multiple perspectives of the same data are presented across different tabs
- Recency Bias Mitigation: Historical context is provided through time-based visualizations
- Framing Effect Mitigation: Data is presented with neutral language and multiple reference points

## Visualization Principles Applied
----------------------------------
### Data-Ink Ratio
-------------
- Non-essential decorative elements are minimized
- Clean, white backgrounds enhance focus on the data
- Gridlines and borders are reduced to essential elements

### Chart Type Appropriateness
---------------------------
- Bar charts for comparing discrete categories (neighborhoods, property types)
- Scatter plots for examining relationships between variables (price vs. area)
- Histograms for understanding distributions (price, rooms)

### Visual Hierarchy
-----------------
- Key metrics positioned prominently at the top
- Larger charts for primary insights, smaller for supporting details
- Color used strategically to highlight important patterns

### Contextual Reference Points
----------------------------
- Average lines and trendlines provide context for individual data points
- Neighborhood averages serve as benchmarks for property evaluation
- Filter states are clearly visible to maintain awareness of the current data context

## User Experience Enhancements
------------------------------
- Interactive Filtering: Sidebar filters allow users to focus on relevant segments
- Responsive Design: Charts adjust to screen size for optimal viewing
- Focus + Context: Detail tables provide granular data while visualizations maintain broader patterns
- Consistent Visual Language: Uniform color scheme, typography, and chart styling throughout

This dashboard balances analytical depth with cognitive accessibility, enabling users to quickly understand market trends while providing tools for detailed property evaluation.
""")
