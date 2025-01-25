import os

class FileWriter:
    def __init__(self, root_dir, cities_chosen, speis, df_nearest_measurement_locations):
        self.root_dir                         = root_dir
        self.df_cities_chosen                 = cities_chosen.df
        self.speis                            = speis
        self.df_nearest_measurement_locations = df_nearest_measurement_locations
        
        for central_city_name in self.df_cities_chosen['Central City'].unique():
            self.create_directory(central_city_name)
            df_central_city = speis.make_city_timeseries_df(central_city_name, self.df_nearest_measurement_locations)
            self.write_xlsxs(df_central_city, central_city_name, central_city_name)

            bordering_cities_names = cities_chosen.get_list_of_bordering_cities(central_city_name)
            for bordering_city_name in bordering_cities_names:
                df_bordering_city = speis.make_city_timeseries_df(bordering_city_name, self.df_nearest_measurement_locations)
                self.write_xlsxs(df_bordering_city, central_city_name, bordering_city_name)

    def create_directory(self, central_city_name):
        os.makedirs(f'./{self.root_dir}/{central_city_name}', exist_ok=True)
    
    def write_xlsxs(self, df_city, primary_city_name, secondary_city_name):
        df_city.to_excel(f'./{self.root_dir}/{primary_city_name}/{secondary_city_name}.xlsx', index=True)