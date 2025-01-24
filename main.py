import pandas as pd
import numpy as np
import json
import os

from city_directory import CityDirectory

def define_cities_of_interest(json_source_file_name):
    with open(json_source_file_name, 'r',encoding='utf-8') as json_source_file:
        DICT_OF_CITIES_TO_SEARCH_FOR = json.load(json_source_file)
        list_of_city_tuples = []
        for central_city, list_of_bordering_cities in DICT_OF_CITIES_TO_SEARCH_FOR.items():
            for bordering_city in list_of_bordering_cities:
                list_of_city_tuples.append( (central_city, bordering_city) )
               
        df_cities_of_interest = pd.DataFrame(list_of_city_tuples, columns=['Central City', 'Bordering City'])
        
        # Convert all city names to uppercase
        df_cities_of_interest['Central City']   = df_cities_of_interest['Central City']  .str.upper()
        df_cities_of_interest['Bordering City'] = df_cities_of_interest['Bordering City'].str.upper()
    return df_cities_of_interest

def find_nearest_measurement_locations(df_cities_coordinates, df_SPEI):
    # Duplicates only the structure of the inputted dataframe, leaving the data out:
    df_nearest_measurement_locations = pd.DataFrame().reindex_like(df_cities_coordinates)
    
    for city in df_nearest_measurement_locations.index:
        CITY_LONGITUDE = df_cities_coordinates.loc[city, 'LONGITUDE']
        CITY_LATITUDE  = df_cities_coordinates.loc[city, 'LATITUDE' ]
        
        min_distance    = float('inf')
        closest_col_lon = None
        closest_col_lat = None
        
        # For every measurement location indicated in df_SPEI, does the following:
        for column in df_SPEI.columns:
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

def make_city_timeseries_dataframe(city_name, df_nearest_measurement_locations):
    # Rebuilding the coordinates from the dataframe columns:
    nearest_column = ','.join( [ 'X', str(df_nearest_measurement_locations.loc[city_name, 'LONGITUDE']), str(df_nearest_measurement_locations.loc[city_name, 'LATITUDE']) ] )
    
    df_city = df_SPEI[[nearest_column]].copy()
    
    # Renomear a primeira coluna para 'Series 1'
    df_city = df_city.rename(columns={df_city.columns[0]: 'Series 1'})
    
    # Converter Series para float e Dates para datetime
    df_city['Series 1'] = df_city['Series 1'].astype(float)
    df_city.index = pd.to_datetime(df_city.index, errors='coerce')

    return df_city

def write_city_timeseries_on_xlsxs(df_cities_of_interest, df_nearest_measurement_locations):
    for central_city_name in df_cities_of_interest['Central City'].unique():
        # Create one subdirectory for each central city, inside the 'Data' directory:
        os.makedirs('./Data/' + central_city_name)
        
        # Creates the xlsx of the central city:
        df_central_city = make_city_timeseries_dataframe(central_city_name, df_nearest_measurement_locations)
        df_central_city.to_excel(f'./Data/{central_city_name}/{central_city_name}.xlsx', index=True)
        
        # Gets a list of all bordering cities names, each time for a different central city:
        bordering_cities_names = df_cities_of_interest[ df_cities_of_interest['Central City'] == central_city_name ]['Bordering City']
        
        # For every bordering city, extracts the nearest column of df_SPEI and write a xlsx file in the correct subdirectory:
        for bordering_city_name in bordering_cities_names:
            # Creates the xlsx of the bordering city:
            df_bordering_city = make_city_timeseries_dataframe(bordering_city_name, df_nearest_measurement_locations)
            df_bordering_city.to_excel(f'./Data/{central_city_name}/{bordering_city_name}.xlsx', index=True)
       
# Create a dataframe to hold all SPEI measurements together with their geographical coordinates:
df_SPEI = pd.read_csv("speiAll_final.csv", delimiter=';', decimal=',', index_col='Dates')

df_cities_of_interest = define_cities_of_interest('cidades.json')
#print(df_cities_of_interest)
cities_of_interest_set = set( pd.concat( [ df_cities_of_interest['Central City'], df_cities_of_interest['Bordering City'] ] ) )

cities = CityDirectory('CoordenadasMunicipios.xlsx')
df_cities_coordinates = cities.narrow_down_by_state_geocode(31)
df_cities_coordinates = cities.narrow_down_by_city_set(cities_of_interest_set)

df_nearest_measurement_locations = find_nearest_measurement_locations(df_cities_coordinates, df_SPEI)

write_city_timeseries_on_xlsxs(df_cities_of_interest, df_nearest_measurement_locations)