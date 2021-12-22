import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
Uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
#db_drop_and_create_all()

# ROUTES
'''
GET /drinks
    it is a public endpoint
    it contain only the drink.short() data representation
returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
def get_drinks():
    try:
        drinks = Drink.query.all()
        return jsonify({
            "success": True,
            "drinks": [drink.short() for drink in drinks]
            }), 200
    except:
        abort(500)


'''
GET /drinks-detail
    it require the 'get:drinks-detail' permission
    it contain the drink.long() data representation
returns status code 200 and json {"success": True, "drinks": drinks}
    where drinks is the list of drinks
    or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_detail_drinks(f):
    if type(f) == AuthError:
        abort(f.status_code)
    try:
        drinks = Drink.query.all()
        return jsonify({
                "success": True,
                "drinks": [drink.long() for drink in drinks]
                }), 200
    except:
        abort(500)

'''
POST /drinks
    it create a new row in the drinks table
    it require the 'post:drinks' permission
    it contain the drink.long() data representation
returns status code 200 and json {"success": True, "drinks": drink}
    where drink an array containing only the newly created drink
    or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drink(f):
    if type(f) == AuthError:
        abort(f.status_code)
    try:
        body = request.get_json()
        recipe = str(body.get('recipe', None)).replace("\'", "\"")
        title = body.get('title', None)
        new_drink = Drink(title=title, recipe=str(recipe))
        new_drink.insert()
        return jsonify({
            "success": True,
            "drinks": new_drink.long()
            }), 200
    except Exception as e:
        abort(422)

'''
PATCH /drinks/<id>
    where <id> is the existing model id
    it respond with a 404 error if <id> is not found
    it update the corresponding row for <id>
    it require the 'patch:drinks' permission
    it contain the drink.long() data representation
returns status code 200 and json {"success": True, "drinks": drink}
    where drink an array containing only the updated drink
    or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(f, id):
    if type(f) == AuthError:
        abort(f.status_code)
    try:
        drink = Drink.query.filter_by(id=id).one_or_none()
        if drink is None:
            abort(404)
        body = request.get_json()
        title = body.get('title', None)
        recipe = body.get('recipe', None)
        if title:
            drink.title = title
        if recipe:
            drink.recipe = str(recipe).replace("\'", "\"")
        drink.update()
        return jsonify({
            "success": True,
            "drinks": [drink.long()]
            }), 200
    except Exception as e:
        abort(422)

'''
DELETE /drinks/<id>
    where <id> is the existing model id
    it respond with a 404 error if <id> is not found
    it delete the corresponding row for <id>
    it require the 'delete:drinks' permission
returns status code 200 and json {"success": True, "delete": id}
    where id is the id of the deleted record
    or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(f, id):
    if type(f) == AuthError:
        abort(f.status_code)
    try:
        drink = Drink.query.filter_by(id=id).one_or_none()
        if drink is None:
            abort(404)
        drink.delete()
        return jsonify({
            "success": True,
            "delete": id
            }), 200
    except:
        abort(422)

# Error Handling


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
error handler for 404
'''
@app.errorhandler(404)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


'''
 error handler for AuthError
'''
@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error['code']
    }), error.status_code
