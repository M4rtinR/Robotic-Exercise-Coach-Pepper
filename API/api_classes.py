from flask import Flask, request
from flask_restful import Resource, Api, reqparse
import pandas as pd
import ast
import firebase_admin
from firebase_admin import db
import json
import logging

from CoachingBehaviourTree import controller
from Policy.policy_wrapper import PolicyWrapper

'''cred_obj = firebase_admin.credentials.Certificate(
    'racketware-policy-api-firebase-adminsdk-sych1-ac7425f5e6.json')
default_app = firebase_admin.initialize_app(cred_obj, {
    'databaseURL': 'https://racketware-policy-api-default-rtdb.firebaseio.com/'
})'''

app = Flask('policy_guide_api')
api = Api(app)

class TimestepCue(Resource):
    def post(self):
        if request.is_json:
            print("request is json")
            content = request.get_json()
            print(content)
            logging.info("Received data from app: {}".format(content))
            if int(content['goal_level']) == PolicyWrapper.PERSON_GOAL:
                logging.info("Received data from app: {}".format(content))
                controller.goal_level = PolicyWrapper.PERSON_GOAL
                controller.name = content['name']
                controller.sessions = int(content['sessions'])
                controller.ability = int(content['ability'])
                controller.completed = controller.COMPLETED_STATUS_UNDEFINED

                while controller.completed == controller.COMPLETED_STATUS_UNDEFINED:
                    pass

                new_data = {
                    'completed': controller.completed,
                    'shotSet': 0
                }

                return new_data, 200

            elif int(content['goal_level']) == PolicyWrapper.SESSION_GOAL:
                print('session goal setting controller values')
                if 'feedback' in content:  # End of session
                    print('end of session')
                    controller.performance = content['performance']
                    controller.goal_level = PolicyWrapper.SESSION_GOAL
                    controller.phase = PolicyWrapper.PHASE_END
                    controller.completed = controller.COMPLETED_STATUS_UNDEFINED

                    while controller.completed == controller.COMPLETED_STATUS_UNDEFINED:
                        pass

                    new_data = {
                        'completed': controller.completed
                    }

                    return new_data, 200
                else:
                    controller.completed = controller.COMPLETED_STATUS_UNDEFINED
                    controller.goal_level = PolicyWrapper.SESSION_GOAL
                    controller.phase = PolicyWrapper.PHASE_START
                    controller.performance = content['performance']

                    while controller.completed == controller.COMPLETED_STATUS_UNDEFINED:
                        pass

                    new_data = {
                        'completed': controller.completed,
                        'shotSet': 0
                    }

                    if not (controller.shot == -1):
                        new_data['shotType'] = controller.shot
                        new_data['hand'] = controller.hand

                    if not (controller.stat == ""):
                        new_data['stat'] = controller.stat

                    return new_data, 200

            elif int(content['goal_level']) == PolicyWrapper.EXERCISE_GOAL:
                print('shot goal setting controller values')
                if 'feedback' in content:  # End of shot
                    print('end of shot')
                    controller.score = content['score']
                    controller.target = content['tgtValue']
                    controller.performance = content['performance']
                    controller.goal_level = PolicyWrapper.EXERCISE_GOAL
                    controller.phase = PolicyWrapper.PHASE_END
                    controller.completed = controller.COMPLETED_STATUS_FALSE

                    while controller.completed == controller.COMPLETED_STATUS_FALSE:
                        pass

                    new_data = {
                        'completed': controller.completed
                    }

                    return new_data, 200
                else:
                    controller.completed = controller.COMPLETED_STATUS_UNDEFINED
                    controller.goal_level = PolicyWrapper.EXERCISE_GOAL
                    controller.phase = PolicyWrapper.PHASE_START

                    if controller.shot == -1:
                        controller.shot = content['shotType']
                        controller.hand = content['hand']
                    if content['initialScore'] == "null":
                        controller.score = None
                    else:
                        controller.score = float(content['initialScore'])
                    if content['performance'] == "":
                        controller.performance = None
                    else:
                        controller.performance = int(controller.performance)

                    while controller.completed == controller.COMPLETED_STATUS_UNDEFINED:
                        pass

                    new_data = {
                        'completed': controller.completed,
                        'shotSet': 1
                    }

                    if not (controller.stat == -1):
                        new_data['stat'] = controller.stat

                    return new_data, 200

            elif int(content['goal_level']) == PolicyWrapper.STAT_GOAL:
                print('stat goal setting controller values')
                if 'feedback' in content:  # End of stat
                    print('end of stat')
                    controller.score = content['score']
                    controller.target = float(content['tgtValue'])
                    controller.performance = content['performance']
                    controller.goal_level = PolicyWrapper.STAT_GOAL
                    controller.phase = PolicyWrapper.PHASE_END
                    controller.completed = controller.COMPLETED_STATUS_UNDEFINED

                    while controller.completed == controller.COMPLETED_STATUS_UNDEFINED:
                        pass

                    new_data = {
                        'completed': controller.completed
                    }

                    return new_data, 200
                else:
                    controller.completed = controller.COMPLETED_STATUS_UNDEFINED
                    controller.goal_level = PolicyWrapper.STAT_GOAL
                    controller.phase = PolicyWrapper.PHASE_START
                    if controller.stat == -1:
                        controller.stat = content['stat']
                    controller.target = float(content['tgtValue'])
                    if content['performance'] == "":
                        controller.performance = None
                    else:
                        controller.performance = int(controller.performance)

                    while controller.completed == controller.COMPLETED_STATUS_UNDEFINED:
                        pass

                    new_data = {
                        'completed': controller.completed,
                        'shotSet': 0
                    }

                    return new_data, 200

            elif int(content['goal_level']) == PolicyWrapper.SET_GOAL:  # Also represents baseline goal
                '''if controller.goal_level == PolicyWrapper.BASELINE_GOAL:  # baseline goal feedback
                    controller.performance = content['performance']
                    controller.score = content['score']
                    controller.goal_level = PolicyWrapper.EXERCISE_GOAL
                else:'''
                print('set goal setting controller values')
                if 'score' in content:  # End of set
                    print('end of set')
                    controller.avg_score = float(content['score'])
                    controller.set_score_list.append(float(content['score']))
                    controller.target = float(content['tgtValue'])
                    controller.performance = int(content['performance'])
                    controller.set_performance_list.append(int(content['performance']))
                    # controller.stat = content['stat']  # Let guide decide what stat to work on based on baseline set.
                    controller.goal_level = PolicyWrapper.SET_GOAL
                    controller.phase = PolicyWrapper.PHASE_END
                    controller.completed = controller.COMPLETED_STATUS_UNDEFINED

                    while controller.completed == controller.COMPLETED_STATUS_UNDEFINED:
                        pass

                    new_data = {
                        'completed': controller.completed,
                        'shotSet': 1
                    }

                    return new_data, 200
                else:  # Start of set
                    controller.goal_level = PolicyWrapper.SET_GOAL
                    controller.phase = PolicyWrapper.PHASE_START
                    controller.completed = controller.COMPLETED_STATUS_UNDEFINED

                    while controller.completed != controller.COMPLETED_STATUS_FALSE:
                        pass

                    new_data = {
                        'completed': controller.completed,
                        'shotSet': 1
                    }

                    return new_data, 200

            elif int(content['goal_level']) == PolicyWrapper.ACTION_GOAL:
                print('action goal setting controller values')
                controller.action_score = float(content['score'])
                performanceValue = PolicyWrapper.MET
                if content['performance'] == 'Very Low':
                    performanceValue = PolicyWrapper.MUCH_REGRESSED
                elif content['performance'] == 'Very High':
                    performanceValue = PolicyWrapper.REGRESSED_SWAP
                elif content['performance'] == 'Low':
                    performanceValue = PolicyWrapper.REGRESSED
                elif content['performance'] == 'High':
                    performanceValue = PolicyWrapper.MET
                elif content['performance'] == 'Under':
                    performanceValue = PolicyWrapper.STEADY
                elif content['performance'] == 'Over':
                    performanceValue = PolicyWrapper.IMPROVED
                elif content['performance'] == 'Good!':
                    performanceValue = PolicyWrapper.MUCH_IMPROVED
                else:
                    print('no performanceValue found')
                controller.performance = performanceValue
                controller.goal_level = PolicyWrapper.ACTION_GOAL
                controller.shot_count += 1

                new_data = {
                    'completed': 1,
                    'shotSet': 0
                }

                if controller.shot_count >= 29:
                    new_data['shotSetComplete'] = 1
                    new_data['stat'] = controller.stat
                else:
                    new_data['shotSetComplete'] = 0

                return new_data, 200

        else:

            parser = reqparse.RequestParser()

            parser.add_argument('goal_level', required=True)
            parser.add_argument('score', required=False)        # For each shot
            parser.add_argument('target', required=False)       # Stat/Set goal
            parser.add_argument('avg_score', required=False)    # Stat/Set goal
            parser.add_argument('performance', required=False)  # Session/Shot goal (performance in last session)
            parser.add_argument('shot', required=False)         # Shot goal
            parser.add_argument('stat', required=False)         # Stat goal
            parser.add_argument('name', required=False)         # Player goal
            parser.add_argument('sessions', required=False)     # Player goal (total number of sessions for this user)
            parser.add_argument('ability', required=False)      # Player goal

            args = parser.parse_args()  # parse arguments to dictionary
            print('recevied post request')
            if int(args['goal_level']) == PolicyWrapper.PERSON_GOAL:
                print('player goal setting controller values')
                controller.goal_level = PolicyWrapper.PERSON_GOAL
                controller.name = args['name']
                controller.sessions = int(args['sessions'])
                controller.ability = int(args['ability'])

                while controller.completed == controller.COMPLETED_STATUS_UNDEFINED:
                    pass

                return {args['goal_level']: controller.completed}, 200

            elif int(args['goal_level']) == PolicyWrapper.SESSION_GOAL:
                print('session goal setting controller values')
                controller.completed = controller.COMPLETED_STATUS_UNDEFINED
                controller.goal_level = PolicyWrapper.SESSION_GOAL
                controller.performance = int(args['performance'])

                while controller.completed == controller.COMPLETED_STATUS_UNDEFINED:
                    pass

                new_data = {
                    'completed': controller.completed
                }

                if not(controller.shot == -1):
                    new_data['shot'] = controller.shot

                return {args['goal_level']: new_data}, 200

            elif int(args['goal_level']) == PolicyWrapper.EXERCISE_GOAL:
                print('shot goal setting controller values')
                controller.completed = controller.COMPLETED_STATUS_UNDEFINED
                controller.goal_level = PolicyWrapper.EXERCISE_GOAL
                controller.performance = int(args['performance'])

                while controller.completed == controller.COMPLETED_STATUS_UNDEFINED:
                    pass

                new_data = {
                    'completed': controller.completed
                }

                if not (controller.stat == -1):
                    new_data['stat'] = controller.stat

                return {args['goal_level']: new_data}, 200

        # create new dataframe containing new values
        '''new_data = {
            'name': args['name'],
            'skill': args['skill'],
            'sessions': args['sessions']
        }'''

        # TODO: Might have to use userID instead of push to retrieve the user info in the controller.
        # new_post_ref = ref.push(new_data)

        # return {new_post_ref.key: new_data}, 200

'''class Users(Resource):
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
api.add_resource(Actions, '/actions')'''

api.add_resource(TimestepCue, '/cue')

if __name__ == '__main__':
    app.run()  # run our Flask app
