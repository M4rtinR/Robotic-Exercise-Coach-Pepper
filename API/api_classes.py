import os

from flask import Flask, request
from flask_restful import Resource, Api, reqparse
import logging

app = Flask('policy_guide_api')
api = Api(app)
expecting_action_goal = False

stat_list_master = ["racketPreparation", "approachTiming", "impactCutAngle", "impactSpeed", "followThroughRoll", "followThroughTime"]
shot_list_master = {"drop": 0, "drive": 1, "cross court lob": 14, "two wall boast": 7, "straight kill": 16, "volley kill": 17, "volley drop": 18}
sessions = 0

participantNo = "P11."

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
                print("goal_level in content")
                if int(content['goal_level']) == 4:
                    print("goal_level == 4")
                    if 'score' in content:
                        print("score in content")
                        '''performance = ""
                        if not content['performance'] == "":
                            performance = content['performance']'''
                        score = content['score']
                        accuracy = content['accuracy']
                        shots = content['count']

                        shot = content['shot']
                        hand = content['hand']

                        # Write to file
                        try:
                            file = open("/home/martin/PycharmProjects/coachingPolicies/SessionDataFiles/" + participantNo + "/" + hand + str(shot) + "/" + str(sessions) + ".txt", "r")
                            file_contents = file.readlines()
                            file.close()
                            print("File exists")
                        except:
                            print("File does not exist")
                            try:
                                os.mkdir("/home/martin/PycharmProjects/coachingPolicies/SessionDataFiles/" + participantNo + "/" + hand + str(shot))
                                print("directory did not exist")
                            except:
                                print("directory already exists")
                            file = open("/home/martin/PycharmProjects/coachingPolicies/SessionDataFiles/" + participantNo + "/" + hand + str(shot) + "/" + str(sessions) + ".txt", "a")
                            file.write("0\n")
                            file.close()
                            file_contents = ["0\n"]

                        setsCount = int(file_contents[0].split("\n")[0])
                        setsCount += 1
                        file_contents[0] = str(setsCount) + "\n"

                        file_contents.append(str(score) + "\n")
                        file_contents.append(str(accuracy) + "\n")
                        file_contents.append(str(shots) + "\n")
                        for stat in stat_list_master:
                            file_contents.append(stat + "\n")
                            file_contents.append(str(content[stat]))
                            statTarget = stat + "Target"
                            file_contents.append(", " + str(content[statTarget]) + "\n")

                        file = open("/home/martin/PycharmProjects/coachingPolicies/SessionDataFiles/" + participantNo + "/" + hand + str(shot) + "/" + str(sessions) + ".txt", "w")
                        file.writelines(file_contents)
                        file.close()

                        print('written shot set data to file')

                        new_data = {
                            'goal_level': 4,
                            'completed': 1,
                            'shotSet': 1
                        }

                        return new_data, 200

                    else:  # Start of set
                        goal_level = 4
                        phase = 0
                        completed = -1

                        while completed != 0:
                            print("stuck in while loop")

                        new_data = {
                            'goal_level': 4,
                            'completed': 0,
                            'shotSet': 1
                        }

                        return new_data, 200

            elif 'stop' in content:
                sessionLine = ""
                for shot in shot_list_master.keys():
                    for hand in ["forehand", "backhand"]:
                        try:
                            filepath = "/home/martin/PycharmProjects/coachingPolicies/SessionDataFiles/" + participantNo + "/" + hand + str(shot) + "/" + str(sessions) + ".txt"
                            print(filepath)
                            file = open("/home/martin/PycharmProjects/coachingPolicies/SessionDataFiles/" + participantNo + "/" + hand + str(shot) + "/" + str(sessions) + ".txt", "r")
                            file_contents = file.readlines()
                            file.close()
                            setsCount = int(file_contents[0])

                            line = 1
                            total = 0
                            for s in range(setsCount):
                                print(file_contents[line].split("\n")[0])
                                total += float(file_contents[line].split("\n")[0][:-1])
                                print("total = " + str(total))
                                line += 15
                                print("line = " + str(line))

                            averageScore = total/setsCount
                            file_contents.insert(0, str(averageScore) + "\n")

                            file = open("/home/martin/PycharmProjects/coachingPolicies/SessionDataFiles/" + participantNo + "/" + hand + str(shot) + "/" + str(sessions) + ".txt", "w")
                            file.writelines(file_contents)
                            file.close()

                            sessionLine = sessionLine + hand + str(shot) + ": " + str(averageScore) + ", "
                            print("Written data for " + hand + str(shot) + " to file.")
                        except:
                            print("Did not play any " + hand + str(shot) + " in this session.")

                file = open("/home/martin/PycharmProjects/coachingPolicies/SessionDataFiles/" + participantNo + "/Sessions.txt", "r")
                file_contents = file.readlines()
                file.close()

                file_contents[0] = str(sessions) + "\n"
                file_contents.append(sessionLine + "\n")

                file = open("/home/martin/PycharmProjects/coachingPolicies/SessionDataFiles/" + participantNo + "/Sessions.txt", "w")
                file.writelines(file_contents)
                file.close()

                new_data = {
                    'stop': 1
                }

                return new_data, 200

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
    try:
        f = open("/home/martin/PycharmProjects/coachingPolicies/SessionDataFiles/" + participantNo + "/Sessions.txt", "r")
        f_contents = f.readlines()
        f.close()
        sessions = int(f_contents[0].split("\n")[0]) + 1
    except:
        os.mkdir("/home/martin/PycharmProjects/coachingPolicies/SessionDataFiles/" + participantNo)
        f = open("/home/martin/PycharmProjects/coachingPolicies/SessionDataFiles/" + participantNo + "/Sessions.txt", "a")
        f.write("1\n")
        f.close()
        sessions = 1
    app.run(host='192.168.1.207', port=4801)  # run our Flask app
