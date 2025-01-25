import pandas as pd

class SPEIDirectory:
    def __init__(self, file_name):
        self.df = pd.read_csv(file_name, delimiter=';', decimal=',', index_col='Dates')

    def make_city_timeseries_df(self, city_name, df_nearest_measurement_locations):
        # Rebuilding the coordinates from the dataframe columns:
        nearest_column = ','.join( [ 'X', str(df_nearest_measurement_locations.loc[city_name, 'LONGITUDE']), str(df_nearest_measurement_locations.loc[city_name, 'LATITUDE']) ] )
        
        df_city = self.df[[nearest_column]].copy()
        
        # Renomear a primeira coluna para 'Series 1'
        df_city = df_city.rename(columns={df_city.columns[0]: 'Series 1'})
        
        # Converter Series para float e Dates para datetime
        df_city['Series 1'] = df_city['Series 1'].astype(float)
        df_city.index = pd.to_datetime(df_city.index, errors='coerce')
        
        return df_city