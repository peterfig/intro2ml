from flask import Flask, request
from flask_restful import Resource, Api
from recommender import CollegeRecommender

college = CollegeRecommender()

class Query(Resource):
    def get(self):
        query_dict = {
            "state": request.args.get('home_state'),
            "math": int(request.args.get('math')),
            "verbal": int(request.args.get('verbal')),
            "writing": int(request.args.get('writing')),
            "out_of_state": request.args.get('out_of_state'),
            "budget": int(request.args.get('budget'))
        }
        return college.doQuery(query_dict)


app = Flask('college')
api = Api(app)
api.add_resource(Query, '/')

if __name__ == '__main__':
    app.run(debug=True)
