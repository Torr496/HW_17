# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class MovieSchema(Schema):
    id = fields.Int(dump_only=True)
    text = fields.Str()
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()


class GenreSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


class DirectorSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


api = Api(app)
movie_ns = api.namespace("movie")
directors_ns = api.namespace("director")
genres_ns = api.namespace("genre")

movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)

genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)

director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)


@movie_ns.route('/')
class MovieViews(Resource):
    def get(self):
        director_id = request.args.get('director_id')
        genre_id = request.args.get('genre_id')
        if director_id and genre_id:
            movies = Movie.query.filter_by(director_id=director_id, genre_id=genre_id).all()
        elif director_id:
            movies = Movie.query.filter_by(director_id=director_id).all()
        elif genre_id:
            movies = Movie.query.filter_by(genre_id=genre_id).all()
        else:
            movies = Movie.query.all()
        if movies:
            return movies_schema.dump(movies), 200
        else:
            return "",404


@movie_ns.route('/<int:nid>')
class MovieView(Resource):
    def get(self, nid):
        movie = Movie.query.get(nid)
        if movie:
            return movie_schema.dump(movie), 200
        else:
            return "", 404


@directors_ns.route("/")
class DirectorPost(Resource):
    def post(self):
        req_json = request.json
        new_director = Genre(**req_json)
        with db.session.begin():
            db.session.add(new_director)
            db.session.commit()
        return "",201


@directors_ns.route("/<int:uid>")
class DirectorView(Resource):

    def put(self, uid: int):
        director = Director.query.get(uid)
        if director:
            req_json = request.json
            director.name = req_json.get("name")
            db.session.add(director)
            db.session.commit()
            return "", 200
        else:
            return "",404

    def delete(self, uid: int):
        director = Director.query.get(uid)
        if director:
            db.session.delete(director)
            db.session.commit()
            return "", 200
        else:
            return "",404


@genres_ns.route("/<int:uid>")
class GenreView(Resource):

    def put(self, uid: int):
        genre = Genre.query.get(uid)
        if genre:
            req_json = request.json
            genre.name = req_json.get("name")
            db.session.add(genre)
            db.session.commit()
            return "", 200
        else:
            return "",404

    def delete(self, uid: int):
        genre = Genre.query.get(uid)
        if genre:
            db.session.delete(genre)
            db.session.commit()
            return "", 200
        else:
            return "",404


if __name__ == '__main__':
    app.run(debug=True)
