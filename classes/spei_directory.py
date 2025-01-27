import pandas as pd

class SPEIDirectory:
    def __init__(self, file_name):
        self.df = pd.read_csv(file_name, delimiter=';', decimal=',', index_col='Dates')
    
    def get_col_coords(self, column):
        # Format: 'X,longitude,latitude'
        return map(float, column.lstrip('X,').split(',') )
    
    def _craft_nearest_col_header(self, city_name, df_nearest_measurement_locations):
        # Rebuilding the coordinates from the dataframe columns:            
        LONGITUDE = str(df_nearest_measurement_locations.loc[city_name, 'LONGITUDE'])
        LATITUDE  = str(df_nearest_measurement_locations.loc[city_name, 'LATITUDE' ])
        
        return f'X,{LONGITUDE},{LATITUDE}'
    
    def _convert_city_timeseries_df_types(self, df_city):
        # Converter Series para float e Dates para datetime
        df_city['Series 1'] = df_city['Series 1'].astype(float)
        df_city.index = pd.to_datetime(df_city.index, errors='coerce')
        
        return df_city
    
    def make_city_timeseries_df(self, city_name, df_nearest_measurement_locations):
        nearest_column_header = self._craft_nearest_col_header(city_name, df_nearest_measurement_locations)
        
        df_city = self.df[[nearest_column_header]].copy()
        df_city = df_city.rename(columns={df_city.columns[0]: 'Series 1'})
        df_city = self._convert_city_timeseries_df_types(df_city)
        
        return df_city