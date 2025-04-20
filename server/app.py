#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify, abort
from flask_migrate import Migrate

from models import db, Bakery, BakedGood

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def home():
    return '<h1>Bakery GET-POST-PATCH-DELETE API</h1>'

@app.route('/baked_goods', methods=['POST'])
def create_baked_good():
    name = request.form.get('name')
    price = request.form.get('price')

    # Validate inputs
    if not name or not price:
        abort(400, description="Missing 'name' or 'price' in form data.")

    try:
        price = float(price)
    except ValueError:
        abort(400, description="'price' must be a valid number.")

    baked_good = BakedGood(name=name, price=price)
    db.session.add(baked_good)
    db.session.commit()

    return jsonify(baked_good.to_dict()), 201 

@app.route('/baked_goods/<int:id>', methods=['DELETE'])
def delete_baked_good(id):
    baked_good = BakedGood.query.filter_by(id=id).first()

    if not baked_good:
        abort(404, description=f"Baked good with id {id} not found.")

    db.session.delete(baked_good)
    db.session.commit()

    return make_response(
        jsonify({"message": f"Baked good with id {id} was successfully deleted."}),
        200
    )
    
@app.route('/bakeries')
def bakeries():
    bakeries = [bakery.to_dict() for bakery in Bakery.query.all()]
    return make_response(  bakeries,   200  )

@app.route('/bakeries/<int:id>', methods=['GET', 'PATCH'])
def bakery_by_id(id):
    bakery = Bakery.query.filter_by(id=id).first()

    if not bakery:
        abort(404, description=f"Bakery with {id} not found.")

    #PATCH Block
    if request.method =='PATCH':
        name = request.form.get('name')
        if name:
            bakery.name =name
            db.session.commit()    

    bakery_serialized = bakery.to_dict()
    return make_response ( bakery_serialized, 200  )

@app.route('/baked_goods/by_price')
def baked_goods_by_price():
    baked_goods_by_price = BakedGood.query.order_by(BakedGood.price.desc()).all()
    baked_goods_by_price_serialized = [
        bg.to_dict() for bg in baked_goods_by_price
    ]
    return make_response( baked_goods_by_price_serialized, 200  )
   

@app.route('/baked_goods/most_expensive')
def most_expensive_baked_good():
    most_expensive = BakedGood.query.order_by(BakedGood.price.desc()).limit(1).first()
    most_expensive_serialized = most_expensive.to_dict()
    return make_response( most_expensive_serialized,   200  )

if __name__ == '__main__':
    app.run(port=5555, debug=True)