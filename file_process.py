from geopy.geocoders import Nominatim
from geopy.exc import GeocoderUnavailable

def read_file(path, year):
    location_dct = {}
    with open(path) as file:
        i = 0
        used_films = []
        for line in file:
            i+=1

            if line is None or i < 15:
                continue
            if not line[0].isalpha():
                if line[0] != '"':
                    continue
            line = line.strip()
            line = line.split('\t')
            line = process_data_and_location(line)
            if line is None:
                continue
            if str(year) not in line[1]:
                continue
            if line[0] in used_films:
                continue
            else:
                used_films.append(line[0])
            location_dct = update_dct(location_dct, line)
            if len(location_dct) == 50:
                print('Please, wait for us to process the data.')
            if len(location_dct) == 500:
                print('Please, wait some more.')
            if len(location_dct) == 1000:
                print('Wow, that\'s a lot of data!')

    print("We're done processing the data. Map is generating now.")
    return location_dct


def get_coords(location: str):
    geolocator = Nominatim(user_agent="my_request")
    try:
        loc = geolocator.geocode(location)
    except GeocoderUnavailable:
        return
    if loc is None:
        location = location.split(',')[1:]
        location = ', '.join(location)
        return get_coords(location)
    return loc.latitude, loc.longitude

def update_dct(data_dct, data):
    location = data[-1]
    name_date = data[:-1]
    if location in data_dct:
        if name_date in data_dct[location]:
            return data_dct
        data_dct[location].append(name_date)
    else:   
        coord = get_coords(location)
        if coord is None:
            return data_dct
        data_dct.setdefault(location, [coord, name_date])
    return data_dct


def process_data_and_location(data):
    new_data = []
    if '"' in data[0]:
        get_name_date = data[0].split('"')
        #film name in this case is get_name_data[1]
        #example ['', '#LawstinWoods', ' (2013) {The Great Divide (#1.4)}']
        new_data.append(get_name_date[1])
        get_name_date = get_name_date[-1].split()
        #get rid of '()' in year date:
        date = get_name_date[0][1:-1]
        new_data.append(date)
    else:
        get_name_date = data[0].split('(')
        name = get_name_date[0].strip()
        date = get_name_date[-1][:4]
        new_data.append(name)
        new_data.append(date)

    if '(' in data[-1]:
        data = data[:-1]

    location = data[-1]
    location_lst = location.split(',')
    if len(location_lst) > 3:
        location = ','.join(location_lst[-3:])
    if 'ederal' in location or 'ighway' in location:
        return
    new_data.append(location)
    return new_data

def create_csv(film_data: dict):
    with open('locations.csv', mode='w') as file:
        file.write('name,year,lat,lon\n')
        for place in film_data:
            name = '"' + film_data[place][1][0] + '"'
            date = film_data[place][1][1]
            lat, lon = film_data[place][0]
            file.write(f"{name},{date},{lat},{lon}\n")

if __name__ == '__main__':
    film_data = read_file('/Users/shevdan/Documents/Programming/Python/semester2/lab2/small_file.list', 2017)
    create_csv(film_data)
