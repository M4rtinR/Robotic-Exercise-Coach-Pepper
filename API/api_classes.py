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
            logging.debug("request is json")
            logging.debug("request is json")
            content = request.get_json()
            logging.debug(content)
            logging.info("Received data from app: {}".format(content))
            if 'goal_level' in content:
                if int(content['goal_level']) == config.PERSON_GOAL:
                    # logging.info("Received data from app: {}".format(content))
                    config.goal_level = config.PERSON_GOAL
                    # config.name = content['name']  # Name was not working so removed here and will set it at the start of each session.
                    # config.sessions = int(content['sessions'])
                    # config.ability = int(content['ability'])
                    config.completed = config.COMPLETED_STATUS_UNDEFINED

                    while config.completed == config.COMPLETED_STATUS_UNDEFINED:
                        pass

                    new_data = {
                        'goal_level': 0,
                        'completed': config.completed,
                        'shotSet': 0
                    }
                    
                    logging.info("Returning data to app: " + str(new_data))
                    return new_data, 200

                elif int(content['goal_level']) == config.SESSION_GOAL:
                    logging.debug('session goal setting controller values')
                    if 'feedback' in content:  # End of session
                        logging.debug('end of session')
                        config.score = float(content['score'][0:len(content['score']) - 1])
                        config.target = 5
                        config.performance = int(content['performance'])
                        config.goal_level = config.SESSION_GOAL
                        config.phase = config.PHASE_END
                        config.completed = config.COMPLETED_STATUS_UNDEFINED
                        config.session_finished = True

                        while config.completed == config.COMPLETED_STATUS_UNDEFINED:
                            pass

                        new_data = {
                            'goal_level': 1,
                            'completed': config.completed
                        }

                        logging.info("Returning data to app: " + str(new_data))
                        return new_data, 200
                    elif 'stop' in content:
                        logging.info("Stop session selected by user.")
                        if config.goal_level == config.ACTION_GOAL and config.during_baseline_goal:
                            config.stop_session_on_baseline = True
                        else:
                            config.stop_set = True  # High level global variable which will be checked at each node until session goal feedback is reached.
                            config.pause_display = True
                            config.goal_level = config.EXERCISE_GOAL
                            # config.phase = config.PHASE_END
                            # config.set_count += 1
                            # config.completed = config.COMPLETED_STATUS_TRUE
                            # config.session_time = config.MAX_SESSION_TIME
                            config.MAX_SESSION_TIME = 1  # Session will stop because time is now > MAX_SESSION_TIME

                        new_data = {
                            'goal_level': 1,
                            'completed': config.completed,
                        }

                        logging.info("Returning data to app: " + str(new_data))
                        return new_data, 200
                    else:
                        logging.debug("Start of session")
                        config.completed = config.COMPLETED_STATUS_UNDEFINED
                        config.goal_level = config.SESSION_GOAL
                        config.phase = config.PHASE_START
                        config.performance = None
                        # config.performance = content['performance']

                        while config.completed == config.COMPLETED_STATUS_UNDEFINED or config.shot is None or not config.shot_confirmed:
                            pass

                        new_data = {
                            'goal_level': 1,
                            'completed': config.completed,
                            'shotSet': 0
                        }

                        logging.debug("sending: " + str(config.shot))
                        config.used_shots.append("" + config.hand + config.shot)
                        if not (config.shot == -1):
                            logging.debug("sending: " + str(config.shot_list_master.get(config.shot)))
                            new_data['shotType'] = config.shot_list_master.get(config.shot)
                            new_data['hand'] = config.hand

                        if not (config.stat == ""):
                            new_data['stat'] = config.stat

                        logging.info("Returning data to app: " + str(new_data))
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
                        config.shot_finished = True

                        while config.completed == config.COMPLETED_STATUS_FALSE:  # or (config.shot is None and config.session_time < config.MAX_SESSION_TIME):
                            pass

                        new_data = {
                            'goal_level': "2",
                            'completed': str(config.completed)
                        }

                        logging.debug("config.tidying = " + str(config.tidying) + ", len(config.shots_dealt_with) = " + str(len(config.shots_dealt_with)) + ", config.stat_confirmed = " + str(config.stat_confirmed) + ", config.stat_count = " + str(config.stat_count))
                        while not config.tidying and ((not config.shot_confirmed or not len(config.shots_dealt_with) == 0) or (not config.stat_confirmed and config.stat_count <= config.STATS_PER_SHOT and config.stat_count != 0)):
                            pass

                        config.stat_confirmed = False

                        if not config.tidying:
                            logging.debug("Sending shot type: " + str(config.hand) + str(config.shot))
                            new_data['shotType'] = config.shot_list_master.get(config.shot)
                            new_data['hand'] = config.hand
                        else:
                            logging.debug("Sending final")
                            new_data['final'] = "1"

                        logging.info("Returning data to app: " + str(new_data))
                        return new_data, 200
                    elif 'stop' in content:  # Stop current set.
                        logging.info("Stop set selected by the user.")
                        if config.expecting_action_goal:
                            if config.goal_level == config.ACTION_GOAL and config.during_baseline_goal:
                                config.stop_on_baseline = True
                            else:
                                config.stop_set = True  # High level global variable which will be checked at each node until set goal feedback loop is reached.
                                config.goal_level = config.EXERCISE_GOAL  # Set to exercise goal so that we wait for end of set feedback from app.
                                config.double_set_count_feedback = 0
                                config.double_set_count_start = 0
                                config.expecting_double_set = True

                        new_data = {
                            'goal_level': 2,
                            'completed': config.completed
                        }

                        logging.info("Returning data to app: " + str(new_data))
                        return new_data, 200
                    else:
                        if content['impactSpeed'] == 'null':
                            logging.debug("api classes, exercise goal received")
                            config.completed = config.COMPLETED_STATUS_UNDEFINED
                            logging.debug("Setting config.goal_level to EXERCISE_GOAL")
                            config.goal_level = config.EXERCISE_GOAL
                            config.phase = config.PHASE_START
                            # config.score = None
                            # config.performance = None

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
                            logging.debug('end of baseline set')

                            config.metric_score_list = []  # Reset the metric score list from last time.
                            logging.debug("setting config.score = " + content['score'])
                            config.score = float(content['score'])
                            accList = {}
                            scoreList = {}
                            targetList = {}
                            logging.debug('Created accList')
                            racketPreparationStringList = content['racketPreparation'].split(", ")
                            logging.debug('Got racket prep list')
                            # config.metric_score_list.append(sum(racketPreparationList) / len(racketPreparationList))
                            # logging.debug('calculated racket prep average')
                            accList['racketPreparation'] = float(content['racketPreparationAcc'])
                            logging.debug('get racket prep acc')
                            scoreList['racketPreparation'] = float(content['racketPreparationScore'][:-1])
                            targetList['racketPreparation'] = float(content['racketPreparationTarget'][:-1])
                            approachTimingStringList = content["approachTiming"].split(", ")
                            logging.debug('got approach timing list')
                            # config.metric_score_list.append(sum(approachTimingList) / len(approachTimingList))
                            # logging.debug('calculated approcah timimng average')
                            accList["approachTiming"] = float(content['approachTimingAcc'])
                            scoreList["approachTiming"] = float(content['approachTimingScore'][:-1])
                            targetList["approachTiming"] = float(content['approachTimingTarget'][:-1])
                            logging.debug('got approach timing acc')
                            impactCutAngleStringList = content["impactCutAngle"].split(", ")
                            logging.debug('got impact cut angle list')
                            # config.metric_score_list.append(sum(impactCutAngleList) / len(impactCutAngleList))
                            # logging.debug('calculated impact cut angle average')
                            accList["impactCutAngle"] = float(content['impactCutAngleAcc'])
                            logging.debug('got impact cut angle acc')
                            scoreList["impactCutAngle"] = float(content['impactCutAngleScore'][:-5])
                            targetList["impactCutAngle"] = float(content['impactCutAngleTarget'][:-5])
                            impactSpeedStringList = content["impactSpeed"].split(", ")
                            logging.debug('got impact speed list')
                            # config.metric_score_list.append(sum(impactSpeedList) / len(impactSpeedList))
                            # logging.debug('calculated impact speed average')
                            accList["impactSpeed"] = float(content['impactSpeedAcc'])
                            scoreList["impactSpeed"] = float(content['impactSpeedScore'][:-9])
                            targetList["impactSpeed"] = float(content['impactSpeedTarget'][:-9])
                            logging.debug('got impact speed acc')
                            followThroughRollStringList = content["followThroughRoll"].split(", ")
                            logging.debug('got follow thorugh roll list')
                            # config.metric_score_list.append(sum(followThroughRollList) / len(followThroughRollList))
                            # logging.debug('calculated follow through roll average')
                            accList["followThroughRoll"] = float(content['followThroughRollAcc'])
                            logging.debug('got follow through roll acc')
                            scoreList["followThroughRoll"] = float(content['followThroughRollScore'][:-5])
                            targetList["followThroughRoll"] = float(content['followThroughRollTarget'][:-5])
                            followThroughTimeStringList = content["followThroughTime"].split(", ")
                            logging.debug('got gollow through time list')
                            # config.metric_score_list.append(sum(followThroughTimeList) / len(followThroughTimeList))
                            # logging.debug('calculated follow through time average')
                            accList["followThroughTime"] = float(content['followThroughTimeAcc'])
                            logging.debug('got follow through time acc')
                            scoreList["followThroughTime"] = float(content['followThroughTimeScore'][:-5])
                            targetList["followThroughTime"] = float(content['followThroughTimeTarget'][:-5])
                            config.stat_list = accList
                            config.metric_score_list = scoreList
                            config.targetList = targetList
                            logging.debug('sorted stat list')

                            '''logging.debug("populating lists with floats")
                            for i in range(len(racketPreparationStringList)):
                                if i == 0:
                                    logging.debug("first list element")
                                    racketPreparationFloatList = [float(racketPreparationStringList[i][1:])]
                                    logging.debug("first racket prep done")
                                    approachTimingFloatList = [float(approachTimingStringList[i][1:])]
                                    logging.debug("first approach timing done")
                                    impactCutAngleFloatList = [float(impactCutAngleStringList[i][1:])]
                                    logging.debug("first impact cut angle done")
                                    impactSpeedFloatList = [float(impactSpeedStringList[i][1:])]
                                    logging.debug("first impact speed done")
                                    followThroughRollFloatList = [float(followThroughRollStringList[i][1:])]
                                    logging.debug("first follow through roll done")
                                    followThroughTimeFloatList = [float(followThroughTimeStringList[i][1:])]
                                    logging.debug("first follow through time done")
                                elif i == len(racketPreparationStringList) - 1:
                                    logging.debug("last list element")
                                    racketPreparationFloatList.append(float(
                                        racketPreparationStringList[i][0:len(racketPreparationStringList[i]) - 1]))
                                    logging.debug("last racket prep done")
                                    approachTimingFloatList.append(float(
                                        approachTimingStringList[i][0:len(approachTimingStringList[i]) - 1]))
                                    logging.debug("last approach timing done")
                                    impactCutAngleFloatList.append(float(
                                        impactCutAngleStringList[i][0:len(impactCutAngleStringList[i]) - 1]))
                                    logging.debug("last impact cut angle done")
                                    impactSpeedFloatList.append(float(
                                        impactSpeedStringList[i][0:len(impactSpeedStringList[i]) - 1]))
                                    logging.debug("last impact speed done")
                                    followThroughRollFloatList.append(float(
                                        followThroughRollStringList[i][0:len(followThroughRollStringList[i]) - 1]))
                                    logging.debug("last follow thorugh roll done")
                                    followThroughTimeFloatList.append(float(
                                        followThroughTimeStringList[i][0:len(followThroughTimeStringList[i]) - 1]))
                                    logging.debug("last follow thorugh time done")
                                else:
                                    logging.debug("Regular element: " + str(i))
                                    racketPreparationFloatList.append(float(racketPreparationStringList[i]))
                                    logging.debug("racket prep done")
                                    approachTimingFloatList.append(float(approachTimingStringList[i]))
                                    logging.debug("approach timing done")
                                    impactCutAngleFloatList.append(float(impactCutAngleStringList[i]))
                                    logging.debug("impact cut angle done")
                                    impactSpeedFloatList.append(float(impactSpeedStringList[i]))
                                    logging.debug("impact speed done")
                                    followThroughRollFloatList.append(float(followThroughRollStringList[i]))
                                    logging.debug("follow through roll done")
                                    followThroughTimeFloatList.append(float(followThroughTimeStringList[i]))
                                    logging.debug("follow through time done")

                            logging.debug("calculating average of lists")
                            for list in [racketPreparationFloatList, approachTimingFloatList, impactCutAngleFloatList,
                                         impactSpeedFloatList, followThroughRollFloatList, followThroughTimeFloatList]:
                                config.metric_score_list.append(sum(list) / len(list))
                            logging.debug("list averages calculated")'''

                            config.goal_level = config.EXERCISE_GOAL
                            config.phase = config.PHASE_END
                            config.completed = config.COMPLETED_STATUS_TRUE

                            logging.debug("waiting for config.stat")
                            while config.stat_confirmed is False:
                                pass

                            logging.debug("returning stat data to app: " + config.stat)
                            config.used_stats.append(config.stat)
                            # config.score = scoreList[config.stat]
                            # logging.debug("Baseline set results, setting config.stat score = " + str(config.score))
                            config.target = targetList[config.stat]
                            logging.debug("Baseline set results, setting config.stat target = " + str(config.target))

                            config.stat_confirmed = False  # Reset stat_confirmed for next time.
                            new_data = {
                                'goal_level': '4',
                                'completed': str(config.completed),
                                'shotSet': '1',
                                'stat': config.stat
                            }
                            if config.stop_session_on_baseline:
                                new_data['stop_on_baseline'] = '1'
                                new_data['final'] = '1'
                                config.stop_session_on_baseline = False
                                config.finish_session_baseline_stop = True
                            else:
                                new_data['stop_on_baseline'] = '0'
                        logging.info("Returning data to app: " + str(new_data))
                        return new_data, 200

                elif int(content['goal_level']) == config.STAT_GOAL:
                    logging.debug('stat goal setting controller values')
                    if 'feedback' in content:  # End of stat
                        logging.debug('end of stat')
                        logging.debug('content = ' + str(content))
                        scoreString = content['score']
                        if scoreString[-1] == "%":
                            scoreString = content['score'][:-1]
                        elif scoreString[-1] == "s":
                            scoreString = content['score'][:-5]
                        elif scoreString[-1] == "c":
                            logging.debug("Getting score string for mtrs\/sec")
                            scoreString = content['score'][:-9]
                            logging.debug("Got score string for mtrs\/sec = " + scoreString)
                        config.score = float(scoreString)
                        targetString = content['tgtValue']
                        if targetString[-1] == "%":
                            targetString = content['tgtValue'][:-1]
                        elif targetString[-1] == "s":
                            targetString = content['tgtValue'][:-5]
                        elif targetString[-1] == "c":
                            logging.debug("Getting targetString for mtrs\/sec")
                            targetString = content['tgtValue'][:-9]
                            logging.debug("Got targetString for mtrs\/sec = " + targetString)

                        config.target = float(targetString)
                        config.performance = int(content['performance'])
                        config.accuracy = float(content['accuracy'])
                        logging.debug("Setting new goal level to STAT_GOAL in API class.")
                        config.goal_level = config.STAT_GOAL
                        config.phase = config.PHASE_END
                        config.completed = config.COMPLETED_STATUS_UNDEFINED
                        config.stat_finished = True

                        while config.completed == config.COMPLETED_STATUS_UNDEFINED:
                            pass

                        new_data = {
                            'goal_level': 3,
                            'completed': config.completed
                        }

                        if config.stat_count == config.STATS_PER_SHOT or config.tidying:  # config.tidying indicates end of session
                            new_data["final"] = 1
                        else:
                            while config.stat_confirmed is False:
                                pass
                            config.stat_confirmed = False
                            logging.debug("New stat = " + str(config.stat))
                            new_data["stat"] = config.stat

                        logging.info("Returning data to app: " + str(new_data))
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
                        if config.stat_count > 1:
                            print("Setting config.performance to None.")
                            config.performance = None

                        while config.completed != config.COMPLETED_STATUS_FALSE:
                            pass

                        new_data = {
                            'goal_level': 3,
                            'completed': config.completed,
                            'shotSet': 0
                        }
                        logging.info("Returning data to app: " + str(new_data))
                        return new_data, 200

                elif int(content['goal_level']) == config.SET_GOAL:  # Also represents baseline goal
                    '''if config.goal_level == config.BASELINE_GOAL:  # baseline goal feedback
                        config.performance = content['performance']
                        config.score = content['score']
                        config.goal_level = config.EXERCISE_GOAL
                    else:'''
                    config.dont_send_action_response = True
                    logging.debug('set goal setting controller values')

                    if 'score' in content:  # End of set
                        if config.expecting_double_set:
                            config.double_set_count_feedback += 1
                            if config.double_set_count_feedback >= 2:
                                config.expecting_double_set = False
                                config.double_set_count_feedback = 0
                                new_data = {
                                    'goal_level': 4,
                                    'completed': config.completed,
                                    'shotSet': 1
                                }

                                logging.info("Returning data to app: " + str(new_data))
                                return new_data, 200
                        logging.debug('end of set')
                        logging.debug('content = ' + str(content))
                        scoreString = content['score']
                        if scoreString[-1] == "%":
                            scoreString = content['score'][:-1]
                        elif scoreString[-1] == "s":
                            scoreString = content['score'][:-5]
                        elif scoreString[-1] == "c":
                            logging.debug("Getting scoreString for mtrs\/sec")
                            scoreString = content['score'][:-9]
                            logging.debug("Got scoreString for mtrs\/sec = " + scoreString)
                        targetString = content['tgtValue']
                        if targetString[-1] == "%":
                            targetString = content['tgtValue'][:-1]
                        elif targetString[-1] == "s":
                            targetString = content['tgtValue'][:-5]
                        elif targetString[-1] == "c":
                            logging.debug("Getting targetString for mtrs\/sec")
                            targetString = content['tgtValue'][:-9]
                            logging.debug("Got targetString for mtrs\/sec = " + targetString)

                        logging.debug('got values from content')
                        config.avg_score = float(scoreString)
                        config.action_score_given = False
                        config.set_score_list.append(float(scoreString))
                        config.target = float(targetString)
                        if not content['performance'] == "":
                            config.performance = int(content['performance'])
                            config.set_performance_list.append(int(content['performance']))
                            # config.stat = content['stat']  # Let guide decide what stat to work on based on baseline set.
                        config.goal_level = config.SET_GOAL
                        config.phase = config.PHASE_END
                        config.completed = config.COMPLETED_STATUS_UNDEFINED
                        config.set_finished = True

                        while config.completed == config.COMPLETED_STATUS_UNDEFINED:
                            pass

                        new_data = {
                            'goal_level': 4,
                            'completed': config.completed,
                            'shotSet': 1
                        }

                        if config.set_count == config.SETS_PER_STAT:
                            new_data["final"] = 1
                        logging.info("Returning data to app: " + str(new_data))
                        return new_data, 200

                    else:  # Start of set
                        logging.debug("Start of set")
                        if config.expecting_double_set:
                            config.double_set_count_start += 1
                            if config.double_set_count_start >= 2:
                                config.expecting_double_set = False
                                config.double_set_count_start = 0
                                new_data = {
                                    'goal_level': 4,
                                    'completed': config.completed,
                                    'shotSet': 1
                                }

                                logging.info("Returning data to app: " + str(new_data))
                                return new_data, 200
                        config.goal_level = config.SET_GOAL
                        config.phase = config.PHASE_START
                        config.completed = config.COMPLETED_STATUS_UNDEFINED

                        logging.debug("Waiting")
                        while config.completed != config.COMPLETED_STATUS_FALSE:
                            pass

                        logging.debug("Setting data")
                        new_data = {
                            'goal_level': 4,
                            'completed': config.completed,
                            'shotSet': 1
                        }

                        logging.info("Returning data to app: " + str(new_data))
                        return new_data, 200

                elif int(content['goal_level']) == config.ACTION_GOAL:
                    config.shots_dealt_with.append("1")
                    if config.expecting_action_goal:
                        logging.debug('action goal setting controller values')
                        config.action_score = float(content['score'])
                        config.action_score_given = True
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
                            logging.debug("updating config.performance: " + str(performanceValue))
                            config.performance = performanceValue            # Not perfect because we might have the same performance for set and action.
                        config.goal_level = config.ACTION_GOAL
                        config.shot_count += 1

                        requestURL = config.screen_post_address + str(config.shot_count) + "/newRep"
                        logging.debug('sending request, url = ' + requestURL)
                        r = requests.post(requestURL)
                        refresh_screen_data = {'silence': 1}
                        r = requests.post(config.post_address, json=refresh_screen_data)

                        self.previous_shot_performance = performanceValue

                        new_data = {
                            'goal_level': 5,
                            'completed': 1,
                            'shotSet': 1
                        }

                        if config.shot_count == config.SHOTS_PER_SET - 1:
                            logging.debug("Setting shot_setComplet = 1")
                            new_data['shotSetComplete'] = 1
                            # new_data['stat'] = config.stat
                        else:
                            new_data['shotSetComplete'] = 0

                    else:
                        logging.debug("Action goal not expected, not using data.")
                        logging.debug("Action goal not expected, not setting controller values.")
                        new_data = {
                            'goal_level': 5,
                            'completed': 1,
                            'shotSet': 1,
                            'shotSetComplete': 0
                        }

                    config.shots_dealt_with.pop(0)
                    logging.debug("sending shot response. Shots still to be dealt with: " + str(config.shots_dealt_with))
                    logging.info("Returning data to app: " + str(new_data))
                    return new_data, 200

            elif 'override' in content:
                logging.debug("dealing with override in API")
                if content['override'] == "True":
                    config.override = True
                else:
                    config.override = False

            elif 'questionResponse' in content:
                logging.debug("dealing with question response in API")
                if content['questionResponse'] == "Pos":
                    config.question_response = config.Q_RESPONSE_POSITIVE
                elif content['questionResponse'] == "Neg":
                    config.question_response = config.Q_RESPONSE_NEGATIVE
                else:
                    config.question_response = None

            else:
                logging.debug("dealing with shot/stat selection in API")
                if 'shot_selection' in content:
                    shotWithSpaces = content['shot_selection'].replace('%20', ' ')
                    config.shot = shotWithSpaces
                    config.hand = content['hand']
                else:
                    config.stat = content['stat_selection'].replace('%20', ' ')
                    logging.debug("New stat = " + config.stat)
                config.override = False

        else:
            logging.debug("request not json")
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
