import pandas as pd
import json

class ChosenCitiesIndex:
    def __init__(self, file_name):
        with open(file_name, 'r',encoding='utf-8') as json_source_file:
            DICT_OF_CITIES_TO_SEARCH_FOR = json.load(json_source_file)
            list_of_city_tuples = []
            for central_city, list_of_bordering_cities in DICT_OF_CITIES_TO_SEARCH_FOR.items():
                for bordering_city in list_of_bordering_cities:
                    list_of_city_tuples.append( (central_city, bordering_city) )
                   
            self.df = pd.DataFrame(list_of_city_tuples, columns=['Central City', 'Bordering City'])
            
            self._uppercase_all_city_names()
    
    def _uppercase_all_city_names(self):
        self.df['Central City'  ] = self.df['Central City'  ].str.upper()
        self.df['Bordering City'] = self.df['Bordering City'].str.upper()
    
    def get_chosen_cities_set(self):
        return set( pd.concat( [ self.df['Central City'], self.df['Bordering City'] ] ) )
    
    def get_chosen_central_cities_set(self):
        return set( self.df['Central City'].astype(str) )
    
    def get_bordering_cities_set(self, central_city_name):
        return set( self.df[ self.df['Central City'] == central_city_name ]['Bordering City'] )