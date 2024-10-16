import pandas as pd
import numpy as np

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

def save_cities_SPEI_on_xlsx(df_nearest_measurement_locations, df_SPEI, DF_DATAS):
    """
    Creates a 2-column xlsx file for the each city, with the first column ('Series 1') being the SPEI values, and the second column ('Data') being the corresponding dates of measurement of the SPEI.

    Parameters
    ----------
    df_nearest_measurement_locations : dataframe
        A dataframe composed of just the sought city names and the coordinates of the corresponding nearest measurement location.
        The city names are index labels (NOME_MUNICIPIO) and the LONGITUDE and LATITUDE are the column names.
    df_SPEI : dataframe
        The dataframe from which the SPEI values will be extracted.
    DF_DATAS : dataframe
        The dataframe from which the dates of measurement will be extracted.

    Returns
    -------
    None.

    """
    for city in df_nearest_measurement_locations.index:
        # Rebuilding the coordinates from the dataframe columns:
        nearest_column = ','.join( [ 'X', str(df_nearest_measurement_locations.loc[city, 'LONGITUDE']), str(df_nearest_measurement_locations.loc[city, 'LATITUDE']) ] )
    
        if nearest_column in df_SPEI.columns:
            df_city = df_SPEI[[nearest_column]].copy()
            
            # Adicionar a coluna 'Data' do DataFrame revisado
            df_city['Data'] = DF_DATAS['Data'].reset_index(drop=True)
            
            # Renomear a primeira coluna para 'Series 1'
            df_city = df_city.rename(columns={df_city.columns[0]: 'Series 1'})
            
            # Converter a primeira coluna para float e a segunda para datetime
            # Converter a primeira coluna para float (substituir vírgulas por pontos)
            df_city['Series 1'] = df_city['Series 1'].str.replace(',', '.').astype(float)
            df_city['Data'] = pd.to_datetime(df_city['Data'], errors='coerce')
            
            # Salva em um arquivo Excel
            df_city.to_excel(f'./Data/{city}.xlsx', index=False)
            print(f'Salvo {city}.xlsx')
        else:
            print(f'Coluna para {city} não encontrada.')


# Abrir o arquivo Excel com a segunda coluna a ser concatenada
DF_DATAS = pd.read_excel('São João da Ponte_revisado_final.xlsx')
        
# Create a dataframe to hold all SPEI measurements together with their geographical coordinates:
df_SPEI = pd.read_csv("speiAll_final.csv",delimiter=';').iloc[11:].reset_index(drop=True)
print(df_SPEI)
df_SPEI.columns = [convert_coordinates_to_negative(col) for col in df_SPEI.columns]

# Create a dataframe to hold just the Minas Gerais cities of interest:
df_cities_coordinates = find_Minas_Gerais_cities_coordinates(CIDADES_PETERSON, 'CoordenadasMunicipios.xlsx')
print(df_cities_coordinates)

# Create a dataframe to hold the coordinates of the nearest measurement locations for each city:
df_nearest_measurement_locations = find_nearest_measurement_locations(df_cities_coordinates, df_SPEI)
print(df_nearest_measurement_locations)

# Create xlsx files for each city, containing the corresponding SPEI series:
save_cities_SPEI_on_xlsx(df_nearest_measurement_locations, df_SPEI, DF_DATAS)
