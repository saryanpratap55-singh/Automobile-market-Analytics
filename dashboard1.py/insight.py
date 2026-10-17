import streamlit as st
import pandas as pd
import plotly.express as px
st.set_page_config(
    page_title="Automobile Market Dashboard",
    page_icon="🚗",
    layout="wide",
)

TEMPLATE = "plotly_dark"
PALETTE = px.colors.qualitative.Set2
@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    data = pd.read_csv(path)
    data = data.drop_duplicates()
    return data


df = load_data("automobile_dataset.csv")


def style(fig, height=400):
    """Apply one consistent look to every chart."""
    fig.update_layout(
        template=TEMPLATE,
        height=height,
        margin=dict(l=10, r=10, t=50, b=10),
        title=dict(x=0.02),
    )
    return fig
st.sidebar.title("Dashboard filters")

all_makes = sorted(df["Make"].unique())
selected_make = st.sidebar.multiselect("Make", options=all_makes, default=all_makes)

all_fuels = sorted(df["Fuel_Type"].dropna().unique())
selected_fuel = st.sidebar.multiselect("Fuel type", options=all_fuels, default=all_fuels)

year_min, year_max = int(df["Year"].min()), int(df["Year"].max())
if year_min < year_max:
    selected_years = st.sidebar.slider(
        "Year range", year_min, year_max, (year_min, year_max)
    )
else:
    selected_years = (year_min, year_max)

price_min, price_max = int(df["Selling_Price"].min()), int(df["Selling_Price"].max())
if price_min < price_max:
    selected_price = st.sidebar.slider(
        "Selling price range ($)", price_min, price_max, (price_min, price_max)
    )
else:
    selected_price = (price_min, price_max)

filtered_df = df[
    df["Make"].isin(selected_make)
    & df["Fuel_Type"].isin(selected_fuel)
    & df["Year"].between(*selected_years)
    & df["Selling_Price"].between(*selected_price)
]

st.sidebar.markdown("---")
st.sidebar.caption(f"Showing {len(filtered_df):,} of {len(df):,} cars")
st.title("🚗 Automobile Market Dashboard")
st.caption("Explore pricing, performance and fuel trends across makes and years.")

if filtered_df.empty:
    st.warning("No cars match the current filters. Widen your selection in the sidebar.")
    st.stop()
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total cars", f"{len(filtered_df):,}")
k2.metric("Avg selling price", f"${filtered_df['Selling_Price'].mean():,.0f}")
k3.metric("Highest price", f"${filtered_df['Selling_Price'].max():,.0f}")
k4.metric("Avg mileage", f"{filtered_df['Mileage'].mean():,.0f} mi")
k5.metric("Avg horsepower", f"{filtered_df['Horsepower'].mean():,.0f} hp")

st.markdown("")
tab_overview, tab_price, tab_perf, tab_data = st.tabs(
    ["Overview", "Price analysis", "Performance", "Data"]
)
with tab_overview:
    avg_price_by_make = (
        filtered_df.groupby("Make")["Selling_Price"]
        .mean()
        .reset_index()
        .sort_values("Selling_Price", ascending=False)
    )
    fig = px.bar(
        avg_price_by_make,
        x="Make",
        y="Selling_Price",
        color="Selling_Price",
        color_continuous_scale="Tealgrn",
        title="Average selling price by make",
        labels={"Selling_Price": "Avg price ($)"},
    )
    st.plotly_chart(style(fig), use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        fig = px.pie(
            filtered_df,
            names="Fuel_Type",
            hole=0.45,
            title="Fuel type distribution",
            color_discrete_sequence=PALETTE,
        )
        fig.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(style(fig), use_container_width=True)

    with c2:
        avg_price_by_year = (
            filtered_df.groupby("Year")["Selling_Price"].mean().reset_index()
        )
        fig = px.line(
            avg_price_by_year,
            x="Year",
            y="Selling_Price",
            markers=True,
            title="Average price by year",
            labels={"Selling_Price": "Avg price ($)"},
        )
        st.plotly_chart(style(fig), use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        count_by_make = (
            filtered_df["Make"]
            .value_counts()
            .reset_index()
            .rename(columns={"count": "Cars", "index": "Make"})
        )
        count_by_make.columns = ["Make", "Cars"]
        fig = px.bar(
            count_by_make,
            x="Cars",
            y="Make",
            orientation="h",
            title="Number of cars by make",
            color_discrete_sequence=[PALETTE[0]],
        )
        fig.update_yaxes(categoryorder="total ascending")
        st.plotly_chart(style(fig), use_container_width=True)

    with c4:
        cars_by_year_fuel = (
            filtered_df.groupby(["Year", "Fuel_Type"]).size().reset_index(name="Cars")
        )
        fig = px.area(
            cars_by_year_fuel,
            x="Year",
            y="Cars",
            color="Fuel_Type",
            title="Fuel type mix over the years",
            color_discrete_sequence=PALETTE,
        )
        st.plotly_chart(style(fig), use_container_width=True)
with tab_price:
    c1, c2 = st.columns(2)
    with c1:
        fig = px.histogram(
            filtered_df,
            x="Selling_Price",
            nbins=30,
            marginal="box",
            title="Selling price distribution",
            labels={"Selling_Price": "Selling price ($)"},
            color_discrete_sequence=[PALETTE[1]],
        )
        st.plotly_chart(style(fig, 450), use_container_width=True)

    with c2:
        fig = px.box(
            filtered_df,
            x="Fuel_Type",
            y="Selling_Price",
            color="Fuel_Type",
            title="Price spread by fuel type",
            color_discrete_sequence=PALETTE,
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(style(fig, 450), use_container_width=True)

    fig = px.box(
        filtered_df,
        x="Make",
        y="Selling_Price",
        color="Make",
        title="Price spread by make",
        color_discrete_sequence=PALETTE,
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(style(fig, 450), use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        fig = px.scatter(
            filtered_df,
            x="Year",
            y="Selling_Price",
            color="Fuel_Type",
            hover_data=["Make"],
            opacity=0.75,
            title="Price vs year",
            color_discrete_sequence=PALETTE,
        )
        st.plotly_chart(style(fig), use_container_width=True)

    with c4:
        fig = px.treemap(
            filtered_df,
            path=["Make", "Fuel_Type"],
            values="Selling_Price",
            color="Selling_Price",
            color_continuous_scale="Tealgrn",
            title="Market value by make and fuel type",
        )
        st.plotly_chart(style(fig), use_container_width=True)
with tab_perf:
    c1, c2 = st.columns(2)
    with c1:
        fig = px.scatter(
            filtered_df,
            x="Horsepower",
            y="Selling_Price",
            color="Fuel_Type",
            size="Mileage",
            hover_data=["Make", "Year"],
            opacity=0.75,
            title="Horsepower vs price (bubble size = mileage)",
            color_discrete_sequence=PALETTE,
        )
        st.plotly_chart(style(fig, 450), use_container_width=True)

    with c2:
        fig = px.scatter(
            filtered_df,
            x="Mileage",
            y="Selling_Price",
            color="Make",
            hover_data=["Year", "Fuel_Type"],
            opacity=0.75,
            title="Mileage vs price",
            color_discrete_sequence=PALETTE,
        )
        st.plotly_chart(style(fig, 450), use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        avg_hp_by_make = (
            filtered_df.groupby("Make")["Horsepower"]
            .mean()
            .reset_index()
            .sort_values("Horsepower", ascending=False)
        )
        fig = px.bar(
            avg_hp_by_make,
            x="Make",
            y="Horsepower",
            color="Horsepower",
            color_continuous_scale="Sunsetdark",
            title="Average horsepower by make",
        )
        st.plotly_chart(style(fig), use_container_width=True)

    with c4:
        numeric_cols = filtered_df.select_dtypes("number")
        if numeric_cols.shape[1] >= 2:
            corr = numeric_cols.corr()
            fig = px.imshow(
                corr,
                text_auto=".2f",
                aspect="auto",
                color_continuous_scale="RdBu_r",
                zmin=-1,
                zmax=1,
                title="Correlation between numeric features",
            )
            st.plotly_chart(style(fig), use_container_width=True)
with tab_data:
    st.subheader("Filtered data")
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)

    st.download_button(
        "Download filtered data (CSV)",
        data=filtered_df.to_csv(index=False).encode("utf-8"),
        file_name="filtered_automobile_data.csv",
        mime="text/csv",
    )

    st.subheader("Summary statistics")
    st.dataframe(filtered_df.describe().round(2), use_container_width=True)