import pandas as pd
import numpy as np


# Lista de cidades para procurar
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

# Abrir o arquivo Excel
DF_COORDS = pd.read_excel('CoordenadasMunicipios.xlsx')

# Abrir o arquivo Excel com a segunda coluna a ser concatenada
DF_DATAS = pd.read_excel('São João da Ponte_revisado_final.xlsx')

# Criar um dicionário com os nomes dos municípios como chaves e suas coordenadas como valores
MUNICIPIOS_DICT = {
    row['NOME_MUNICIPIO']: {
        'longitude': round(row['LONGITUDE'], 2), 
        'latitude': round(row['LATITUDE'], 2)
    }
    for _, row in DF_COORDS.iterrows()
}

# Encontrar as coordenadas das cidades procuradas e deixar os nomes em caixa alta
RESULTADOS = {cidade.upper(): MUNICIPIOS_DICT.get(cidade.upper(), 'Cidade não encontrada') for cidade in CIDADES_A_PROCURAR}

# Exibir os resultados
for cidade, coords in RESULTADOS.items():
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

# Aplicar a função em todas as colunas
dfSpei.columns = [convert_to_negative(col) for col in dfSpei.columns]

# Função para calcular a distância Euclidiana entre duas coordenadas
def euclidean_distance(coord1, coord2):
    return np.sqrt((coord1[0] - coord2[0])**2 + (coord1[1] - coord2[1])**2)

# Armazenar os resultados
result_dict = {}

# Iterar sobre cada município e encontrar a coluna mais próxima
for municipio, coords in RESULTADOS.items():
    lat_municipio = coords['latitude']
    lon_municipio = coords['longitude']
    
    # Converter colunas para coordenadas
    min_distance = float('inf')
    closest_col = None
    
    for col in dfSpei.columns:
        # Supondo o formato das coordenadas como 'X,lon,lat'
        (lon_col, lat_col) = col.lstrip("X,").split(',')
        # Calcular a distância
        distance = euclidean_distance((lat_municipio, lon_municipio), (lat_col, lon_col))
        
        # Encontrar a coluna com a menor distância
        if distance < min_distance:
            min_distance = distance
            closest_col = col
    
    # Adicionar o resultado ao dicionário
    result_dict[municipio] = closest_col

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
