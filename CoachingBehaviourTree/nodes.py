"""Behaviour Tree Leaf Nodes

This script contains all of the leaf nodes which implement the behaviour to be used by the robot coach. All classes in
this file are Behaviour Tree Nodes.
...
Classes
-------
GetBehaviour(Node)
    Query the policy wrapper for the next behaviour to confirm given the current state of the interaction.
FormatAction(Node)
    Create an instance of the Action class using the given behaviour.
CheckForBehaviour(Node)
    Compare the currently selected behaviour to a given behaviour category.
DisplayBehaviour(Node)
    Have the robot perform the formatted action.
GetStats(Node)
    Retrieve the user stats (motivation level, playing experience, no. of sessions) from the guide and user.
GetDuration(Node)
    Retrieve the user's choice of how long they wish to practice for via the robot interface.
CreateSubgoal(Node)
    Tell the guide via the API that a new subgoal is required.
TimestepCue(Node)
    Receive a notification from the guide that an action is required from the robot.
DurationCheck(Node)
    Check if the session has reached the time limit selected by the user.
GetUserChoice(Node)
    Ask for a choice from the user as to their preference on shot or stat to work on.
EndSetEvent(Node)
    Check if the user has chosen to end the set.
"""
import logging
import os
from statistics import mean, mode
import time
from datetime import datetime, timedelta

from task_behavior_engine.node import Node
from task_behavior_engine.tree import NodeStatus
from multiprocessing import Process, Queue, Pipe

from API import api_classes
from CoachingBehaviourTree import controller, config
from CoachingBehaviourTree.action import Action
from CoachingBehaviourTree.behaviour_library import BehaviourLibraryFunctions, squash_behaviour_library
from Policy.policy import Policy
from Policy.policy_wrapper import PolicyWrapper
import numpy as np
import random
import requests
import operator

'''# Robot through Peppernet router:
# post_address = 'http://192.168.1.237:4999/output'

# Simulation on 4G:
# post_address = 'http://192.168.43.19:4999/output'
# post_address = 'http://192.168.1.174:4999/output'

# Robot through ITT Pepper router:
post_address = "http://192.168.1.207:4999/output"
screen_post_address = "http://192.168.1.207:8000/"

# Robot through hotspot:
# post_address = "http://192.168.43.19:4999/output"

behaviour = -1
need_new_behaviour = False'''

class GetBehaviour(Node):
    """
    Query the policy wrapper for the next behaviour to confirm given the current state of the interaction.
    ...
    Attributes
    ----------
    belief :type list[float]
        Belief distribution over all 12 policies (based on data from semi-structured interviews with coaches and
        physios).
    state :type int
        Previous state based on observation from policy.
    goal_level :type int
        Which level of goal we are currently in (e.g. SET_GOAL).
    performance :type int
        Which level of performance the player achieved in their last action/set/shot etc (e.g. MET).
    phase :type int
        Whether in the intro or feedback sequences (PHASE_START or PHASE_END).

    Methods
    -------
    configure(nodedata)
        Set up the initial values needed by the policy based on information stored in the blackboard.
    run(nodedata)
        Query the policy wrapper for a behaviour based on the state, goal_level, performance and phase of interaction.
    cleanup(nodedata)
        Reset values in the blackboard so as not to interfere with the next behaviour selection.
    """

    def __init__(self, name, *args, **kwargs):
        super(GetBehaviour, self).__init__(
            name,
            run_cb=self.run,
            configure_cb=self.configure,
            cleanup_cb=self.cleanup,
            *args, **kwargs)

    def configure(self, nodedata):
        """
        Set up the initial values needed by the policy based on information stored in the blackboard.
        :param nodedata :type Blackboard: the blackboard associated with this Behaviour Tree containing all relevant
            state information.
        :return: None
        """
        print("Configuring GetBehaviour: " + self._name)
        logging.debug("Configuring GetBehaviour: " + self._name)
        # logging.debug(str(nodedata))
        self.belief = nodedata.get_data('belief')            # Belief distribution over policies.
        self.goal_level = nodedata.get_data('goal')          # Which level of goal we are currently in (e.g. SET_GOAL)
        self.performance = nodedata.get_data('performance')  # Which level of performance the player achieved (e.g. MET)
        self.phase = nodedata.get_data('phase')              # PHASE_START or PHASE_END
        self.previous_phase = nodedata.get_data('previous_phase', config.PHASE_START)  # PHASE_START or PHASE_END
        self.state = config.observation # Have to set observation as global variable in controller because when we're in the while loop, the pre-behav-node will be different the first time to the subsequent times.
        self.need_score = nodedata.get_data('need_score', False)
        '''if self.previous_phase == config.PHASE_START:
            self.state = nodedata.get_data('state')  # Previous state based on observation.
        else:
            self.state = nodedata.get_data('feedback_state')'''

    def run(self, nodedata):
        """
        Query the policy wrapper for a behaviour based on the state, goal_level, performance and phase of interaction.
        :param nodedata :type Blackboard: the blackboard on which we will store the obtained behaviour and observation
            for accesses by other nodes.
        :return: NodeStatus.SUCCESS when a behaviour and observation has been obtained from the policy wrapper.
        """
        if not config.stop_set and not config.stop_session:
            # print('GetBehaviour, self.goal_level = ' + str(self.goal_level) + ', nodedata.goal = ' + str(nodedata.goal))
            # policy = PolicyWrapper(self.belief)  # TODO: generate this at start of interaction and store on blackboard.
            #, nodedata.obs_behaviour
            # nodedata.behaviour = policy.get_behaviour(self.state, self.goal_level, self.performance, self.phase)
            if config.behaviour_displayed:  # If we need a new behaviour, return active so that control as passed back to controller to generate new behaviour from policy.
                config.need_new_behaviour = True
                logging.debug("Returning ACTIVE from GetBehaviour, nodedata = " + str(nodedata))
                return NodeStatus(NodeStatus.ACTIVE, "Need new behaviour")
            else:
                # config.need_new_behaviour = True
                nodedata.behaviour = config.behaviour
                print('GetBehaviour Got behaviour: ' + str(config.behaviour))

                # If behaviour occurs twice, just skip to pre-instruction.
                """if nodedata.behaviour in config.used_behaviours and (self.goal_level == config.SESSION_GOAL or self.goal_level == config.EXERCISE_GOAL or self.goal_level == config.SET_GOAL):
                    nodedata.behaviour = config.A_PREINSTRUCTION
                    logging.debug('Got new behaviour: 1')
                    # config.matching_behav = 0
                else:
                    config.used_behaviours.append(nodedata.behaviour)
        
                config.prev_behav = nodedata.behaviour
        
                config.observation = policy.get_observation(self.state, nodedata.behaviour)"""
                print("self.need_score = " + str(self.need_score) + ", config.scores_provided = " + str(config.scores_provided) + ", config.has_score_been_provided = " + str(config.has_score_been_provided))
                if self.need_score and config.scores_provided < 1:
                    config.has_score_been_provided = False
                    print("set has_score_been_provided to False")
                # logging.debug('Got observation: ' + str(nodedata.behaviour))
                print("Returning SUCCESS from GetBehaviour, nodedata = " + str(nodedata))
                logging.debug("Returning SUCCESS from GetBehaviour, nodedata = " + str(nodedata))
                return NodeStatus(NodeStatus.SUCCESS, "Obtained behaviour " + str(nodedata.behaviour))
        else:
            return NodeStatus(NodeStatus.SUCCESS, "Stop set/session get behaviour")

    def cleanup(self, nodedata):
        """
        Reset values in the blackboard so as not to interfere with the next behaviour selection.
        :param nodedata :type Blackboard: the blackboard associated with this Behaviour Tree containing all relevant
            state information.
        :return: None
        """
        nodedata.previous_phase = config.PHASE_START


class FormatAction(Node):
    """
    Create an instance of the Action class using the given behaviour.
    ...
    Attributes
    ----------
    goal_level :type int
        Which level of goal we are currently in (e.g. SET_GOAL).
    performance :type int
        Which level of performance the player achieved in their last action/set/shot etc (e.g. MET).
    phase :type int
        Whether in the intro or feedback sequences (PHASE_START or PHASE_END).
    score :type float
        Numerical score from sensor relating to a stat (can be None if no previous data is available).
    target :type float
        Numerical target score for stat (can be None).
    behaviour_lib :type BehaviourLibraryFunctions
        The behaviour library to be used in generating actions (created at start of session).

    Methods
    -------
    configure(nodedata)
        Set up the initial values needed to generate appropriate utterances based on information stored in the
        blackboard.
    run(nodedata)
        Generate pre_ and post_ messages suitable for the given behaviour using Behaviour Library functions.
    """

    def __init__(self, name, *args, **kwargs):
        super(FormatAction, self).__init__(
            name,
            run_cb=self.run,
            configure_cb=self.configure,
            *args, **kwargs)

    def configure(self, nodedata):
        """
        Set up the initial values needed to generate appropriate utterances based on information stored in the
        blackboard.
        :param nodedata :type Blackboard: the blackboard associated with this Behaviour Tree containing all relevant
            state and behaviour information.
        :return: None
        """
        # print("Configuring FormatAction: " + self._name + ". PHASE = " + str(nodedata.get_data('phase')) + ". performance = " + str(nodedata.get_data('performance')) + ". config.performance = " + str(config.performance) + ". shot = " + str(nodedata.get_data('shot')))
        # logging.debug("FormatAction nodedata: " + str(nodedata))
        self.goal_level = nodedata.get_data('goal')          # Which level of goal we are currently in (e.g. SET_GOAL)
        self.performance = nodedata.get_data('performance', 0)  # Which level of performance the player achieved (e.g. MET)
        self.phase = nodedata.get_data('phase')              # PHASE_START or PHASE_END
        self.score = nodedata.get_data('score')              # Numerical score from sensor relating to a stat (can be None)
        self.target = nodedata.get_data('target')            # Numerical target score for stat (can be None)
        self.behaviour_lib = nodedata.get_data('bl')         # The behaviour library to be used in generating actions
        self.behaviour = nodedata.get_data('behaviour')      # The type of behaviour to create an action for.
        self.name = config.name                          # The name of the current user.
        self.shot = nodedata.get_data('shot', config.shot)   # The shot type (can be None)
        self.hand = nodedata.get_data('hand', config.hand)   # Forehand or backhand associated with shot (can be None)
        self.stat = nodedata.get_data('stat', config.stat)   # The stat type (can be None)

    def run(self, nodedata):
        """
        Generate pre_ and post_ messages suitable for the given behaviour using Behaviour Library functions.
        :param nodedata :type Blackboard: the blackboard on which we will store the created action for accesses by other
            nodes.
        :return: NodeStatus.SUCCESS when an action has been created.
        """
        if not config.stop_set and not config.stop_session:
            print("Formatting action: behaviour = {behaviour}, goal_level = {goal_level}, performance = {performance}, name = {name}, shot = {shot}, hand = {hand}".format(behaviour=self.behaviour, goal_level=self.goal_level, performance=self.performance, name=self.name, shot=self.shot, hand=self.hand))
            logging.info("Formatting action: behaviour = {behaviour}, goal_level = {goal_level}, performance = {performance}, name = {name}, exercise = {exercise}".format(behaviour=self.behaviour, goal_level=self.goal_level, performance=self.performance, name=self.name, exercise=self.shot))
            if not(self.behaviour == config.A_SILENCE):
                demo = None
                if self.behaviour in [config.A_POSITIVEMODELING, config.A_NEGATIVEMODELING,
                                      config.A_PREINSTRUCTION_POSITIVEMODELING, config.A_PREINSTRUCTION_NEGATIVEMODELING,
                                      config.A_POSTINSTRUCTIONPOSITIVE_POSITIVE_MODELING,
                                      config.A_POSTINSTRUCTIONPOSITIVE_NEGATIVE_MODELING,
                                      config.A_POSTINSTRUCTIONNEGATIVE_POSITIVEMODELING,
                                      config.A_POSTINSTRUCTIONNEGATIVE_NEGATIVEMODELING,
                                      config.A_QUESTIONING_NEGATIVEMODELING,
                                      config.A_POSITIVEMODELING_POSTINSTRUCTIONPOSITIVE,
                                      config.A_NEGATIVEMODELING_POSTINSTRUCTIONNEGATIVE,
                                      config.A_POSITIVEMODELING_PREINSTRUCTION, config.A_SCOLD_POSITIVEMODELING,
                                      config.A_CONCURRENTINSTRUCTIONPOSITIVE_POSITIVEMODELING,
                                      config.A_CONCURRENTINSTRUCTIONNEGATIVE_NEGATIVEMODELING,
                                      config.A_MANUALMANIPULATION_POSITIVEMODELING, config.A_QUESTIONING_POSITIVEMODELING,
                                      config.A_POSITIVEMODELING_CONCURRENTINSTRUCTIONPOSITIVE,
                                      config.A_POSITIVEMODELING_QUESTIONING, config.A_POSITIVEMODELING_HUSTLE,
                                      config.A_POSITIVEMODELING_PRAISE]:
                    demo = self.behaviour_lib.get_demo_string(self.behaviour, self.goal_level, self.shot, self.hand, self.stat, config.leftHand)
                question = None
                if self.behaviour in [config.A_QUESTIONING, config.A_QUESTIONING_FIRSTNAME,
                                      config.A_QUESTIONING_POSITIVEMODELING,
                                      config.A_POSITIVEMODELING_QUESTIONING, config.A_QUESTIONING_NEGATIVEMODELING]:
                    if not (self.behaviour in [config.A_PREINSTRUCTION_POSITIVEMODELING, config.A_PREINSTRUCTION,
                                               config.A_POSITIVEMODELING_PREINSTRUCTION,
                                               config.A_PREINSTRUCTION_PRAISE,
                                               config.A_PREINSTRUCTION_NEGATIVEMODELING,
                                               config.A_PREINSTRUCTION_QUESTIONING,
                                               config.A_PREINSTRUCTION_MANUALMANIPULATION,
                                               config.A_PREINSTRUCTION_FIRSTNAME,
                                               config.A_MANUALMANIPULATION_PREINSTRUCTION] and (
                                    self.goal_level == config.SESSION_GOAL or self.goal_level == config.EXERCISE_GOAL)):
                        if self.goal_level == config.ACTION_GOAL:
                            question = "Concurrent"
                        else:
                            if self.performance is None:
                                question = "FirstTime"
                            else:
                                question = "GoodBad"

                # If this is the start of a new exercise set, we need to reset the counter on Pepper's screen.
                if self.behaviour in [config.A_PREINSTRUCTION_POSITIVEMODELING, config.A_PREINSTRUCTION,
                                      config.A_POSITIVEMODELING_PREINSTRUCTION, config.A_PREINSTRUCTION_PRAISE,
                                      config.A_PREINSTRUCTION_NEGATIVEMODELING,
                                      config.A_PREINSTRUCTION_QUESTIONING,
                                      config.A_PREINSTRUCTION_MANUALMANIPULATION,
                                      config.A_PREINSTRUCTION_FIRSTNAME,
                                      config.A_MANUALMANIPULATION_PREINSTRUCTION] and self.goal_level == config.SET_GOAL:
                    r = requests.post(config.screen_post_address + "0/newRep")

                pre_msg = self.behaviour_lib.get_pre_msg(self.behaviour, self.goal_level, self.performance, self.phase, self.name, self.shot, self.hand, self.stat, config.shot_count == 3 and config.set_count == 1, config.set_count == 1)
                if (self.score is None and self.performance is None):  # or config.given_score >= 2:
                    nodedata.action = Action(pre_msg, demo=demo, question=question)
                else:
                    nodedata.action = Action(pre_msg, self.score, self.target, demo=demo, question=question, goal=self.goal_level)
                    #if self.goal_level == config.EXERCISE_GOAL or self.goal_level == config.SESSION_GOAL or self.goal_level == config.PERSON_GOAL:
                    #    config.given_score += 1
            else:
                # If silence, we still need to update the screen display on Pepper because a rep may have been done.
                output = {
                    "silence": "True"
                }
                # Send post request to Pepper
                r = requests.post(config.post_address, json=output)

                print("Returning FAIL from FormatAction, behaviour = " + str(self.behaviour))
                logging.debug("Returning FAIL from FormatAction, behaviour = " + str(self.behaviour))
                return NodeStatus(NodeStatus.FAIL, "Behaviour == A_SILENCE")

            print("Returning SUCCESS from FormatAction, action = " + str(nodedata.action))
            logging.debug("Returning SUCCESS from FormatAction, action = " + str(nodedata.action))
            return NodeStatus(NodeStatus.SUCCESS, "Created action from given behaviour.")
        else:
            return NodeStatus(NodeStatus.SUCCESS, "Stop set/session format action")


class CheckForBehaviour(Node):
    """
    Compare the currently selected behaviour to a given behaviour category.
    ...
    Attributes
    ----------
    behaviour :type int
        The current behaviour selected from the policy.
    check_behaviour :type int
        The behaviour category to check against.

    Methods
    -------
    configure(nodedata)
        Set up the initial behaviour and check_behaviour values to compare based on information stored in the
        blackboard.
    run()
        Check if the current behaviour is a member of the given check_behaviour category
        e.g. A_PREINSTRUCTION_POSITIVEMODELLING is a member of the A_PREINSTRUCTION category.
    """

    def __init__(self, name, *args, **kwargs):
        super(CheckForBehaviour, self).__init__(
            name,
            run_cb=self.run,
            configure_cb=self.configure,
            *args, **kwargs)

    def configure(self, nodedata):
        """
        Set up the initial behaviour and check_behaviour values to compare based on information stored in the
        blackboard.
        :param nodedata :type Blackboard: the blackboard associated with this Behaviour Tree containing all relevant
            behaviour information.
        :return: None
        """
        print("Configuring CheckForBehaviour: " + self._name + ", goal_level = " + str(config.goal_level))
        self.behaviour = nodedata.get_data('behaviour')              # The behaviour selected from the policy
        self.check_behaviour = nodedata.get_data('check_behaviour')  # The behaviour to check against
        self.goal_level = nodedata.get_data('goal', config.goal_level)

    def run(self, nodedata):
        """
        Check if the current behaviour is a member of the given check_behaviour category
        e.g. A_PREINSTRUCTION_POSITIVEMODELLING is a member of the A_PREINSTRUCTION category.

        Behaviour categories are defined as the 16 unique behaviours on the original observation instrument. Most likely
        categories are A_PREINSTRUCTION, A_POSTINSTRUCTIONPOSITIVE and A_POSTINSTRUCTIONNEGATIVE.
        :return: NodeStatus.SUCCESS if the behaviour is a member of the given category, NodeStatus.FAIL otherwise.
        """
        if not config.stop_set and not config.stop_session:
            # TODO: Update for variants of check_behaviour.
            # SUCCESS if next behaviour is given behaviour, else FAIL
            if self._is_example_of_behaviour(self.behaviour, self.check_behaviour):
                config.used_behaviours = []
                logging.debug("Returning SUCCESS from CheckForBehaviour, behaviour found = " + str(self.behaviour))
                # config.completed = config.COMPLETED_STATUS_FALSE
                return NodeStatus(NodeStatus.SUCCESS, "Behaviour " + str(self.check_behaviour) + " found in the form " + str(self.behaviour))
            else:
                logging.debug("Returning FAIL from CheckForBehaviour, behaviour not found = " + str(self.check_behaviour) + ", input behaviour = " + str(self.behaviour))
                return NodeStatus(NodeStatus.FAIL, "Behaviour " + str(self.check_behaviour) + " not found.")
        else:
            return NodeStatus(NodeStatus.SUCCESS, "Stop set/session check behaviour")

    def _is_example_of_behaviour(self, behaviour, check_behaviour):
        if check_behaviour == config.A_PREINSTRUCTION:
            check_list = [config.A_PREINSTRUCTION, config.A_PREINSTRUCTION_PRAISE, config.A_PREINSTRUCTION_QUESTIONING,
                          config.A_PREINSTRUCTION_POSITIVEMODELING, config.A_POSITIVEMODELING_PREINSTRUCTION,
                          config.A_PREINSTRUCTION_FIRSTNAME, config.A_PREINSTRUCTION_MANUALMANIPULATION,
                          config.A_PREINSTRUCTION_NEGATIVEMODELING, config.A_MANUALMANIPULATION_PREINSTRUCTION]
        else:
            check_list = [config.A_QUESTIONING, config. A_PREINSTRUCTION_QUESTIONING, config.A_QUESTIONING_FIRSTNAME,
                          config.A_QUESTIONING_POSITIVEMODELING, config.A_POSITIVEMODELING_QUESTIONING,
                          config.A_CONCURRENTINSTRUCTIONPOSITIVE_QUESTIONING, config.A_MANUALMANIPULATION_QUESTIONING,
                          config.A_POSTINSTRUCTIONNEGATIVE_QUESTIONING, config.A_POSTINSTRUCTIONPOSITIVE_QUESTIONING,
                          config.A_QUESTIONING_NEGATIVEMODELING]

        return True if behaviour in check_list else False



class DisplayBehaviour(Node):
    """
    Have the robot perform the formatted action.
    ...
    Attributes
    ----------
    action :type Action
        The action we want the robot to perform.

    Methods
    -------
    configure(nodedata)
        Obtain the next specified action to be executed from the blackboard.
    run()
        Execute the specified action.
    """

    # TODO: Will eventually have the action performed by the robot, but for now just print message.
    def __init__(self, name, *args, **kwargs):
        super(DisplayBehaviour, self).__init__(
            name,
            run_cb=self.run,
            configure_cb=self.configure,
            *args, **kwargs)

    def configure(self, nodedata):
        """
        Obtain the next specified action to be executed from the blackboard.
        :param nodedata :type Blackboard: the blackboard associated with this Behaviour Tree containing the action to
            be performed.
        :return: None
        """
        print("Configuring DisplayBehaviour: " + self._name)
        logging.debug("Configuring DisplayBehaviour: " + self._name)
        self.action = nodedata.get_data('action')
        self.set_start = nodedata.get_data('set_start', False)
        self.score = nodedata.get_data('score', None)
        self.goal_level = nodedata.get_data('goal_level')

    def run(self, nodedata):
        """
        Execute the specified action.
        :return: NodeStatus.SUCCESS if action sent successfully to robot, NodeStatus.FAIL otherwise.
        """
        if not config.stop_set and not config.stop_session:
            print(str(self.action))
            logging.debug(str(self.action))
            logging.info("Displaying action {}".format(str(self.action)))
            output = {
                "utterance": str(self.action)
            }
            if self.action.demo is not None:
                output['demo'] = self.action.demo
            if self.action.question is not None:
                output['question'] = self.action.question
            # Send post request to tablet output API
            if config.goal_level > 1:
                phase = "exercise"
            else:
                phase = "non-exercise"
            #utteranceURL = "http://192.168.43.19:8000/Test Utterance/non-exercise/newUtterance".replace(' ', '%20')
            if config.overridePreInstructionOption or config.overrideQuestioningOption:
                if self.goal_level == config.SESSION_GOAL:
                    goal_level = "shot"
                else:
                    goal_level = "stat"
                if config.overridePreInstructionOption:
                    utteranceURL = config.screen_post_address + str(self.action).replace(' ', '%20') + "/pre/" + goal_level + "/overrideOption"
                    config.overridePreInstructionOption = False
                else:
                    utteranceURL = config.screen_post_address + str(self.action).replace(' ', '%20') + "/question/" + goal_level + "/overrideOption"
                    config.overrideQuestioningOption = False
            else:
                utteranceURL = config.screen_post_address + str(self.action).replace(' ', '%20') + "/" + phase + "/newUtterance"
            r = requests.post(utteranceURL)
            # Send post request to Pepper
            r = requests.post(config.post_address, json=output)

            # Wait for response before continuing because the session might be paused.
            while not (r.status_code == 200):
                time.sleep(0.2)

            config.behaviour_displayed = True
            #config.need_new_behaviour = True
            if self.score is not None and config.has_score_been_provided is False:
                config.has_score_been_provided = True
                config.scores_provided += 1
                print("Setting has_score_been_provided to True")
            if self.set_start:
                api_classes.expecting_action_goal = True
            logging.debug("Returning SUCCESS from DisplayBehaviour")
            return NodeStatus(NodeStatus.SUCCESS, "Printed action message to output.")
        else:
            return NodeStatus(NodeStatus.SUCCESS, "Stop set/session display behaviour")

    def sendBehaviour(self, child_conn):
        child_conn.send(self.action)
        child_conn.close()


class GetStats(Node):
    """
    Retrieve the user stats (motivation level, playing experience, no. of sessions) from the guide and user.
    ...
    Methods
    -------
    run(nodedata)
        Set the player's motivation, ability and no. of sessions on the blackboard.
    """
    # TODO: Dummy class which will eventually get user stats from user and API
    def __init__(self, name, *args, **kwargs):
        super(GetStats, self).__init__(
            name,
            run_cb=self.run,
            *args, **kwargs)

    def run(self, nodedata):
        """
        Set the player's motivation on the blackboard.

        The ability and no. of sessions will be given by the guide. The motivation will vary each session and will have
        to be obtained from the user.
        :param nodedata :type Blackboard: the blackboard on which we will store the obtained stats for access by other
            nodes.
        :return: NodeStatus.ACTIVE when waiting for data, NodeStatus.SUCCESS when got data and added to blackboard,
            NodeStatus.FAIL otherwise.
        """
        if not config.stop_session:
            logging.debug("Running GetStats: " + self._name)

            '''output = {
                "start": str(1)
            }
            r = requests.post(post_address, json=output)'''

            # Will be ACTIVE when waiting for data and SUCCESS when got data and added to blackboard, FAIL when connection error.
            # logging.debug("In get stats")
            nodedata.motivation = config.motivation
            nodedata.player_ability = config.ability
            logging.info("Stats set, motivation = {motivation}, ability = {ability}".format(motivation=nodedata.motivation, ability=nodedata.player_ability))
            #nodedata.sessions = 6
            # logging.debug("After setting stats in GetStats: " + str(nodedata))
            logging.debug("Returning SUCCESS from GetStats, stats = " + str(nodedata))
            return NodeStatus(NodeStatus.SUCCESS, "Set stats to dummy values.")
        else:
            return NodeStatus(NodeStatus.SUCCESS, "Stop session get stats")


class GetDuration(Node):
    """
    Retrieve the user's choice of how long they wish to practice for via the robot interface.
    ...
    Methods
    -------
    run(nodedata)
        Display and obtain user input requesting the session duration in minutes.
    """
    # TODO: Dummy class which will eventually get time input from user
    def __init__(self, name, *args, **kwargs):
        super(GetDuration, self).__init__(
            name,
            run_cb=self.run,
            configure_cb=self.configure,
            *args, **kwargs)

    def configure(self, nodedata):
        """
        Obtain the current goal level (e.g. SESSION_GOAL) and optional shot/stat choice from the blackboard.
        :param nodedata :type Blackboard: the blackboard associated with this Behaviour Tree containing the goal level.
        :return: None
        """
        print("Configuring GetDuration: " + self._name)
        self.session_duration = nodedata.get_data('session_duration', 1)
        self.start_time = nodedata.get_data('start_time', 0)

    def run(self, nodedata):
        """
        Display and obtain user input requesting the session duration in minutes.
        :param nodedata :type Blackboard: the blackboard on which we will store the obtained duration for access by
            other nodes.
        :return: NodeStatus.ACTIVE when waiting for user's input, NodeStatus.SUCCESS when user's input has been received
            and data has been stored in the blackboard, NodeStatus.FAIL otherwise.
        """
        if not config.stop_session:
            logging.debug("Running GetDuration: " + self._name)
            # Will be ACTIVE when waiting for data and SUCCESS when got data and added to blackboard, FAIL when connection error.
            logging.info("Set session duration to: {duration}".format(duration=nodedata.session_duration))
            logging.debug("Returning SUCCESS from GetDuration, session duration = " + str(nodedata.session_duration))
            return NodeStatus(NodeStatus.SUCCESS, "Set session duration to dummy value 1.")
        else:
            return NodeStatus(NodeStatus.SUCCESS, "Stop session get duration")


class CreateSubgoal(Node):
    """
    Tell the guide via the API that a new subgoal is required.
    ...
    Attributes
    ----------
    previous_goal_level :type int
        The goal level (e.g. SESSION_GOAL) we are currently on (before creating a subgoal).

    Methods
    -------
    configure(nodedata)
        Obtain the current goal level (e.g. SESSION_GOAL) from the blackboard.
    run(nodedata)
        Send request to the API for the guide to create a subgoal.
    """
    # TODO: Dummy class which will eventually communicate with guide via API
    def __init__(self, name, *args, **kwargs):
        super(CreateSubgoal, self).__init__(
            name,
            run_cb=self.run,
            configure_cb=self.configure,
            *args, **kwargs)

    def configure(self, nodedata):
        """
        Obtain the current goal level (e.g. SESSION_GOAL) and optional shot/stat choice from the blackboard.
        :param nodedata :type Blackboard: the blackboard associated with this Behaviour Tree containing the goal level.
        :return: None
        """
        print("Configuring CreateSubgoal: " + self._name)
        print(("createSubgoal nodedata = " + str(nodedata)))
        logging.debug("Configuring CreateSubgoal: " + self._name)
        logging.debug("createSubgoal nodedata = " + str(nodedata))
        self.previous_goal_level = nodedata.get_data('goal', -1)
        self.shot = nodedata.get_data('shot')
        self.stat = nodedata.get_data('stat')

    def run(self, nodedata):
        """
        Send request to the API for the guide to create a subgoal.
        :param nodedata :type Blackboard: the blackboard on which we will update the goal level.
        :return: NodeStatus.SUCCESS when request is sent to API, NodeStatus.FAIL if current goal level is ACTION_GOAL
            or cannot connect to API.
        """
        if not config.stop_set and not config.stop_session:
            config.overriden = False
            # Will return SUCCESS once request sent to API, FAIL if called on ACTION_GOAL or connection error.
            if self.previous_goal_level == config.BASELINE_GOAL:
                nodedata.new_goal = config.STAT_GOAL
                logging.info("Created subgoal, new goal level = {}".format(nodedata.new_goal))
                logging.debug("Returning SUCCESS from CreateSubGoal, new goal level = " + str(nodedata.goal))
                return NodeStatus(NodeStatus.SUCCESS, "Created subgoal: 3 from BASELINE_GOAL")
            elif self.previous_goal_level > config.BASELINE_GOAL:
                logging.debug("Returning FAIL from CreateSubGoal, previous goal level = " + str(self.previous_goal_level))
                return NodeStatus(NodeStatus.FAIL, "Cannot create subgoal of ACTION_GOAL.")
            else:
                if self.previous_goal_level == config.EXERCISE_GOAL and self.exercise_data is False:
                    nodedata.new_goal = 6
                else:
                    nodedata.new_goal = self.previous_goal_level + 1
                    # Select which exercise to perform.
                    if nodedata.new_goal == config.EXERCISE_GOAL:
                        config.set_count = 0  # Reset the set count for this session to 0.
                        config.performance = None
                        config.score = -1

                        # Update exercise picture on Pepper's tablet screen and reset the counter
                        if nodedata.get_data("new_exercise") == 0:
                            exerciseString = "TabletopCircles"
                        elif nodedata.get_data("new_exercise") == 1:
                            exerciseString = "TowelSlides"
                        elif nodedata.get_data("new_exercise") == 2:
                            exerciseString = "CaneRotations"
                        else:
                            exerciseString = "ShoulderOpeners"
                        utteranceURL = config.screen_post_address + exerciseString + "/newPicture"
                        r = requests.post(utteranceURL)
                        r = requests.post(config.screen_post_address + "0/newRep")
                config.phase = config.PHASE_START  # Start of goal will always be before something happens.
                print("Created subgoal, new goal level = {}".format(nodedata.new_goal))
                logging.info("Created subgoal, new goal level = {}".format(nodedata.new_goal))
                logging.debug("Returning SUCCESS from CreateSubGoal, new goal level = " + str(nodedata.new_goal))
                return NodeStatus(NodeStatus.SUCCESS, "Created subgoal: " + str(self.previous_goal_level + 1))
        else:
            if config.stop_session:
                nodedata.skipped_create = True
            return NodeStatus(NodeStatus.SUCCESS, "Stop set/session create subgoal")


class EndSubgoal(Node):
    """
    Tell the guide via the API that the subgoal is completed.
    ...
    Attributes
    ----------
    goal_level :type int
        The goal level (e.g. SESSION_GOAL) we are currently on (which is now completed).

    Methods
    -------
    configure(nodedata)
        Obtain the current goal level (e.g. SESSION_GOAL) from the blackboard.
    run(nodedata)
        Send request to the API for the guide to complete the goal.
    """
    def __init__(self, name, *args, **kwargs):
        super(EndSubgoal, self).__init__(
            name,
            run_cb=self.run,
            configure_cb=self.configure,
            *args, **kwargs)

    def configure(self, nodedata):
        """
        Obtain the current goal level (e.g. SESSION_GOAL) from the blackboard.
        :param nodedata :type Blackboard: the blackboard associated with this Behaviour Tree containing the goal level.
        :return: None
        """
        print("Configuring EndSubgoal: " + self._name)
        logging.debug("Configuring EndSubgoal: " + self._name)
        self.goal_level = nodedata.get_data('goal', -1)

    def run(self, nodedata):
        """
        Send request to the API for the guide to create a subgoal.
        :param nodedata :type Blackboard: the blackboard on which we will update the goal level.
        :return: NodeStatus.SUCCESS when request is sent to API, NodeStatus.FAIL if current goal level is ACTION_GOAL
            or cannot connect to API.
        """
        if not config.stop_set or self.skipped_create:
            # Will return SUCCESS once request sent to API, FAIL if called on goal > 6 or connection error.
            if self.goal_level > 6 or self.goal_level < 0:
                print("Returning FAIL from EndSubgoal, goal_level = " + str(self.goal_level))
                logging.debug("Returning FAIL from EndSubgoal, goal_level = " + str(self.goal_level))
                return NodeStatus(NodeStatus.FAIL, "Cannot create subgoal of " + str(self.goal_level))
            else:
                if self.goal_level == config.BASELINE_GOAL:
                    nodedata.stat = 1
                    nodedata.phase = config.PHASE_END
                    nodedata.new_goal = config.STAT_GOAL
                    config.completed = config.COMPLETED_STATUS_TRUE
                else:
                    config.goal_level -= 1
                    # TODO: I've set max set_count to 3 but there may be some freedom there depending on user performance.
                    if ((self.goal_level == config.SET_GOAL and config.set_count == 3) or self.goal_level == config.STAT_GOAL or self.goal_level == config.EXERCISE_GOAL or self.goal_level == config.SESSION_GOAL) and not config.stop_session:
                        config.phase = config.PHASE_END
                    else:
                        config.phase = config.PHASE_START
                    nodedata.new_goal = self.goal_level - 1
                    nodedata.phase = config.PHASE_START  # All behaviours have happened so its start of new goal.
                    config.completed = config.COMPLETED_STATUS_TRUE
                    config.scores_provided = 0  # At new goal level we will need to provide the average score again.
                    if self.goal_level == config.EXERCISE_GOAL:
                        config.session_time += 1
                        config.shot = None
                    if self.goal_level == config.STAT_GOAL:
                        config.stat = None
                        config.used_stats = []

                print("Ended subgoal {old_goal}. New goal level = {new_goal}.".format(old_goal=self.goal_level, new_goal=nodedata.new_goal))
                logging.info("Ended subgoal {old_goal}. New goal level = {new_goal}.".format(old_goal=self.goal_level, new_goal=nodedata.new_goal))
                logging.debug("Returning SUCCESS from EndSubgoal, new subgoal level = " + str(nodedata.new_goal))
                return NodeStatus(NodeStatus.SUCCESS, "Completed subgoal: " + str(self.goal_level - 1))
        else:
            if self.skipped_create:
                # Set the time to be the max session time so the session can stop.
                config.session_time = config.MAX_SESSION_TIME
            return NodeStatus(NodeStatus.SUCCESS, "Stop set/session endsubgoal")


class TimestepCue(Node):
    """
    Receive a notification from the guide that an action is required from the robot.

    This can come at any goal level, either in the intro or feedback stage, and crucially will be called by the guide
    after every shot played by the user so that the robot can perform actions at the appropriate time during exercise.
    ...
    Methods
    -------
    run(nodedata)
        Check if the guide has requested an action be performed, and if so update the blackboard with the data about the
        current state given by the guide.
    """
    def __init__(self, name, *args, **kwargs):
        super(TimestepCue, self).__init__(
            name,
            run_cb=self.run,
            configure_cb=self.configure,
            *args, **kwargs)

    def configure(self, nodedata):
        print("Configureing TimestepCue: " + self._name + ", nodedata: " + str(nodedata))
        logging.debug("Configuring TimestepCue: " + self._name)
        self.goal_level = nodedata.get_data('goal')
        self.phase = nodedata.get_data('phase')
        self.shot = nodedata.get_data('shot', config.shot)
        self.hand = nodedata.get_data('hand', config.hand)
        self.stat = nodedata.get_data('stat', config.stat)
        config.completed = config.COMPLETED_STATUS_FALSE

    def run(self, nodedata):
        """
        Check if the guide has requested an action be performed, and if so update the blackboard with the data about the
        current state given by the guide.

        All communication will be done through the API. A queue stack structure will be used to store timestepCue calls
        by the guide and the stack will be emptied each time this method is called (but only the top member acted upon).
        This will mean the robot never falls behind the interaction state (but may sometimes stay silent).

        Layout of participant history files:
            Directory: <participant number>
                File: Sessions.txt
                    Contents:
                        <no. of sessions> (Updated at end of person goal)
                        <performance for 1st session> (Updated at end of session goal)
                        <performance for 2nd session>
                        ...
                Directory: <exercise name>
                    File: Baseline.txt (updated at end of baseline goal)
                        Contents:
                            <stat name>
                            <stat score>, <stat performance>
                            ...
                    File: Aggregator.txt (aggregated at end of exercise)
                        Contents:
                            <previous score>
                            <previous performance>
                            <stat name>
                            <stat score>, <stat performance>
                            <stat name>
                            <stat score>, <stat performance>
                            ...
                    File: <session no.>.txt
                        Contents:
                            <score> (aggregated at end of exercise)
                            <performance>
                            <stat name>
                            <stat score>, <stat performance>
                            <no. of sets>
                            <stat score 1st set>, <stat performance 1st set>
                            <stat score 2nd set>, <stat performance 2nd set>
                            ...
                            <stat name>
                            <stat score>, <stat performance>
                            <no. of sets>
                            <stat score 1st set>, <stat performance 1st set>
                            <stat score 2nd set>, <stat performance 2nd set>
                            ...
                    ...
                    File: <current session no.>.txt
                        Contents: (updated as session progresses)
                            <stat name>
                            <stat score>, <stat performance>  (Aggregated at end of stat)
                            <no. of sets>
                            <stat score 1st set>, <stat performance 1st set>
                            <stat score 2nd set>, <stat performance 2nd set>
                            ...
                            <stat name>
                            <no. of sets>
                            <stat score 1st set>, <stat performance 1st set>
                            <stat score 2nd set>, <stat performance 2nd set>
                            ...
                Directory: <exercise name>
                    ...
                ...

            # OLD
            <number of sessions>
            <performance for session 1>
            <performance for session 2>
            ...
            <exercise name>
            <number of times exercise has been in a session>
            <exercise performance for session 1>,<exercise score for session 1>
            <stat name>
            <stat performance>,<stat score>
            <st
            <exercise performance for session 2>,<exercise score for session 2>
            ...
            Current session
            <exercise performance for 1st set>,<exercise score for first set>  # collated into <exercise performance for session x> at completion of
            <exercise performance for 2nd set>,<exercise score for first set>  # exercise and "Current session" section removed.
            ...
            <exercise name>
            ...

        :param nodedata :type Blackboard: the blackboard on which we will store the data provided by the guide.
        :return: NodeStatus.ACTIVE when waiting for data from the guide, NodeStatus.SUCCESS when data has been received
            and added to the blackboard, NodeStatus.FAIL otherwise.
        """
        if not config.stop_set and (
                not config.stop_session and config.phase == config.PHASE_START):  # If the session is stopped, we still need to go into timestep cue to write the appropriate data up to now to the file.
            # Will be ACTIVE when waiting for data and SUCCESS when got data and added to blackboard, FAIL when connection error.
            if self.goal_level == -1:  # Person goal created after receiving info from guide.
                print("Timestep Cue, self.goal_level = " + str(self.goal_level))
                if config.goal_level == config.PERSON_GOAL:  # For person goal should have name, ability and no. of sessions.
                    if config.phase == config.PHASE_END:  # Feedback sequence
                        nodedata.phase = config.PHASE_END
                        nodedata.performance = mode(config.session_performance_list)
                        # Write updated no. of sessions to file.
                        f = open("~/PycharmProjects/coachingPolicies/SessionDataFiles/" + config.participantNo + "/Sessions.txt", "r")
                        file_contents = f.readlines()
                        f.close()

                        file_contents[0] = str(config.sessions) + "\n"
                        f = open("~/PycharmProjects/coachingPolicies/SessionDataFiles/" + config.participantNo + "/Sessions.txt", "w")
                        f.writelines(file_contents)
                        f.close()

                        nodedata.phase = config.PHASE_END
                        logging.info(
                            "Feedback for session, performance = {performance}".format(performance=nodedata.performance))
                        logging.debug("Returning SUCCESS from TimestepCue person goal (end), stats = " + str(nodedata))
                        return NodeStatus(NodeStatus.SUCCESS, "Data for stat goal obtained from guide:" + str(nodedata))
                    else:
                        # Get no. of sessions from file.
                        try:
                            f = open("~/PycharmProjects/coachingPolicies/SessionDataFiles/" + config.participantNo + "/Sessions.txt", "r")
                            file_contents = f.readlines()
                            f.close()
                            config.sessions = int(file_contents[0]) + 1
                        except:
                            config.sessions = 1
                            os.mkdir("/home/martin/PycharmProjects/coachingPolicies/SessionDataFiles/" + config.participantNo)
                            f = open("/home/martin/PycharmProjects/coachingPolicies/SessionDataFiles/" + config.participantNo + "/Sessions.txt", "a")
                            f.write(str(config.sessions) + "\n")  # Write participant number and 0 sessions to the new file.
                            f.close()

                        nodedata.sessions = config.sessions
                        nodedata.player_ability = config.ability
                        nodedata.name = config.name
                        nodedata.phase = config.PHASE_START
                        logging.debug("Returning SUCCESS from TimestepCue player goal, stats = " + str(nodedata))
                        return NodeStatus(NodeStatus.SUCCESS, "Data for person goal obtained from guide:" + str(nodedata))
                else:
                    logging.debug("Returning ACTIVE from TimestepCue player goal")
                    return NodeStatus(NodeStatus.ACTIVE, "Waiting for person goal data from guide.")

            elif self.goal_level == config.SESSION_GOAL:  # For session goal should have performance from previous session.
                logging.debug("TimestepCue, config.goal_level = " + str(config.goal_level))
                if config.goal_level == config.SESSION_GOAL:
                    if config.phase == config.PHASE_END:  # Feedback sequence
                        nodedata.phase = config.PHASE_END
                        if not (len(config.session_performance_list) == 0):
                            nodedata.performance = mode(config.session_performance_list)
                            # Write session performance to file.
                            f = open("/home/martin/PycharmProjects/coachingPolicies/SessionDataFiles/" + config.participantNo + "/Sessions.txt", "r")
                            file_contents = f.readlines()
                            f.close()

                            file_contents[config.sessions] = str(nodedata.performance) + "\n"
                            f = open("/home/martin/PycharmProjects/coachingPolicies/SessionDataFiles/" + config.participant_filename, "w")
                            f.writelines(file_contents)
                            f.close()

                        nodedata.phase = config.PHASE_END

                        config.stop_session = False  # Resume the final behaviours of the session.

                        logging.info(
                            "Feedback for session, performance = {performance}".format(performance=nodedata.performance))
                        logging.debug("Returning SUCCESS from TimestepCue session goal (end), stats = " + str(nodedata))
                        return NodeStatus(NodeStatus.SUCCESS, "Data for stat goal obtained from guide:" + str(nodedata))
                    else:
                        if config.sessions > 1:  # If this is not the first session, get previous performance from file.
                            f = open("/home/martin/PycharmProjects/coachingPolicies/SessionDataFiles/" + config.participantNo + "/Sessions.txt", "r")
                            file_contents = f.readlines()
                            f.close()

                            config.performance = int(file_contents[config.sessions])
                        nodedata.performance = config.performance
                        nodedata.phase = config.PHASE_START
                        logging.debug("Returning SUCCESS from TimestepCue session goal, stats = " + str(nodedata))
                        return NodeStatus(NodeStatus.SUCCESS, "Data for session goal obtained from guide:" + str(nodedata))
                else:
                    # config.goal_level = config.SESSION_GOAL
                    logging.debug("Returning ACTIVE from TimestepCue session goal")
                    return NodeStatus(NodeStatus.ACTIVE, "Waiting for session goal data from guide.")

            elif self.goal_level == config.EXERCISE_GOAL:  # For shot goal should have performance from last time this shot was practiced.
                if config.goal_level == config.EXERCISE_GOAL:
                    if config.phase == config.PHASE_END:  # Feedback sequence
                        if config.completed == config.COMPLETED_STATUS_TRUE:  # This is actually the end of a baseline goal. Might need to update this so it's not as weirdly laid out.
                            logging.debug("Baseline goal feedback sequence")
                            # Will get list of scores.
                            nodedata.phase = config.PHASE_END
                            nodedata.score = config.metric_score_list
                            nodedata.performance = config.metric_performance_list

                            f = open("/home/martin/PycharmProjects/coachingPolicies/SessionDataFiles/" + config.participantNo + "/" + self.hand + str(self.shot) + "/Baseline.txt", "r")
                            file_contents = f.readlines()
                            f.close()

                            index = 1
                            for score, performance in nodedata.score, nodedata.performance:
                                file_contents[index] = str(score) + ", " + str(performance) + ", \n"
                                index += 2

                                # Create sorted stat list. Stat with the lowest score will come first.
                                stat_set = {}
                                stat_set[file_contents[index-1]] = score

                            sorted_stat_set = sorted(stat_set.items(), key=operator.itemgetter(1))
                            sorted_stat_list = []
                            for i in sorted_stat_set:
                                sorted_stat_list.append(i[0])
                            sorted_stat_list.reverse()  # Reverse to get most important shot first.

                            config.sorted_stat_list = sorted_stat_list

                            f = open("/home/martin/PycharmProjects/coachingPolicies/SessionDataFiles/" + config.participantNo + "/" + self.hand + str(self.shot) + "/Baseline.txt", "w")
                            f.writelines(file_contents)
                            f.close()

                            logging.debug("Returning SUCCESS from TimestepCue shot goal (end), stats = " + str(nodedata))
                            return NodeStatus(NodeStatus.SUCCESS, "Data for shot goal obtained from guide:" + str(nodedata))
                        elif config.completed == config.COMPLETED_STATUS_FALSE:  # Feedback Sequence
                            logging.debug("Exercise goal feedback sequence")
                            nodedata.phase = config.PHASE_END
                            if not (len(config.shot_performance_list) == 0):
                                nodedata.performance = config.performance
                                config.session_performance_list.append(nodedata.performance)
                                nodedata.score = config.score
                                config.session_score_list.append(nodedata.score)

                                # Write performance data about the exercise just completed to file.
                                f = open("/home/martin/PycharmProjects/coachingPolicies/SessionDataFiles/" + config.participantNo + "/" + self.hand + str(self.shot) + "/Aggregator.txt", "r")
                                aggregator_contents = f.readlines()
                                f.close()
                                print("File contents = " + str(aggregator_contents))

                                f = open("/home/martin/PycharmProjects/coachingPolicies/SessionDataFiles/" + config.participantNo + "/" + self.hand + str(self.shot) + "/" + config.sessions + ".txt", "r")
                                this_session_contents = f.readlines()
                                f.close()

                                f = open("/home/martin/PycharmProjects/coachingPolicies/SessionDataFiles/" + config.participantNo + "/" + self.hand + str(self.shot) + "/Baseline.txt", "r")
                                baseline_contents = f.readlines()
                                f.close()

                                this_session_contents.insert(0, nodedata.score + "\n")
                                this_session_contents.insert(1, nodedata.performance + "\n")

                                aggregator_contents[0] = nodedata.score + "\n"
                                aggregator_contents[1] = nodedata.performance + "\n"

                                this_session_line_no = 2
                                while len(this_session_contents) > this_session_line_no:
                                    stat = this_session_contents[this_session_line_no] + "\n"
                                    this_session_line_no += 1
                                    if not (stat in aggregator_contents):
                                        aggregator_contents.append(stat)
                                        aggregator_contents.append(this_session_contents[this_session_line_no] + "\n")
                                    else:
                                        index = aggregator_contents.index(stat)
                                        aggregator_contents[index+1] = this_session_contents[this_session_line_no] + "\n"

                                    # Update baseline file
                                    index = baseline_contents.index(stat)
                                    baseline_contents[index + 1] = this_session_contents[this_session_line_no] + "\n"

                                    this_session_line_no += 1

                                print("File contents = " + str(aggregator_contents))

                                f = open("/home/martin/PycharmProjects/coachingPolicies/SessionDataFiles/" + config.participantNo + "/" + self.hand + str(self.shot) + "/Aggregator.txt", "w")
                                f.writelines(aggregator_contents)
                                f.close()

                                f = open("/home/martin/PycharmProjects/coachingPolicies/SessionDataFiles/" + config.participantNo + "/" + self.hand + str(self.shot) + "/" + config.sessions + ".txt", "w")
                                f.writelines(this_session_contents)
                                f.close()

                                f = open("/home/martin/PycharmProjects/coachingPolicies/SessionDataFiles/" + config.participantNo + "/" + self.hand + str(self.shot) + "/Baseline.txt", "w")
                                f.writelines(baseline_contents)
                                f.close()

                            # Clear the controller's lists for the exercise that has just happened.
                            config.shot_performance_list = []
                            config.shot_score_list = []
                            nodedata.target = config.target

                            nodedata.phase = config.PHASE_END
                            logging.info(
                                "Feedback for shot, score = {score}, target = {target}, performance = {performance}".format(
                                    score=nodedata.score, target=nodedata.target, performance=nodedata.performance))
                            logging.debug("Returning SUCCESS from TimestepCue shot goal (end), stats = " + str(nodedata))
                            return NodeStatus(NodeStatus.SUCCESS, "Data for shot goal obtained from guide:" + str(nodedata))
                        else:
                            logging.debug("Returning ACTIVE from TimestepCue shot goal, config.completed = COMPLETED_STATUS_UNDEFINED")
                            return NodeStatus(NodeStatus.ACTIVE, "Waiting for shot goal data from guide.")
                    else:
                        # Get performance data of previous time user did this exercise from file.
                        try:
                            f = open("/home/martin/PycharmProjects/coachingPolicies/SessionDataFiles/" + config.participantNo + "/" + self.hand + str(self.shot) + "/Aggregator.txt", "r")
                            file_contents = f.readlines()
                            f.close()
                            config.performance = file_contents[1]
                            config.score = file_contents[0]

                            try:
                                # Create sorted stat list. Stat with the lowest score will come first. If this shot hasn't
                                # been performed before, this will be done at the end of the baseline goal.
                                f = open("/home/martin/PycharmProjects/coachingPolicies/SessionDataFiles/" + config.participantNo + "/" + self.hand + str(self.shot) + "/Baseline.txt", "r")
                                file_contents = f.readlines()
                                f.close()

                                stat_set = {}
                                max = len(file_contents)
                                index = 0
                                while index < max:
                                    stat_set[file_contents[index]] = float(file_contents[index+1].split(", ")[0])
                                    index += 2

                                sorted_stat_set = sorted(stat_set.items(), key=operator.itemgetter(1))
                                sorted_stat_list = []
                                for i in sorted_stat_set:
                                    sorted_stat_list.append(i[0])
                                sorted_stat_list.reverse()  # Reverse to get most important shot first.

                                config.sorted_stat_list = sorted_stat_list
                            except:
                                print("Aggregator text file found but baseline text file not found, in start of exercise goal.")

                        except:  # If file doesn't exist, create it.
                            print(config.participantNo)
                            print(self.hand)
                            print(self.shot)
                            os.mkdir("/home/martin/PycharmProjects/coachingPolicies/SessionDataFiles/" + config.participantNo + "/" + self.hand + str(self.shot))
                            f = open("/home/martin/PycharmProjects/coachingPolicies/SessionDataFiles/" + config.participantNo + "/" + self.hand + str(self.shot) + "/Aggregator.txt", "a")
                            file_contents = "0"
                            f.write(file_contents)
                            f.close()
                            config.performance = None
                            config.score = None

                        print("got data from file.")
                        nodedata.performance = config.performance
                        nodedata.score = config.score
                        nodedata.target = config.target

                        nodedata.phase = config.PHASE_START
                        # config.goal_level = config.SET_GOAL
                        logging.debug("Returning SUCCESS from TimestepCue exercise goal, stats = " + str(nodedata))
                        return NodeStatus(NodeStatus.SUCCESS, "Data for exercise goal obtained from guide:" + str(nodedata))
                else:
                    logging.debug("Returning ACTIVE from TimestepCue exercise goal, config.goal_level != 2")
                    return NodeStatus(NodeStatus.ACTIVE, "Waiting for exercise goal data from guide.")

            elif self.goal_level == config.STAT_GOAL:  # For stat goal should have target and performance from last time this stat was practiced.
                if config.goal_level == config.STAT_GOAL:
                    if config.phase == config.PHASE_END:  # Feedback sequence
                        # Aggregate performance data about this stat and write it to file.
                        if not (len(config.stat_performance_list) == 0):
                            nodedata.performance = config.performance
                            nodedata.phase = config.PHASE_END
                            nodedata.score = config.score
                            nodedata.target = config.target

                            f = open("/home/martin/PycharmProjects/coachingPolicies/SessionDataFiles/" + config.participantNo + "/" + self.hand + str(self.shot) + "/" + config.sessions + ".txt", "r")
                            file_contents = f.readlines()
                            f.close()

                            stat_name = str(self.stat) + "\n"
                            index = file_contents.index(stat_name)
                            file_contents.insert(index+1, nodedata.score + ", " + nodedata.performance + ", \n")

                            f = open("/home/martin/PycharmProjects/coachingPolicies/SessionDataFiles/" + config.participantNo + "/" + self.hand + str(self.shot) + "/" + config.sessions + ".txt", "w")
                            f.writelines(file_contents)
                            f.close()

                            config.shot_performance_list.append(nodedata.performance)
                            config.shot_score_list.sppend(nodedata.score)

                            # Clear the controller's lists for the stat that has just happened.
                            config.stat_performance_list = []
                            config.stat_score_list = []

                            nodedata.phase = config.PHASE_END

                        logging.info("Feedback for stat, score = {score}, target = {target}, performance = {performance}".format(score=nodedata.score, target=nodedata.target, performance=nodedata.performance))
                        logging.debug("Returning SUCCESS from TimestepCue stat goal, stats = " + str(nodedata))
                        return NodeStatus(NodeStatus.SUCCESS, "Data for stat goal obtained from guide:" + str(nodedata))
                    else:
                        # Get performance data of previous time user did this stat for this exercise from file.
                        stat_name = None
                        try:
                            f = open("/home/martin/PycharmProjects/coachingPolicies/SessionDataFiles/" + config.participantNo + "/" + self.hand + str(self.shot) + "/Aggregator.txt", "r")
                            file_contents = f.readlines()
                            f.close()

                            stat_name = str(self.stat) + "\n"
                            if stat_name in file_contents:
                                index = file_contents.index(stat_name)
                                split = file_contents[index+1].split(", ")
                                config.score = split[0]
                                config.performance = split[1]
                            else:
                                config.performance = None
                                config.score = None
                        except:
                            print("File error")

                        f = open("/home/martin/PycharmProjects/coachingPolicies/SessionDataFiles/" + config.participantNo + "/" + self.hand + str(self.shot) + "/" + config.sessions + ".txt", "r")
                        file_contents = f.readlines()
                        f.close()

                        file_contents.append(stat_name)
                        f = open("/home/martin/PycharmProjects/coachingPolicies/SessionDataFiles/" + config.participantNo + "/" + self.hand + str(self.shot) + "/" + config.sessions + ".txt", "w")
                        f.writelines(file_contents)
                        f.close()

                        nodedata.performance = config.performance
                        nodedata.phase = config.PHASE_START
                        logging.debug("Returning SUCCESS from TimestepCue stat goal, stats = " + str(nodedata))
                        return NodeStatus(NodeStatus.SUCCESS, "Data for stat goal obtained from guide:" + str(nodedata))
                else:
                    logging.debug("Returning ACTIVE from TimestepCue stat goal")
                    return NodeStatus(NodeStatus.ACTIVE, "Waiting for stat goal data from guide.")

            elif self.goal_level == config.SET_GOAL:
                if config.goal_level == config.SET_GOAL:
                    print("config.goal_level == config.SET_GOAL")
                    if config.phase == config.PHASE_END:  # Just finished previous goal level so into feedback sequence.
                        nodedata.phase = config.PHASE_END
                        if not (len(config.stat_performance_list) == 0):
                            # print("performance list = " + str(config.set_performance_list) + ", mode = " + str(mode(config.set_performance_list)))
                            nodedata.performance = config.performance
                            # print("Average performance = " + str(nodedata.performance))
                            nodedata.score = config.avg_score
                            # Update score in controller
                            config.stat_performance_list.append(nodedata.performance)
                            config.stat_score_list.append(nodedata.score)

                            # Write to file
                            f = open("/home/martin/PycharmProjects/coachingPolicies/SessionDataFiles/" + config.participantNo + "/" + self.hand + str(self.shot) + "/" + config.sessions + ".txt", "r")
                            file_contents = f.readlines()
                            f.close()

                            file_contents.append(str(nodedata.score) + ", " + str(nodedata.performance) + ", \n")
                            f = open("/home/martin/PycharmProjects/coachingPolicies/SessionDataFiles/" + config.participantNo + "/" + self.hand + str(self.shot) + "/" + config.sessions + ".txt", "w")
                            f.writelines(file_contents)
                            f.close()

                        # Clear the controller's lists for the set that has just happened.
                        config.set_performance_list = []
                        config.set_score_list = []
                        nodedata.target = config.target
                        logging.info("Feedback for exercise set, score = {score}, target = {target}, performance = {performance}".format(score=nodedata.score, target=nodedata.target, performance=nodedata.performance))
                        logging.debug("Returning SUCCESS from TimestepCue set goal feedback, stats = " + str(nodedata))
                        return NodeStatus(NodeStatus.SUCCESS, "Data for set goal obtained from guide:" + str(nodedata))
                    else:  # For set goal we need information about the previous set if this is not the first set of this exercise.
                        nodedata.phase = config.PHASE_START

                        f = open("/home/martin/PycharmProjects/coachingPolicies/SessionDataFiles/" + config.participantNo + "/" + self.hand + str(self.shot) + "/" + config.sessions + ".txt", "r")
                        file_contents = f.readlines()
                        f.close()
                        stat_name = str(self.stat) + "\n"

                        if len(config.stat_performance_list) > 0:
                            nodedata.performance = config.stat_performance_list[len(config.set_performance_list) - 1]  # Get last entry of stat performance list.
                            nodedata.score = config.stat_score_list[len(config.stat_score_list) - 1]

                            index = file_contents.index(stat_name)
                            file_contents.insert(index+1, config.set_count)
                            f = open("/home/martin/PycharmProjects/coachingPolicies/SessionDataFiles/" + config.participantNo + "/" + self.hand + str(self.shot) + "/" + config.sessions + ".txt", "w")
                            f.writelines(file_contents)
                            f.close()
                        else:
                            nodedata.performance = None
                            nodedata.score = None

                            file_contents.append(config.set_count)
                            f = open("/home/martin/PycharmProjects/coachingPolicies/SessionDataFiles/" + config.participantNo + "/" + self.hand + str(self.shot) + "/" + config.sessions + ".txt", "w")
                            f.writelines(file_contents)
                            f.close()

                        config.shot_count = 0
                        # config.completed = config.COMPLETED_STATUS_FALSE
                        logging.debug("Returning SUCCESS from TimestepCue set goal, stats = " + str(nodedata))
                        return NodeStatus(NodeStatus.SUCCESS, "Data for set goal obtained from guide:" + str(nodedata))
                else:
                    # config.goal_level = config.SET_GOAL
                    # config.phase = config.PHASE_END
                    print("Returning ACTIVE from TimestepCue set goal")
                    logging.debug("Returning ACTIVE from TimestepCue set goal")
                    return NodeStatus(NodeStatus.ACTIVE, "Waiting for set goal data from guide.")

            elif self.goal_level == config.ACTION_GOAL and not config.stop_session:
                print("Timestep cue action goal")
                if config.goal_level == config.ACTION_GOAL:
                    config.goal_level = config.SET_GOAL
                    nodedata.phase = config.PHASE_END
                    nodedata.performance = config.performance
                    config.set_performance_list.append(nodedata.performance)
                    nodedata.score = config.score
                    config.set_score_list.append(nodedata.score)
                    nodedata.target = config.target
                    print("Returning SUCCESS from TimestepCue action goal")
                    logging.debug("Returning SUCCESS from TimestepCue action goal, stats = " + str(nodedata))
                    return NodeStatus(NodeStatus.SUCCESS, "Data for action goal obtained from guide:" + str(nodedata))
                else:
                    # config.goal_level = config.ACTION_GOAL
                    print("Returning ACTIVE from TimestepCue action goal")
                    logging.debug("Returning ACTIVE from TimestepCue action goal")
                    return NodeStatus(NodeStatus.ACTIVE, "Waiting for action goal input from operator.")

            elif self.goal_level == config.BASELINE_GOAL:
                if config.goal_level == 4:  # Baseline goal intro sequence
                    nodedata.phase = config.PHASE_START
                    config.shot_count = 0
                    config.completed = config.COMPLETED_STATUS_FALSE

                    # Create file for baseline goal.
                    f = open("/home/martin/PycharmProjects/coachingPolicies/SessionDataFiles/" + config.participantNo + "/" + self.hand + str(self.shot) + "/Baseline.txt", "a")
                    file_contents = ["racketPreparation\n",
                                     "0\n",
                                     "downSwingSpeed\n",
                                     "0\n",
                                     "impactCutAngle\n",
                                     "0\n",
                                     "impactSpeed\n",
                                     "0\n",
                                     "followThroughSwing\n",
                                     "0\n",
                                     "followThroughTime\n",
                                     "0\n"]
                    f.writelines(file_contents)
                    f.close()
                    logging.debug("Returning SUCCESS from TimestepCue baseline goal, stats = " + str(nodedata))
                    return NodeStatus(NodeStatus.SUCCESS, "Data for baseline goal obtained from guide:" + str(nodedata))
                else:
                    logging.debug("Returning ACTIVE from TimestepCue baseline goal")
                    return NodeStatus(NodeStatus.ACTIVE, "Waiting for baseline goal data from guide.")

            nodedata.performance = config.MET
            nodedata.phase = config.PHASE_START
            nodedata.target = 0.80
            nodedata.score = 0.79
            logging.debug("Returning SUCCESS from TimestepCue, stats = " + str(nodedata))
            return NodeStatus(NodeStatus.SUCCESS, "Set timestep cue values to dummy values MET, PHASE_START, 0.80, 0.79.")
        else:
            return NodeStatus(NodeStatus.SUCCESS, "Stop set timestep cue")


class DurationCheck(Node):
    """
    Check if the session has reached the time limit selected by the user.
    ...
    Attributes
    ----------
    start_time :type long
        The time (in seconds) at which the session started.
    session_duration :type int
        The time (in minutes) the user requested the session to last.

    Methods
    -------
    configure(nodedata)
        Obtain the session start time and requested session duration from the blackboard.
    run()
        Compare the requested session duration to the amount of time the session has been running.
    """
    def __init__(self, name, *args, **kwargs):
        super(DurationCheck, self).__init__(
            name,
            run_cb=self.run,
            configure_cb=self.configure,
            *args, **kwargs)

    def configure(self, nodedata):
        """
        Obtain the session start time and requested session duration from the blackboard.
        :param nodedata :type Blackboard: the blackboard associated with this Behaviour Tree containing the time data.
        :return: None
        """
        print("Configuring DurationCheck: " + self._name)
        logging.debug("Configuring DurationCheck: " + self._name)
        self.start_time = nodedata.get_data('start_time')
        self.session_duration = nodedata.get_data('session_duration')
        # Only use until getting actual time:
        self.current_time = config.session_time

    def run(self, nodedata):
        """
        Compare the requested session duration to the amount of time the session has been running.
        :return: NodeStatus.FAIL when session duration has not been reached, NodeStatus.SUCCESS otherwise.
        """
        if not config.stop_set and not config.stop_session:
            # TODO update once getting actual time from user
            # Will return FAIL when when duration has not been reached. SUCCESS when it has.
            # self.current_time += 1
            if self.session_duration > self.current_time:
                print("Session time limit NOT reached, current duration = {a}, session limit = {limit}.".format(
                    a=self.current_time, limit=self.session_duration))
                logging.info("Session time limit NOT reached, current duration = {a}, session limit = {limit}.".format(a=self.current_time - self.start_time, limit=self.session_duration))
                logging.debug("Returning FAIL from DurationCheck - time limit not yet reached, current time = " + str(self.current_time))
                return NodeStatus(NodeStatus.FAIL, "Time limit not yet reached.")
            else:
                print("Session time limit reached, current duration = {a}, session limit = {limit}.".format(
                    a=self.current_time, limit=self.session_duration))
                logging.info("Session time limit reached, current duration = {a}, session limit = {limit}.".format(
                    a=self.current_time - self.start_time, limit=self.session_duration))
                logging.debug("Returning SUCCESS from DurationCheck - Time limit reached, current time = " + str(self.current_time))
                return NodeStatus(NodeStatus.SUCCESS, "Session time limit reached.")
        else:
            return NodeStatus(NodeStatus.FAIL, "Stop set/session duration check")


class GetChoice(Node):
    """
    Ask for a choice from the user as to their preference on shot or stat to work on, or decide which shot/stat to work
    on.
    ...
    Attributes
    ----------
    choice_type :type int
        Whether we are asking the user to choose a shot or a stat (SHOT_CHOICE or STAT_CHOICE).
    whos_choice :type int
        Whether we are deciding what shot/stat to choose or are getting the user's choice.
    Methods
    -------
    run()
        Ask the user which shot/stat they would like to work on (display options on screen of Pepper), or choose
        ourselves.
    """

    def __init__(self, name, *args, **kwargs):
        super(GetChoice, self).__init__(
            name,
            run_cb=self.run,
            configure_cb=self.configure,
            *args, **kwargs)

    def configure(self, nodedata):
        print("Configuring GetChoice: " + self._name)
        self.choice_type = nodedata.get_data('choice_type')
        self.whos_choice = nodedata.get_data('whos_choice')
        self.sorted_shot_list = nodedata.get_data('shot_list')
        self.sorted_stat_list = nodedata.get_data('stat_list')

    def run(self, nodedata):
        """
        Display available options on screen (sorted by guide's preferred order) and verbally ask user to pick.
        :return: NodeStatus.SUCCESS once options have been displayed to user.
        """
        if not config.stop_set and not config.stop_session:
            if self.whos_choice == config.CHOICE_BY_SYSTEM:
                if self.choice_type == config.SHOT_CHOICE:
                    s = 0
                    shot = self.sorted_shot_list[s]
                    while shot in config.used_shots:
                        s += 1
                        shot = self.sorted_shot_list[s]

                    config.used_shots.append(shot)
                    config.performance = None
                    config.score = -1

                    '''# Update exercise picture on Pepper's tablet screen and reset the counter
                    if nodedata.get_data("new_exercise") == 0:
                        exerciseString = "TabletopCircles"
                    elif nodedata.get_data("new_exercise") == 1:
                        exerciseString = "TowelSlides"
                    elif nodedata.get_data("new_exercise") == 2:
                        exerciseString = "CaneRotations"
                    else:
                        exerciseString = "ShoulderOpeners"
                    utteranceURL = config.screen_post_address + exerciseString + "/newPicture"
                    r = requests.post(utteranceURL)
                    r = requests.post(config.screen_post_address + "0/newRep")'''
                    nodedata.shot = config.shot_list_master.get(shot[2:])
                    nodedata.hand = shot[:2]

                    config.shot = nodedata.shot
                    config.hand = nodedata.hand

                    print("Hand = " + str(config.hand) + ", shot = " + str(config.shot))

                    logging.debug("Returning SUCCESS from GetUserChoice, shot = " + str(nodedata.hand) + " " + str(nodedata.shot))
                    return NodeStatus(NodeStatus.SUCCESS,"Returning SUCCESS from GetUserChoice, shot = " + str(nodedata.hand) + " " + str(nodedata.shot))
                else:  # STAT_CHOICE
                    s = 0
                    stat = config.sorted_stat_list[s]
                    while stat in config.used_stats:
                        s += 1
                        stat = config.sorted_stat_list[s]

                    config.used_stats.append(stat)
                    config.performance = None
                    config.score = -1

                    nodedata.stat = stat
                    config.stat = stat
                    config.set_count = 0  # Reset the set count for this session to 0.
                    logging.debug("Returning SUCCESS from GetUserChoice, stat = " + str(nodedata.stat))
                    return NodeStatus(NodeStatus.SUCCESS,"Returning SUCCESS from GetUserChoice, stat = " + str(nodedata.stat))
            else:  # CHOICE_BY_PERSON
                if self.choice_type == config.SHOT_CHOICE:
                    if config.shot is None:
                        return NodeStatus(NodeStatus.ACTIVE, "Waiting on user's shot choice")

                    nodedata.shot = config.shot
                    nodedata.hand = config.hand
                    config.used_shots.append(str(config.shot) + str(config.hand))
                    config.performance = None
                    config.score = -1
                    logging.debug("Returning SUCCESS from GetUserChoice, shot = " + str(nodedata.hand) + " " + str(nodedata.shot))
                    return NodeStatus(NodeStatus.SUCCESS, "Returning SUCCESS from GetUserChoice, shot = " + str(nodedata.hand) + " " + str(nodedata.shot))
                else:  # STAT_CHOICE
                    if config.stat is None:
                        return NodeStatus(NodeStatus.ACTIVE, "Waiting on user's stat choice")

                    nodedata.stat = config.stat
                    config.used_stats.append(config.stat)
                    config.performance = None
                    config.score = -1
                    logging.debug("Returning SUCCESS from GetUserChoice, stat = " + str(nodedata.stat))
                    return NodeStatus(NodeStatus.SUCCESS, "Returning SUCCESS from GetUserChoice, stat = " + str(nodedata.stat))
        else:
            return NodeStatus(NodeStatus.SUCCESS, "Stop set/session get user choice")


class EndSetEvent(Node):
    """
        Check if the user has chosen to end the set.

        This option only becomes available after 30 actions in the set have been detected by the sensor.
        ...
        Methods
        -------
        run()
            Check if at least 30 shots have been played and if so, check if the user has pressed the button.
        """

    def __init__(self, name, *args, **kwargs):
        super(EndSetEvent, self).__init__(
            name,
            configure_cb=self.configure,
            run_cb=self.run,
            *args, **kwargs)

    def configure(self, nodedata):
        logging.debug("Configuring EndSetEvent: " + self._name + ", setting shotcount to " + str(config.shot_count))
        self.shotcount = config.shot_count
        self.firstTime = config.set_count == 0

    def run(self, nodedata):
        """
        Check if at least 30 shots have been played and if so, check if the user has pressed the button.
        :return: NodeStatus.SUCCESS once the end set button has been pressed by the user, NodeStatus.FAIL otherwise.
        """
        # TODO Update once getting actual choice from user. Will probably need two nodes, one for displaying button,
        #   one for waiting for user selection so that the tree doesn't grind to a halt.
        # self.shotcount += 1  # TODO Set this to 0 when set starts.

        if self.shotcount >= 30 or config.stop_set or config.stop_session:
            api_classes.expecting_action_goal = False
            config.completed = config.COMPLETED_STATUS_TRUE
            config.set_count += 1
            config.phase = config.PHASE_END  # When a set is completed, feedback should be given, so phase becomes end.
            # config.repetitions = -1
            config.stop_set = False  # Ending set so reset this variable so the session can continue.

            output = {
                "stop": str(1)
            }
            logging.info("Stopping set: That's 30, you can stop there.")
            r = requests.post(config.post_address, json=output)

            logging.info("Shot set completed.")
            logging.debug("Returning SUCCESS from EndSetEvent, shot count = " + str(self.shotcount))
            return NodeStatus(NodeStatus.SUCCESS, "Shot set ended.")
        else:
            logging.debug("Returning FAIL from EndSetEvent, shot count = " + str(self.shotcount))
            return NodeStatus(NodeStatus.FAIL, "Shot set at " + str(self.shotcount) + ". Not ended yet.")

class InitialiseBlackboard(Node):
    """
    Node to initialise the belief distribution and initial state of the interaction before selecting the first coaching
    behaviour.
    ...
    Attributes
    ----------


    Methods
    -------
    configure(nodedata)
        Set up the initial values needed to calculate the belief distribution.
    run(nodedata)
        Calculate the belief distribution for this session and use it to calculate the start state.
    _constrainedSumSamplePos(n, total, rangeGap)
        Helper function used when generating a random belief distribution.
    _get_start(style)
        Helper function to get the start state based on the given style.
    """

    def __init__(self, name, *args, **kwargs):
        super(InitialiseBlackboard, self).__init__(
            name,
            run_cb=self.run,
            configure_cb=self.configure,
            *args, **kwargs)

    def configure(self, nodedata):
        """
        Set up the initial values needed to calculate the belief distribution.
        :param nodedata :type Blackboard: the blackboard associated with this Behaviour Tree containing all relevant
            state information.
        :return: None
        """
        logging.debug("Configuring InitialiseBlackboard: " + self._name)
        self.name = nodedata.get_data('name')
        self.motivation = nodedata.get_data('motivation')
        self.ability = nodedata.get_data('player_ability')
        if self.ability < 4:
            self.experience = "low"
        else:
            self.experience = "high"
        pass

    def run(self, nodedata):
        """
        Calculate the belief distribution for this session and use it to calculate the start state.
        :param nodedata :type Blackboard: the blackboard on which we will store the calculated belief and start state.
        :return: NodeStatus.SUCCESS when the belief distribution has been calculated and all values stored in the
            blackboard.
        """

        logging.info("Initialising blackboard.")

        belief_distribution = []
        # TODO: Not sure I need this anymore because the environment will deal with the policy selection.
        if config.policy == -1:
            belief_distribution = [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0] if self.experience == "high" else [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]
        else:
            for i in range(12):
                if config.policy == i:
                    belief_distribution.append(1)
                else:
                    belief_distribution.append(0)
        # belief_distribution = [x / 100 for x in self._constrainedSumSamplePos(12, 100, 0.001)]
        nodedata.belief = belief_distribution

        style = 0
        max_style = 0
        max_belief = 0.0
        for b in belief_distribution:
            if b > max_belief:
                max_belief = b
                max_style = style
            style += 1

        nodedata.state = self._get_start(max_style)
        nodedata.performance = -1
        nodedata.phase = config.PHASE_START
        nodedata.bl = BehaviourLibraryFunctions("SquashDict", squash_behaviour_library)
        nodedata.start_time = 0  # TODO: update with actual time.

        # Create file for this participant if it is their first session.
        try:
            f = open("/home/martin/PycharmProjects/coachingPolicies/SessionDataFiles/" + config.participant_filename, "r")
            f.close()
        except:
            f = open("/home/martin/PycharmProjects/coachingPolicies/SessionDataFiles/" + config.participant_filename, "a")
            f.write(config.participantNo + "\n0\n")  # Write participant number and 0 sessions to the new file.
            f.close()

        # Populate the sorted_shot_list with data stored in file from previous sessions.
        shot_set = {}
        for shot in config.shot_list_master:
            for hand in ["FH", "BH"]:
                try:
                    f = open("/home/martin/PycharmProjects/coachingPolicies/SessionDataFiles/" + config.participantNo + "/" + hand + shot + "/Aggregator.txt", "r")
                    aggregator_contents = f.readlines()
                    f.close()

                    score = float(aggregator_contents[0])
                except:
                    score = 0.5
                # Assign a score to each shot based on the importance of the shot (taken from racketware) and data
                # about the previous user performance for each shot. Shots that the user has done really well on in the
                # past will be selected after shots that the user has struggled with (improve their weaknesses).
                shot_set[str(hand) + str(shot)] = (1 - score) + (config.shot_list_importance[shot] * 0.35)

        sorted_shot_set = sorted(shot_set.items(), key=operator.itemgetter(1))
        sorted_shot_list = []
        for i in sorted_shot_set:
            sorted_shot_list.append(i[0])
        sorted_shot_list.reverse()  # Reverse to get most important shot first.
        print("InitialiseBlackboard, sorted shot list = " + str(sorted_shot_list))

        nodedata.sorted_shot_list = sorted_shot_list

        logging.info("Chosen policy = {}".format(max_style))
        logging.debug("Returning SUCCESS from InitialiseBlackboard")
        return NodeStatus(NodeStatus.SUCCESS, "Set belief distribution " + str(belief_distribution) + ". Start state ="
                          + str(nodedata.get_data('state')))

    def _constrainedSumSamplePos(self, n, total, rangeGap):
        """Return a randomly chosen list of n positive integers summing to total.
        Each such list is equally likely to occur."""
        numpyRange = np.arange(0.0, total, rangeGap)
        range = np.ndarray.tolist(numpyRange)
        dividers = sorted(random.sample(range, n - 1))
        return [a - b for a, b in zip(dividers + [total], [0.0] + dividers)]

    def _get_start(self, style):
        if style == 0:
            return 0
        elif style == 1:
            return 45
        elif style == 2:
            return 90
        elif style == 3:
            return 135
        elif style == 4:
            return 180
        elif style == 5:
            return 225
        elif style == 6:
            return 270
        elif style == 7:
            return 323
        elif style == 8:
            return 376
        elif style == 9:
            return 429
        elif style == 10:
            return 482
        else:
            return 535


class OverrideOption(Node):
    """
        Check if the operator has indicated that an exercise has been completed.

        This will eventually be replaced with the vision system using OpenPose.
        ...
        Methods
        -------
        run()
            Check if the operator has pressed the return key.
        """

    def __init__(self, name, *args, **kwargs):
        super(OverrideOption, self).__init__(
            name,
            run_cb=self.run,
            configure_cb=self.configure,
            *args, **kwargs)

    def configure(self, nodedata):
        """
        Set up the initial values needed to calculate exercise performance.
        :param nodedata :type Blackboard: the blackboard associated with this Behaviour Tree containing all relevant
            state information.
        :return: None
        """
        print("Configuring OverrideOption " + self._name)
        self.original_behaviour = nodedata.get_data("original_behaviour")

    def run(self, nodedata):
        """
        Check if user has selected to override the policy's choice to select/question for shot/stat option.
        :return: NodeStatus.SUCCESS if user has overriden. NodeStatus.FAIL if user has not overriden.
         NodeStatus.ACTIVE if still waiting for choice.
        """

        if (not config.stop_set and not config.stop_session) or config.overriden:
            if config.override is None:
                print("Returning ACTIVE from OverrideOption, Waiting for user to decide whether to override.")
                return NodeStatus(NodeStatus.ACTIVE, "Waiting for user to decide whether to override.")
            else:
                if config.override:
                    config.overriden = True
                    if self.original_behaviour == config.A_PREINSTRUCTION:
                        config.behaviour = config.A_QUESTIONING
                    else:
                        config.behaviour = config.A_PREINSTRUCTION

                    config.override = None
                    print("Returning SUCCESS from OverrideOption, User decided to override")
                    return NodeStatus(NodeStatus.SUCCESS, "User decided to override")
                else:
                    config.override = None
                    print("Returning FAIL from OverrideOption, User decided not to override")
                    return NodeStatus(NodeStatus.FAIL, "User decided not to override")
        else:
            config.override = None
            return NodeStatus(NodeStatus.FAIL, "Stop set/session override option")


class CheckDoneBefore(Node):
    """
        Check if this exercise has been done by this user in a previous session.

        ...
        Methods
        -------
        run()
            Check if the exercise has been done before.
        """

    def __init__(self, name, *args, **kwargs):
        super(CheckDoneBefore, self).__init__(
            name,
            run_cb=self.run,
            configure_cb=self.configure,
            *args, **kwargs)

    def configure(self, nodedata):
        """
        Set up the initial values needed to check if the user has done this exercies.
        :param nodedata :type Blackboard: the blackboard associated with this Behaviour Tree containing all relevant
            state information.
        :return: None
        """
        logging.debug("Configuring OverrideOption " + self._name)
        self.shot = nodedata.get_data("shot")
        self.hand = nodedata.get_data("hand")

    def run(self, nodedata):
        """
        CCheck if this exercise has been done by this user in a previous session.
        :return: NodeStatus.SUCCESS if there is a file for this user containing information on the given exercies.
         NodeStatus.FAIL if otherwise.
        """

        if not config.stop_set and not config.stop_session:
            try:
                f = open("/home/martin/PycharmProjects/coachingPolicies/SessionDataFiles/" + config.participantNo + "/" + self.hand + str(self.shot) + "/Aggregator.txt", "r")
                f.close()
                return NodeStatus(NodeStatus.SUCCESS, "Found file containing this exercise.")
            except:
                return NodeStatus(NodeStatus.FAIL, "Failed to find file containing this exercise.")
        else:
            return NodeStatus(NodeStatus.FAIL, "Stop set/session override option")


'''
class OperatorInput(Node):
    """
        Check if the operator has indicated that an exercise has been completed.

        This will eventually be replaced with the vision system using OpenPose.
        ...
        Methods
        -------
        run()
            Check if the operator has pressed the return key.
        """

    def __init__(self, name, *args, **kwargs):
        super(OperatorInput, self).__init__(
            name,
            run_cb=self.run,
            configure_cb=self.configure,
            *args, **kwargs)

    def configure(self, nodedata):
        """
        Set up the initial values needed to calculate exercise performance.
        :param nodedata :type Blackboard: the blackboard associated with this Behaviour Tree containing all relevant
            state information.
        :return: None
        """
        logging.debug("Configuring OperatorInput: " + self._name)
        self.target_time = nodedata.get_data('target')

    def run(self, nodedata):
        """
        Check if the operator has pressed the return key.
        :return: NodeStatus.SUCCESS if return key has been pressed. NodeStatus.ACTIVE otherwise.
        """

        if config.exercise_count == 0:
            input("Press enter to indicate start of exercise")
            config.start_time = datetime.now()

        input("Press enter to indicate completion of exercise")
        ex_time = datetime.now()
        # Get the time between start and key press
        rep_time = ex_time - config.start_time
        rep_time_delta = rep_time.total_seconds()
        # Compare time to target time and update performance
        diff_from_target = self.target_time - rep_time_delta
        performance = config.GOOD
        if 0.5 < diff_from_target:
            performance = config.FAST
        elif diff_from_target < -0.5:
            performance = config.SLOW
        config.performance = float(performance)
        nodedata.performance = float(performance)
        config.score = rep_time_delta
        nodedata.score = rep_time_delta
        config.exercise_count += 1
        # Send exercise count to Pepper's tablet screen
        r = requests.post(config.screen_post_address + str(config.exercise_count) + "/newRep")

        # Controller start_time will be reset when the action goal is created.

        config.goal_level = config.ACTION_GOAL
        print("Rep time = " + str(rep_time_delta) + ", diff_from_target = " + str(diff_from_target) + ", performance = " + str(performance))
        logging.info("Rep time = " + str(rep_time))
        logging.debug("Returning SUCCESS from OperatorInput")
        return NodeStatus(NodeStatus.SUCCESS, "Time = " + str(rep_time))
'''
