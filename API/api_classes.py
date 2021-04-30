from flask import Flask
from flask_restful import Resource, Api, reqparse
import pandas as pd
import ast
import firebase_admin
from firebase_admin import db

cred_obj = firebase_admin.credentials.Certificate(
    'racketware-policy-api-firebase-adminsdk-sych1-ac7425f5e6.json')
default_app = firebase_admin.initialize_app(cred_obj, {
    'databaseURL': 'https://racketware-policy-api-default-rtdb.firebaseio.com/'
})

app = Flask('policy_guide_api')
api = Api(app)


class Users(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('userID', required=True)
        args = parser.parse_args()

        ref = db.reference("/Users")
        users = ref.get()

        if args['userID'] in [key for key in users]:
            user_ref = db.reference("/Users/" + args['userID'])
            user = user_ref.get()

            return user, 200
        else:
            return {
                       'message': f"'{args['userID']}' user not found."
                   }, 404

    def post(self):
        parser = reqparse.RequestParser()

        parser.add_argument('name', required=True)
        parser.add_argument('skill', required=True)
        parser.add_argument('sessions', required=True)

        args = parser.parse_args()  # parse arguments to dictionary

        ref = db.reference("/Users")

        # create new dataframe containing new values
        new_data = {
            'name': args['name'],
            'skill': args['skill'],
            'sessions': args['sessions']
        }

        # TODO: Might have to use userID instead of push to retrieve the user info in the controller.
        new_post_ref = ref.push(new_data)

        return {new_post_ref.key: new_data}, 200

    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('userID', required=True)
        parser.add_argument('name', required=False)
        parser.add_argument('skill', required=False)
        parser.add_argument('sessions', required=False)

        args = parser.parse_args()

        ref = db.reference("/Users")
        users = ref.get()

        if args['userID'] in [key for key in users]:
            user_ref = db.reference("/Users/" + args['userID'])
            user = user_ref.get()

            updated_data = {}
            updated = 0

            if not (args['name'] is None):
                ref.child(args['userID']).update({'name': args['name']})
                updated_data['name'] = args['name']
                updated = 1
            if not (args['skill'] is None):
                ref.child(args['userID']).update({'skill': args['skill']})
                updated_data['skill'] = args['skill']
                updated = 1
            if not (args['sessions'] is None):
                ref.child(args['userID']).update({'sessions': args['sessions']})
                updated_data['sessions'] = args['sessions']
                updated = 1

            if updated:
                return {args['userID']: updated_data}, 200
            else:
                return {
                           'message': f"'{args['userID']}' invalid arguments."
                       }, 500

        else:
            return {
                       'message': f"'{args['userID']}' user not found."
                   }, 404


class Goals(Resource):
    # controller requests new goal and guide posts new goal

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('userID', required=True)
        args = parser.parse_args()

        ref = db.reference("/Users")
        users = ref.get()

        if args['userID'] in [key for key in users]:
            goals_ref = db.reference("/Users/" + args['userID'] + "/Goals")
            goals = goals_ref.get()

            return goals, 200
        else:
            return {
                       'message': f"'{args['userID']}' user not found."
                   }, 404

    def post(self):
        # controller will post a goal request
        parser = reqparse.RequestParser()

        parser.add_argument('userID', required=True)
        parser.add_argument('goal_type', required=True)
        parser.add_argument('shotOrStat', required=False)

        args = parser.parse_args()  # parse arguments to dictionary

        ref = db.reference("/Users")
        users = ref.get()

        if args['userID'] in [key for key in users]:

            # create new dataframe containing new values
            new_data = {
                'goal_type': args['goal_type'],
            }

            if not(args['shotOrStat'] is None):
                new_data['shotOrStat'] = args['shotOrStat']

            ref.child(args['userID']).child('Goals').push(new_data)

            return new_data, 200
        else:
            return {
                       'message': f"'{args['userID']}' user not found."
                   }, 404

    def put(self):
        # guide will put new information in the goal once it has created it and controller will update completed once
        # the correct stage of the behaviour tree has been reached.
        parser = reqparse.RequestParser()
        parser.add_argument('userID', required=True)
        parser.add_argument('goalID', required=True)
        parser.add_argument('completed', required=True)
        parser.add_argument('performance', required=False)
        parser.add_argument('target', required=False)
        parser.add_argument('score', required=False)

        args = parser.parse_args()

        ref = db.reference("/Users")
        users = ref.get()

        if args['userID'] in [key for key in users]:
            goals_ref = db.reference("/Users/" + args['userID'] + "/Goals")
            goals = goals_ref.get()

            if args['goalID'] in [key for key in goals]:

                updated_data = {}
                updated = 0

                if not (args['completed'] is None):
                    goals_ref.child(args['goalID']).update({'completed': args['completed']})
                    updated_data['completed'] = args['completed']
                    updated = 1

                if not (args['performance'] is None):
                    goals_ref.child(args['goalID']).update({'performance': args['performance']})
                    updated_data['performance'] = args['performance']
                    updated = 1

                if not (args['target'] is None):
                    goals_ref.child(args['goalID']).update({'target': args['target']})
                    updated_data['target'] = args['target']
                    updated = 1

                if not (args['score'] is None):
                    goals_ref.child(args['goalID']).update({'score': args['score']})
                    updated_data['score'] = args['score']
                    updated = 1

                if updated:
                    return {args['goalID']: updated_data}, 200
                else:
                    return {
                               'message': f"'{args['goalID']}' invalid arguments."
                           }, 500
            else:
                return {
                           'message': f"'{args['goalID']}' goal not found."
                       }, 404
        else:
            return {
                       'message': f"'{args['userID']}' user not found."
                   }, 404


class Actions(Resource):
    # guide posts every time shot is played or goal has been created

    def get(self):
        # controller will get the actions
        parser = reqparse.RequestParser()
        parser.add_argument('userID', required=True)
        parser.add_argument('goalID', required=True)
        args = parser.parse_args()

        ref = db.reference("/Users")
        users = ref.get()

        if args['userID'] in [key for key in users]:
            goals_ref = db.reference("/Users/" + args['userID'] + "/Goals")
            goals = goals_ref.get()

            if args['goalID'] in [key for key in goals]:
                actions_ref = db.reference("/Users/" + args['userID'] + "/Goals/" + args['goalID'] + "/Actions")
                actions = actions_ref.get()

                return actions, 200
            else:
                return {
                           'message': f"'{args['goalID']}' goal not found."
                       }, 404
        else:
            return {
                       'message': f"'{args['userID']}' user not found."
                   }, 404

    def post(self):
        # guide will post an action every time the user hits a shot
        parser = reqparse.RequestParser()

        parser.add_argument('userID', required=True)
        parser.add_argument('goalID', required=True)
        parser.add_argument('score', required=True)
        parser.add_argument('target', required=True)

        args = parser.parse_args()  # parse arguments to dictionary

        ref = db.reference("/Users")
        users = ref.get()

        if args['userID'] in [key for key in users]:
            goals_ref = db.reference("/Users/" + args['userID'] + "/Goals")
            goals = goals_ref.get()

            if args['goalID'] in [key for key in goals]:
                # create new dataframe containing new values
                new_data = {
                    'score': args['score'],
                    'target': args['target']
                }

                new_post_ref = goals_ref.child(args['goalID']).child('Actions').push(new_data)

                return {new_post_ref.key: new_data}, 200
            else:
                return {
                           'message': f"'{args['goalID']}' goal not found."
                       }, 404
        else:
            return {
                       'message': f"'{args['userID']}' user not found."
                   }, 404

    def delete(self):
        # guide will delete all actions before posting a new one so that the controller is always up to date with the interaction
        parser = reqparse.RequestParser()

        parser.add_argument('userID', required=True)
        parser.add_argument('goalID', required=True)

        args = parser.parse_args()  # parse arguments to dictionary

        ref = db.reference("/Users")
        users = ref.get()

        if args['userID'] in [key for key in users]:
            goals_ref = db.reference("/Users/" + args['userID'] + "/Goals")
            goals = goals_ref.get()

            if args['goalID'] in [key for key in goals]:
                actions_ref = db.reference("/Users/" + args['userID'] + "/Goals/" + args['goalID'] + "/Actions")
                actions = actions_ref.get()

                if not(actions is None):

                    for action_key in actions:
                        actions_ref.child(action_key).set({})

                    return {actions_ref.key: actions}, 200
                else: return {
                           'message': f"no actions available to delete."
                       }, 404

            else:
                return {
                           'message': f"'{args['goalID']}' goal not found."
                       }, 404
        else:
            return {
                       'message': f"'{args['userID']}' user not found."
                   }, 404


api.add_resource(Users, '/users')
api.add_resource(Goals, '/goals')
api.add_resource(Actions, '/actions')

if __name__ == '__main__':
    app.run()  # run our Flask app
