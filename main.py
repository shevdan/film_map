'''
Module that creates html page containing icons with 10 locations
where films were filmed in specific year, which are nearest to uesr location
'''

from math import radians, cos, sin, asin, sqrt
import folium
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderUnavailable
import file_process as fp


def user_interaction() -> tuple:
    '''
    Returns information from user about user location, preferred year
    and path to the folder of dataset
    '''
    year = int(input("Please enter a year you would like to have a map for:\n"))
    location = input("Please enter your location (format: lat, long):\n")
    path = input('Please, enter path to directory, where datset is stored wothout "/".\n\
Example: /Users/shevdan/Documents/Programming. :\n')
    location = location.rstrip().split(',')
    location = tuple(map(float, location))
    return location, year, path

def haversin(loc1, loc2):
    '''
    Function that implements haversin formula.
    haversin(dist/r) = haversin((lat2-lat1)/2)+ cos(lat2)*cos(lat1)*haversin((lon2-lon1)/2)
    haversin = sin^2(a/2)
    lon, lat in radians
    >>> haversin((49.841952, 24.0315921), (50.431759, 30.517023))
    466.6983447240942
    '''
    lat1, lon1 = loc1
    lat2, lon2 = loc2
    radius = 6371
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    hav_dist = sin((lat2 - lat1)/2)**2 + cos(lat2)*cos(lat1)*sin((lon2 - lon1)/2)**2
    distance = radius * 2 * asin(sqrt(hav_dist))
    return distance

def find_distance(df_films: pd.DataFrame, user_loc: tuple) -> pd.DataFrame:
    '''
    Operates over the DataFrame containing film names, year and location coordinates
    and adds another Series to DataFrame, containing distance from location to user
    '''
    lat = df_films['lat'].tolist()
    lon = df_films['lon'].tolist()
    dist = []
    lat_len = len(lat)
    for i in range(lat_len):
        dist.append(haversin((float(lat[i]), float(lon[i])), user_loc))
    df_films['dist'] = dist
    df_films.sort_values('dist')
    return df_films.sort_values('dist')


def info_about_user(user_loc: tuple) -> str:
    '''
    Returns information about location by its coordinates
    >>> info_about_user((50.431759, 30.517023))
    '57/3, Велика Васильківська вулиця, Печерський район, Київ, \
Київська міська громада, 03150, Україна'
    '''
    location = f'{user_loc[0]}, {user_loc[1]}'
    geolocator = Nominatim(user_agent="my_request")
    try:
        loc = geolocator.geocode(location)
    except GeocoderUnavailable:
        return 'Information about your location is unavailable'
    return loc.address

def create_map(df_films, user_loc: tuple):
    '''
    Creates html page containing map
    '''

    map_test = folium.Map(location=[*user_loc], zoom_start=10)
    df_films = df_films.head(10)
    lat = df_films['lat']
    lon = df_films['lon']
    dist = df_films['dist']
    film_name = df_films['name']
    year = df_films.iloc[1, 1]

    def color_creator(dist):
        if dist < 1000:
            return 'green'
        if dist < 5000:
            return 'yellow'
        return 'red'

    fg = folium.FeatureGroup(name='Films nearby')
    for lt,ln,dst,name  in zip(lat, lon, dist, film_name):
        fg.add_child(folium.CircleMarker(location=[lt, ln],
                                    radius= 10,
                                    popup=f'{name} was filmed here in {year}.\nDistance = {str(round(dst))} km',
                                    fill_color=color_creator(dst),
                                    color='red',
                                    fill_opacity=0.5))
    map_test.add_child(fg)

    fg = folium.FeatureGroup(name='User location')
    fg.add_child(folium.Marker(location=[user_loc[0], user_loc[1]],
                                    popup=f"Your location is {info_about_user(user_loc)}",
                                    icon= folium.Icon()))
    map_test.add_child(fg)

    map_test.save('film_map.html')

def main_func():
    '''
    Main function, that gets information from user, operates
    over the dataset and creates html page containing icons with 10 locations
    where films were filmed in specific year, which are nearest to uesr location
    '''
    user_location, year, path = user_interaction()
    film_data = fp.read_file(path + '/locations.list', year)
    fp.create_csv(film_data)
    df = pd.read_csv('locations.csv')
    df = find_distance(df, user_location)
    create_map(df, user_location)
    print('Finished. Please, have a look at film_map.html')



if __name__ == '__main__':
    main_func()
