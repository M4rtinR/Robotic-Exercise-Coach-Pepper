import time

import numpy
import requests
from flask import Flask, request
from flask_restful import Resource, Api, reqparse
import json
import logging

from CoachingBehaviourTree import controller, nodes, config
from Policy.policy_wrapper import PolicyWrapper

app = Flask('policy_guide_api')
api = Api(app)

class TimestepCue(Resource):
    previous_shot_performance = None
    def post(self):
        if request.is_json:
            print("request is json")
            logging.debug("request is json")
            content = request.get_json()
            logging.debug(content)
            logging.info("Received data from app: {}".format(content))
            if 'goal_level' in content:
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
                    print('session goal setting controller values')
                    if 'feedback' in content:  # End of session
                        logging.debug('end of session')
                        config.score = float(content['score'][0:len(content['score']) - 1])
                        config.target = 5
                        config.performance = int(content['performance'])
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
                    elif 'stop' in content:
                        print("stop session")
                        config.stop_session = True  # High level global variable which will be checked at each node until session goal feedback is reached.
                        config.goal_level = config.SESSION_GOAL
                        config.phase = config.PHASE_END
                        config.set_count += 1
                        config.completed = config.COMPLETED_STATUS_TRUE
                        config.session_time = config.MAX_SESSION_TIME

                        new_data = {
                            'goal_level': 1,
                            'completed': config.completed,
                        }

                        return new_data, 200
                    else:
                        config.completed = config.COMPLETED_STATUS_UNDEFINED
                        config.goal_level = config.SESSION_GOAL
                        config.phase = config.PHASE_START
                        config.performance = None
                        # config.performance = content['performance']

                        while config.completed == config.COMPLETED_STATUS_UNDEFINED or config.shot is None:
                            pass

                        new_data = {
                            'goal_level': 1,
                            'completed': config.completed,
                            'shotSet': 0
                        }

                        print("sending: " + str(config.shot))
                        if not (config.shot == -1):
                            print("sending: " + str(config.shot_list_master.get(config.shot)))
                            new_data['shotType'] = config.shot_list_master.get(config.shot)
                            new_data['hand'] = config.hand

                        if not (config.stat == ""):
                            new_data['stat'] = config.stat

                        return new_data, 200

                elif int(content['goal_level']) == config.EXERCISE_GOAL:
                    logging.debug('shot goal setting controller values')
                    if 'feedback' in content:  # End of shot
                        logging.debug('end of shot')
                        config.score = float(content['score'][0:len(content['score']) - 1])
                        config.target = 5
                        config.performance = int(content['performance'])
                        config.goal_level = config.EXERCISE_GOAL
                        config.phase = config.PHASE_END
                        config.completed = config.COMPLETED_STATUS_FALSE

                        while config.completed == config.COMPLETED_STATUS_FALSE:  # or (config.shot is None and config.session_time < config.MAX_SESSION_TIME):
                            pass

                        new_data = {
                            'goal_level': "2",
                            'completed': str(config.completed)
                        }

                        if config.session_time < config.MAX_SESSION_TIME:
                            while not config.shot_confirmed or not len(config.shots_dealt_with) == 0:
                                pass
                            print("Sending shot type: " + str(config.hand) + str(config.shot))
                            new_data['shotType'] = config.shot_list_master.get(config.shot)
                            new_data['hand'] = config.hand
                        else:
                            new_data['final'] = "1"

                        return new_data, 200
                    elif 'stop' in content:
                        if config.expecting_action_goal:
                            config.stop_set = True  # High level global variable which will be checked at each node until set goal feedback loop is reached.

                        new_data = {
                            'goal_level': 2,
                            'completed': config.completed
                        }

                        return new_data, 200
                    else:
                        if content['impactSpeed'] == 'null':
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

                        else:
                            print('end of baseline set')

                            config.metric_score_list = []  # Reset the metric score list from last time.
                            print("setting config.score = " + content['score'])
                            config.score = float(content['score'])
                            accList = {}
                            scoreList = {}
                            print('Created accList')
                            racketPreparationStringList = content['racketPreparation'].split(", ")
                            print('Got racket prep list')
                            # config.metric_score_list.append(sum(racketPreparationList) / len(racketPreparationList))
                            # print('calculated racket prep average')
                            accList['racketPreparation'] = float(content['racketPreparationAcc'])
                            print('get racket prep acc')
                            scoreList['racketPreparation'] = float(content['racketPreparationScore'][:-1])
                            approachTimingStringList = content["approachTiming"].split(", ")
                            print('got approach timing list')
                            # config.metric_score_list.append(sum(approachTimingList) / len(approachTimingList))
                            # print('calculated approcah timimng average')
                            accList["approachTiming"] = float(content['approachTimingAcc'])
                            scoreList["approachTiming"] = float(content['approachTimingScore'])
                            print('got approach timing acc')
                            impactCutAngleStringList = content["impactCutAngle"].split(", ")
                            print('got impact cut angle list')
                            # config.metric_score_list.append(sum(impactCutAngleList) / len(impactCutAngleList))
                            # print('calculated impact cut angle average')
                            accList["impactCutAngle"] = float(content['impactCutAngleAcc'])
                            print('got impact cut angle acc')
                            scoreList["impactCutAngle"] = float(content['impactCutAngleScore'])
                            impactSpeedStringList = content["impactSpeed"].split(", ")
                            print('got impact speed list')
                            # config.metric_score_list.append(sum(impactSpeedList) / len(impactSpeedList))
                            # print('calculated impact speed average')
                            accList["impactSpeed"] = float(content['impactSpeedAcc'])
                            scoreList["impactSpeed"] = float(content['impactSpeedScore'])
                            print('got impact speed acc')
                            followThroughRollStringList = content["followThroughRoll"].split(", ")
                            print('got follow thorugh roll list')
                            # config.metric_score_list.append(sum(followThroughRollList) / len(followThroughRollList))
                            # print('calculated follow through roll average')
                            accList["followThroughRoll"] = float(content['followThroughRollAcc'])
                            print('got follow through roll acc')
                            scoreList["followThroughRoll"] = float(content['followThroughRollScore'])
                            followThroughTimeStringList = content["followThroughTime"].split(", ")
                            print('got gollow through time list')
                            # config.metric_score_list.append(sum(followThroughTimeList) / len(followThroughTimeList))
                            # print('calculated follow through time average')
                            accList["followThroughTime"] = float(content['followThroughTimeAcc'])
                            print('got follow through time acc')
                            scoreList["followThroughTime"] = float(content['followThroughTimeScore'])
                            config.stat_list = accList
                            config.metric_score_list = scoreList
                            print('sorted stat list')

                            print("populating lists with floats")
                            for i in range(len(racketPreparationStringList)):
                                if i == 0:
                                    print("first list element")
                                    racketPreparationFloatList = [float(racketPreparationStringList[i][1:])]
                                    print("first racket prep done")
                                    approachTimingFloatList = [float(approachTimingStringList[i][1:])]
                                    print("first approach timing done")
                                    impactCutAngleFloatList = [float(impactCutAngleStringList[i][1:])]
                                    print("first impact cut angle done")
                                    impactSpeedFloatList = [float(impactSpeedStringList[i][1:])]
                                    print("first impact speed done")
                                    followThroughRollFloatList = [float(followThroughRollStringList[i][1:])]
                                    print("first follow through roll done")
                                    followThroughTimeFloatList = [float(followThroughTimeStringList[i][1:])]
                                    print("first follow through time done")
                                elif i == len(racketPreparationStringList) - 1:
                                    print("last list element")
                                    racketPreparationFloatList.append(float(
                                        racketPreparationStringList[i][0:len(racketPreparationStringList[i]) - 1]))
                                    print("last racket prep done")
                                    approachTimingFloatList.append(float(
                                        approachTimingStringList[i][0:len(approachTimingStringList[i]) - 1]))
                                    print("last approach timing done")
                                    impactCutAngleFloatList.append(float(
                                        impactCutAngleStringList[i][0:len(impactCutAngleStringList[i]) - 1]))
                                    print("last impact cut angle done")
                                    impactSpeedFloatList.append(float(
                                        impactSpeedStringList[i][0:len(impactSpeedStringList[i]) - 1]))
                                    print("last impact speed done")
                                    followThroughRollFloatList.append(float(
                                        followThroughRollStringList[i][0:len(followThroughRollStringList[i]) - 1]))
                                    print("last follow thorugh roll done")
                                    followThroughTimeFloatList.append(float(
                                        followThroughTimeStringList[i][0:len(followThroughTimeStringList[i]) - 1]))
                                    print("last follow thorugh time done")
                                else:
                                    print("Regular element: " + str(i))
                                    racketPreparationFloatList.append(float(racketPreparationStringList[i]))
                                    print("racket prep done")
                                    approachTimingFloatList.append(float(approachTimingStringList[i]))
                                    print("approach timing done")
                                    impactCutAngleFloatList.append(float(impactCutAngleStringList[i]))
                                    print("impact cut angle done")
                                    impactSpeedFloatList.append(float(impactSpeedStringList[i]))
                                    print("impact speed done")
                                    followThroughRollFloatList.append(float(followThroughRollStringList[i]))
                                    print("follow through roll done")
                                    followThroughTimeFloatList.append(float(followThroughTimeStringList[i]))
                                    print("follow through time done")

                            print("calculating average of lists")
                            for list in [racketPreparationFloatList, approachTimingFloatList, impactCutAngleFloatList,
                                         impactSpeedFloatList, followThroughRollFloatList, followThroughTimeFloatList]:
                                config.metric_score_list.append(sum(list) / len(list))
                            print("list averages calculated")

                            config.goal_level = config.EXERCISE_GOAL
                            config.phase = config.PHASE_END
                            config.completed = config.COMPLETED_STATUS_TRUE

                            print("waiting for config.stat")
                            while config.stat_confirmed is False:
                                pass

                            print("returning stat data to app: " + config.stat)
                            config.stat_confirmed = False  # Reset stat_confirmed for next time.
                            new_data = {
                                'goal_level': '4',
                                'completed': str(config.completed),
                                'shotSet': '1',
                                'stat': config.stat
                            }
                        print("returning data to app: " + str(new_data))
                        return new_data, 200

                elif int(content['goal_level']) == config.STAT_GOAL:
                    print('stat goal setting controller values')
                    if 'feedback' in content:  # End of stat
                        print('end of stat')
                        print('content = ' + str(content))
                        scoreString = content['score']
                        if scoreString[-1] == "%":
                            scoreString = content['score'][:-1]
                        elif scoreString[-1] == "s":
                            scoreString = content['score'][:-5]
                        elif scoreString[-1] == "c":
                            print("Getting score string for mtrs\/sec")
                            scoreString = content['score'][:-9]
                            print("Got score string for mtrs\/sec = " + scoreString)
                        config.score = float(scoreString)
                        targetString = content['tgtValue']
                        if targetString[-1] == "%":
                            targetString = content['tgtValue'][:-1]
                        elif targetString[-1] == "s":
                            targetString = content['tgtValue'][:-5]
                        elif targetString[-1] == "c":
                            print("Getting targetString for mtrs\/sec")
                            targetString = content['tgtValue'][:-9]
                            print("Got targetString for mtrs\/sec = " + targetString)
                        config.target = float(targetString)
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

                        if config.stat_count == 2:
                            new_data["final"] = 1
                        else:
                            while config.stat_confirmed is False:
                                pass
                            print("New stat = " + str(config.stat))
                            new_data["stat"] = config.stat

                        return new_data, 200
                    else:
                        config.completed = config.COMPLETED_STATUS_UNDEFINED
                        config.goal_level = config.STAT_GOAL
                        config.phase = config.PHASE_START
                        if config.stat == -1:
                            config.stat = content['stat']
                        targetString = content['tgtValue']
                        if targetString[-1] == "%":
                            targetString = content['tgtValue'][:-1]
                        elif targetString[-1] == "s":
                            targetString = content['tgtValue'][:-5]
                        elif targetString[-1] == "c":
                            targetString = content['tgtValue'][:-9]
                        config.target = float(targetString)
                        # config.score = -1
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
                        print("returning from stat goal start")
                        return new_data, 200

                elif int(content['goal_level']) == config.SET_GOAL:  # Also represents baseline goal
                    '''if config.goal_level == config.BASELINE_GOAL:  # baseline goal feedback
                        config.performance = content['performance']
                        config.score = content['score']
                        config.goal_level = config.EXERCISE_GOAL
                    else:'''
                    config.dont_send_action_response = True
                    print('set goal setting controller values')

                    if 'score' in content:  # End of set
                        print('end of set')
                        print('content = ' + str(content))
                        scoreString = content['score']
                        if scoreString[-1] == "%":
                            scoreString = content['score'][:-1]
                        elif scoreString[-1] == "s":
                            scoreString = content['score'][:-5]
                        elif scoreString[-1] == "c":
                            print("Getting scoreString for mtrs\/sec")
                            scoreString = content['score'][:-9]
                            print("Got scoreString for mtrs\/sec = " + scoreString)
                        targetString = content['tgtValue']
                        if targetString[-1] == "%":
                            targetString = content['tgtValue'][:-1]
                        elif targetString[-1] == "s":
                            targetString = content['tgtValue'][:-5]
                        elif targetString[-1] == "c":
                            print("Getting targetString for mtrs\/sec")
                            targetString = content['tgtValue'][:-9]
                            print("Got targetString for mtrs\/sec = " + targetString)

                        print('got values from content')
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

                        if config.set_count == config.SETS_PER_STAT:
                            new_data["final"] = 1
                        print("returning new_data: " + str(new_data))
                        return new_data, 200

                    else:  # Start of set
                        print("Start of set")
                        config.goal_level = config.SET_GOAL
                        config.phase = config.PHASE_START
                        config.completed = config.COMPLETED_STATUS_UNDEFINED

                        print("Waiting")
                        while config.completed != config.COMPLETED_STATUS_FALSE:
                            pass

                        print("Setting data")
                        new_data = {
                            'goal_level': 4,
                            'completed': config.completed,
                            'shotSet': 1
                        }

                        print("Returning")
                        return new_data, 200

                elif int(content['goal_level']) == config.ACTION_GOAL:
                    config.shots_dealt_with.append("1")
                    if config.expecting_action_goal:
                        print('action goal setting controller values')
                        config.action_score = float(content['score'])
                        config.has_score_been_provided = False
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
                            print("updating config.performance: " + str(performanceValue))
                            config.performance = performanceValue            # Not perfect because we might have the same performance for set and action.
                        config.goal_level = config.ACTION_GOAL
                        config.shot_count += 1

                        self.previous_shot_performance = performanceValue

                        new_data = {
                            'goal_level': 5,
                            'completed': 1,
                            'shotSet': 1
                        }

                        if config.shot_count == config.SHOTS_PER_SET - 1:
                            print("Setting shot_setComplet = 1")
                            new_data['shotSetComplete'] = 1
                            # new_data['stat'] = config.stat
                        else:
                            new_data['shotSetComplete'] = 0

                    else:
                        print("Action goal not expected, not using data.")
                        logging.debug("Action goal not expected, not setting controller values.")
                        new_data = {
                            'goal_level': 5,
                            'completed': 1,
                            'shotSet': 1,
                            'shotSetComplete': 0
                        }

                    config.shots_dealt_with.pop(0)
                    print("sending shot response. Shots still to be dealt with: " + str(config.shots_dealt_with))
                    return new_data, 200

            elif 'override' in content:
                print("dealing with override in API")
                if content['override'] == "True":
                    config.override = True
                else:
                    config.override = False

            else:
                print("dealing with shot/stat selection in API")
                if 'shot_selection' in content:
                    shotWithSpaces = content['shot_selection'].replace('%20', ' ')
                    config.shot = shotWithSpaces
                    config.hand = content['hand']
                else:
                    config.stat = content['stat_selection'].replace('%20', ' ')
                    print("New stat = " + config.stat)
                config.override = False

        else:
            print("request not json")
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
