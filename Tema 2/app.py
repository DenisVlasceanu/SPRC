from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from sqlalchemy.sql import func

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Countries(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    country_name = db.Column(db.String(64), index=True, unique=True)
    latitude = db.Column(db.Float, index=True)
    longitude = db.Column(db.Float, index=True)
    cities_cascade = db.relationship('Cities', backref='countries', cascade='all, delete-orphan', lazy=True)

class Cities(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'), nullable=False, index=True)
    city_name = db.Column(db.String(64), index=True)
    latitude = db.Column(db.Float, index=True)
    longitude = db.Column(db.Float, index=True)
    temperatures = db.relationship('Temperatures', backref='cities', cascade='all, delete-orphan', lazy=True)
    __table_args__ = (db.UniqueConstraint('country_id', 'city_name', name='_country_city_uc'),)

class Temperatures(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Float, index=True)
    timestamp = db.Column(db.DateTime(timezone=True), server_default=func.now(), index=True)
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id'), nullable=False, index=True)
    __table_args__ = (db.UniqueConstraint('city_id', 'timestamp', name='_city_timestamp_uc'),)


def int_to_float(x):
    if isinstance(x, float):
        return x
    elif isinstance(x, int):
        return x + 0.0
    else:
        return float('inf')


@app.route('/')
def index():
    return 'Hello, there\nGeneral Kenobi'









# POST /api/countries
@app.route('/api/countries', methods=['POST'])
def add_country():
    data = request.get_json()
    if not data or not 'nume' in data or not 'lat' in data or not 'lon' in data:
        return jsonify({"error": "Bad Request"}), 400

    if data['nume'] == None or data['lat'] == None or data['lon'] == None:
        return jsonify({"error": "Cannot Have NULL Values In Body"}), 400

    if not isinstance(data['nume'], str) or int_to_float(data['lat']) == float('inf') or int_to_float(data['lon']) == float('inf'):
        return jsonify({"error": "Incorrect Value Type"}), 400

    if Countries.query.filter_by(country_name=data['nume']).first():
        return jsonify({"error": "Country Already Exists"}), 409

    new_country = Countries(
        country_name=data['nume'],
        latitude=data['lat'],
        longitude=data['lon']
    )
    db.session.add(new_country)
    db.session.commit()
    return jsonify({"id": new_country.id}), 201


# GET /api/countries
@app.route('/api/countries', methods=['GET'])
def get_countries():
    countries = Countries.query.all()
    return jsonify([{
        "id": country.id,
        "nume": country.country_name,
        "lat": country.latitude,
        "lon": country.longitude
    } for country in countries]), 200


# PUT /api/countries/<int:id>
@app.route('/api/countries/<int:id>', methods=['PUT'])
def update_country(id):
    data = request.get_json()
    if not data or not 'id' in data or not 'nume' in data or not 'lat' in data or not 'lon' in data:
        return jsonify({"error": "Bad Request"}), 400

    if data['id'] == None or data['nume'] == None or data['lat'] == None or data['lon'] == None:
        return jsonify({"error": "Cannot Have NULL Values In Body"}), 400

    if not isinstance(data['id'], int) or not isinstance(data['nume'], str) or int_to_float(data['lat']) == float('inf') or int_to_float(data['lon']) == float('inf'):
        return jsonify({"error": "Incorrect Value Type"}), 400

    if data['id'] != id:
        return jsonify({"error": "URL ID and Body ID don't match"}), 400

    country = Countries.query.get(id)
    if not country:
        return jsonify({"error": "Not Found"}), 404

    if Countries.query.filter_by(country_name=data['nume']).first():
        if country.country_name == data['nume']:
            country.latitude = data['lat']
            country.longitude = data['lon']
            db.session.commit()
            return jsonify({"success": True}), 200
        else:
            return jsonify({"error": "Country Already Exists With Different ID"}), 409

    country.country_name = data['nume']
    country.latitude = data['lat']
    country.longitude = data['lon']
    db.session.commit()
    return jsonify({"success": True}), 200


# DELETE /api/countries/<int:id>
@app.route('/api/countries/<int:id>', methods=['DELETE'])
def delete_country(id):
    if not isinstance(id, int):
        return jsonify({"error": "Invalid ID"}), 400

    country = Countries.query.get(id)
    if not country:
        return jsonify({"error": "Not Found"}), 404

    db.session.delete(country)
    db.session.commit()
    return jsonify({"success": True}), 200










# POST /api/cities
@app.route('/api/cities', methods=['POST'])
def add_city():
    data = request.get_json()
    if not data or not 'idTara' in data or not 'nume' in data or not 'lat' in data or not 'lon' in data:
        return jsonify({"error": "Bad Request"}), 400

    if data['idTara'] == None or data['nume'] == None or data['lat'] == None or data['lon'] == None:
        return jsonify({"error": "Cannot Have NULL Values In Body"}), 400

    if not isinstance(data['idTara'], int) or not isinstance(data['nume'], str) or int_to_float(data['lat']) == float('inf') or int_to_float(data['lon']) == float('inf'):
        return jsonify({"error": "Incorrect Value Type"}), 400

    country = Countries.query.get(data['idTara'])
    if not country:
        return jsonify({"error": "Country Not Found"}), 404

    existing_city = Cities.query.filter_by(country_id=data['idTara'], city_name=data['nume']).first()
    if existing_city:
        return jsonify({"error": "City Within Country Already Exists"}), 409

    new_city = Cities(
        country_id=data['idTara'],
        city_name=data['nume'],
        latitude=data['lat'],
        longitude=data['lon']
    )
    db.session.add(new_city)
    db.session.commit()
    return jsonify({"id": new_city.id}), 201


# GET /api/cities
@app.route('/api/cities', methods=['GET'])
def get_cities():
    cities = Cities.query.all()
    return jsonify([{
        "id": city.id,
        "idTara": city.country_id,
        "nume": city.city_name,
        "lat": city.latitude,
        "lon": city.longitude
    } for city in cities]), 200


# GET /api/cities/country/<int:idTara>
@app.route('/api/cities/country/<int:idTara>', methods=['GET'])
def get_cities_by_country(idTara):
    cities = Cities.query.filter_by(country_id=idTara).all()
    return jsonify([{
        "id": city.id,
        "idTara": city.country_id,
        "nume": city.city_name,
        "lat": city.latitude,
        "lon": city.longitude
    } for city in cities]), 200


# PUT /api/cities/<int:id>
@app.route('/api/cities/<int:id>', methods=['PUT'])
def update_city(id):
    data = request.get_json()
    if not data or not 'id' in data or not 'idTara' in data or not 'nume' in data or not 'lat' in data or not 'lon' in data:
        return jsonify({"error": "Bad Request"}), 400

    if data['id'] == None or data['idTara'] == None or data['nume'] == None or data['lat'] == None or data['lon'] == None:
        return jsonify({"error": "Cannot Have NULL Values In Body"}), 400

    if not isinstance(data['id'], int) or not isinstance(data['idTara'], int) or not isinstance(data['nume'], str) or int_to_float(data['lat']) == float('inf') or int_to_float(data['lon']) == float('inf'):
        return jsonify({"error": "Incorrect Value Type"}), 400

    if data['id'] != id:
        return jsonify({"error": "URL ID and Body ID don't match"}), 400

    city = Cities.query.get(id)
    if not city:
        return jsonify({"error": "City Not Found"}), 404

    country = Countries.query.get(data['idTara'])
    if not country:
        return jsonify({"error": "Country Not Found"}), 404

    if Cities.query.filter_by(country_id=data['idTara'], city_name=data['nume']).first():
        if city.country_id == data['idTara'] and city.city_name == data['nume']:
            city.latitude = data['lat']
            city.longitude = data['lon']
            db.session.commit()
            return jsonify({"success": True}), 200
        else:
            return jsonify({"error": "City Within Country Already Exists"}), 409

    city.country_id = data['idTara']
    city.city_name = data['nume']
    city.latitude = data['lat']
    city.longitude = data['lon']
    db.session.commit()
    return jsonify({"success": True}), 200


# DELETE /api/cities/<int:id>
@app.route('/api/cities/<int:id>', methods=['DELETE'])
def delete_city(id):
    if not isinstance(id, int):
        return jsonify({"error": "Invalid ID"}), 400

    city = Cities.query.get(id)
    if not city:
        return jsonify({"error": "Not Found"}), 404

    db.session.delete(city)
    db.session.commit()
    return jsonify({"success": True}), 200










# POST /api/temperatures
@app.route('/api/temperatures', methods=['POST'])
def add_temperature():
    data = request.get_json()
    if not data or not 'idOras' in data or not 'valoare' in data:
        return jsonify({"error": "Bad Request"}), 400

    if data['idOras'] == None or data['valoare'] == None:
        return jsonify({"error": "Cannot Have NULL Values In Body"}), 400

    if not isinstance(data['idOras'], int) or int_to_float(data['valoare']) == float('inf'):
        return jsonify({"error": "Incorrect Value Type"}), 400

    city = Cities.query.get(data['idOras'])
    if not city:
        return jsonify({"error": "City Not Found"}), 404

    new_temperature = Temperatures(
        city_id=data['idOras'],
        value=data['valoare']
    )
    db.session.add(new_temperature)
    db.session.commit()
    return jsonify({"id": new_temperature.id}), 201


# GET /api/temperatures
@app.route('/api/temperatures', methods=['GET'])
def get_temperatures():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    from_date = request.args.get('from')
    until_date = request.args.get('until')

    query = Temperatures.query

    if lat and not lon:
        cities = Cities.query.filter_by(latitude=lat).all()
        direct_city_ids = [city.id for city in cities]
        countries = Countries.query.filter_by(latitude=lat).all()
        country_city_ids = []
        for country in countries:
            cities = Cities.query.filter_by(country_id=country.id).all()
            country_city_ids = country_city_ids + [city.id for city in cities]
        city_ids = direct_city_ids + country_city_ids
        query = query.filter(Temperatures.city_id.in_(city_ids))
    if not lat and lon:
        cities = Cities.query.filter_by(longitude=lon).all()
        direct_city_ids = [city.id for city in cities]
        countries = Countries.query.filter_by(longitude=lon).all()
        country_city_ids = []
        for country in countries:
            cities = Cities.query.filter_by(country_id=country.id).all()
            country_city_ids = country_city_ids + [city.id for city in cities]
        city_ids = direct_city_ids + country_city_ids
        query = query.filter(Temperatures.city_id.in_(city_ids))
    if lat and lon:
        cities = Cities.query.filter_by(latitude=lat, longitude=lon).all()
        direct_city_ids = [city.id for city in cities]
        countries = Countries.query.filter_by(latitude=lat, longitude=lon).all()
        country_city_ids = []
        for country in countries:
            cities = Cities.query.filter_by(country_id=country.id).all()
            country_city_ids = country_city_ids + [city.id for city in cities]
        city_ids = direct_city_ids + country_city_ids
        query = query.filter(Temperatures.city_id.in_(city_ids))

    if from_date:
        query = query.filter(Temperatures.timestamp >= from_date)
    if until_date:
        query = query.filter(Temperatures.timestamp <= until_date)

    temperatures = query.all()
    return jsonify([{
        "id": temp.id,
        "valoare": temp.value,
        "timestamp": temp.timestamp
    } for temp in temperatures]), 200


# GET /api/temperatures/cities/<int:id_oras>
@app.route('/api/temperatures/cities/<int:id_oras>', methods=['GET'])
def get_temperatures_by_city(id_oras):
    from_date = request.args.get('from')
    until_date = request.args.get('until')

    query = Temperatures.query.filter_by(city_id=id_oras)

    if from_date:
        query = query.filter(Temperatures.timestamp >= from_date)
    if until_date:
        query = query.filter(Temperatures.timestamp <= until_date)

    temperatures = query.all()
    return jsonify([{
        "id": temp.id,
        "valoare": temp.value,
        "timestamp": temp.timestamp
    } for temp in temperatures]), 200


# GET /api/temperatures/countries/<int:id_tara>
@app.route('/api/temperatures/countries/<int:id_tara>', methods=['GET'])
def get_temperatures_by_country(id_tara):
    from_date = request.args.get('from')
    until_date = request.args.get('until')

    cities = Cities.query.filter_by(country_id=id_tara).all()
    city_ids = [city.id for city in cities]
    query = Temperatures.query.filter(Temperatures.city_id.in_(city_ids))

    if from_date:
        query = query.filter(Temperatures.timestamp >= from_date)
    if until_date:
        query = query.filter(Temperatures.timestamp <= until_date)

    temperatures = query.all()
    return jsonify([{
        "id": temp.id,
        "valoare": temp.value,
        "timestamp": temp.timestamp
    } for temp in temperatures]), 200


# PUT /api/temperatures/<int:id>
@app.route('/api/temperatures/<int:id>', methods=['PUT'])
def update_temperature(id):
    data = request.get_json()
    if not data or not 'id' in data or not 'idOras' in data or not 'valoare' in data:
        return jsonify({"error": "Bad Request"}), 400

    if data['id'] == None or data['idOras'] == None or data['valoare'] == None:
        return jsonify({"error": "Cannot Have NULL Values In Body"}), 400

    if not isinstance(data['id'], int) or not isinstance(data['idOras'], int) or int_to_float(data['valoare']) == float('inf'):
        return jsonify({"error": "Incorrect Value Type"}), 400

    if data['id'] != id:
        return jsonify({"error": "URL ID and Body ID don't match"}), 400

    temperature = Temperatures.query.get(id)
    if not temperature:
        return jsonify({"error": "Temperature Not Found"}), 404

    city = Cities.query.get(data['idOras'])
    if not city:
        return jsonify({"error": "City Not Found"}), 404

    temperature.city_id = data['idOras']
    temperature.value = data['valoare']
    db.session.commit()
    return jsonify({"success": True}), 200


# DELETE /api/temperatures/<int:id>
@app.route('/api/temperatures/<int:id>', methods=['DELETE'])
def delete_temperature(id):
    if not isinstance(id, int):
        return jsonify({"error": "Invalid ID"}), 400

    temperature = Temperatures.query.get(id)
    if not temperature:
        return jsonify({"error": "Not Found"}), 404

    db.session.delete(temperature)
    db.session.commit()
    return jsonify({"success": True}), 200







if __name__ == '__main__':
    app.run(host='0.0.0.0')
