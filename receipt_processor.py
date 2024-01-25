from flask import Flask, jsonify, request
from jsonschema import validate, ValidationError
import math
import uuid 
from datetime import datetime

app = Flask(__name__)

receipts_data = {}

item_schema = {
    "type": "object",
    "required": ["shortDescription", "price"],
    "properties": {
        "shortDescription": {"type": "string", "pattern": "^[\\w\\s\\-]+$"},
        "price": {"type": "string", "pattern": "^\\d+\\.\\d{2}$"}
    }
}

receipt_schema = {
    "type": "object",
    "required": ["retailer", "purchaseDate", "purchaseTime", "items", "total"],
    "properties": {
        "retailer": {"type": "string", "pattern": "^\\S+$"},
        "purchaseDate": {"type": "string", "format": "date"},
        "purchaseTime": {"type": "string", "format": "time"},
        "items": {"type": "array", "minItems": 1, "items": item_schema},
        "total": {"type": "string", "pattern": "^\\d+\\.\\d{2}$"}
    }
}

def is_valid_receipt(json_data):
    try:
        validate(json_data, receipt_schema)
        return True
    except ValidationError:
        return False

@app.route('/receipts/process', methods=['POST'])
def process_receipt():
    
    receipt_json = request.json

    if is_valid_receipt(receipt_json):
        unique_id = str(uuid.uuid4()).replace("-", "")

        while unique_id in receipts_data.keys():
            unique_id = str(uuid.uuid4()).replace("-", "")

        receipts_data[unique_id] = receipt_json
        response_data = {"id": unique_id}  
        return jsonify(response_data), 200
    else:
        return jsonify({"description": "The receipt is invalid"}), 400


def calculate_score(receipt):
    total_score = 0

    retailer_name = receipt["retailer"]
    #check number of alphanumeric characters
    for char in retailer_name:
        if char.isalnum():
            total_score += 1

    #check if total is round dollar amount with no cents
    receipt_total = receipt["total"]
    if float(receipt_total) % 1 == 0:
        total_score += 50

    #check if total is multiple of 0.25
    if float(receipt_total) % 0.25 == 0:
        total_score += 25

    #5 points for every two items
    num_items = len(receipt["items"])
    total_score += (num_items // 2) * 5

    #check if length of item description is multiple of 3
    for item in receipt["items"]:
        description = item["shortDescription"]
        price = item["price"]

        if len(description.strip()) % 3 == 0:
            rounded_price = math.ceil(float(price) * 0.2)
            total_score += rounded_price 

    #check if purchase date is odd
    purchase_date = datetime.strptime(receipt["purchaseDate"], "%Y-%m-%d")
    if purchase_date.day % 2 == 1:
        total_score += 6

    #check if time of purchase is after 2 pm and before 4 pm
    purchase_time = datetime.strptime(receipt["purchaseTime"], "%H:%M")
    start_time = datetime.strptime("14:00", "%H:%M")
    end_time = datetime.strptime("16:00", "%H:%M")

    if purchase_time > start_time and purchase_time < end_time:
        total_score += 10

    return total_score

@app.route('/receipts/<string:id>/points', methods=['GET'])
def get_receipt_points(id):
    if id not in receipts_data.keys():
        return jsonify({"description": "No receipt found for that id"}), 404

    receipt = receipts_data[id]
    points = calculate_score(receipt)
    return jsonify({"points": points}), 200 

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
