import pandas as pd
import numpy as np

# Lista de cidades para procurar
cidades_a_procurar = [
    'Capitão Enéas',
    'Ibiracatu',
    'Janaúba',
    'Japonvar',
    'Lontra',
    'Montes Claros',
    'Patis',
    'Varzelândia',
    'Verdelândia',
    'São João da Ponte'
]
cidades_a_procurar = [cidade.upper() for cidade in cidades_a_procurar]

# Abrir o arquivo Excel com a segunda coluna a ser concatenada
DF_DATAS = pd.read_excel('São João da Ponte_revisado_final.xlsx')

# Filtrar para apenas os municipios de Minas Gerais (codigos iniciados com 31)
# Minas Gerais tem 853 municipios.
city_coordinates = pd.read_excel('CoordenadasMunicipios.xlsx', index_col='GEOCODIGO_MUNICIPIO')
city_coordinates = city_coordinates[ city_coordinates.index.astype(str).str.startswith('31') ].set_index('NOME_MUNICIPIO')

# Criar um dicionário com os nomes dos municípios como chaves e suas coordenadas como valores
# Encontrar as coordenadas das cidades procuradas e deixar os nomes em caixa alta
found_cities = {}
for sought_city in cidades_a_procurar:
    found_cities[sought_city] = {
        "longitude" : float(city_coordinates.loc[sought_city]['LONGITUDE']),
        "latitude"  : float(city_coordinates.loc[sought_city]['LATITUDE'])
    }

# Exibir os resultados
for cidade, coords in found_cities.items():
    print(f'{cidade}: {coords}')
    
# Abrir o arquivo CSV
dfSpei = pd.read_csv("speiAll_final.csv",delimiter=';')

# Remover as primeiras 11 linhas
dfSpei = dfSpei.iloc[11:].reset_index(drop=True)

print(dfSpei)

# Função para converter as coordenadas em valores negativos
def convert_to_negative(coord):
    # Divide a string em partes
    parts = coord.split(',')
    # Pega a latitude e longitude
    latitude = '-'+parts[1] + '.' + parts[2]
    longitude = '-'+parts[4] + '.' + parts[5]
    # Converte para negativos e retorna no formato original
    return f'X,{float(latitude) },{float(longitude) }'

# Função para calcular a distância Euclidiana entre duas coordenadas
def euclidean_distance(coord1, coord2):
    return np.sqrt((coord1[0] - coord2[0])**2 + (coord1[1] - coord2[1])**2)

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
    DF_COORDS = pd.read_excel(DF_COORDS, usecols=['NOME_MUNICIPIO', 'LONGITUDE', 'LATITUDE'])
    
    MUNICIPIOS_DICT = {
        row['NOME_MUNICIPIO']: {
            'longitude': round(row['LONGITUDE'], 2), 
            'latitude': round(row['LATITUDE'], 2)
        }
        for _, row in DF_COORDS.iterrows()
    }
   
    # Encontrar as coordenadas das cidades procuradas e deixar os nomes em caixa alta
    CITIES_COORDINATES_DICT = {cidade.upper(): MUNICIPIOS_DICT.get(cidade.upper(), 'Cidade não encontrada') for cidade in CIDADES_A_PROCURAR}
    
    # Exibir os resultados
    for cidade, coords in CITIES_COORDINATES_DICT.items():
        print(f'{cidade}: {coords}')    

    return CITIES_COORDINATES_DICT

# Exibir os resultados
for cidade, coords in RESULTADOS.items():
    print(f'{cidade}: {coords}')
     
# Abrir o arquivo CSV, remover as 11 primeiras linhas, e converter todos os nomes de colunas para números negativos
dfSpei = pd.read_csv("speiAll_final.csv",delimiter=';').iloc[11:].reset_index(drop=True)
print(dfSpei)
dfSpei.columns = [convert_coordinates_to_negative(col) for col in dfSpei.columns]

# Armazenar os resultados
result_dict = {}

def find_nearest_city(municipio, coords, dfSpei):
    lat_municipio = coords['latitude']
    lon_municipio = coords['longitude']

    # Converter colunas para coordenadas
    min_distance = float('inf')
    closest_col = None

    for col in dfSpei.columns:
        # Supondo o formato das coordenadas como 'X,lon,lat'
        (lon_col, lat_col) = map(float, col.lstrip("X,").split(',') )
        # Calcular a distância
        coordinates_euclidean_distance = lambda COORD1, COORD2 : np.sqrt((COORD1[0] - COORD2[0])**2 + (COORD1[1] - COORD2[1])**2)
        distance = coordinates_euclidean_distance((lat_municipio, lon_municipio), (lat_col, lon_col))
        
        # Encontrar a coluna com a menor distância
        if distance < min_distance:
            min_distance = distance
            closest_col = col
    return closest_col

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
    else:
        print(f'Coluna para {cidade} não encontrada.')
  
def convert_coordinates_to_negative(COORD):
    # Divide a string em partes
    PARTS = COORD.split(',')
    # Pega a latitude e longitude
    LATITUDE  = '-' + PARTS[1] + '.' + PARTS[2]
    LONGITUDE = '-' + PARTS[4] + '.' + PARTS[5]
    # Converte para negativos e retorna no formato original
    return f'X,{float(LATITUDE) },{float(LONGITUDE) }'

def coordinates_euclidean_distance(COORD1, COORD2):
    return np.sqrt((COORD1[0] - COORD2[0])**2 + (COORD1[1] - COORD2[1])**2)


# Abrir o arquivo Excel com a segunda coluna a ser concatenada
DF_DATAS = pd.read_excel('São João da Ponte_revisado_final.xlsx')
    
# Abrir o arquivo CSV
dfSpei = pd.read_csv("speiAll_final.csv",delimiter=';')

# Remover as primeiras 11 linhas
dfSpei = dfSpei.iloc[11:].reset_index(drop=True)
print(dfSpei)

# Aplicar função em todas as colunas
dfSpei.columns = [convert_coordinates_to_negative(col) for col in dfSpei.columns]

result_dict = {}   
for municipio, coords in find_cities_coordinates().items():
    result_dict[municipio] = find_nearest_city(municipio, coords, dfSpei)

for cidade, coluna_proxima in result_dict.items():
    save_city_SPEI_on_xlsx(cidade, coluna_proxima, dfSpei, DF_DATAS)
