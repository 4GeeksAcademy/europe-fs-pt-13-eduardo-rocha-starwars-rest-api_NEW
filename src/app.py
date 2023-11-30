"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planets, Vehicles, UserFavorites


app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

# USER-----------------------------------------------------------------------------------------------

#Get all users
@app.route('/users', methods=['GET'])
def get_users():
    #access all registered users
    users_querys = User.query.all()
    #map users to convert into an array and return an array of objects
    results = list(map(lambda user: user.serialize(), users_querys))

    #is users empty, returns error code
    if results == []:
        return jsonify({"msg": "No registered users"}), 404
    
    #display results of access
    response_body = {
        "msg": "These are the registered users", 
        "results": results
    }
    return jsonify(response_body), 200

#DGet user by id
@app.route('/users/<int:user_id>', methods=['GET'])
def get_one_user(user_id):
    #filter all users by id
    user_query = User.query.filter_by(id = user_id).first()

    if user_query is None:
        return jsonify({"msg": "User with id: " + str(user_id) + " doesn't exist"}), 404
    
    response_body = {
        "msg": "User is", 
        "result": user_query.serialize()
    }

    return jsonify(response_body), 200

#Returns ALL People
@app.route('/people', methods=['GET'])
def get_people():
    people_querys = People.query.all()
    results = list(map(lambda people: people.serialize(), people_querys))
    
    if results == []:
        return jsonify({"msg": "No hay personajes registrados"}), 404
    
    response_body = {
        "msg": "Hola, estos son los personajes", 
        "results": results
    }

    return jsonify(response_body), 200

#Return Person by id
@app.route('/people/<int:people_id>', methods=['GET'])
def get_one_person(people_id):
    person_query = People.query.filter_by(id = people_id).first()

    if person_query is None:
        return jsonify({"msg": "Person with id: " + str(people_id) + " doesn't exist"}), 404
    
    response_body = {
        "msg": "Person is:", 
        "result": person_query.serialize()
    }

    return jsonify(response_body), 200

#Return ALL Planets
@app.route('/planets', methods=['GET'])
def get_planets():
    planets_querys = Planets.query.all()
    results = list(map(lambda planet: planet.serialize(), planets_querys))

    if results == []:
        return jsonify({"msg": "No Planets registered"}), 404
    
    response_body = {
        "msg": "These are the Planets", 
        "results": results
    }

    return jsonify(response_body), 200

#Return Planet by id
@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_one_planet(planet_id):
    planet_query = Planets.query.filter_by(id = planet_id).first()

    if planet_query is None:
        return jsonify({"msg": "Planet with id: " + str(planet_id) + " doesn't exist"}), 404
    
    response_body = {
        "msg": "Planet is:", 
        "result": planet_query.serialize()
    }

    return jsonify(response_body), 200

#Returns ALL Vehicles
@app.route('/vehicles', methods=['GET'])
def get_vehicles():
    vehicles_querys = Vehicles.query.all()
    results = list(map(lambda vehicle: vehicle.serialize(), vehicles_querys))

    if results == []:
        return jsonify({"msg": "No Vehicles regstered"}), 404
    
    response_body = {
        "msg": "These are the Vehicles", 
        "results": results
    }

    return jsonify(response_body), 200

#returns Vehicle by id
@app.route('/vehicles/<int:vehicle_id>', methods=['GET'])
def get_one_vehicle(vehicle_id):
    vehicle_query = Vehicles.query.filter_by(id = vehicle_id).first()

    if vehicle_query is None:
        return jsonify({"msg": "Vehicle with id: " + str(vehicle_id) + " doesn't exist"}), 404
    
    response_body = {
        "msg": "This is the Vehicle", 
        "result": vehicle_query.serialize()
    }

    return jsonify(response_body), 200

#Returns ALL User Favorites
@app.route('/users/<int:id>/fav', methods=['GET'])
def get_user_fav(id):
    favs_querys = UserFavorites.query.filter_by(user_id = id)
    results = list(map(lambda fav: fav.serialize(), favs_querys))
    user_query = User.query.filter_by(id = id).first()
    if user_query is None:
        return jsonify({"msg": "User isn't registered"}), 404
    if results == []:
        return jsonify({"msg": "No Favoritos registered"}), 404
    
    response_body = {
        "msg": "These are the User Favorites", 
        "results": results
    }

    return jsonify(response_body), 200

#Add a Planet to User Favorites
@app.route('/fav/planets/<int:planeta_id>', methods=['POST'])
def add_planet_fav(planet_id):
    
    request_body = request.get_json(force=True)

    user_query = User.query.filter_by(id = request_body["user_id"]).first()
    if user_query is None:
        return jsonify({"msg": "User isn't registered"}), 404
    
    planet_query = Planets.query.filter_by(id = planet_id).first()
    if planet_query is None:
        return jsonify({"msg": "Planeta doesn't exist"}), 404
    
    fav = UserFavorites.query.filter_by(user_id = request_body["user_id"]).filter_by(planets_id = planet_id).first() 
    if fav: 
        return jsonify({"msg": "Planet is already a favorite"}), 404
    
    new_planet_fav = UserFavorites(user_id = request_body["user_id"], planets_id = planet_id)
    db.session.add(new_planet_fav)
    db.session.commit()

    request_body = {
        "msg": "Planet added as favorite"
    }
    return jsonify(request_body), 200

#Delete Planet from User Favorites
@app.route('/fav/planets/<int:planeta_id>', methods=['DELETE'])
def delete_planet_fav(planet_id):
    
    request_body = request.get_json(force=True)

    user_query = User.query.filter_by(id = request_body["user_id"]).first()
    if user_query is None:
        return jsonify({"msg": "User isn't registered"}), 404
    
    planet_query = Planets.query.filter_by(id = planet_id).first()
    if planet_query is None:
        return jsonify({"msg": "Planet trying to delete doesn't exist"}), 404
    
    fav = UserFavorites.query.filter_by(user_id = request_body["user_id"]).filter_by(planets_id = planet_id).first()
    if fav is None:
        return jsonify({"msg": "Planet trying to delete isn't a favorite"}), 404

    db.session.delete(fav)
    db.session.commit()

    request_body = {
        "msg": "Planet deleted from favorites"
    }
    return jsonify(request_body), 200

#Add a Person to User Favorites
@app.route('/fav/people/<int:person_id>', methods=['POST'])
def add_person_fav(person_id):
    
    request_body = request.get_json(force=True)

    user_query = User.query.filter_by(id = request_body["user_id"]).first() 
    if user_query is None:
        return jsonify({"msg": "User ins't registred"}), 404
    
    people_query = People.query.filter_by(id = person_id).first()
    if people_query is None:
        return jsonify({"msg": "Person doesn't exist"}), 404
    
    fav = UserFavorites.query.filter_by(user_id = request_body["user_id"]).filter_by(people_id = person_id).first()
    if fav: 
        return jsonify({"msg": "Person is already in favorites"}), 404
    
    new_person_fav = UserFavorites(user_id = request_body["user_id"], people_id = person_id)
    db.session.add(new_person_fav)
    db.session.commit()

    request_body = {
        "msg": "Person added to favorites"
    }
    return jsonify(request_body), 200

#Delete Person from User Favorites
@app.route('/fav/people/<int:person_id>', methods=['DELETE'])
def delete_person_fav(person_id):
    
    request_body = request.get_json(force=True)

    user_query = User.query.filter_by(id = request_body["user_id"]).first()
    if user_query is None:
        return jsonify({"msg": "User doen't exist"}), 404
    
    people_query = People.query.filter_by(id = person_id).first() 
    if people_query is None:
        return jsonify({"msg": "Person to delete doesn't existe"}), 404
    
    fav = UserFavorites.query.filter_by(user_id = request_body["user_id"]).filter_by(people_id = person_id).first()
    if fav is None:
        return jsonify({"msg": "Person to delete isn't in favorites"}), 404

    db.session.delete(fav)
    db.session.commit()

    request_body = {
        "msg": "Person deleted from favorites"
    }
    return jsonify(request_body), 200


#Add a Vehicle to User Favorites
@app.route('/fav/vehicles/<int:vehicle_id>', methods=['POST'])
def add_vehicle_fav(vehicle_id):
    
    request_body = request.get_json(force=True)

    user_query = User.query.filter_by(id = request_body["user_id"]).first() 
    if user_query is None:
        return jsonify({"msg": "User doesn't exist"}), 404
  
    vehicles_query = Vehicles.query.filter_by(id = vehicle_id).first()
    if vehicles_query is None:
        return jsonify({"msg": "Vehicle doesn't exist"}), 404
    
    fav = UserFavorites.query.filter_by(user_id = request_body["user_id"]).filter_by(vehicles_id = vehicle_id).first()
    if fav: 
        return jsonify({"msg": "Vehicle already in favories"}), 404
    
    new_vehicle_fav = Fav(user_id = request_body["user_id"], vehicles_id = vehicle_id)
    db.session.add(new_vehicle_fav)
    db.session.commit()

    request_body = {
        "msg": "Vehicle added to favorites"
    }
    return jsonify(request_body), 200

#Delete a Vehicle from User Favorites
@app.route('/fav/vehicles/<int:vehicle_id>', methods=['DELETE'])
def delete_vehicle_fav(vehicle_id):
    
    request_body = request.get_json(force=True)

    user_query = User.query.filter_by(id = request_body["user_id"]).first()
    if user_query is None:
        return jsonify({"msg": "User isn't registered"}), 404
    
    people_query = Vehicles.query.filter_by(id = vehicle_id).first() 
    if people_query is None:
        return jsonify({"msg": "Vehicle to delete doesn't exist"}), 404
    
    fav = UserFavorites.query.filter_by(user_id = request_body["user_id"]).filter_by(vehicles_id = vehicle_id).first()
    if fav is None:
        return jsonify({"msg": "Vehicle to delete isn't in favorites"}), 404

    db.session.delete(fav)
    db.session.commit()

    request_body = {
        "msg": "Vehcle deleted from favorites"
    }
    return jsonify(request_body), 200


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
