import pandas as pd
import numpy as np
import json
import os

def convert_coordinates_to_negative(COORD):
    """
    Return negative coordinates provided any coordinates.
    For example, 'X,47,95,,19,55' will be converted to 'X,-47.95,-19.55'

    Parameters
    ----------
    COORD : string
        Any coordinates.

    Returns
    -------
    str
        The negative coordinates.

    """
    # Divide a string em partes
    PARTS = COORD.split(',')
    # Pega a latitude e longitude
    LATITUDE  = '-' + PARTS[1] + '.' + PARTS[2]
    LONGITUDE = '-' + PARTS[4] + '.' + PARTS[5]
    # Converte para negativos e retorna no formato original
    return f'X,{float(LATITUDE) },{float(LONGITUDE) }'

def define_cities_of_interest(json_source_file_name):
    """
    Return the cities of interest, given a file that has this information.

    Parameters
    ----------
    json_source_file_name : string
        The filename of the JSON file where the city names are stored.
        The JSON file must be structured as a dictionary where the keys are the central cities, and the values are lists of bordering cities.

    Returns
    -------
    df_cities_of_interest : dataframe
        A dataframe, in long format, that lists all central cities on the first column and their corresponding bordering cities on the second column.

    """
    with open(json_source_file_name, 'r') as json_source_file:
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

def find_Minas_Gerais_cities_coordinates(df_of_cities_to_search_for, cities_coordinates_spreadsheet_name):
    # Creates the dataframe by reading the spreadsheet:
    df_cities_coordinates = pd.read_excel(cities_coordinates_spreadsheet_name, index_col='GEOCODIGO_MUNICIPIO')
    # Narrow down the dataframe by keeping only Minas Gerais cities:
    df_cities_coordinates = df_cities_coordinates[ df_cities_coordinates.index.astype(str).str.startswith('31') ].set_index('NOME_MUNICIPIO')
    
    # Narrow down the dataframe by keeping only the sought Minas Gerais cities:
    set_of_all_sought_city_names = set( pd.concat( [ df_cities_of_interest['Central City'], df_cities_of_interest['Bordering City'] ] ) )
    df_cities_coordinates = df_cities_coordinates[df_cities_coordinates.index.isin(set_of_all_sought_city_names)]
    
    return df_cities_coordinates

def find_nearest_measurement_locations(df_cities_coordinates, df_SPEI):
    """
    Return geographical coordinates of the nearest measurement location, given city coordinates.

    Parameters
    ----------
    df_cities_coordinates : dataframe
        A dataframe composed of just the sought city names and their corresponding coordinates.
        The city names are index labels (NOME_MUNICIPIO) and the LONGITUDE and LATITUDE are the column names.
    df_SPEI : dataframe
        A dataframe composed of SPEI measurements filed under geographical coordinates as column names.

    Returns
    -------
    df_nearest_measurement_locations : dataframe
        A dataframe composed of just the sought city names and the coordinates of the corresponding nearest measurement location.
        The city names are index labels (NOME_MUNICIPIO) and the LONGITUDE and LATITUDE are the column names.

    """
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

    df_city['Data'] = DF_DATAS['Data'].reset_index(drop=True)
    
    # Renomear a primeira coluna para 'Series 1'
    df_city = df_city.rename(columns={df_city.columns[0]: 'Series 1'})
    
    # Converter a primeira coluna para float e a segunda para datetime
    # Converter a primeira coluna para float (substituir vírgulas por pontos)
    df_city['Series 1'] = df_city['Series 1'].str.replace(',', '.').astype(float)
    df_city['Data'] = pd.to_datetime(df_city['Data'], errors='coerce')

    return df_city


def write_city_timeseries_on_xlsxs(df_cities_of_interest, df_nearest_measurement_locations):
    for central_city_name in df_cities_of_interest['Central City'].unique():
        # Create one subdirectory for each central city, inside the 'Data' directory:
        os.makedirs('./Data/' + central_city_name)
        
        # Creates the xlsx of the central city:
        df_central_city = make_city_timeseries_dataframe(central_city_name, df_nearest_measurement_locations)
        df_central_city.to_excel(f'./Data/{central_city_name}/{central_city_name}.xlsx', index=False)
        
        # Gets a list of all bordering cities names, each time for a different central city:
        bordering_cities_names = df_cities_of_interest[ df_cities_of_interest['Central City'] == central_city_name ]['Bordering City']
        
        # For every bordering city, extracts the nearest column of df_SPEI and write a xlsx file in the correct subdirectory:
        for bordering_city_name in bordering_cities_names:
            # Creates the xlsx of the bordering city:
            df_bordering_city = make_city_timeseries_dataframe(bordering_city_name, df_nearest_measurement_locations)
            df_bordering_city.to_excel(f'./Data/{central_city_name}/{bordering_city_name}.xlsx', index=False)

# Abrir o arquivo Excel com a segunda coluna a ser concatenada
DF_DATAS = pd.read_excel('São João da Ponte_revisado_final.xlsx')
        
# Create a dataframe to hold all SPEI measurements together with their geographical coordinates:
df_SPEI = pd.read_csv("speiAll_final.csv",delimiter=';').iloc[11:].reset_index(drop=True)
df_SPEI.columns = [convert_coordinates_to_negative(col) for col in df_SPEI.columns]

df_cities_of_interest = define_cities_of_interest('cidades.json')

df_cities_coordinates = find_Minas_Gerais_cities_coordinates(df_cities_of_interest, 'CoordenadasMunicipios.xlsx')

df_nearest_measurement_locations = find_nearest_measurement_locations(df_cities_coordinates, df_SPEI)

write_city_timeseries_on_xlsxs(df_cities_of_interest, df_nearest_measurement_locations)
