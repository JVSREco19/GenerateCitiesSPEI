import pandas as pd
import numpy  as np

class NearestLocator:
    def __init__(self, cities_coordinates_directory):
        # Duplicates only the structure of the inputted dataframe, leaving the data out:
        self.df = pd.DataFrame().reindex_like(cities_coordinates_directory.df)
    
    def find_nearest_measurement_locations(self, cities_coordinates_directory, speis):
        for city in self.df.index:
            CITY_LONGITUDE = cities_coordinates_directory.df.loc[city, 'LONGITUDE']
            CITY_LATITUDE  = cities_coordinates_directory.df.loc[city, 'LATITUDE' ]
            
            min_distance    = float('inf')
            closest_col_lon = None
            closest_col_lat = None
            
            # For every measurement location indicated in df_SPEI, does the following:
            for column in speis.df.columns:
                # Coordinates as 'X,lon,lat':
                (COL_LONGITUDE, COL_LATITUDE) = map(float, column.lstrip("X,").split(',') )
                
                # Calculate the distance between the city and the measurement location (col)
                coordinates_euclidean_distance = lambda COORD1, COORD2 : np.sqrt((COORD1[0] - COORD2[0])**2 + (COORD1[1] - COORD2[1])**2)
                distance = coordinates_euclidean_distance((CITY_LATITUDE, CITY_LONGITUDE), (COL_LATITUDE, COL_LONGITUDE))
                
                # Find the geographically nearest measurement location:
                if distance < min_distance:
                    min_distance    = distance
                    closest_col_lon = COL_LONGITUDE
                    closest_col_lat = COL_LATITUDE
                
            self.df.loc[city, 'LONGITUDE'] = closest_col_lon
            self.df.loc[city, 'LATITUDE' ] = closest_col_lat
        