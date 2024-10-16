import pandas as pd
import numpy as np

def find_cities_coordinates(cidades_a_procurar, DF_COORDS):
    """
    Return the cities' coordinates given their names.

    Parameters
    ----------
    CIDADES_A_PROCURAR : list of city names to search for on DF_COORDS.
    DF_COORDS          : a xlsx file that has info about all Minas Gerais cities -- name, longitude and latitude.

    Returns
    -------
    CITIES_COORDINATES_DICT : dictionary of cities and their corresponding coordinates (longitude and latitude).
                            The city names are the keys, and their coordinates are the values.
                            The coordinates, in turn, are a subdictionary composed of 'longitude' and 'latitude' as keys, and the numbers as values.

    """
    cidades_a_procurar = [cidade.upper() for cidade in cidades_a_procurar]
    
    # Filtrar para apenas os municipios de Minas Gerais (codigos iniciados com 31)
    # Minas Gerais tem 853 municipios.
    city_coordinates = pd.read_excel(DF_COORDS, index_col='GEOCODIGO_MUNICIPIO')
    city_coordinates = city_coordinates[ city_coordinates.index.astype(str).str.startswith('31') ].set_index('NOME_MUNICIPIO')
    
    found_cities = {}
    for sought_city in cidades_a_procurar:
        found_cities[sought_city] = {
            "longitude" : float(city_coordinates.loc[sought_city]['LONGITUDE']),
            "latitude"  : float(city_coordinates.loc[sought_city]['LATITUDE'])
        }
        
    # Exibir os resultados
    for cidade, coords in found_cities.items():
        print(f'{cidade}: {coords}')    
    print()
    
    return found_cities

def find_nearest_gauging_station(coords, dfSpei):
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

    for col in dfSpei.columns:
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
    
CIDADES_PETERSON = [
    'Espinosa',
    'Rio Pardo de Minas',
    'São Francisco',
    'São João da Ponte',
    'Lassance'
]

# Abrir o arquivo Excel com a segunda coluna a ser concatenada
DF_DATAS = pd.read_excel('São João da Ponte_revisado_final.xlsx')

# Abrir o arquivo CSV, remover as 11 primeiras linhas, e converter todos os nomes de colunas para números negativos
dfSpei = pd.read_csv("speiAll_final.csv",delimiter=';').iloc[11:].reset_index(drop=True)
print(dfSpei)
dfSpei.columns = [convert_coordinates_to_negative(col) for col in dfSpei.columns]

nearest_coordinates_dict = {}   
for municipio, coords in find_cities_coordinates(CIDADES_PETERSON, 'CoordenadasMunicipios.xlsx').items():
    nearest_coordinates_dict[municipio] = find_nearest_gauging_station(coords, dfSpei)

for cidade, coluna_proxima in nearest_coordinates_dict.items():
    save_city_SPEI_on_xlsx(cidade, coluna_proxima, dfSpei, DF_DATAS)
