import pandas as pd
import numpy as np
import json
import os

def define_cities_of_interest(json_source_file_name):
    """
    Return the cities of interest, given a file that has this information.

    Parameters
    ----------
    json_source_file_name : string
        The filename of the JSON file where the city names are stored.
        The JSON file must be structured as a dictionary where the keys are the central cities, and the values are lists of bordering cities.

    Returns
    -------
    df_cities_of_interest : dataframe
        A dataframe, in long format, that lists all central cities on the first column and their corresponding bordering cities on the second column.

    """
    with open(json_source_file_name, 'r',encoding='utf-8') as json_source_file:
        DICT_OF_CITIES_TO_SEARCH_FOR = json.load(json_source_file)
        list_of_city_tuples = []
        for central_city, list_of_bordering_cities in DICT_OF_CITIES_TO_SEARCH_FOR.items():
            for bordering_city in list_of_bordering_cities:
                list_of_city_tuples.append( (central_city, bordering_city) )
               
        df_cities_of_interest = pd.DataFrame(list_of_city_tuples, columns=['Central City', 'Bordering City'])
        
        # Convert all city names to uppercase
        df_cities_of_interest['Central City']   = df_cities_of_interest['Central City']  .str.upper()
        df_cities_of_interest['Bordering City'] = df_cities_of_interest['Bordering City'].str.upper()
    return df_cities_of_interest

def find_Minas_Gerais_cities_coordinates(df_of_cities_to_search_for, cities_coordinates_spreadsheet_name):
    # Creates the dataframe by reading the spreadsheet:
    df_cities_coordinates = pd.read_excel(cities_coordinates_spreadsheet_name, index_col='GEOCODIGO_MUNICIPIO')
    # Narrow down the dataframe by keeping only Minas Gerais cities:
    df_cities_coordinates = df_cities_coordinates[ df_cities_coordinates.index.astype(str).str.startswith('31') ].set_index('NOME_MUNICIPIO')
    
    # Narrow down the dataframe by keeping only the sought Minas Gerais cities:
    set_of_all_sought_city_names = set( pd.concat( [ df_cities_of_interest['Central City'], df_cities_of_interest['Bordering City'] ] ) )
    df_cities_coordinates = df_cities_coordinates[df_cities_coordinates.index.isin(set_of_all_sought_city_names)]
    
    return df_cities_coordinates

def find_nearest_measurement_locations(df_cities_coordinates, df_SPEI):
    """
    Return geographical coordinates of the nearest measurement location, given city coordinates.

    Parameters
    ----------
    df_cities_coordinates : dataframe
        A dataframe composed of just the sought city names and their corresponding coordinates.
        The city names are index labels (NOME_MUNICIPIO) and the LONGITUDE and LATITUDE are the column names.
    df_SPEI : dataframe
        A dataframe composed of SPEI measurements filed under geographical coordinates as column names.

    Returns
    -------
    df_nearest_measurement_locations : dataframe
        A dataframe composed of just the sought city names and the coordinates of the corresponding nearest measurement location.
        The city names are index labels (NOME_MUNICIPIO) and the LONGITUDE and LATITUDE are the column names.

    """
    # Duplicates only the structure of the inputted dataframe, leaving the data out:
    df_nearest_measurement_locations = pd.DataFrame().reindex_like(df_cities_coordinates)
    
    for city in df_nearest_measurement_locations.index:
        CITY_LONGITUDE = df_cities_coordinates.loc[city, 'LONGITUDE']
        CITY_LATITUDE  = df_cities_coordinates.loc[city, 'LATITUDE' ]
        
        min_distance    = float('inf')
        closest_col_lon = None
        closest_col_lat = None
        
        # For every measurement location indicated in df_SPEI, does the following:
        for column in df_SPEI.columns:
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
            
        df_nearest_measurement_locations.loc[city, 'LONGITUDE'] = closest_col_lon
        df_nearest_measurement_locations.loc[city, 'LATITUDE' ] = closest_col_lat
    
    return df_nearest_measurement_locations

def make_city_timeseries_dataframe(city_name, df_nearest_measurement_locations):
    # Rebuilding the coordinates from the dataframe columns:
    nearest_column = ','.join( [ 'X', str(df_nearest_measurement_locations.loc[city_name, 'LONGITUDE']), str(df_nearest_measurement_locations.loc[city_name, 'LATITUDE']) ] )
    
    df_city = df_SPEI[[nearest_column]].copy()

    df_city['Data'] = DF_DATES['Date'].reset_index(drop=True)
    
    # Renomear a primeira coluna para 'Series 1'
    df_city = df_city.rename(columns={df_city.columns[0]: 'Series 1'})
    
    # Converter a primeira coluna para float e a segunda para datetime
    # Converter a primeira coluna para float (substituir vírgulas por pontos)
    df_city['Series 1'] = df_city['Series 1'].str.replace(',', '.').astype(float)
    df_city['Data'] = pd.to_datetime(df_city['Data'], errors='coerce')

    return df_city


def write_city_timeseries_on_xlsxs(df_cities_of_interest, df_nearest_measurement_locations):
    for central_city_name in df_cities_of_interest['Central City'].unique():
        # Create one subdirectory for each central city, inside the 'Data' directory:
        os.makedirs('./Data/' + central_city_name)
        
        # Creates the xlsx of the central city:
        df_central_city = make_city_timeseries_dataframe(central_city_name, df_nearest_measurement_locations)
        df_central_city.to_excel(f'./Data/{central_city_name}/{central_city_name}.xlsx', index=False)
        
        # Gets a list of all bordering cities names, each time for a different central city:
        bordering_cities_names = df_cities_of_interest[ df_cities_of_interest['Central City'] == central_city_name ]['Bordering City']
        
        # For every bordering city, extracts the nearest column of df_SPEI and write a xlsx file in the correct subdirectory:
        for bordering_city_name in bordering_cities_names:
            # Creates the xlsx of the bordering city:
            df_bordering_city = make_city_timeseries_dataframe(bordering_city_name, df_nearest_measurement_locations)
            df_bordering_city.to_excel(f'./Data/{central_city_name}/{bordering_city_name}.xlsx', index=False)

# Abrir o arquivo Excel com a segunda coluna a ser concatenada
DATES = ['1961-12-01', '1962-01-01', '1962-02-01', '1962-03-01', '1962-04-01', '1962-05-01', '1962-06-01', '1962-07-01', '1962-08-01', '1962-09-01', '1962-10-01', '1962-11-01', '1962-12-01', '1963-01-01', '1963-02-01', '1963-03-01', '1963-04-01', '1963-05-01', '1963-06-01', '1963-07-01', '1963-08-01', '1963-09-01', '1963-10-01', '1963-11-01', '1963-12-01', '1964-01-01', '1964-02-01', '1964-03-01', '1964-04-01', '1964-05-01', '1964-06-01', '1964-07-01', '1964-08-01', '1964-09-01', '1964-10-01', '1964-11-01', '1964-12-01', '1965-01-01', '1965-02-01', '1965-03-01', '1965-04-01', '1965-05-01', '1965-06-01', '1965-07-01', '1965-08-01', '1965-09-01', '1965-10-01', '1965-11-01', '1965-12-01', '1966-01-01', '1966-02-01', '1966-03-01', '1966-04-01', '1966-05-01', '1966-06-01', '1966-07-01', '1966-08-01', '1966-09-01', '1966-10-01', '1966-11-01', '1966-12-01', '1967-01-01', '1967-02-01', '1967-03-01', '1967-04-01', '1967-05-01', '1967-06-01', '1967-07-01', '1967-08-01', '1967-09-01', '1967-10-01', '1967-11-01', '1967-12-01', '1968-01-01', '1968-02-01', '1968-03-01', '1968-04-01', '1968-05-01', '1968-06-01', '1968-07-01', '1968-08-01', '1968-09-01', '1968-10-01', '1968-11-01', '1968-12-01', '1969-01-01', '1969-02-01', '1969-03-01', '1969-04-01', '1969-05-01', '1969-06-01', '1969-07-01', '1969-08-01', '1969-09-01', '1969-10-01', '1969-11-01', '1969-12-01', '1970-01-01', '1970-02-01', '1970-03-01', '1970-04-01', '1970-05-01', '1970-06-01', '1970-07-01', '1970-08-01', '1970-09-01', '1970-10-01', '1970-11-01', '1970-12-01', '1971-01-01', '1971-02-01', '1971-03-01', '1971-04-01', '1971-05-01', '1971-06-01', '1971-07-01', '1971-08-01', '1971-09-01', '1971-10-01', '1971-11-01', '1971-12-01', '1972-01-01', '1972-02-01', '1972-03-01', '1972-04-01', '1972-05-01', '1972-06-01', '1972-07-01', '1972-08-01', '1972-09-01', '1972-10-01', '1972-11-01', '1972-12-01', '1973-01-01', '1973-02-01', '1973-03-01', '1973-04-01', '1973-05-01', '1973-06-01', '1973-07-01', '1973-08-01', '1973-09-01', '1973-10-01', '1973-11-01', '1973-12-01', '1974-01-01', '1974-02-01', '1974-03-01', '1974-04-01', '1974-05-01', '1974-06-01', '1974-07-01', '1974-08-01', '1974-09-01', '1974-10-01', '1974-11-01', '1974-12-01', '1975-01-01', '1975-02-01', '1975-03-01', '1975-04-01', '1975-05-01', '1975-06-01', '1975-07-01', '1975-08-01', '1975-09-01', '1975-10-01', '1975-11-01', '1975-12-01', '1976-01-01', '1976-02-01', '1976-03-01', '1976-04-01', '1976-05-01', '1976-06-01', '1976-07-01', '1976-08-01', '1976-09-01', '1976-10-01', '1976-11-01', '1976-12-01', '1977-01-01', '1977-02-01', '1977-03-01', '1977-04-01', '1977-05-01', '1977-06-01', '1977-07-01', '1977-08-01', '1977-09-01', '1977-10-01', '1977-11-01', '1977-12-01', '1978-01-01', '1978-02-01', '1978-03-01', '1978-04-01', '1978-05-01', '1978-06-01', '1978-07-01', '1978-08-01', '1978-09-01', '1978-10-01', '1978-11-01', '1978-12-01', '1979-01-01', '1979-02-01', '1979-03-01', '1979-04-01', '1979-05-01', '1979-06-01', '1979-07-01', '1979-08-01', '1979-09-01', '1979-10-01', '1979-11-01', '1979-12-01', '1980-01-01', '1980-02-01', '1980-03-01', '1980-04-01', '1980-05-01', '1980-06-01', '1980-07-01', '1980-08-01', '1980-09-01', '1980-10-01', '1980-11-01', '1980-12-01', '1981-01-01', '1981-02-01', '1981-03-01', '1981-04-01', '1981-05-01', '1981-06-01', '1981-07-01', '1981-08-01', '1981-09-01', '1981-10-01', '1981-11-01', '1981-12-01', '1982-01-01', '1982-02-01', '1982-03-01', '1982-04-01', '1982-05-01', '1982-06-01', '1982-07-01', '1982-08-01', '1982-09-01', '1982-10-01', '1982-11-01', '1982-12-01', '1983-01-01', '1983-02-01', '1983-03-01', '1983-04-01', '1983-05-01', '1983-06-01', '1983-07-01', '1983-08-01', '1983-09-01', '1983-10-01', '1983-11-01', '1983-12-01', '1984-01-01', '1984-02-01', '1984-03-01', '1984-04-01', '1984-05-01', '1984-06-01', '1984-07-01', '1984-08-01', '1984-09-01', '1984-10-01', '1984-11-01', '1984-12-01', '1985-01-01', '1985-02-01', '1985-03-01', '1985-04-01', '1985-05-01', '1985-06-01', '1985-07-01', '1985-08-01', '1985-09-01', '1985-10-01', '1985-11-01', '1985-12-01', '1986-01-01', '1986-02-01', '1986-03-01', '1986-04-01', '1986-05-01', '1986-06-01', '1986-07-01', '1986-08-01', '1986-09-01', '1986-10-01', '1986-11-01', '1986-12-01', '1987-01-01', '1987-02-01', '1987-03-01', '1987-04-01', '1987-05-01', '1987-06-01', '1987-07-01', '1987-08-01', '1987-09-01', '1987-10-01', '1987-11-01', '1987-12-01', '1988-01-01', '1988-02-01', '1988-03-01', '1988-04-01', '1988-05-01', '1988-06-01', '1988-07-01', '1988-08-01', '1988-09-01', '1988-10-01', '1988-11-01', '1988-12-01', '1989-01-01', '1989-02-01', '1989-03-01', '1989-04-01', '1989-05-01', '1989-06-01', '1989-07-01', '1989-08-01', '1989-09-01', '1989-10-01', '1989-11-01', '1989-12-01', '1990-01-01', '1990-02-01', '1990-03-01', '1990-04-01', '1990-05-01', '1990-06-01', '1990-07-01', '1990-08-01', '1990-09-01', '1990-10-01', '1990-11-01', '1990-12-01', '1991-01-01', '1991-02-01', '1991-03-01', '1991-04-01', '1991-05-01', '1991-06-01', '1991-07-01', '1991-08-01', '1991-09-01', '1991-10-01', '1991-11-01', '1991-12-01', '1992-01-01', '1992-02-01', '1992-03-01', '1992-04-01', '1992-05-01', '1992-06-01', '1992-07-01', '1992-08-01', '1992-09-01', '1992-10-01', '1992-11-01', '1992-12-01', '1993-01-01', '1993-02-01', '1993-03-01', '1993-04-01', '1993-05-01', '1993-06-01', '1993-07-01', '1993-08-01', '1993-09-01', '1993-10-01', '1993-11-01', '1993-12-01', '1994-01-01', '1994-02-01', '1994-03-01', '1994-04-01', '1994-05-01', '1994-06-01', '1994-07-01', '1994-08-01', '1994-09-01', '1994-10-01', '1994-11-01', '1994-12-01', '1995-01-01', '1995-02-01', '1995-03-01', '1995-04-01', '1995-05-01', '1995-06-01', '1995-07-01', '1995-08-01', '1995-09-01', '1995-10-01', '1995-11-01', '1995-12-01', '1996-01-01', '1996-02-01', '1996-03-01', '1996-04-01', '1996-05-01', '1996-06-01', '1996-07-01', '1996-08-01', '1996-09-01', '1996-10-01', '1996-11-01', '1996-12-01', '1997-01-01', '1997-02-01', '1997-03-01', '1997-04-01', '1997-05-01', '1997-06-01', '1997-07-01', '1997-08-01', '1997-09-01', '1997-10-01', '1997-11-01', '1997-12-01', '1998-01-01', '1998-02-01', '1998-03-01', '1998-04-01', '1998-05-01', '1998-06-01', '1998-07-01', '1998-08-01', '1998-09-01', '1998-10-01', '1998-11-01', '1998-12-01', '1999-01-01', '1999-02-01', '1999-03-01', '1999-04-01', '1999-05-01', '1999-06-01', '1999-07-01', '1999-08-01', '1999-09-01', '1999-10-01', '1999-11-01', '1999-12-01', '2000-01-01', '2000-02-01', '2000-03-01', '2000-04-01', '2000-05-01', '2000-06-01', '2000-07-01', '2000-08-01', '2000-09-01', '2000-10-01', '2000-11-01', '2000-12-01', '2001-01-01', '2001-02-01', '2001-03-01', '2001-04-01', '2001-05-01', '2001-06-01', '2001-07-01', '2001-08-01', '2001-09-01', '2001-10-01', '2001-11-01', '2001-12-01', '2002-01-01', '2002-02-01', '2002-03-01', '2002-04-01', '2002-05-01', '2002-06-01', '2002-07-01', '2002-08-01', '2002-09-01', '2002-10-01', '2002-11-01', '2002-12-01', '2003-01-01', '2003-02-01', '2003-03-01', '2003-04-01', '2003-05-01', '2003-06-01', '2003-07-01', '2003-08-01', '2003-09-01', '2003-10-01', '2003-11-01', '2003-12-01', '2004-01-01', '2004-02-01', '2004-03-01', '2004-04-01', '2004-05-01', '2004-06-01', '2004-07-01', '2004-08-01', '2004-09-01', '2004-10-01', '2004-11-01', '2004-12-01', '2005-01-01', '2005-02-01', '2005-03-01', '2005-04-01', '2005-05-01', '2005-06-01', '2005-07-01', '2005-08-01', '2005-09-01', '2005-10-01', '2005-11-01', '2005-12-01', '2006-01-01', '2006-02-01', '2006-03-01', '2006-04-01', '2006-05-01', '2006-06-01', '2006-07-01', '2006-08-01', '2006-09-01', '2006-10-01', '2006-11-01', '2006-12-01', '2007-01-01', '2007-02-01', '2007-03-01', '2007-04-01', '2007-05-01', '2007-06-01', '2007-07-01', '2007-08-01', '2007-09-01', '2007-10-01', '2007-11-01', '2007-12-01', '2008-01-01', '2008-02-01', '2008-03-01', '2008-04-01', '2008-05-01', '2008-06-01', '2008-07-01', '2008-08-01', '2008-09-01', '2008-10-01', '2008-11-01', '2008-12-01', '2009-01-01', '2009-02-01', '2009-03-01', '2009-04-01', '2009-05-01', '2009-06-01', '2009-07-01', '2009-08-01', '2009-09-01', '2009-10-01', '2009-11-01', '2009-12-01', '2010-01-01', '2010-02-01', '2010-03-01', '2010-04-01', '2010-05-01', '2010-06-01', '2010-07-01', '2010-08-01', '2010-09-01', '2010-10-01', '2010-11-01', '2010-12-01', '2011-01-01', '2011-02-01', '2011-03-01', '2011-04-01', '2011-05-01', '2011-06-01', '2011-07-01', '2011-08-01', '2011-09-01', '2011-10-01', '2011-11-01', '2011-12-01', '2012-01-01', '2012-02-01', '2012-03-01', '2012-04-01', '2012-05-01', '2012-06-01', '2012-07-01', '2012-08-01', '2012-09-01', '2012-10-01', '2012-11-01', '2012-12-01', '2013-01-01', '2013-02-01', '2013-03-01', '2013-04-01', '2013-05-01', '2013-06-01', '2013-07-01', '2013-08-01', '2013-09-01', '2013-10-01', '2013-11-01', '2013-12-01', '2014-01-01', '2014-02-01', '2014-03-01', '2014-04-01', '2014-05-01', '2014-06-01', '2014-07-01', '2014-08-01', '2014-09-01', '2014-10-01', '2014-11-01', '2014-12-01', '2015-01-01', '2015-02-01', '2015-03-01', '2015-04-01', '2015-05-01', '2015-06-01', '2015-07-01', '2015-08-01', '2015-09-01', '2015-10-01', '2015-11-01', '2015-12-01', '2016-01-01', '2016-02-01', '2016-03-01', '2016-04-01', '2016-05-01', '2016-06-01', '2016-07-01', '2016-08-01', '2016-09-01', '2016-10-01', '2016-11-01', '2016-12-01', '2017-01-01', '2017-02-01', '2017-03-01', '2017-04-01', '2017-05-01', '2017-06-01', '2017-07-01', '2017-08-01', '2017-09-01', '2017-10-01', '2017-11-01', '2017-12-01', '2018-01-01', '2018-02-01', '2018-03-01', '2018-04-01', '2018-05-01', '2018-06-01', '2018-07-01', '2018-08-01', '2018-09-01', '2018-10-01', '2018-11-01', '2018-12-01', '2019-01-01', '2019-02-01', '2019-03-01', '2019-04-01', '2019-05-01', '2019-06-01', '2019-07-01', '2019-08-01', '2019-09-01', '2019-10-01', '2019-11-01', '2019-12-01', '2020-01-01', '2020-02-01', '2020-03-01', '2020-04-01', '2020-05-01', '2020-06-01', '2020-07-01']
DF_DATES = pd.Series(DATES).to_frame(name='Date')
        
# Create a dataframe to hold all SPEI measurements together with their geographical coordinates:
df_SPEI = pd.read_csv("speiAll_final.csv",delimiter=';').reset_index(drop=True)

df_cities_of_interest = define_cities_of_interest('cidades.json')
print(df_cities_of_interest)

df_cities_coordinates = find_Minas_Gerais_cities_coordinates(df_cities_of_interest, 'CoordenadasMunicipios.xlsx')

df_nearest_measurement_locations = find_nearest_measurement_locations(df_cities_coordinates, df_SPEI)

write_city_timeseries_on_xlsxs(df_cities_of_interest, df_nearest_measurement_locations)
