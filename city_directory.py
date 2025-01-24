import pandas as pd

class CityDirectory:
    def __init__(self, spreadsheet_name):
        self.data = pd.read_excel(spreadsheet_name, index_col='GEOCODIGO_MUNICIPIO')
    
    def narrow_down_by_state_geocode(self, state_code):
        self.data = self.data[self.data.index.astype(str).str.startswith(str(state_code) )].set_index('NOME_MUNICIPIO')
        return self.data
    
    def narrow_down_by_city_set(self, city_set):
        self.data = self.data[self.data.index.isin(city_set)]
        return self.data
    
    def get_coords_by_city_name(self, city_name):
        return self.data.loc[city_name]