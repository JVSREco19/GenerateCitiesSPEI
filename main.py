import pandas as pd
import numpy as np

import os
os.chdir('E:\POSCOMP\Python\GenerateCitiesSPEI-local-paráfrase')

CIDADES_PETERSON = [
    'Espinosa',
    'Rio Pardo de Minas',
    'São Francisco',
    'São João da Ponte',
    'Lassance'
]

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

def find_Minas_Gerais_cities_coordinates(list_of_cities_to_search_for, cities_coordinates_spreadsheet_name):
    """
    Return geographical coordinates given a list of city names.

    Parameters
    ----------
    list_of_cities_to_search_for : list
        The list of cities to search for.
    cities_coordinates_spreadsheet_name : string
        The name of the spreadsheet containing all Brazillian city coordinates.

    Returns
    -------
    df_cities_coordinates : dataframe
        A dataframe composed of just the sought city names and their corresponding coordinates.
        The city names are index labels (NOME_MUNICIPIO) and the LONGITUDE and LATITUDE are the column names.

    """
    # Uppercase all city names:
    list_of_cities_to_search_for = [city.upper() for city in list_of_cities_to_search_for]
    # Creates the dataframe by reading the spreadsheet:
    df_cities_coordinates = pd.read_excel(cities_coordinates_spreadsheet_name, index_col='GEOCODIGO_MUNICIPIO')
    # Narrow down the dataframe by keeping only Minas Gerais cities:
    df_cities_coordinates = df_cities_coordinates[ df_cities_coordinates.index.astype(str).str.startswith('31') ].set_index('NOME_MUNICIPIO')
    # Narrow down the dataframe by keeping only the sought Minas Gerais cities:
    df_cities_coordinates = df_cities_coordinates[df_cities_coordinates.index.isin(list_of_cities_to_search_for)]
    
    return df_cities_coordinates

def find_nearest_gauging_station(coords, df_SPEI):
    """
    Return the coordinates for the nearest gauging station, given the coordinates of the city of interest.

    Parameters
    ----------
    coords : the coordinates of the city of interest.
    dfSpei : the dataframe in which to do the search. It has the coordinates of every gauging station as column names.

    Returns
    -------
    closest_col : the coordinates of the gauging station geographically nearest to the city of interest.

    """
    
    lat_municipio = coords['latitude']
    lon_municipio = coords['longitude']
    
    # Converter colunas para coordenadas
    min_distance = float('inf')
    closest_col_name = None

    for col in df_SPEI.columns:
        # Supondo o formato das coordenadas como 'X,lat,lon'
        parts = col.split(',')
        lon_col = float(parts[1])
        lat_col = float(parts[2])
        # Calcular a distância
        coordinates_euclidean_distance = lambda COORD1, COORD2 : np.sqrt((COORD1[0] - COORD2[0])**2 + (COORD1[1] - COORD2[1])**2)
        distance = coordinates_euclidean_distance((lat_municipio, lon_municipio), (lat_col, lon_col))
        
        # Encontrar a coluna com a menor distância
        if distance < min_distance:
            min_distance = distance
            closest_col_name = col

    return closest_col_name

def save_city_SPEI_on_xlsx(cidade, coluna_proxima, dfSpei, DF_DATAS):
    """
    Creates a 2-column xlsx file for a city, with the first column ('Series 1') being the SPEI values, and the second column ('Data') being the corresponding dates of measurement of the SPEI.

    Parameters
    ----------
    cidade : string
        The city name.
    coluna_proxima : dictionary
        The city's longitude and latitude.
    dfSpei : dataframe
        The dataframe from which the SPEI values will be extracted.
    DF_DATAS : dataframe
        The dataframe from which the dates of measurement will be extracted.

    Returns
    -------
    bool
        True if the file is created successfully.
        False if the city's column is not found.

    """
    if coluna_proxima in dfSpei.columns:
        df_city = dfSpei[[coluna_proxima]].copy()
        
        # Adicionar a coluna 'Data' do DataFrame revisado
        df_city['Data'] = DF_DATAS['Data'].reset_index(drop=True)
        
        # Renomear a primeira coluna para 'Series 1'
        df_city = df_city.rename(columns={df_city.columns[0]: 'Series 1'})
        
        # Converter a primeira coluna para float e a segunda para datetime
        # Converter a primeira coluna para float (substituir vírgulas por pontos)
        df_city['Series 1'] = df_city['Series 1'].str.replace(',', '.').astype(float)
        df_city['Data'] = pd.to_datetime(df_city['Data'], errors='coerce')
        
        # Salva em um arquivo Excel
        df_city.to_excel(f'./Data/{cidade}.xlsx', index=False)
        print(f'Salvo {cidade}.xlsx')
        return True
    else:
        print(f'Coluna para {cidade} não encontrada.')
        return False


# Abrir o arquivo Excel com a segunda coluna a ser concatenada
DF_DATAS = pd.read_excel('São João da Ponte_revisado_final.xlsx')

# Create a dataframe to hold all SPEI measurements together with their geographical coordinates:
df_SPEI = pd.read_csv("speiAll_final.csv",delimiter=';').iloc[11:].reset_index(drop=True)
print(df_SPEI)
df_SPEI.columns = [convert_coordinates_to_negative(col) for col in df_SPEI.columns]

# Create a dataframe to hold just the Minas Gerais cities of interest:
df_cities_coordinates = find_Minas_Gerais_cities_coordinates(CIDADES_PETERSON, 'CoordenadasMunicipios.xlsx')
print(df_cities_coordinates)

# Create a dictionary to hold the coordinates of the nearest gauging station in relation to the sought city:
nearest_coordinates_dict = {}   
for city in df_cities_coordinates.index:
    nearest_coordinates_dict[city] = find_nearest_gauging_station({'longitude': df_cities_coordinates.loc[city, 'LONGITUDE'], 'latitude': df_cities_coordinates.loc[city, 'LATITUDE']}, df_SPEI)
    
for cidade, coluna_proxima in nearest_coordinates_dict.items():
    save_city_SPEI_on_xlsx(cidade, coluna_proxima, df_SPEI, DF_DATAS)
