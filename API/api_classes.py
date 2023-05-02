"""API Classes

*** This file should require no changes to extend the system to another domain. Although it is useful to understand ***
*** the code in here so that correctly formed data can be passed by the movement analysis software.                 ***

This script acts as an interface between the controller in the processing layer and the movement analysis software in
the tracking layer. It accepts post requests from the tracking layer and updates the corresponding config variables
accordingly.
...
Classes
-------
TimestepCue(Resource)
    Wait for a post request from the movement analysis software, processes its contents, and returns an appropriate
    response.
"""

import requests
from flask import Flask, request
from flask_restful import Resource, Api, reqparse
import logging

from CoachingBehaviourTree import config

# Create the instance of the flask app and api, which is started from the controller.
app = Flask('policy_guide_api')
api = Api(app)

class TimestepCue(Resource):
    """
    Wait for a post request from the movement analysis software, processes its contents, and returns an appropriate
    response.
    """
    previous_shot_performance = None
    def post(self):
        if request.is_json:
            logging.debug("request is json")
            logging.debug("request is json")
            content = request.get_json()
            logging.debug(content)
            logging.info("Received data from app: {}".format(content))
            if 'goal_level' in content:

                # Person Goal
                if int(content['goal_level']) == config.PERSON_GOAL:
                    # Update config variables.
                    config.goal_level = config.PERSON_GOAL
                    config.completed = config.COMPLETED_STATUS_UNDEFINED

                    # Wait for the behaviour tree to execute for the person goal.
                    while config.completed == config.COMPLETED_STATUS_UNDEFINED:
                        pass

                    new_data = {
                        'goal_level': 0,
                        'completed': config.completed,
                        'shotSet': 0
                    }
                    
                    logging.info("Returning data to app: " + str(new_data))
                    return new_data, 200

                # Session Goal
                elif int(content['goal_level']) == config.SESSION_GOAL:
                    logging.debug('session goal setting controller values')
                    if 'feedback' in content:  # End of session
                        logging.debug('end of session')
                        # Update config variables with information passed in through post request.
                        config.score = float(content['score'][0:len(content['score']) - 1])  # Numerical value of score without any trailing characters.
                        config.target = 5
                        config.performance = int(content['performance'])
                        config.goal_level = config.SESSION_GOAL
                        config.phase = config.PHASE_END
                        config.completed = config.COMPLETED_STATUS_UNDEFINED
                        config.session_finished = True

                        # Wait for the behaviour tree to execute for the session goal.
                        while config.completed == config.COMPLETED_STATUS_UNDEFINED:
                            pass

                        new_data = {
                            'goal_level': 1,
                            'completed': config.completed
                        }

                        logging.info("Returning data to app: " + str(new_data))
                        return new_data, 200
                    elif 'stop' in content:  # Session stopped early by user
                        logging.info("Stop session selected by user.")
                        if config.goal_level == config.ACTION_GOAL and config.during_baseline_goal:
                            # Special behaviour is needed to deal with the situation when the user has decided to end the session during the baseline set.
                            config.stop_session_on_baseline = True
                        else:
                            config.stop_set = True  # High level global variable which will be checked at each node until session goal feedback is reached.
                            config.pause_display = True
                            config.goal_level = config.EXERCISE_GOAL
                            config.MAX_SESSION_TIME = 1  # Session will stop because time is now > MAX_SESSION_TIME

                        new_data = {
                            'goal_level': 1,
                            'completed': config.completed,
                        }

                        logging.info("Returning data to app: " + str(new_data))
                        return new_data, 200
                    else:  # Start of session
                        logging.debug("Start of session")
                        config.completed = config.COMPLETED_STATUS_UNDEFINED
                        config.goal_level = config.SESSION_GOAL
                        config.phase = config.PHASE_START
                        config.performance = None

                        # Wait until the behaviour tree has executed for the session goal and the user/system has chosen a shot (exercise in general) which has been confirmed.
                        while config.completed == config.COMPLETED_STATUS_UNDEFINED or config.shot is None or not config.shot_confirmed:
                            pass

                        new_data = {
                            'goal_level': 1,
                            'completed': config.completed,
                            'shotSet': 0
                        }

                        # Return the selected shot (exercise in general) and stat if applicable to the movement analysis module so it knows what to look for in the user's movements.
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

                # Exercise Goal
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

                        while config.completed == config.COMPLETED_STATUS_FALSE:
                            pass

                        new_data = {
                            'goal_level': "2",
                            'completed': str(config.completed)
                        }

                        # If the user has chosen to stop the session early, we need to check if we are at an appropriate place to continue and send data back to the tracking layer.
                        # If we are not at an appropriate place, we need to wait for the behaviour tree to execute and tidy things up so that we can return appropriate data and communicate that the session is stopping.
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
                            # Let the tracking layer know this is the last shot.
                            new_data['final'] = "1"

                        logging.info("Returning data to app: " + str(new_data))
                        return new_data, 200

                    elif 'stop' in content:  # Stop current set.
                        logging.info("Stop set selected by the user.")
                        if config.expecting_action_goal:
                            if config.goal_level == config.ACTION_GOAL and config.during_baseline_goal:
                                # Special behaviour needed for stopping on baseline set.
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
                    else:  # Start of shot
                        if content['impactSpeed'] == 'null':  # Start of shot
                            logging.debug("api classes, exercise goal received")
                            config.completed = config.COMPLETED_STATUS_UNDEFINED
                            logging.debug("Setting config.goal_level to EXERCISE_GOAL")
                            config.goal_level = config.EXERCISE_GOAL
                            config.phase = config.PHASE_START

                            if config.shot == -1:
                                config.shot = content['shotType']
                                config.hand = content['hand']

                            # Wait for the behaviour tree to execute.
                            while config.completed == config.COMPLETED_STATUS_UNDEFINED:
                                pass

                            new_data = {
                                'goal_level': 2,
                                'completed': config.completed,
                                'shotSet': 1
                            }

                            if not (config.stat == -1):
                                new_data['stat'] = config.stat

                        else:  # End of baseline set
                            logging.debug('end of baseline set')

                            config.metric_score_list = []  # Reset the metric score list from last time.
                            logging.debug("setting config.score = " + content['score'])
                            config.score = float(content['score'])
                            accList = {}
                            scoreList = {}
                            targetList = {}
                            logging.debug('Created accList')

                            # Retrieve and format all of the data for each stat/metric from the post request.
                            accList['racketPreparation'] = float(content['racketPreparationAcc'])
                            logging.debug('get racket prep acc')
                            scoreList['racketPreparation'] = float(content['racketPreparationScore'][:-1])
                            targetList['racketPreparation'] = float(content['racketPreparationTarget'][:-1])

                            accList["approachTiming"] = float(content['approachTimingAcc'])
                            scoreList["approachTiming"] = float(content['approachTimingScore'][:-1])
                            targetList["approachTiming"] = float(content['approachTimingTarget'][:-1])
                            logging.debug('got approach timing acc')

                            accList["impactCutAngle"] = float(content['impactCutAngleAcc'])
                            logging.debug('got impact cut angle acc')
                            scoreList["impactCutAngle"] = float(content['impactCutAngleScore'][:-5])
                            targetList["impactCutAngle"] = float(content['impactCutAngleTarget'][:-5])

                            accList["impactSpeed"] = float(content['impactSpeedAcc'])
                            scoreList["impactSpeed"] = float(content['impactSpeedScore'][:-9])
                            targetList["impactSpeed"] = float(content['impactSpeedTarget'][:-9])
                            logging.debug('got impact speed acc')

                            accList["followThroughRoll"] = float(content['followThroughRollAcc'])
                            logging.debug('got follow through roll acc')
                            scoreList["followThroughRoll"] = float(content['followThroughRollScore'][:-5])
                            targetList["followThroughRoll"] = float(content['followThroughRollTarget'][:-5])

                            accList["followThroughTime"] = float(content['followThroughTimeAcc'])
                            logging.debug('got follow through time acc')
                            scoreList["followThroughTime"] = float(content['followThroughTimeScore'][:-5])
                            targetList["followThroughTime"] = float(content['followThroughTimeTarget'][:-5])

                            # Set config values based on the information retreived from the post request
                            config.stat_list = accList
                            config.metric_score_list = scoreList
                            config.targetList = targetList
                            logging.debug('sorted stat list')

                            config.goal_level = config.EXERCISE_GOAL
                            config.phase = config.PHASE_END
                            config.completed = config.COMPLETED_STATUS_TRUE

                            logging.debug("waiting for config.stat")
                            while config.stat_confirmed is False:
                                pass

                            logging.debug("returning stat data to app: " + config.stat)
                            config.used_stats.append(config.stat)
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

                # Stat Goal
                elif int(content['goal_level']) == config.STAT_GOAL:
                    logging.debug('stat goal setting controller values')
                    if 'feedback' in content:  # End of stat
                        logging.debug('end of stat')
                        logging.debug('content = ' + str(content))

                        # Format the score and target score into a number depending on the format
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
                            # Wait for behaviour tree to execute until the stat choice is confirmed.
                            while config.stat_confirmed is False:
                                pass
                            config.stat_confirmed = False
                            logging.debug("New stat = " + str(config.stat))
                            new_data["stat"] = config.stat

                        logging.info("Returning data to app: " + str(new_data))
                        return new_data, 200
                    else: # Start of stat
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

                        if config.stat_count > 1:
                            logging.debug("Setting config.performance to None.")
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
                    config.dont_send_action_response = True  # Ignores any shots played by the user until this is set back to False at the start of a set.
                    logging.debug('set goal setting controller values')

                    if 'score' in content:  # End of set
                        if config.expecting_double_set:  # True when the user has chosen to stop the set early because of execution pattern in behaviour tree.
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
                        if config.expecting_double_set:  # True when user has chosen to end the set early.
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
                        # Only process the data if it has come at the right time, otherwise it is likely the player is bouncing the ball/tapping the racket etc between sets.
                        logging.debug('action goal setting controller values')
                        config.action_score = float(content['score'])
                        config.action_score_given = True
                        config.has_score_been_provided = False

                        # Translate the performance value into something usable.
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

                        # Send a signal to the screen API asking it to update the robot's screen with the new rep number
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

                    # This keeps track of things when the shots come in faster than we can deal with.
                    # We provide an appropriate behaviour based on the latest shot.
                    config.shots_dealt_with.pop(0)
                    logging.debug("sending shot response. Shots still to be dealt with: " + str(config.shots_dealt_with))
                    logging.info("Returning data to app: " + str(new_data))
                    return new_data, 200

            elif 'override' in content:  # The user has decided to override the system decision to choose/ask the user for the shot/stat choice.
                logging.debug("dealing with override in API")
                if content['override'] == "True":
                    config.override = True
                else:
                    config.override = False

            elif 'questionResponse' in content:  # Get the question response from the robot to be used in calculating the RL reward.
                logging.debug("dealing with question response in API")
                if content['questionResponse'] == "Pos":
                    config.question_response = config.Q_RESPONSE_POSITIVE
                elif content['questionResponse'] == "Neg":
                    config.question_response = config.Q_RESPONSE_NEGATIVE
                else:
                    config.question_response = None

            else:  # Get the selection of shot/stat from the robot (user selects from Pepper's screen).
                logging.debug("dealing with shot/stat selection in API")
                if 'shot_selection' in content:
                    shotWithSpaces = content['shot_selection'].replace('%20', ' ')
                    config.shot = shotWithSpaces
                    config.hand = content['hand']
                else:
                    config.stat = content['stat_selection'].replace('%20', ' ')
                    logging.debug("New stat = " + config.stat)
                config.override = False

        else:  # Default in case something goes wrong and the request received is not in a json format.
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


api.add_resource(TimestepCue, '/cue')

# For testing purposes. The Flask app is normally run through the controller.
if __name__ == '__main__':
    app.run()  # run our Flask app
