import pandas as pd
import numpy as np
import streamlit as st
import pydeck as pdk

st.title("Rental properties in New York City")

## function to get property locations and data
@st.cache_data
def get_df():
    new_df = pd.read_csv('https://raw.githubusercontent.com/muumrar/columns/main/nylatlonv4.csv', na_values= '#DIV/0!')
    new_df = new_df.dropna(axis=0, how='any')
    new_df = new_df[new_df["price"] < 10000]
    new_df = new_df[new_df["price"] > 999]
    new_df["solo_salary"] = new_df["price_per_bed"] / 0.025
    new_df["unit_salary"] = new_df["price"] / 0.025
    return new_df

new_df = get_df()


## shootings data
@st.cache_data
def get_crime():
    crime_data = pd.read_csv('https://raw.githubusercontent.com/muumrar/columns/main/NYPD_Shooting_Incident_Data__Year_To_Date_Clean.csv')
    crime_data.columns = crime_data.columns.str.lower()
    crime_data = crime_data.rename(columns={'longitude': 'lon', 'latitude': 'lat'})
    return crime_data

crime_data = get_crime()

## get tree data (massive file so needs to be cached)
@st.cache_data
def get_trees():
    tree_data = pd.read_csv('https://raw.githubusercontent.com/muumrar/columns/main/Forestry_Tree_Points_clean.csv')
    return tree_data

#tree_data = get_trees()

## colour scale for tree heat map
COLOR_BREWER_BLUE_SCALE = [
    [0,100,0],
    [34,139,34],
    [50,205,50],
    [152,251,152],
    [0,250,154],
    [32,178,170],
]

def get_color(price):
    if price < 1500:
        return [34, 139, 34]  # Forest Green
    elif price < 2500:
        return [255, 215, 0]  # Gold
    elif price < 4000:
        return [255, 140, 0]  # Dark Orange
    else:
        return [178, 34, 34]  # Firebrick Red

new_df["color"] = new_df["price_per_bed"].apply(get_color)


## for salary and affordability calcs, start at nyc average of 45k
salary = 45000

## this allows users to input their salary and filter the visible properties using this field
with st.sidebar:
    number = st.number_input("Insert your yearly salary",  min_value=0, step=10000)
    show_afford = st.checkbox("Show only properties within budget")

salary = number if number != 0 else 0

# Create an "afford" column, but don't modify the original DataFrame
new_df["afford"] = np.where(new_df["price_per_bed"] < (salary / 12) * 0.3, "affordable", "not affordable")

# Only filter when the checkbox is checked
filtered_df = new_df[new_df["afford"] == "affordable"] if show_afford else new_df

# Ensure map renders with filtered dataset only if necessary
filtered_df["price_per_bed_scale"] = filtered_df["price_per_bed"] / filtered_df["price_per_bed"].max() * 500


if show_afford:
    new_df = new_df[new_df["afford"] == "affordable"]

#print(df.info())


#st.map(new_df)

#st.map(df)
#data = df.to_json(orient='table')
#print(data)

new_df["price_per_bed_scale"] = new_df["price_per_bed"] / new_df["price_per_bed"].max() * 500

## initial view state for pydeck
view = pdk.ViewState(
         latitude=40.65,
         longitude=-74.00,
         zoom=10,
         pitch=50,
     )

## properties map layer, height dictates cost, colour grade dictates proximity to metro
column_layer = pdk.Layer(
    "ColumnLayer",
    data=filtered_df,
    #data=crime_data,
    get_position=["lon", "lat"],
    get_elevation="price_per_bed_scale",
    elevation_scale=5,
    radius=100,
    get_fill_color="color",
    #get_fill_color=[255, 100, 255, 255],
    #get_fill_color=["price_per_bed_scale ", "price_per_bed_scale / 8", "price_per_bed_scale", 255],
    # get_fill_color=["100 / distance_between ", "distance_between", "100 / distance_between", 140],
    pickable=True,
    auto_highlight=True,
)

## shows tree coverage over the city
#tree_heat = pdk.Layer(
#     "HeatmapLayer",
#     data=tree_data,
#     #data=new_df,
#     opacity=0.9,
#     get_position=["lon", "lat"],
#     aggregation=pdk.types.String("MEAN"),
#     color_range=COLOR_BREWER_BLUE_SCALE,
#     threshold=1,
#     #get_weight="weight",
#     pickable=True,
# )

## not used
# crime_layer = pdk.Layer(
#     "ScatterplotLayer",
#     crime_data,
#     pickable=True,
#     opacity=0.8,
#     stroked=True,
#     filled=True,
#     radius_scale=5,
#     radius_min_pixels=1,
#     radius_max_pixels=100,
#     line_width_min_pixels=1,
#     get_position=["lon", "lat"],
#     get_radius=100,
#     get_fill_color=[255, 140, 0],
#     get_line_color=[0, 0, 0],
# )

## shows shooting concentration in the city
hex_layer = pdk.Layer(
    "HexagonLayer",
    crime_data,
    get_position=["lon", "lat"],
    auto_highlight=True,
    elevation_scale=0,
    pickable=True,
    elevation_range=[0, 3000],
    extruded=True,
    coverage=1,
)

tooltip = {
    "html": "<b>Price per bed:</b> ${price_per_bed}<br/>"
            "<b>Location:</b> {borough} (<b>{lat}, {lon}</b>)<br/>"
            "<b>Nearest metro:</b> {nearest_station}, {distance_between} km away",
    "style": {"background": "rgba(0, 0, 0, 0.7)", "color": "white", "font-family": "Arial"}
}




r_prop = pdk.Deck(
    #[column_layer, hex_layer],
    column_layer,
    initial_view_state=view,
    tooltip=tooltip,
    map_provider="mapbox",
    map_style=pdk.map_styles.SATELLITE,
)



# r_crime = pdk.Deck(
#     hex_layer,
#     initial_view_state=view,
#     tooltip=tooltip,
#     map_provider="mapbox",
#     map_style=pdk.map_styles.SATELLITE,
# )

#r_tree = pdk.Deck(
#     tree_heat,
#     initial_view_state=view,
#     map_provider="mapbox",
#     map_style=pdk.map_styles.SATELLITE
# )


st.pydeck_chart(r_prop)
st.write("_The elevation of the columns in the above chart indicate the price of the property. The colour gradient indicates how close the nearest metro station is, with darker colours being further away than the lighter pink_")


    
with st.expander('Show Raw Data'):
    st.subheader('Raw Data')
    st.write(new_df)

# with st.expander("Show shootings info"):
#     st.subheader('Police data on shootings in NYC in last year')
#     st.pydeck_chart(r_crime)

#st.subheader('Tree coverage in the city')
#st.pydeck_chart(r_tree)




