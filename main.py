from classes import CityDirectory, SPEIDirectory, ChosenCitiesIndex, FileWriter, NearestLocator

speis                             = SPEIDirectory     ('speiAll_final.csv')
cities_coordinates_directory      = CityDirectory     ('CoordenadasMunicipios.xlsx')
cities_chosen                     = ChosenCitiesIndex ('cidades.json')

cities_coordinates_directory.narrow_down_by_state_geocode(31)
cities_coordinates_directory.narrow_down_by_city_set(cities_chosen.get_chosen_cities_set())

nearest_locator                   = NearestLocator    (cities_coordinates_directory)
nearest_locator.find_nearest_measurement_locations(cities_coordinates_directory, speis)

file_writer   = FileWriter        ('Data', cities_chosen, speis, nearest_locator.df)