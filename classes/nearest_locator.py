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
    
    def _get_col_coords(self, speis, col_header):
        LONGITUDE, LATITUDE = speis.get_col_coords(col_header)
        
        return {'LONGITUDE' : LONGITUDE,
                'LATITUDE'  : LATITUDE}
    
    def _set_city_coords(self, CITY_NAME, COORDS_DICT):
        self.df.loc[CITY_NAME] = COORDS_DICT
    
    def _calculate_col_distances(self, COORDS_CITY, speis):
        distances_dict = {}
        for col_header in speis.df.columns:
            COORDS_COL = self._get_col_coords(speis, col_header)
            
            distances_dict[col_header] = self._calculate_euclidean_distance(COORDS_CITY, COORDS_COL)
        
        return distances_dict
    
    def _find_nearest_col(self, COORDS_CITY, speis):
        distances_dict     = self._calculate_col_distances(COORDS_CITY, speis)            
        coords_closest_col = self._find_min_distance(distances_dict, speis)
    
        return coords_closest_col
        
    def _find_min_distance(self, distances_dict, speis):
        min_distance       = float('inf')
        coords_closest_col = None
        
        for col_header, distance in distances_dict.items():
            if distance < min_distance:
                min_distance       = distance
                COORDS_COL         = self._get_col_coords(speis, col_header)
                coords_closest_col = COORDS_COL.copy()
                
        return coords_closest_col
    
    def find_nearest_measurement_locations(self, cities_coordinates_directory, speis):
        for city in self.df.index:
            COORDS_CITY        = self._get_city_coords (city, cities_coordinates_directory)
            coords_closest_col = self._find_nearest_col(COORDS_CITY, speis)
            self._set_city_coords(city, coords_closest_col)