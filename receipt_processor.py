from flask import Flask, jsonify, request
import uuid 

app = Flask(__name__)

receipts_data = {}

def is_valid_receipt(json_data):
    expected_format = {
        "retailer": str,
        "purchaseDate": str,
        "purchaseTime": str,
        "total": str,
        "items": list
    }

    if all(key in json_data for key in expected_format):
        if all(isinstance(json_data[key], expected_format[key]) for key in expected_format):
            if "items" in json_data and all(
                    isinstance(item, dict) and "shortDescription" in item and "price" in item
                    for item in json_data["items"]
            ):
                return True
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


@app.route('/receipts/<int:id>/points')
def get_receipt_points(id):
    # Logic to retrieve points for a specific receipt id
    return jsonify({"receipt_id": id, "points": 100})  # Replace with actual logic

if __name__ == '__main__':
    app.run(debug=True)