import os

class FileWriter:
    def __init__(self, root_dir):
        self.root_dir = './' + root_dir

    def create_directory(self, central_city_name):
        path = os.path.join(self.root_dir, central_city_name)
        os.makedirs(path, exist_ok=True)
    
    def write_xlsx(self, df_city, primary_city_name, secondary_city_name):
        path = os.path.join(self.root_dir, primary_city_name)
        df_city.to_excel(f'{path}/{secondary_city_name}.xlsx', index=True)