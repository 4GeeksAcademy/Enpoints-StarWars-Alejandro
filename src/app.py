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
from models import db, User, People, Planets, Favorite
#from models import Person

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

# Ver todos los usuarios
@app.route('/user', methods=['GET'])
def get_user():
    user_list = User.query.all()
    response = [user.serialize() for user in user_list]

    if not user_list:
        return jsonify({"Error": "Not user"}), 400

    return jsonify(response), 200

# Ver los personaje
@app.route('/people', methods=['GET'])
def get_people():
    people_list = People.query.all()
    response = [person.serialize() for person in people_list]

    if not people_list:
        return jsonify({"Error": "Not character"}), 404

    return jsonify(response), 200

# Ver el personaje indicado
@app.route('/people/<int:character_id>', methods=['GET'])
def get_character(character_id):
    people_list = People.query.filter(People.id == character_id).all()
    response = [person.serialize() for person in people_list]

    if not people_list:
        return jsonify({"Error": "Character not found"}), 400
    
    return jsonify(response), 200

# Ver el planeta
@app.route('/planets', methods=['GET'])
def get_planets():
    planet_list = Planets.query.all()
    response = [planet.serialize() for planet in planet_list]

    if not planet_list:
        return jsonify({"Error": "Not planet"}), 400

    return jsonify(response), 200

# Ver el planeta indicado
@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet_list = Planets.query.filter(Planets.id == planet_id).all()
    response = [planet.serialize() for planet in planet_list]

    if not planet_list:
        return jsonify({"Error": "Planet not found"}), 400
    
    return jsonify(response), 200

# Ver todos los favoritos
@app.route('/favorite', methods=['GET'])
def get_favorite():
    favorite_query = Favorite.query.all()
    response = [favorite.serialize() for favorite in favorite_query]

    if not favorite_query:
        return jsonify({"Error": "Favorite not found"}), 400

    return jsonify(response), 200

# Ver los favoritos del usuario seleccionado 
@app.route('/<string:user_name>/favorite', methods=['GET'])
def get_user_favorite(user_name):
    user = User.query.filter_by(name=user_name).first()

    if not user:
        return jsonify({"Error": "User not found"}), 400
    
    response = [favorite.serialize() for favorite in user.favorite]

    return jsonify(response), 200

# Añadir un planeta que por defecto se añade con el primer usuario y
# pasandole un nombre favortio dinamico.
# Sin tener que escribir un body en el post JSON.
@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def post_planet_favorite(planet_id):
    query_planet = Planets.query.get(planet_id)
    if not query_planet:
        return jsonify({"Error": "Planet not found"}), 400 

    duplicates = Favorite.query.filter_by(user_id=1, planet_id=planet_id).first()
    if duplicates:
        return jsonify({"Error": "Ya tienes este planeta en favoritos"}), 400
    
    user_currently = User.query.get(1)
    if not user_currently:
        return jsonify({"Error": "User not found"}), 400

    new_favorite = Favorite(
        name=f'Favorte {user_currently}', 
        user_id=1, people_id=None, 
        planet_id=planet_id
    )
    db.session.add(new_favorite)
    db.session.commit()

    favorite_query = Favorite.query.all()
    response = [favorite.serialize() for favorite in favorite_query]
    return jsonify(response), 200

# Añadir un personaje favorito pero esta vez si que tienes que escribir el body JSON
@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def post_people_favorite(people_id):
    data = request.get_json()

    favorite_name = data.get("favorite_name")
    user_name = data.get("user_name")
    planet_name = data.get("planet_name")

    pleople_query = People.query.get(people_id)
    if not pleople_query:
        return jsonify({"Error": "Not found character"}), 400
    
    user_query = User.query.filter_by(name=user_name).first()
    if not user_query:
        return jsonify({"Error": "Not found user"}), 400
    
    planet_query = Planets.query.filter_by(planet=planet_name).first()
    if not planet_query:
        return jsonify({"Error": "Not found planet"}), 400
    
    duplicates = Favorite.query.filter_by(people_id=people_id).first()
    if duplicates:
        return jsonify({"Error": "Ya tienes este personaje en favoritos"}), 400
    
    new_favorite = Favorite(
        name=favorite_name,
        user_id=user_query.id,
        people_id=people_id,
        planet_id=planet_query.id,
    )

    # Ejemplo de lo que habria que pasar por el body del POST
    # {
    #     "favorite_name": "Mi mercurio para user 2",
    #     "user_name": "user2",
    #     "planet_name": "mercurio"
    # }

    db.session.add(new_favorite)
    db.session.commit()

    return jsonify(new_favorite.serialize()), 201

# Eliminar Planeta por id
@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_planet(planet_id):
    favorite_id = Favorite.query.filter_by(planet_id=planet_id).first()

    if not favorite_id:
        return jsonify({"Error": "Not found planet"}), 400
    
    db.session.delete(favorite_id)
    db.session.commit()
    return jsonify({"Succes": "Se ha eliminado el planeta de favoritos"}), 200

# Eliminar Personaje por id
@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_people(people_id):
    favorite_id = Favorite.query.filter_by(people_id=people_id).first()

    if not favorite_id:
        return jsonify({"Error": "Not found people"}), 400
    
    db.session.delete(favorite_id)
    db.session.commit()
    return jsonify({"Succes": "Se ha eliminado el personaje de favoritos"}), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
