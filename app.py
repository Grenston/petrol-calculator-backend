
import requests
import math
from bs4 import BeautifulSoup
import urllib3
from flask import Flask,jsonify,request
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_petrol_price_ernakulam():
    URL = 'https://www.goodreturns.in/petrol-price-in-ernakulam.html'
    page = requests.get(URL, verify=False)
    soup = BeautifulSoup(page.content, "html.parser")
    petrol_price_block = soup.find("div", class_="fuel-block-details").prettify()
    petrol_price_ernakulam = float(petrol_price_block.split('\n')[2].strip())    
    return petrol_price_ernakulam

def calculate_total_perol_cost(price_per_litre, total_distance, avg_mileage):
    required_petrol = total_distance/avg_mileage
    total_petrol_cost = required_petrol * price_per_litre
    return round(required_petrol,2), round(total_petrol_cost,2)

def roundup(x):
    return int(math.ceil(x / 50.0)) * 50

app = Flask(__name__)
@app.route('/')
def petrol_price_intro():
    response = {'message':'Call url/get-cost to get the cost. Provide values for distance and mileage. Example url/get-cost?distance=400&mileage=15'}
    return jsonify(response)
@app.route('/get-cost')
def petrol():
    petrol_price_ernakulam = get_petrol_price_ernakulam()
    total_distance = request.args.get('distance', default = 0.0, type = float)
    avg_mileage = request.args.get('mileage', default = 0.0, type = float)
    if total_distance <= 0.0 or avg_mileage <= 0.0:
        response = {'message':'Provide proper values for distance and mileage'}
        return jsonify(response)
    else:
        required_petrol, total_petrol_cost = calculate_total_perol_cost(petrol_price_ernakulam,total_distance,avg_mileage)
        rounded_petrol_cost = roundup(total_petrol_cost)

        response = { 'current_petrol_price_ekm': petrol_price_ernakulam,
                    'total_petrol_required_in_litres': required_petrol,
                    'total_petrol_cost': total_petrol_cost,
                    'total_petrol_cost_rounded': rounded_petrol_cost
                    }
        return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000)