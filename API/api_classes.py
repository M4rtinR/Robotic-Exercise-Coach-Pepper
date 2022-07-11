import time

import requests
from flask import Flask, request
from flask_restful import Resource, Api, reqparse
import json
import logging

from CoachingBehaviourTree import controller, nodes, config
from Policy.policy_wrapper import PolicyWrapper

app = Flask('policy_guide_api')
api = Api(app)
expecting_action_goal = False

stat_list_master = ["racketPreparation", "downSwingSpeed", "impactCutAngle", "impactSpeed", "followThroughSwing", "followThroughTime"]
shot_list_master = {"drop": 0, "drive": 1, "cross court lob": 14, "two wall boast": 7, "straight kill": 16, "volley kill": 17, "volley drop": 18}
sessions = 0

participantNo = "TestingBaseline0"

'''
Layout of participant history files:
    Directory: <participant number>
        File: Sessions.txt
            Contents: (Updated at end of session, when operator types end)
                <no. of sessions>
                <exercise name>: <score in first session>, <exercise name>: <score in first session>, ...
                <exercise name>: <score in second session>, <exercise name>: <score in second session>, ...
                ...
        Directory: <exercise name>
            File: <session no.>.txt
                Contents:
                    <overall score> (updated at end of session)
                    <no. of sets> (updated at end of set)
                    <first set score>
                    <stat name>
                    <score list for each shot in set>
                    <stat name»
                    <score list for each shot in set>
                    ...
                    <second set score>
                    <stat name>
                    <score list for each shot in set>
                    <stat name>
                    <score list for each shot in set>
                    ...
            ...
        Directory: <exercise name>
            ...
        ...
'''

class TimestepCue(Resource):
    previous_shot_performance = None
    def post(self):
        global sessions
        if request.is_json:
            print("request is json")
            logging.debug("request is json")
            content = request.get_json()
            logging.debug(content)
            logging.info("Received data from app: {}".format(content))
            if 'goal_level' in content:
                if int(content['goal_level']) == 4:
                    if 'score' in content:
                        performance = ""
                        if not content['performance'] == "":
                            performance = content['performance']
                        score = content['score']

                        shot = content['shot']
                        hand = content['hand']

                        # Write to file
                        try:
                            file = open("/home/martin/PycharmProjects/coachingPolicies/SessionDataFiles/" + participantNo + "/" + hand + shot + "/" + sessions + ".txt", "r")
                            file_contents = file.readlines()
                            file.close()
                        except:
                            file = open("/home/martin/PycharmProjects/coachingPolicies/SessionDataFiles/" + participantNo + "/" + hand + shot + "/" + sessions + ".txt", "a")
                            file.write("0\n")
                            file.close()
                            file_contents = ["0\n"]

                        setsCount = int(file_contents[0].split("\n")[0])
                        setsCount += 1
                        file_contents.insert(0, str(setsCount))

                        file_contents.append(score + "\n")
                        for stat in stat_list_master:
                            file_contents.append(stat + "\n")
                            file_contents.append(content[stat] + "\n")

                        file = open("/home/martin/PycharmProjects/coachingPolicies/SessionDataFiles/" + participantNo + "/" + hand + shot + "/" + sessions + ".txt", "w")
                        file.writelines(file_contents)
                        file.close()

                        logging.debug('written shot set data to file')

                        new_data = {
                            'goal_level': 4,
                            'completed': config.COMPLETED_STATUS_TRUE,
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

            elif 'stop' in content:
                sessionLine = ""
                for shot in shot_list_master.values():
                    for hand in ["FH", "BH"]:
                        try:
                            file = open("/home/martin/PycharmProjects/coachingPolicies/SessionDataFiles/" + participantNo + "/" + hand + str(shot) + "/" + sessions + ".txt", "r")
                            file_contents = file.readlines()
                            file.close()
                            setsCount = int(file_contents[0])

                            line = 1
                            total = 0
                            for s in range(setsCount):
                                total += float(file_contents[line].split("\n")[0])
                                line += 12

                            averageScore = total/setsCount
                            file_contents.insert(0, str(averageScore) + "\n")

                            file = open("/home/martin/PycharmProjects/coachingPolicies/SessionDataFiles/" + participantNo + "/" + hand + str(shot) + "/" + sessions + ".txt", "w")
                            file.writelines(file_contents)
                            file.close()

                            sessionLine = sessionLine + hand + str(shot) + ": " + str(averageScore) + ", "
                        except:
                            print("Did not play any " + hand + str(shot) + " in this session.")

                file = open("/home/martin/PycharmProjects/coachingPolicies/SessionDataFiles/" + participantNo + "/Sessions.txt", "r")
                file_contents = f.readlines()
                file.close()

                file_contents[0] = str(sessions) + "\n"
                file_contents.insert(sessions, sessionLine + "\n")

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


api.add_resource(TimestepCue, '/cue')

if __name__ == '__main__':
    global sessions
    try:
        f = open("/home/martin/PycharmProjects/coachingPolicies/SessionDataFiles/" + participantNo + "/Sessions.txt", "r")
        f_contents = f.readlines()
        f.close()
        sessions = int(f_contents[0].split("\n")[0]) + 1
    except:
        f = open("/home/martin/PycharmProjects/coachingPolicies/SessionDataFiles/" + participantNo + "/Sessions.txt", "a")
        f.write("1\n")
        f.close()
        sessions = 1
    app.run()  # run our Flask app
