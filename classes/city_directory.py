import pandas as pd

class CityDirectory:
    def __init__(self, file_name):
        self.df = pd.read_excel(file_name, index_col='GEOCODIGO_MUNICIPIO')
    
    def narrow_down_by_state_geocode(self, state_code):
        self.df = self.df[self.df.index.astype(str).str.startswith(str(state_code) )].set_index('NOME_MUNICIPIO')
    
    def narrow_down_by_city_set(self, city_set):
        self.df = self.df[self.df.index.isin(city_set)]
    
    def get_coords_by_city_name(self, city_name):
        return self.df.loc[city_name]