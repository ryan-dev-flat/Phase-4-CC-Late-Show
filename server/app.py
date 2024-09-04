from flask import Flask, request, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource
from werkzeug.exceptions import NotFound

from models import db, Episode, Guest, Appearance

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)

class AllEpisodes(Resource):
    def get(self):
        try:
            episodes_dict = [e.to_dict(only=('id', 'date', 'number')) for e  in Episode.query.all()]
            response = make_response(episodes_dict, 200,)
            return response
        except:
            response = make_response({'error': f'Episode {id} not found.'}, 404)
            return response
api.add_resource(AllEpisodes, '/episodes')

class EpisodeDetail(Resource):
    def get(self, id):
        episode = Episode.query.get(id)
        if episode:
            guests = [
                {
                    "id": guest.id,
                    "name": guest.name,
                    "occupation": guest.occupation
                }
                for guest in episode.guests
                ]
            episode_dict = {
                "id": episode.id,
                "date": episode.date,
                "number": episode.number,
                "guests": guests
            }
            return make_response(episode_dict, 200)
        else:
            return make_response({"error": "404: Episode not found"}, 404)

api.add_resource(EpisodeDetail, '/episodes/<int:id>')

class OneEpisode(Resource):
    def delete(self, id):
        q = Episode.query.filter_by(id=id).first()
        if(not q):
            return make_response({'error': '404: Episode not found'}, 404)
        db.session.delete(q)
        db.session.commit()
        return make_response({}, 204)
api.add_resource(OneEpisode, '/episodes/<int:id>')

class AllGuests(Resource):
    def get(self):
        guests = Guest.query.all()
        docs_list = [g.to_dict(only=('id', 'name', 'occupation')) for g in guests]
        return make_response(docs_list, 200)

api.add_resource(AllGuests, '/guests')

class CreateAppearance(Resource):
    def post(self):

        data = request.get_json()

        rating = data.get('rating')
        episode_id = data.get('episode_id')
        guest_id = data.get('guest_id')

        
        if not (1 <= rating <= 5):
            raise ValueError('Raing must be between 1 and 5')

        episode = Episode.query.get(episode_id)
        guest = Guest.query.get(guest_id)

        if episode and guest:
            new_app = Appearance(rating=rating, episode_id=episode_id, guest_id=guest_id)
            db.session.add(new_app)
            db.session.commit()

            appearance_dict = {
                "id": new_app.id,
                "rating": new_app.rating,
                "episode_id": episode.id,
                "guest_id": guest.id,
                "episode": {
                    "id": episode.id,
                    "date": episode.date,
                    "number": episode.number
                },
                "guest": {
                    "id": guest.id,
                    "name": guest.name,
                    "occupation": guest.occupation
                }
            }
            return make_response(appearance_dict, 201)
        else:
            return make_response({"error": "400: Validation error."}, 400)


api.add_resource(CreateAppearance, '/appearances')


if __name__ == "__main__":
    app.run(port=5555, debug=True)