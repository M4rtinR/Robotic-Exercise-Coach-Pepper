from flask import Flask, request
from flask_restful import Resource, Api, reqparse
import pandas as pd
import ast
import firebase_admin
from firebase_admin import db
import json
import logging

from CoachingBehaviourTree import config
from Policy.policy_wrapper import PolicyWrapper

'''cred_obj = firebase_admin.credentials.Certificate(
    'racketware-policy-api-firebase-adminsdk-sych1-ac7425f5e6.json')
default_app = firebase_admin.initialize_app(cred_obj, {
    'databaseURL': 'https://racketware-policy-api-default-rtdb.firebaseio.com/'
})'''

app = Flask('policy_guide_api')
api = Api(app)
expecting_action_goal = False

class TimestepCue(Resource):
    previous_shot_performance = None
    def post(self):
        if request.is_json:
            logging.debug("request is json")
            content = request.get_json()
            logging.debug(content)
            logging.info("Received data from app: {}".format(content))
            if int(content['goal_level']) == config.PERSON_GOAL:
                # logging.info("Received data from app: {}".format(content))
                config.goal_level = config.PERSON_GOAL
                # config.name = content['name']  # Name was not working so removed here and will set it at the start of each session.
                config.sessions = int(content['sessions'])
                config.ability = int(content['ability'])
                config.completed = config.COMPLETED_STATUS_UNDEFINED

                while config.completed == config.COMPLETED_STATUS_UNDEFINED:
                    pass

                new_data = {
                    'goal_level': 0,
                    'completed': config.completed,
                    'shotSet': 0
                }

                return new_data, 200

            elif int(content['goal_level']) == config.SESSION_GOAL:
                logging.debug('session goal setting controller values')
                if 'feedback' in content:  # End of session
                    logging.debug('end of session')
                    config.performance = content['performance']
                    config.goal_level = config.SESSION_GOAL
                    config.phase = config.PHASE_END
                    config.completed = config.COMPLETED_STATUS_UNDEFINED

                    while config.completed == config.COMPLETED_STATUS_UNDEFINED:
                        pass

                    new_data = {
                        'goal_level': 1,
                        'completed': config.completed
                    }

                    return new_data, 200
                else:
                    config.completed = config.COMPLETED_STATUS_UNDEFINED
                    config.goal_level = config.SESSION_GOAL
                    config.phase = config.PHASE_START
                    config.performance = None
                    # config.performance = content['performance']

                    while config.completed == config.COMPLETED_STATUS_UNDEFINED:
                        pass

                    new_data = {
                        'goal_level': 1,
                        'completed': config.completed,
                        'shotSet': 0
                    }

                    if not (config.shot == -1):
                        new_data['shotType'] = config.shot
                        new_data['hand'] = config.hand

                    if not (config.stat == ""):
                        new_data['stat'] = config.stat

                    return new_data, 200

            elif int(content['goal_level']) == config.EXERCISE_GOAL:
                logging.debug('shot goal setting controller values')
                if 'feedback' in content:  # End of shot
                    logging.debug('end of shot')
                    config.score = content['score']
                    config.target = content['tgtValue']
                    config.performance = content['performance']
                    config.goal_level = config.EXERCISE_GOAL
                    config.phase = config.PHASE_END
                    config.completed = config.COMPLETED_STATUS_FALSE

                    while config.completed == config.COMPLETED_STATUS_FALSE:
                        pass

                    new_data = {
                        'goal_level': 2,
                        'completed': config.completed
                    }

                    return new_data, 200
                else:
                    config.completed = config.COMPLETED_STATUS_UNDEFINED
                    config.goal_level = config.EXERCISE_GOAL
                    config.phase = config.PHASE_START
                    config.score = None
                    config.performance = None

                    if config.shot == -1:
                        config.shot = content['shotType']
                        config.hand = content['hand']
                    '''if content['initialScore'] == "null":
                        config.score = None
                    else:
                        config.score = float(content['initialScore'])
                    if content['performance'] == "":
                        config.performance = None
                    else:
                        config.performance = int(config.performance)'''

                    while config.completed == config.COMPLETED_STATUS_UNDEFINED:
                        pass

                    new_data = {
                        'goal_level': 2,
                        'completed': config.completed,
                        'shotSet': 1
                    }

                    if not (config.stat == -1):
                        new_data['stat'] = config.stat

                    return new_data, 200

            elif int(content['goal_level']) == config.STAT_GOAL:
                logging.debug('stat goal setting controller values')
                if 'feedback' in content:  # End of stat
                    logging.debug('end of stat')
                    config.score = float(content['score'])
                    config.target = float(content['tgtValue'])
                    config.performance = int(content['performance'])
                    config.goal_level = config.STAT_GOAL
                    config.phase = config.PHASE_END
                    config.completed = config.COMPLETED_STATUS_UNDEFINED

                    while config.completed == config.COMPLETED_STATUS_UNDEFINED:
                        pass

                    new_data = {
                        'goal_level': 3,
                        'completed': config.completed
                    }

                    return new_data, 200
                else:
                    config.completed = config.COMPLETED_STATUS_UNDEFINED
                    config.goal_level = config.STAT_GOAL
                    config.phase = config.PHASE_START
                    if config.stat == -1:
                        config.stat = content['stat']
                    config.target = float(content['tgtValue'])
                    '''if content['performance'] == "":
                        config.performance = None
                    else:
                        config.performance = int(config.performance)'''
                    config.performance = None

                    while config.completed != config.COMPLETED_STATUS_FALSE:
                        pass

                    new_data = {
                        'goal_level': 3,
                        'completed': config.completed,
                        'shotSet': 0
                    }

                    return new_data, 200

            elif int(content['goal_level']) == config.SET_GOAL:  # Also represents baseline goal
                '''if config.goal_level == config.BASELINE_GOAL:  # baseline goal feedback
                    config.performance = content['performance']
                    config.score = content['score']
                    config.goal_level = config.EXERCISE_GOAL
                else:'''
                logging.debug('set goal setting controller values')
                if 'score' in content:  # End of set
                    logging.debug('end of set')
                    scoreString = content['score']
                    if scoreString[-1] == "%":
                        scoreString = content['score'][:-1]
                    elif scoreString[-1] == "s":
                        scoreString = content['score'][:-5]
                    targetString = content['tgtValue']
                    if targetString[-1] == "%":
                        targetString = content['tgtValue'][:-1]
                    elif targetString[-1] == "s":
                        targetString = content['tgtValue'][:-5]
                    config.avg_score = float(scoreString)
                    config.set_score_list.append(float(scoreString))
                    config.target = float(targetString)
                    if not content['performance'] == "":
                        config.performance = int(content['performance'])
                        config.set_performance_list.append(int(content['performance']))
                        # config.stat = content['stat']  # Let guide decide what stat to work on based on baseline set.
                        config.goal_level = config.SET_GOAL
                        config.phase = config.PHASE_END
                        config.completed = config.COMPLETED_STATUS_UNDEFINED

                        while config.completed == config.COMPLETED_STATUS_UNDEFINED:
                            pass

                    new_data = {
                        'goal_level': 4,
                        'completed': config.completed,
                        'shotSet': 1
                    }

                    return new_data, 200

                else:  # Start of set
                    config.goal_level = config.SET_GOAL
                    config.phase = config.PHASE_START
                    config.completed = config.COMPLETED_STATUS_UNDEFINED

                    while config.completed != config.COMPLETED_STATUS_FALSE:
                        pass

                    new_data = {
                        'goal_level': 4,
                        'completed': config.completed,
                        'shotSet': 1
                    }

                    return new_data, 200

            elif int(content['goal_level']) == config.ACTION_GOAL:
                #if expecting_action_goal:
                logging.debug('action goal setting controller values')
                config.action_score = float(content['score'])
                performanceValue = config.MET
                if content['performance'] == 'Very Low':
                    performanceValue = config.MUCH_REGRESSED
                elif content['performance'] == 'Very High':
                    performanceValue = config.REGRESSED_SWAP
                elif content['performance'] == 'Low':
                    performanceValue = config.REGRESSED
                elif content['performance'] == 'High':
                    performanceValue = config.MET
                elif content['performance'] == 'Under':
                    performanceValue = config.STEADY
                elif content['performance'] == 'Over':
                    performanceValue = config.IMPROVED
                elif content['performance'] == 'Good!':
                    performanceValue = config.MUCH_IMPROVED
                else:
                    logging.debug('no performanceValue found')
                if config.performance == self.previous_shot_performance:  # We haven't received the set goal feedback so can safely update config.performance
                    config.performance = performanceValue            # Not perfect because we might have the same performance for set and action.
                config.goal_level = config.ACTION_GOAL
                config.shot_count += 1
                config.completed = config.COMPLETED_STATUS_UNDEFINED

                self.previous_shot_performance = performanceValue

                while expecting_action_goal is False and not config.completed == config.COMPLETED_STATUS_TRUE:
                    pass

                new_data = {
                    'goal_level': 5,
                    'completed': 1,
                    'shotSet': 1
                }

                if config.shot_count == 29:
                    new_data['shotSetComplete'] = 1
                    new_data['stat'] = config.stat
                else:
                    new_data['shotSetComplete'] = 0

                '''else:
                    logging.info("Action goal not expected, not using data.")
                    logging.debug("Action goal not expected, not setting controller values.")
                    new_data = {
                        'goal_level': 5,
                        'completed': 1,
                        'shotSet': 1,
                        'shotSetComplete': 0
                    }'''

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
            logging.debug('recevied post request')
            if int(args['goal_level']) == config.PERSON_GOAL:
                logging.debug('player goal setting controller values')
                config.goal_level = config.PERSON_GOAL
                config.name = args['name']
                config.sessions = int(args['sessions'])
                config.ability = int(args['ability'])

                while config.completed == config.COMPLETED_STATUS_UNDEFINED:
                    pass

                return {args['goal_level']: config.completed}, 200

            elif int(args['goal_level']) == config.SESSION_GOAL:
                logging.debug('session goal setting controller values')
                config.completed = config.COMPLETED_STATUS_UNDEFINED
                config.goal_level = config.SESSION_GOAL
                config.performance = int(args['performance'])

                while config.completed == config.COMPLETED_STATUS_UNDEFINED:
                    pass

                new_data = {
                    'completed': config.completed
                }

                if not(config.shot == -1):
                    new_data['shot'] = config.shot

                return {args['goal_level']: new_data}, 200

            elif int(args['goal_level']) == config.EXERCISE_GOAL:
                logging.debug('shot goal setting controller values')
                config.completed = config.COMPLETED_STATUS_UNDEFINED
                config.goal_level = config.EXERCISE_GOAL
                config.performance = int(args['performance'])

                while config.completed == config.COMPLETED_STATUS_UNDEFINED:
                    pass

                new_data = {
                    'completed': config.completed
                }

                if not (config.stat == -1):
                    new_data['stat'] = config.stat

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
