
import requests
import math
from bs4 import BeautifulSoup
import urllib3
from flask import Flask,jsonify,request
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# State values available:
# --------------------------------
# AndamanAndNicobar
# AndhraPradesh
# ArunachalPradesh
# Assam
# Bihar
# Chandigarh
# Chhatisgarh
# DadraAndNagarHaveli
# DamanAndDiu
# Delhi
# Goa
# Gujarat
# Haryana
# HimachalPradesh
# JammuAndKashmir
# Jharkhand
# Karnataka
# Kerala
# MadhyaPradesh
# Maharashtra
# Manipur
# Meghalaya
# Mizoram
# Nagaland
# Odisha
# Pondicherry
# Punjab
# Rajasthan
# Sikkim
# TamilNadu
# Telangana
# Tripura
# UttarPradesh
# Uttarakhand
# WestBengal

def get_all_state_prices(URL):
    page = requests.get(URL, verify=False)
    soup = BeautifulSoup(page.content, "html.parser")
    table = soup.find("table")
    table_body = table.find("tbody")
    rows = table_body.findAll('tr')
    fuel_price_dict = {}
    i = 1
    while i<len(rows):
        cols = rows[i].findAll('td')
        state = cols[0].find('a')
        fuel_price = cols[1]
        key_value = state.contents[0].replace(' ','')
        value = float(fuel_price.contents[0].split(' ')[0])
        fuel_price_dict[key_value]= value
        i=i+1
    return fuel_price_dict

def calculate_total_fuel_cost(price_per_litre, total_distance, avg_mileage):
    required_fuel = total_distance/avg_mileage
    total_fuel_cost = required_fuel * price_per_litre
    return round(required_fuel,2), round(total_fuel_cost,2)

def roundup(x):
    return int(math.ceil(x / 50.0)) * 50

def get_response(all_state_prices, total_distance, avg_mileage, state_name, diesel=False):
    if all_state_prices.get(state_name, -1) == -1:
        response = {'message':'Provide proper values for state',
                    'availableStates': list(all_state_prices.keys())}
        return jsonify(response)
    else:
        price_per_litre = all_state_prices[state_name]
        if total_distance <= 0.0 or avg_mileage <= 0.0:
            response = {'message':'Provide proper values for distance and mileage'}
            return jsonify(response)
        else:
            required_fuel, total_fuel_cost = calculate_total_fuel_cost(price_per_litre,total_distance,avg_mileage)
            rounded_fuel_cost = roundup(total_fuel_cost)
            response = { 'current_petrol_price': price_per_litre,
                        'total_petrol_required_in_litres': required_fuel,
                        'total_petrol_cost': total_fuel_cost,
                        'total_petrol_cost_rounded': rounded_fuel_cost
                        }
            if diesel:
                response = { 'current_diesel_price': price_per_litre,
                        'total_diesel_required_in_litres': required_fuel,
                        'total_diesel_cost': total_fuel_cost,
                        'total_diesel_cost_rounded': rounded_fuel_cost
                        }
            return jsonify(response)

app = Flask(__name__)
@app.route('/')
def fuel_price_intro():
    URL = 'https://www.ndtv.com/fuel-prices/petrol-price-in-all-state'
    all_state_prices = get_all_state_prices(URL)
    response = {'message':'Call url/get-cost to get the cost. Provide values for distance, mileage and state. Example url/get-cost?distance=400&mileage=15&state=Kerala',
                'availableStates': list(all_state_prices.keys())}               
    return jsonify(response)

@app.route('/get-cost')
def petrol():
    URL = 'https://www.ndtv.com/fuel-prices/petrol-price-in-all-state'
    all_state_prices = get_all_state_prices(URL)
    total_distance = request.args.get('distance', default = 0.0, type = float)
    avg_mileage = request.args.get('mileage', default = 0.0, type = float)
    state_name = request.args.get('state', default = 'Kerala', type = str)
    response = get_response(all_state_prices, total_distance, avg_mileage, state_name)
    return response

@app.route('/get-cost-diesel')
def diesel():
    URL = 'https://www.ndtv.com/fuel-prices/diesel-price-in-all-state'
    all_state_prices = get_all_state_prices(URL)
    total_distance = request.args.get('distance', default = 0.0, type = float)
    avg_mileage = request.args.get('mileage', default = 0.0, type = float)
    state_name = request.args.get('state', default = 'Kerala', type = str)
    response = get_response(all_state_prices, total_distance, avg_mileage, state_name, diesel=True)
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000)