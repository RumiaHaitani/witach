import time
from flask import Flask, request, jsonify, make_response
from Validate import Validate
from Functions import Functions
from Model.User import User
from Model.Item import Item 
from Model.Category import Category
from Model.Type import Type
from JWTService import JWTService
from flask_cors import CORS
from functools import wraps



app = Flask(__name__)

CORS(app)

cookies = []

def send_response(json, status):
  response = make_response(json, status)
  for cookie in cookies:
    response.set_cookie(cookie['key'], cookie['value'], max_age=cookie['max_age'])
  return response


##########################################################################################################################################################################
#LOGIN LIST
########################################################################################################################################################################


def login_required(func):
  @wraps(func)
  def decorator(*args,**kwargs):
    token_access=request.cookies.get("access")
    if not token_access: #нету токена access
      response=make_response(jsonify("no token"),401)
      return response
    # проверка access tokena
    check_access = JWTService.check_token(token_access)
    if not check_access['status'] and check_access['error'] == 'other':
      response=make_response(jsonify("token is not valid"),401)
      return response
    elif not check_access['status'] and check_access['error'] == 'old':
      user = User.query_get(
        get_params=["id", "refresh_token"],
        fetch_mode="one",
        where=[ ['access_token', '=', token_access, 'value'] ]
      )
      if not user:
        response = make_response(jsonify("You are not loged in"),401)
        response.set_cookie("access", "", max_age=int(time.time()) - 1)
        return response
      if not user['refresh_token'] or not JWTService.check_token(user['refresh_token'])['status']:
        User.update_col({
          "refresh_token":None,
          "access_token":None,
        }, [ ['id', '=', user['id'], 'value'] ])
        response = make_response(jsonify("You are not loged in[2]"), 401)
        response.set_cookie("access", "", max_age=int(time.time()) - 1)
        return response
      new_access = JWTService.create_access_token( {'id':user['id'], 'role':'user'} )
      User.update_col({
        "access_token":new_access,
      }, [ ['id', '=', user['id'], 'value'] ])
      cookies.append({"key":"access","value":new_access,"max_age":int(time.time())+60*60*24*30})
      return func({'id':user['id'], 'role':'user'},*args,**kwargs)
    
    return func(check_access['payload']['data'],*args,**kwargs)
  return decorator






@app.route('/registration', methods=["POST"])
def registration():
  data = request.get_json()
  validated = Validate.required_params(data, ["name", "phone", "password"])
  if not validated['status']:
    return jsonify({"message":"Data is not valid", "errors":validated['errors']}), 400
  
  data['password'] = Functions.create_password_hash(data['password'])
  add = User.query_add(data)
  if add:
    return jsonify({
      "message":"User added successfully"
    }), 201
  return jsonify({
    "message":"Registration failed!"
  }), 400


@app.route('/login', methods=["POST"])
def login():
  data = request.get_json()
  validated = Validate.required_params(data, ["login", "password"])
  if not validated['status']:
    return jsonify({"message":"Data is not valid", "errors":validated['errors']}), 400
  user = User.query_get(
    get_params=["*"],
    fetch_mode="one",
    where=[
      ['phone', '=', data['login'], 'value']
    ]
  )

  if not user:
    return make_response(jsonify({"message":"The user was not found"}), 400)
  
  if Functions.check_password(data['password'], user['password']): # пользователя можно авторизовать
    access_token = JWTService.create_access_token({
      "id":user['id'],
      "role":"user"
    })
    refresh_token = JWTService.create_refresh_token({
      "id":user['id'],
      "role":"user"
    })
    update = User.update_col(
      {
        "access_token":access_token,
        "refresh_token":refresh_token,
      },
      [
        ['id', '=', user['id'], 'value']
      ]
    )
    if update:
      # установка куки
      res = make_response(jsonify({
        "message":"Successful login, welcome",
        "user":{
          "id":user['id'],
        }
      }), 200)
      res.set_cookie("access", access_token, max_age=int(time.time())+60*60*24*30)
      return res 
    return jsonify({"message":"Authorization failed"}), 400
  
  return jsonify({"message":"The user was not found"}), 400


@app.route('/user/<int:user_id>', methods=["GET"])
@login_required
def get_user(payload, user_id):
    user = User.get_one(user_id)
    if not user:
        return send_response(jsonify({'message': "User was not found"}), 400)
    return send_response(jsonify({'user': user}), 200)


@app.route('/profile/<int:user_id>', methods=["GET"])
@login_required
def get_profile(payload, user_id):
    user = User.get_one(user_id)
    if not user:
        return send_response(jsonify({'message': "User was not found"}), 400)
    return send_response(jsonify({'user': user}), 200)




@app.route('/user/<int:id>', methods=["PUT"])
@login_required
def update_user(payload, id):
    user = User.get_one(id)
    if not user:
        return jsonify({"message": "user not found"}), 404

    if user['id'] != payload['id']:
        return jsonify({"message": "You don't have permission to update this user"}), 403

    data = request.get_json()


    required_fields = ["name"]
    validated = Validate.required_params(data, required_fields)
    if not validated['status']:
        return jsonify({"message": "Data is not valid", "errors": validated['errors']}), 400

    update_data = {
        "name": data['name']
    }

    update = User.update_col(update_data, [['id', '=', id, 'value']])

    if update:
        updated_user = User.get_one(id)
        return jsonify({
            "message": "user updated successfully",
            "user": updated_user
        }), 200
    
    return jsonify({"message": "Failed to update user"}), 500



@app.route('/logout', methods=["GET"])
@login_required
def logout(payload):
  res = make_response(jsonify("Logout from system"), 200)
  res.set_cookie("access", "", max_age=int(time.time())-1)
  return res

##########################################################################################################################################################################
#ITEMS LIST
########################################################################################################################################################################


@app.route('/item/<int:item_id>', methods=["GET"])
@login_required
def get_item(payload, item_id):
    item = Item.get_one(item_id)
    if not item:
        return send_response(jsonify({'message': "Item is not found"}), 400)
    return send_response(jsonify({'item': item}), 200)


@app.route('/items', methods=["GET"])
@login_required
def get_items(payload): 
    items = Item.get_all()
    if items is None:
        return send_response(jsonify({'message': "Items were not found"}), 400)
    return send_response(jsonify({'items': items}), 200)


@app.route('/item', methods=["POST"])
@login_required
def set_item(payload):
    data = request.get_json()  # данные для добавления
    validated = Validate.required_params(data, [
        "name", "description",
        "id_category", "id_type"
    ])
    if not validated['status']:
        return jsonify({"message": "Data is not valid", "errors": validated['errors']}), 400

    # Use the user ID from the payload instead of requiring it in the request
    add = Item.query_add({
        "name": data['name'],
        "description": data['description'],
        "id_category": data['id_category'],
        "id_type": data['id_type'],
        "id_user": payload['id'],  # Use the authenticated user's ID
    })
    if not add:
        return send_response(jsonify({'message': "Item was not added"}), 400)
    return send_response(jsonify({'message': "Item was added"}), 200)


@app.route('/item/<int:item_id>', methods=["PUT"])
@login_required
def update_item(payload, item_id):
    item = Item.get_one(item_id)
    if not item:
        return jsonify({"message": "Item not found"}), 404

    if item['id_user'] != payload['id']:
        return jsonify({"message": "You don't have permission to update this item"}), 403

    data = request.get_json()


    required_fields = ["name", "description", "id_category", "id_type"]
    validated = Validate.required_params(data, required_fields)
    if not validated['status']:
        return jsonify({"message": "Data is not valid", "errors": validated['errors']}), 400

    if not Category.get_one(data['id_category']):
        return jsonify({"message": "Invalid category ID"}), 400
    if not Type.get_one(data['id_type']):
        return jsonify({"message": "Invalid type ID"}), 400

    update_data = {
        "name": data['name'],
        "description": data['description'],
        "id_category": data['id_category'],
        "id_type": data['id_type'],
    }

    update = Item.update_col(update_data, [['id', '=', item_id, 'value']])

    if update:
        updated_item = Item.get_one(item_id)
        return jsonify({
            "message": "Item updated successfully",
            "item": updated_item
        }), 200
    
    return jsonify({"message": "Failed to update item"}), 500


@app.route('/item/<int:item_id>', methods=["DELETE"])
@login_required
def delete_item(payload, item_id):
    item = Item.delete(item_id)
    if not item:
        return send_response(jsonify({'message': "Item was not deleted"}), 400)
    return send_response(jsonify({'message':"item was deleted successfully!"}), 200)



##########################################################################################################################################################################
#CATEGORY LIST
########################################################################################################################################################################

@app.route('/category/<int:category_id>', methods=["GET"])
@login_required
def get_category(payload, category_id):
    category = Category.get_one(category_id)
    if not category:
        return send_response(jsonify({'message': "category is not found"}), 400)
    return send_response(jsonify({'category': category}), 200)




@app.route('/categories', methods=["GET"])
@login_required
def get_categories(payload):
  categories = Category.get_all()
  if categories == None:
    return send_response(jsonify({'message':"Categories were not found"}), 400)
  return send_response(jsonify({'categories':categories}), 200)


@app.route('/category', methods=["POST"])
@login_required
def set_category(payload):
    data = request.get_json()  # данные для добавления
    validated = Validate.required_params(data, ["name"])
    if not validated['status']:
        return jsonify({"message": "Data is not valid", "errors": validated['errors']}), 400


    add = Category.query_add({
        "name": data['name'],
        "id_user": data['id_user'],})
    if not add:
        return send_response(jsonify({'message': "Category was not added"}), 400)
    return send_response(jsonify({'message': "Category was added"}), 200)


@app.route('/category/<int:category_id>', methods=["PUT"])
@login_required
def update_category(payload, category_id):
    category = Category.get_one(category_id)
    if not category:
        return jsonify({"message": "Category is not found"}), 404

    if category['id_user'] != payload['id']:
        return jsonify({"message": "You don't have permission to update this category"}), 403

    data = request.get_json()


    required_fields = ["name"]
    validated = Validate.required_params(data, required_fields)
    if not validated['status']:
        return jsonify({"message": "Data is not valid", "errors": validated['errors']}), 400
    
    update_data = {
        "name": data['name'],
        
    }

    update = Category.update_col(update_data, [['id', '=', category_id, 'value']])

    if update:
        updated_category = Category.get_one(category_id)
        return jsonify({
            "message": "Category updated successfully",
            "category": updated_category
        }), 200
    
    return jsonify({"message": "Failed to update category"}), 500


@app.route('/category/<int:category_id>', methods=["DELETE"])
@login_required
def delete_category(payload, category_id):
    category = Category.delete(category_id)
    if not category:
        return send_response(jsonify({'message': "Category was not deleted"}), 400)
    return send_response(jsonify({'message':"Category was deleted successfully!"}), 200)



##########################################################################################################################################################################
#TYPE LIST
########################################################################################################################################################################


@app.route('/type/<int:type_id>', methods=["GET"])
@login_required
def get_type(payload, type_id):
    type = Type.get_one(type_id)
    if not type:
        return send_response(jsonify({'message': "type is not found"}), 400)
    return send_response(jsonify({'type': type}), 200)




@app.route('/types', methods=["GET"])
@login_required
def get_types(payload):
  types = Type.get_all()
  if types == None:
    return send_response(jsonify({'message':"types were not found"}), 400)
  return send_response(jsonify({'types':types}), 200)


@app.route('/type', methods=["POST"])
@login_required
def set_type(payload):
    data = request.get_json()  # данные для добавления
    validated = Validate.required_params(data, ["name"])
    if not validated['status']:
        return jsonify({"message": "Data is not valid", "errors": validated['errors']}), 400


    add = Type.query_add({
        "name": data['name'],})
    if not add:
        return send_response(jsonify({'message': "type was not added"}), 400)
    return send_response(jsonify({'message': "type was added"}), 200)


@app.route('/type/<int:type_id>', methods=["PUT"])
@login_required
def update_type(payload, type_id):
    type = Type.get_one(type_id)
    if not type:
        return jsonify({"message": "type is not found"}), 404
    
    data = request.get_json()


    required_fields = ["name"]
    validated = Validate.required_params(data, required_fields)
    if not validated['status']:
        return jsonify({"message": "Data is not valid", "errors": validated['errors']}), 400
    
    update_data = {
        "name": data['name'],
        
    }

    update = Type.update_col(update_data, [['id', '=', type_id, 'value']])

    if update:
        updated_type = Type.get_one(type_id)
        return jsonify({
            "message": "type updated successfully",
            "type": updated_type
        }), 200
    
    return jsonify({"message": "Failed to update type"}), 500


@app.route('/type/<int:type_id>', methods=["DELETE"])
@login_required
def delete_type(payload, type_id):
    type = Type.delete(type_id)
    if not type:
        return send_response(jsonify({'message': "Type was not deleted"}), 400)
    return send_response(jsonify({'message':"Type was deleted successfully!"}), 200)



##########################################################################################################################################################################
#Statistics(?)
########################################################################################################################################################################

@app.route('/stat/user/<int:user_id>', methods=["GET"])
@login_required
def get_items_count(payload, user_id):
    if payload['id'] != user_id:
        return jsonify({"message": "You don't have permission to view this data"}), 403

    user_items = Item.query_get(
        get_params=["id"],
        fetch_mode="all",
        where=[['id_user', '=', user_id, 'value']]
    )

    if user_items is None:
        return jsonify({"message": "Failed to retrieve items"}), 500

    total_items = len(user_items)

    return jsonify({
        "user_id": user_id,
        "total_items": total_items
    }), 200


















if __name__ == '__main__':
  app.run()