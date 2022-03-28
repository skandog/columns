import pandas as pd
import numpy as np
import streamlit as st
import pydeck as pdk

st.title("Rental properties in New York City")


#df = pd.read_csv('https://raw.githubusercontent.com/muumrar/columns/main/nylatlonv2.csv', na_values= '#DIV/0!')
df = pd.read_csv('https://raw.githubusercontent.com/muumrar/columns/main/nylatlonv4.csv', na_values= '#DIV/0!')
df.info()

#df = pd.read_csv('https://raw.githubusercontent.com/muumrar/columns/main/nylatlon.csv', na_values= '#DIV/0!')
#df.replace(to_replace = np.nan, value = 1)
new_df = df.dropna(axis=0, how = 'any')
#new_df.info()
new_df = new_df[new_df["price"] < 10000]
new_df = new_df[new_df["price"] > 999]
new_df["solo_salary"] = new_df["price_per_bed"] / 0.025
new_df["unit_salary"] = new_df["price"] / 0.025

number = st.number_input("Insert your yearly salary")


salary = number
new_df["afford"] = np.where(new_df["price_per_bed"] < (salary/12) * 0.3, "affordable", "not affordable")
#new_df.assign(new_df["affordability"]= "affordable".where(new_df.unit_salary < (salary/12) * 0.3, "not affordable"))

# if new_df["unit_salary"] < (salary/12) * 0.3:
#     new_df["affordability"] = "affordable"
# else:
#     new_df["affordability"] = "not affordable"


new_df.info()

#print(new_df.info())
#print(new_df.head())

crime_data = pd.read_csv('https://raw.githubusercontent.com/muumrar/columns/main/NYPD_Shooting_Incident_Data__Year_To_Date_Clean.csv')
crime_data.columns = crime_data.columns.str.lower()
crime_data = crime_data.rename(columns={'longitude': 'lon', 'latitude': 'lat'})
#crime_data.info()


tree_data = pd.read_csv('https://raw.githubusercontent.com/muumrar/columns/main/Forestry_Tree_Points_clean.csv')
#tree_data.info()


COLOR_BREWER_BLUE_SCALE = [
    [0,100,0],
    [34,139,34],
    [50,205,50],
    [152,251,152],
    [0,250,154],
    [32,178,170],
]
#cols = ["price_per_bed", "price_per_bed_scale"]
#bool_series = pd.isnull(df[cols])
#print(df[bool_series])

#cols = ["beds", "price_per_bed", "price_per_bed_scale"]

#df[cols] = df[cols].astype(int)
#df["price"] = df["price"].astype(float)

#print(df.head())

#df.dropna()

#print(df["price_per_bed"])
#df["price_per_bed"] = df["price_per_bed"].astype(float, errors = 'raise')
#df = pd.read_csv('https://raw.githubusercontent.com/muumrar/columns/main/nylatlonbasic.csv')
#df['price / bed'] = df['price']/df['beds']

#print(df.head())

if st.checkbox('Show raw data'):
    st.subheader('Raw Data')
    st.write(new_df)



#print(df.info())


st.map(new_df)

#st.map(df)
#data = df.to_json(orient='table')
#print(data)



view = pdk.ViewState(
         latitude=40.65,
         longitude=-74.00,
         zoom=10,
         pitch=50,
     )


column_layer = pdk.Layer(
    "ColumnLayer",
    data=new_df,
    #data=crime_data,
    get_position=["lon", "lat"],
    get_elevation="price_per_bed_scale",
    elevation_scale=5,
    radius=100,
    #get_fill_color=[255, 100, 255, 255],
    #get_fill_color=["price_per_bed_scale ", "price_per_bed_scale / 8", "price_per_bed_scale", 255],
    get_fill_color=["100 / distance_between ", "distance_between", "100 / distance_between", 140],
    pickable=True,
    auto_highlight=True,
)

tree_heat = pdk.Layer(
    "HeatmapLayer",
    data=tree_data,
    #data=new_df,
    opacity=0.9,
    get_position=["lon", "lat"],
    aggregation=pdk.types.String("MEAN"),
    color_range=COLOR_BREWER_BLUE_SCALE,
    threshold=1,
    #get_weight="weight",
    pickable=True,
)


crime_layer = pdk.Layer(
    "ScatterplotLayer",
    crime_data,
    pickable=True,
    opacity=0.8,
    stroked=True,
    filled=True,
    radius_scale=5,
    radius_min_pixels=1,
    radius_max_pixels=100,
    line_width_min_pixels=1,
    get_position=["lon", "lat"],
    get_radius=100,
    get_fill_color=[255, 140, 0],
    get_line_color=[0, 0, 0],
)

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
    "html": "<b>${price_per_bed}</b> per bed, location: {borough} (<b>{lat}, {lon}</b>), <br/> Nearest metro: <b>{nearest_station}</b>, {distance_between}km away",
    "style": {"background": "grey", "color": "white", "font-family": '"Helvetica Neue", Arial', "z-index": "10000"},
}




r_prop = pdk.Deck(
    #[column_layer, hex_layer],
    column_layer,
    initial_view_state=view,
    tooltip=tooltip,
    map_provider="mapbox",
    map_style=pdk.map_styles.SATELLITE,
)

r_crime = pdk.Deck(
    hex_layer,
    initial_view_state=view,
    tooltip=tooltip,
    map_provider="mapbox",
    map_style=pdk.map_styles.SATELLITE,
)

r_tree = pdk.Deck(
    tree_heat,
    initial_view_state=view,
    map_provider="mapbox",
    map_style=pdk.map_styles.SATELLITE
)


#st.map(r)
st.pydeck_chart(r_prop)

st.subheader('Police data on shootings in NYC in last year')
st.pydeck_chart(r_crime)

st.subheader('Tree coverage in the city')
#st.map(tree_data)
st.pydeck_chart(r_tree)
