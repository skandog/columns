import pandas as pd
import numpy as np
import streamlit as st
import pydeck as pdk

st.title("Rental properties in New York City")

df = pd.read_csv('https://raw.githubusercontent.com/muumrar/columns/main/nylatlon.csv')
#df = pd.read_csv('https://raw.githubusercontent.com/muumrar/columns/main/nylatlonbasic.csv')
#df['price / bed'] = df['price']/df['beds']

#print(df.head())

if st.checkbox('Show raw data'):
    st.subheader('Raw Data')
    st.write(df)

st.map(df)

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
    data=df,
    get_position=["lon", "lat"],
    get_elevation=10,
    elevation_scale=100,
    radius=100,
    get_fill_color=[255, 100, 255, 255],
    #get_fill_color=["price / 10", "price", "price / 10", 255],
    #get_fill_color=["mrt_distance * 10", "mrt_distance", "mrt_distance * 10", 140],
    pickable=True,
    auto_highlight=True,
)


r = pdk.Deck(
    column_layer,
    initial_view_state=view,
    #tooltip=tooltip,
    map_provider="mapbox",
    map_style=pdk.map_styles.SATELLITE,
)

#st.map(r)
st.pydeck_chart(r)