import requests
import json

URL_POTS_READINGS = 'http://172.17.51.226:5000/'


def get_all_pots_readings():
    response_pots_readings = requests.get(URL_POTS_READINGS)
    return json.loads(response_pots_readings.text)
