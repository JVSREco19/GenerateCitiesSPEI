import pandas as pd
import numpy as np

def find_cities_coordinates():
    CIDADES_A_PROCURAR = [
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
    
    DF_COORDS = pd.read_excel('CoordenadasMunicipios.xlsx')
    
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
        distance = coordinates_euclidean_distance((lat_municipio, lon_municipio), (lat_col, lon_col))
        
        # Encontrar a coluna com a menor distância
        if distance < min_distance:
            min_distance = distance
            closest_col_name = col

    return closest_col_name

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
    result_dict[municipio] = find_nearest_gauging_station(coords, dfSpei)

# Cria uma planilha para cada cidade com base na coluna mais próxima
for cidade, coluna_proxima in result_dict.items():
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
