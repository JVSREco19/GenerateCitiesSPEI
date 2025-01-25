import pandas as pd
import numpy as np
import os

from city_directory      import CityDirectory
from spei_directory      import SPEIDirectory
from chosen_cities_index import ChosenCitiesIndex

def find_nearest_measurement_locations(df_cities_coordinates, df_speis):
    # Duplicates only the structure of the inputted dataframe, leaving the data out:
    df_nearest_measurement_locations = pd.DataFrame().reindex_like(df_cities_coordinates)
    
    for city in df_nearest_measurement_locations.index:
        CITY_LONGITUDE = df_cities_coordinates.loc[city, 'LONGITUDE']
        CITY_LATITUDE  = df_cities_coordinates.loc[city, 'LATITUDE' ]
        
        min_distance    = float('inf')
        closest_col_lon = None
        closest_col_lat = None
        
        # For every measurement location indicated in df_SPEI, does the following:
        for column in df_speis.columns:
            # Coordinates as 'X,lon,lat':
            (COL_LONGITUDE, COL_LATITUDE) = map(float, column.lstrip("X,").split(',') )
            
            # Calculate the distance between the city and the measurement location (col)
            coordinates_euclidean_distance = lambda COORD1, COORD2 : np.sqrt((COORD1[0] - COORD2[0])**2 + (COORD1[1] - COORD2[1])**2)
            distance = coordinates_euclidean_distance((CITY_LATITUDE, CITY_LONGITUDE), (COL_LATITUDE, COL_LONGITUDE))
            
            # Find the geographically nearest measurement location:
            if distance < min_distance:
                min_distance    = distance
                closest_col_lon = COL_LONGITUDE
                closest_col_lat = COL_LATITUDE
            
        df_nearest_measurement_locations.loc[city, 'LONGITUDE'] = closest_col_lon
        df_nearest_measurement_locations.loc[city, 'LATITUDE' ] = closest_col_lat
    
    return df_nearest_measurement_locations

def write_city_timeseries_on_xlsxs(speis, df_cities_of_interest, df_nearest_measurement_locations):
    for central_city_name in df_cities_of_interest['Central City'].unique():
        # Create one subdirectory for each central city, inside the 'Data' directory:
        os.makedirs('./Data/' + central_city_name)
        
        # Creates the xlsx of the central city:
        df_central_city = speis.make_city_timeseries_df(central_city_name, df_nearest_measurement_locations)
        df_central_city.to_excel(f'./Data/{central_city_name}/{central_city_name}.xlsx', index=True)
        
        # Gets a list of all bordering cities names, each time for a different central city:
        bordering_cities_names = df_cities_of_interest[ df_cities_of_interest['Central City'] == central_city_name ]['Bordering City']
        
        # For every bordering city, extracts the nearest column of df_SPEI and write a xlsx file in the correct subdirectory:
        for bordering_city_name in bordering_cities_names:
            # Creates the xlsx of the bordering city:
            df_bordering_city = speis.make_city_timeseries_df(bordering_city_name, df_nearest_measurement_locations)
            df_bordering_city.to_excel(f'./Data/{central_city_name}/{bordering_city_name}.xlsx', index=True)
       

# Creating objects:
speis         = SPEIDirectory     ('speiAll_final.csv')
cities_all    = CityDirectory     ('CoordenadasMunicipios.xlsx')
cities_chosen = ChosenCitiesIndex ('cidades.json')

# Manipulating object 'cities_all'   :
df_cities_coordinates = cities_all.narrow_down_by_state_geocode(31)
df_cities_coordinates = cities_all.narrow_down_by_city_set(cities_chosen.get_chosen_cities_set())

df_nearest_measurement_locations = find_nearest_measurement_locations(df_cities_coordinates, speis.df)

write_city_timeseries_on_xlsxs(speis, cities_chosen.df, df_nearest_measurement_locations)