from classes import CityDirectory, SPEIDirectory, ChosenCitiesIndex, FileWriter, NearestLocator

speis                             = SPEIDirectory     ('speiAll_final.csv')
cities_coordinates_directory      = CityDirectory     ('CoordenadasMunicipios.xlsx')
cities_chosen                     = ChosenCitiesIndex ('cidades.json')
file_writer                       = FileWriter        ('Data')

cities_coordinates_directory.narrow_down_by_state_geocode(31)
cities_coordinates_directory.narrow_down_by_city_set(cities_chosen.get_chosen_cities_set())

nearest_locator                   = NearestLocator    (cities_coordinates_directory)
nearest_locator.find_nearest_measurement_locations(cities_coordinates_directory, speis)

# Saving the generated data as XLSX files:
for central_city_name in cities_chosen.get_chosen_central_cities_set():
    file_writer.create_directory(central_city_name)
    df_city = speis.make_city_timeseries_df(central_city_name, nearest_locator.df)
    file_writer.write_xlsx      (df_city, central_city_name, central_city_name)
    
    for bordering_city_name in cities_chosen.get_bordering_cities_set(central_city_name):
        df_city = speis.make_city_timeseries_df(bordering_city_name, nearest_locator.df)
        file_writer.write_xlsx      (df_city, central_city_name, bordering_city_name)