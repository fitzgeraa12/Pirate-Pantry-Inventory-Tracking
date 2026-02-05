from typing import List, Any, Optional
from flask import Flask, request, jsonify
from flask.typing import ResponseReturnValue

from schema import db, FoodType

# https://dev.to/hardy_mervana/how-to-create-rest-api-with-python-a-step-by-step-guide-g93

api = Flask(__name__)
api.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db.init_app(api)

# Food type
@api.route('/food_types', methods=['GET'])
def get_food_types() -> ResponseReturnValue:
    food_types: List[FoodType] = FoodType.query.all()
    return  {'food_types': [food_type.serialize() for food_type in food_types]}

@api.route('/food_type/<int:id>', methods=['GET'])
def get_food_type(id: int) -> ResponseReturnValue:
    food_type: Optional[FoodType] = FoodType.query.filter_by(id=id).first()
    if food_type is None:
        return jsonify({'error': 'FoodType not found'}), 404

    return food_type.serialize()

@api.route('/food_type', methods=['POST'])
def create_food_type() -> ResponseReturnValue:
    # TODO: add error handling
    data = request.get_json()
    id: int = int(data['id'])
    # TODO: fill in other fields based off id
    brand_id: int = int(0) # default value for now

    food_type = FoodType(id, brand_id)
    db.session.add(food_type)
    db.session.commit()

    return jsonify(food_type.serialize())

@api.route('/food_type/<int:id>', methods=['DELETE'])
def delete_food_type(id: int) -> ResponseReturnValue:
    food_type = FoodType.query.filter_by(id=id).first()
    db.session.delete(food_type)
    db.session.commit()

    return jsonify({'message': 'FoodType deleted'})
