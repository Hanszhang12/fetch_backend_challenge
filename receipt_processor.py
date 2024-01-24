from flask import Flask, jsonify, request
from jsonschema import validate, ValidationError

import uuid 

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

# Define the schema for the Receipt
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
    # Validate the JSON data against the receipt schema
    try:
        validate(json_data, receipt_schema)
        return True
    except ValidationError:
        return False

@app.route('/receipts/process', methods=['POST'])
def process_receipt():
    # check if receipt is valid 
    # if it is, we return status code 200
    # else, we return status code 400

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


@app.route('/receipts/<string:id>/points', methods=['GET'])
def get_receipt_points(id):
    if id not in receipts_data.keys():
        return jsonify({"description": "No receipt found for that id"}), 404

    return jsonify({"receipt_id": id, "points": 100})  

if __name__ == '__main__':
    app.run(debug=True)