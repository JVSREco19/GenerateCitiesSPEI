import pandas as pd
import numpy  as np

class NearestLocator:
    def __init__(self, cities_coordinates_directory):
        # Duplicates only the structure of the inputted dataframe, leaving the data out:
        self.df = pd.DataFrame().reindex_like(cities_coordinates_directory.df)
        
    def _calculate_euclidean_distance(self, COORDS_CITY, COORDS_COL):
        # Calculate the distance between the city and the measurement location (col)
        coords_euclidean_distance = lambda COORD1, COORD2 : np.sqrt((COORD1[0] - COORD2[0])**2 + (COORD1[1] - COORD2[1])**2)
        return coords_euclidean_distance((COORDS_CITY['LATITUDE'], COORDS_CITY['LONGITUDE']), (COORDS_COL['LATITUDE'], COORDS_COL['LONGITUDE']))
    
    def _get_city_coords(self, CITY_NAME, cities_coordinates_directory):
        return {'LONGITUDE' : cities_coordinates_directory.get_coords_by_city_name(CITY_NAME).LONGITUDE, 
                'LATITUDE'  : cities_coordinates_directory.get_coords_by_city_name(CITY_NAME).LATITUDE}
    
    def _set_city_coords(self, CITY_NAME, COORDS_DICT):
        self.df.loc[CITY_NAME] = COORDS_DICT
    
    def _find_nearest_col(self, COORDS_CITY, speis):
        # For a given city, runs over all cols of speis and finds the nearest one.
        min_distance       = float('inf')
        
        # For every measurement location (col) indicated in df_SPEI, does the following:
        for column in speis.df.columns:
            COORDS_COL = {}
            (COORDS_COL['LONGITUDE'], COORDS_COL['LATITUDE']) = speis.get_col_coords(column)
            
            distance = self._calculate_euclidean_distance(COORDS_CITY, COORDS_COL)
            
            # Find the geographically nearest measurement location:
            if distance < min_distance:
                min_distance       = distance
                coords_closest_col = COORDS_COL.copy()
                
        return coords_closest_col
    
    def find_nearest_measurement_locations(self, cities_coordinates_directory, speis):
        for city in self.df.index:
            COORDS_CITY        = self._get_city_coords (city, cities_coordinates_directory)
            coords_closest_col = self._find_nearest_col(COORDS_CITY, speis)
            self._set_city_coords(city, coords_closest_col)