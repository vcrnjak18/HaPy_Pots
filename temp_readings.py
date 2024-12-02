import xml.etree.ElementTree as ET
from urllib.request import urlopen

def temp_reading():
    with urlopen('https://prognoza.hr/prognoza_danas.xml') as url:
            tree = ET.parse(url)
            root = tree.getroot()[1]

    for child in root:
        if child.attrib['name'] == 'Zagreb': 
            for i in child:
                if i.attrib['name'] == 'Tmn':
                    city_temp_min = float(i.attrib['value'])
                elif i.attrib['name'] == 'Tmx':
                    city_temp_max = float(i.attrib['value'])

    city_temp = round(((city_temp_max + city_temp_min)/2), 1)

    return city_temp