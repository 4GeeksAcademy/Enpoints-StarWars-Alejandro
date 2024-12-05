from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    is_active = db.Column(db.Boolean(), nullable=False)

    favorite = db.relationship('Favorite', back_populates='user')

    def __repr__(self):
        return f'{self.name}'

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
        }

class People(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    character = db.Column(db.String(255), unique=True, nullable=False)

    favorite = db.relationship('Favorite', back_populates='people')

    def __repr__(self):
        return f'<People {self.character}>'

    def serialize(self):
        return {
            "id": self.id,
            "character": self.character
        }

class Planets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    planet = db.Column(db.String(255), unique=True, nullable=False)
    
    favorite = db.relationship('Favorite', back_populates='planet')

    def __repr__(self):
        return f'<Planets {self.planet}>'

    def serialize(self):
        return {
            "id": self.id,
            "planet": self.planet
        }

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    people_id = db.Column(db.Integer, db.ForeignKey('people.id'), nullable=True)
    planet_id = db.Column(db.Integer, db.ForeignKey('planets.id'), nullable=False)

    user = db.relationship('User', back_populates='favorite')
    people = db.relationship('People', back_populates='favorite')
    planet = db.relationship('Planets', back_populates='favorite')

    def __repr__(self):
        return f'<Favorite {self.name}>'

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "user_name": self.user.name if self.user else None,
            "people_name": self.people.character if self.people else None,
            "planet_name": self.planet.planet if self.planet else None,
        }
