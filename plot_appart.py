# from folium.plugins import MarkerCluster
# from io import BytesIO
# import requests
import os.path

import numpy as np
from geopy.geocoders import Nominatim
import pandas as pd
import folium
from folium.plugins import BeautifyIcon
import webbrowser
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cmx
from routingpy import MapboxValhalla, ORS

from scipy import spatial

# /data/covid/real_state/plot_appart.py





def colourcode(rent_price):
    if (rent_price < lower_price_bracket):
        return('green')
    elif (rent_price >= lower_price_bracket and rent_price < mid_price_bracket):
        return('orange')
    else:
        return('red')


def create_colorcode(df):
    #create a colour coding function
    lower_price_bracket = np.percentile(df['Price m2 '],30)
    mid_price_bracket = np.percentile(df['Price m2 '],70)


def auto_open(path, f_map):
    html_page = f'{path}'
    f_map.save(html_page)
    # open in browser.
    new = 2
    webbrowser.open(html_page, new=new)


def get_scalar_map(scale_vmin, scale_vmax):
    gistNcar = cm = plt.get_cmap()  # 'jet'  'coolwarm'
    cNorm = colors.Normalize(vmin=scale_vmin, vmax=scale_vmax)
    return cmx.ScalarMappable(norm=cNorm, cmap=gistNcar)


def shift_same_locations(lat_long):
    dt = 0.0007; deltas = [[0, dt], [dt, 0], [dt, dt], [0, -dt], [-dt, 0], [-dt, -dt]]
    _, idx, counts = np.unique(lat_long, return_index=True, axis=0, return_counts=True)
    tree = spatial.KDTree(lat_long)
    for id_loc, count in zip(idx, counts):
        if count > 1:
            nearest_dist, nearest_idx = tree.query(lat_long[id_loc], k=count)
            for r_id, c_id in zip(nearest_idx[1:], range(count - 1)):
                lat_long[r_id] += deltas[c_id]
    return lat_long





#The price per squere meter is color coded plotted in the center of the circle, the total price is in de border.


ors_key = "Create your ORS account and put your routingpy  key here"
googleSheetId = 'Put your google sheet ID here'
worksheetName = 'Sheet1'
URL = 'https://docs.google.com/spreadsheets/d/{0}/gviz/tq?tqx=out:csv&sheet={1}'.format(googleSheetId, worksheetName)

df = pd.read_csv(URL)
# print(df)
#create empty lists to store values later on


geolocator = Nominatim(user_agent="put the email from your Nominatim account")
stras_location = geolocator.geocode("Strasbourg, Pl. de la Gare, 67000 Strasbourg")
stras_lon_lat = [stras_location[1][1], stras_location[1][0]]
sgmap = folium.Map(location=stras_location[1], zoom_start=13)  # create a map of Strasbourg
dur_f = "/data/covid/real_state/cache_appart_durations.npy"
latlon_f = dur_f.replace("durations", "lat_longs")
if os.path.exists(dur_f):
    with open(dur_f, 'rb') as f:
        [durations, paths, distances] = np.load(f, allow_pickle=True)[()]  # [()]  #
else: durations={}; paths={}; distances={}  # long = []

unique_addresses = df['Address '].unique()
client = ORS(api_key=ors_key)  #  MapboxValhalla(api_key='mapbox_key')
for i in range(0, len(unique_addresses)):
    u_addr = str(unique_addresses[i])
    if u_addr in distances.keys(): continue

    locator = geolocator.geocode(u_addr)
    lat_lon=locator[1]
    route = client.directions(
    locations = [[lat_lon[1], lat_lon[0]], stras_lon_lat],
    profile='cycling-regular',
    # dry_run=True
    )
    geo_path = np.array(route.geometry); geo_path=np.array([geo_path[:,1], geo_path[:,0]])
    durations[u_addr] = route.duration/60.0
    paths[u_addr] = (geo_path.T).tolist()
    distances[u_addr] = route.distance
with open(dur_f, 'wb') as f:  #When crash, reload and complete missing when request limit reached.
    np.save(f, [durations, paths, distances])

if os.path.exists(latlon_f):
    with open(latlon_f, 'rb') as f:
        [location, lat_long] = np.load(f, allow_pickle=True)[()]  # [()]  #
    lat_long = lat_long.astype(np.float)
else:
    location = [];    lat_long = [];
    for i in range(0, len(df.index)):  # loop through the addresses collected from the website to generate latitude and longitude values
        locator = geolocator.geocode(str(df['Address '][i]))
        location.append(locator); lat_lon=location[i][1]
        lat_long.append(list(lat_lon))
    lat_long = np.array(lat_long)
    with open(latlon_f, 'wb') as f:
        np.save(f, [location, lat_long])

lat_df = pd.DataFrame(lat_long[:, 0], columns=["Latitude"])  # create the latitude and longitude dataframes
long_df = pd.DataFrame(lat_long[:, 1], columns=["Longitude"])

df = pd.concat([df, lat_df, long_df], axis=1)  # combine the lat and long df into the main dataset

latitudes = df['Latitude']; longitudes = df['Longitude']; years = df['Deliver ']  # store latitude data and longitude data in dataframes
prices_m2 = df['Price m2 ']; prices = df['Price ']; addresses = df['Address ']; sizes = df['Size ']; urls = df['url ']

scalarMap_price_m2 = get_scalar_map(np.min(df['Price m2 ']), np.max(df['Price m2 ']) )
scalarMap_price = get_scalar_map(np.min(df['Price ']), np.max(df['Price ']) )
key_min = min(durations.keys(), key=(lambda k: durations[k]))
scalarMap_duration = get_scalar_map(durations[key_min], 30 )

lat_long = shift_same_locations(lat_long)

delivers = pd.unique(years); d_ys={}
for d_ye in delivers:
    d_ye=str(d_ye)
    d_ys[d_ye]=folium.FeatureGroup(name=d_ye)
    # sgmap.add_child(d_ys[d_ye])
# fp = folium.FeatureGroup(name="Price")# fpTm2 = folium.FeatureGroup(name="PriceT&m2")
# icon_square = BeautifyIcon(
#     # icon_shape='doughnut',
#     border_color= 'transparent',   #colors.to_hex(scalarMap_price.to_rgba(130000)),
#     text_color=colors.to_hex(scalarMap_price.to_rgba(130000)),
#     # border_width=6,
#     background_color=colors.to_hex(scalarMap_price_m2.to_rgba(5600)),
#     number=1,
#     inner_icon_style='font-size:30px;',
#     iconSize=30
# )
# folium.Marker(stras_location[1], tooltip='square', icon=icon_square, popup=str(40) + ' m2, ' + str(5000) + ' $/m2').add_to(fp)

#loop to find the houses on the map using coordinates
for lt_ln, size, price, price_m2, year, url, address in zip(lat_long, sizes, prices, prices_m2, years, urls, addresses):
    # folium.Marker(location = [latitude,longitude],popup=str(address) + ' $' + str(price), icon = folium.Icon(color=colors.to_hex(scalarMap.to_rgba(price)))).add_to(sgmap)
    # folium.CircleMarker(location=lt_ln.tolist(),radius=11, weight=1, popup=str(size) + ' m2, ' + str(price)+' $', fill=True,  # Set fill to True
    #                     fill_color=colors.to_hex(scalarMap_price_m2.to_rgba(price_m2)), color='black', fill_opacity=0.7).add_to(fpm2)
    # # folium.CircleMarker(location=lt_ln.tolist(), radius=9, weight=1, popup=str(size) + ' m2, ' + str(price_m2)+' $/m2',
    #                     fill=True, fill_color=colors.to_hex(scalarMap_price.to_rgba(price)), color='white', fill_opacity=0.7).add_to(fp)
    po_str = "{:.0f} m2, {:.2f}k$, {:.2f}k/m2, {} {}".format(size, price, price_m2/1000, url[12:19], year)
    folium.CircleMarker(location=(lt_ln).tolist(), radius=9, weight=4, popup=po_str,  #+np.array([.001,.001])
                        fill=True, fill_color=colors.to_hex(scalarMap_price_m2.to_rgba(price_m2)), color=colors.to_hex(scalarMap_price.to_rgba(price)),
                        fill_opacity=0.7, opacity=0.7).add_to(d_ys[str(year)])

for add_k  in paths.keys():
    path = paths[add_k]
    duration = durations[add_k]
    dist = distances[add_k]/1000
    po_pa_str = "{:.0f} min, {:.2f}km".format(duration, dist)  #  price_m2/1000, url[12:19], year  , {:.2f}/m2, {} {}
    folium.PolyLine(path, color=colors.to_hex(scalarMap_duration.to_rgba(duration)), popup=po_pa_str, weight=4, opacity=0.6).add_to(sgmap)

for d_ys_k in delivers:
    d_ys_k = str(d_ys_k)
    sgmap.add_child(d_ys[d_ys_k])
# sgmap.add_child(fpm2);  sgmap.add_child(fpTm2); sgmap.add_child(fp);
sgmap.add_child(folium.LayerControl())
auto_open("sgmap.html", sgmap)




df['Address ']
