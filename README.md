# GenerateCitiesSPEI
Este projeto realiza a análise e processamento de dados climáticos e coordenadas geográficas de municípios. Ele inclui  a integração de dados adicionais de um arquivo revisado e a exportação dos resultados em arquivos Excel individuais para cada município. 

## Entradas
1. `CoordenadasMunicipios.xlsx` → dfCoords
2. `speiAll_final.csv` → dfSpei
3. `São João da Ponte_revisado_final.xlsx` → df_revisado

## Saídas
Uma planilha `.xlsx` para cada cidade procurada (listada em `cidades_procuradas`), no diretório `Data`.

## Descrição do algoritmo
O algoritmo é como se segue:

### ATO 1
Pré-processamento de `CoordenadasMunicipios.xlsx`
1. recebe uma `list` de cidades a pesquisar (`cidades_procuradas`);
2. lê uma planilha eletrônica (`CoordenadasMunicipios.xlsx`), gerando um `DataFrame` (`dfCoords`), de correlação entre nomes de municípios e suas coordenadas geográficas;
3. percorre todas as linhas de `dfCoords`, gerando um `dict` geral correspondente (`municipios_dict`), no qual as chaves são os nomes dos municípios e os valores são latitudes e longitudes;
4. a partir de `cidades_procuradas`, busca as longitudes e latitudes correspondentes em `municipios_dict`, e copia essas informações para um novo `dict`, específico (`resultados`);
5. imprime `resultados`.

### ATO 2
Pré-processamento de `speiAll_final.csv`
1. lê um arquivo `CSV` (`speiAll_final.csv`), gerando um `DataFrame` (`dfSpei`);
2. remove as 11 primeiras linhas de `nan` do `dfSpei`;
3. imprime `dfSpei`;
4. define uma função para converter as coordenadas para valores negativos (`convert_to_negative`);
5. aplica `convert_to_negative` a todos os rótulos das colunas de `dfSpei`, que é onde as coordenadas se localizam.

### ATO 3
Busca dos municípios mais próximos daqueles procurados
1. define uma função para calcular a distância Euclideana entre duas coordenadas (`euclidean_distance`);
2. cria um segundo dicionário de resultados, vazio (`result_dict`);
3. para cada município (chave) presente em `resultados` (ATO 1), extrai latitude e longitude (valores). Então, para cada coluna de `dfSpei` (ATO 2), calcula a distância Euclidena mediante `euclidean_distance` e encontra a coluna mais próxima geograficamente. Esta então é registrada no `result_dict` (ATO 3) com a chave sendo o município no qual a busca se baseou.

### ATO 4
Gera planilhas eletrônicas individuais para cada cidade, contendo a série histórica do índice de seca SPEI
1. lê uma planilha eletrônica (`São João da Ponte_revisado_final.xlsx`), gerando um `DataFrame` (`df_revisado`);
2. para cada par chave-valor de `result_dict` (ATO 3), ou seja, para cada par `cidade`-`coluna_proxima`, confere se a `coluna_proxima` está presente em `dfSpei` (ATO 2), oferecendo um erro caso `FALSE`. Por outro lado, caso `TRUE`, cria um `DataFrame` `df_city` que recebe de `dfSpei` (ATO 2): uma 1ª coluna `Series 1` com a série histórica do índice de seca SPEI, e uma 2ª coluna com o `datetime` correspondente. Salva então uma planilha eletrônica para cada cidade com esses dados.
