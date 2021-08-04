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
from statistics import mean
from time import time

from task_behavior_engine.node import Node
from task_behavior_engine.tree import NodeStatus
from multiprocessing import Process, Queue, Pipe

from API import api_classes
from CoachingBehaviourTree import controller
from CoachingBehaviourTree.action import Action
from CoachingBehaviourTree.behaviour_library import BehaviourLibraryFunctions, squash_behaviour_library
from Policy.policy import Policy
from Policy.policy_wrapper import PolicyWrapper
import numpy as np
import random
import requests

# Robot through Peppernet router:
post_address = 'http://192.168.1.237:4999/output'

# Simulation on 4G:
# post_address = 'http://192.168.43.19:4999/output'


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
        logging.debug("Configuring GetBehaviour: " + self._name)
        logging.debug(str(nodedata))
        self.belief = nodedata.get_data('belief')            # Belief distribution over policies.
        self.goal_level = nodedata.get_data('goal')          # Which level of goal we are currently in (e.g. SET_GOAL)
        self.performance = nodedata.get_data('performance')  # Which level of performance the player achieved (e.g. MET)
        self.phase = nodedata.get_data('phase')              # PHASE_START or PHASE_END
        self.previous_phase = nodedata.get_data('previous_phase', PolicyWrapper.PHASE_START)  # PHASE_START or PHASE_END
        if self.previous_phase == PolicyWrapper.PHASE_START:
            self.state = nodedata.get_data('state')  # Previous state based on observation.
        else:
            self.state = nodedata.get_data('feedback_state')

    def run(self, nodedata):
        """
        Query the policy wrapper for a behaviour based on the state, goal_level, performance and phase of interaction.
        :param nodedata :type Blackboard: the blackboard on which we will store the obtained behaviour and observation
            for accesses by other nodes.
        :return: NodeStatus.SUCCESS when a behaviour and observation has been obtained from the policy wrapper.
        """
        logging.debug('GetBehaviour, self.goal_level = ' + str(self.goal_level) + ', nodedata.goal = ' + str(nodedata.goal))
        policy = PolicyWrapper(self.belief)  # TODO: generate this at start of interaction and store on blackboard.
        nodedata.behaviour, nodedata.obs_behaviour = policy.get_behaviour(self.state, self.goal_level, self.performance, self.phase)
        logging.debug('Got behaviour: ' + str(nodedata.behaviour))

        # If behaviour occurs twice, just skip to pre-instruction.
        if nodedata.behaviour in controller.used_behaviours and (self.goal_level == PolicyWrapper.SESSION_GOAL or self.goal_level == PolicyWrapper.EXERCISE_GOAL or self.goal_level == PolicyWrapper.BASELINE_GOAL or self.goal_level == PolicyWrapper.SET_GOAL or self.goal_level == PolicyWrapper.STAT_GOAL):
            nodedata.behaviour = Policy.A_PREINSTRUCTION
            logging.debug('Got new behaviour: 1')
            # controller.matching_behav = 0
        else:
            controller.used_behaviours.append(nodedata.behaviour)

        controller.prev_behav = nodedata.behaviour

        nodedata.observation = policy.get_observation(self.state, nodedata.obs_behaviour)
        # logging.debug('Got observation: ' + str(nodedata.behaviour))
        logging.debug("Returning SUCCESS from GetBehaviour, nodedata = " + str(nodedata))
        return NodeStatus(NodeStatus.SUCCESS, "Obtained behaviour " + str(nodedata.behaviour))

    def cleanup(self, nodedata):
        """
        Reset values in the blackboard so as not to interfere with the next behaviour selection.
        :param nodedata :type Blackboard: the blackboard associated with this Behaviour Tree containing all relevant
            state information.
        :return: None
        """
        nodedata.previous_phase = PolicyWrapper.PHASE_START


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
        logging.debug("Configuring FormatAction: " + self._name)
        # logging.debug("FormatAction nodedata: " + str(nodedata))
        self.goal_level = nodedata.get_data('goal')          # Which level of goal we are currently in (e.g. SET_GOAL)
        self.performance = nodedata.get_data('performance', 0)  # Which level of performance the player achieved (e.g. MET)
        self.phase = nodedata.get_data('phase')              # PHASE_START or PHASE_END
        self.score = nodedata.get_data('score')              # Numerical score from sensor relating to a stat (can be None)
        self.target = nodedata.get_data('target')            # Numerical target score for stat (can be None)
        self.behaviour_lib = nodedata.get_data('bl')         # The behaviour library to be used in generating actions
        self.behaviour = nodedata.get_data('behaviour')      # The type of behaviour to create an action for.
        self.name = controller.name                # The name of the current user.
        self.shot = nodedata.get_data('shot')                # The shot type (can be None)
        self.hand = nodedata.get_data('hand')                # Forehand or backhand associated with shot (can be None)
        self.stat = nodedata.get_data('stat')                # The stat type (can be None)

    def run(self, nodedata):
        """
        Generate pre_ and post_ messages suitable for the given behaviour using Behaviour Library functions.
        :param nodedata :type Blackboard: the blackboard on which we will store the created action for accesses by other
            nodes.
        :return: NodeStatus.SUCCESS when an action has been created.
        """
        logging.info("Formatting action: behaviour = {behaviour}, goal_level = {goal_level}, performance = {performance}, name = {name}, shot = {shot}, hand = {hand}, stat = {stat}".format(behaviour=self.behaviour, goal_level=self.goal_level, performance=self.performance, name=self.name, shot=self.shot, hand=self.hand, stat=self.stat))
        if not(self.behaviour == Policy.A_SILENCE):
            demo = None
            if self.behaviour in [Policy.A_POSITIVEMODELING, Policy.A_NEGATIVEMODELING,
                                  Policy.A_PREINSTRUCTION_POSITIVEMODELING, Policy.A_PREINSTRUCTION_NEGATIVEMODELING,
                                  Policy.A_POSTINSTRUCTIONPOSITIVE_POSITIVE_MODELING,
                                  Policy.A_POSTINSTRUCTIONPOSITIVE_NEGATIVE_MODELING,
                                  Policy.A_POSTINSTRUCTIONNEGATIVE_POSITIVEMODELING,
                                  Policy.A_POSTINSTRUCTIONNEGATIVE_NEGATIVEMODELING,
                                  Policy.A_QUESTIONING_NEGATIVEMODELING,
                                  Policy.A_POSITIVEMODELING_POSTINSTRUCTIONPOSITIVE,
                                  Policy.A_NEGATIVEMODELING_POSTINSTRUCTIONNEGATIVE,
                                  Policy.A_POSITIVEMODELING_PREINSTRUCTION, Policy.A_SCOLD_POSITIVEMODELING,
                                  Policy.A_CONCURRENTINSTRUCTIONPOSITIVE_POSITIVEMODELING,
                                  Policy.A_CONCURRENTINSTRUCTIONNEGATIVE_NEGATIVEMODELING,
                                  Policy.A_MANUALMANIPULATION_POSITIVEMODELING, Policy.A_QUESTIONING_POSITIVEMODELING,
                                  Policy.A_POSITIVEMODELING_CONCURRENTINSTRUCTIONPOSITIVE,
                                  Policy.A_POSITIVEMODELING_QUESTIONING, Policy.A_POSITIVEMODELING_HUSTLE,
                                  Policy.A_POSITIVEMODELING_PRAISE]:
                demo = self.behaviour_lib.get_demo_string(self.behaviour, self.goal_level, self.shot, self.hand, self.stat)
            pre_msg = self.behaviour_lib.get_pre_msg(self.behaviour, self.goal_level, self.performance, self.phase, self.name, self.shot, self.hand, self.stat)
            if self.score is None and self.performance is None:
                nodedata.action = Action(pre_msg, demo=demo)
            else:
                nodedata.action = Action(pre_msg, self.score, self.target, demo=demo)
        else:
            logging.debug("Returning FAIL from FormatAction, behaviour = " + str(self.behaviour))
            return NodeStatus(NodeStatus.FAIL, "Behaviour == A_SILENCE")

        logging.debug("Returning SUCCESS from FormatAction, action = " + str(nodedata.action))
        return NodeStatus(NodeStatus.SUCCESS, "Created action from given behaviour.")


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
        logging.debug("Configuring CheckForBehaviour: " + self._name)
        self.behaviour = nodedata.get_data('behaviour')              # The behaviour selected from the policy
        self.check_behaviour = nodedata.get_data('check_behaviour')  # The behaviour to check against

    def run(self, nodedata):
        """
        Check if the current behaviour is a member of the given check_behaviour category
        e.g. A_PREINSTRUCTION_POSITIVEMODELLING is a member of the A_PREINSTRUCTION category.

        Behaviour categories are defined as the 16 unique behaviours on the original observation instrument. Most likely
        categories are A_PREINSTRUCTION, A_POSTINSTRUCTIONPOSITIVE and A_POSTINSTRUCTIONNEGATIVE.
        :return: NodeStatus.SUCCESS if the behaviour is a member of the given category, NodeStatus.FAIL otherwise.
        """
        # TODO: Update for variants of check_behaviour.
        # SUCCESS if next behaviour is given behaviour, else FAIL
        if self._is_example_of_behaviour(self.behaviour, self.check_behaviour):
            controller.used_behaviours = []
            logging.debug("Returning SUCCESS from CheckForBehaviour, behaviour found = " + str(self.behaviour))
            # controller.completed = controller.COMPLETED_STATUS_FALSE
            return NodeStatus(NodeStatus.SUCCESS, "Behaviour " + str(self.check_behaviour) + " found in the form " + str(self.behaviour))
        else:
            logging.debug("Returning FAIL from CheckForBehaviour, behaviour not found = " + str(self.check_behaviour) + ", input behaviour = " + str(self.behaviour))
            return NodeStatus(NodeStatus.FAIL, "Behaviour " + str(self.check_behaviour) + " not found.")

    def _is_example_of_behaviour(self, behaviour, check_behaviour):
        if check_behaviour == Policy.A_PREINSTRUCTION:
            check_list = [Policy.A_PREINSTRUCTION, Policy.A_PREINSTRUCTION_PRAISE, Policy.A_PREINSTRUCTION_QUESTIONING,
                          Policy.A_PREINSTRUCTION_POSITIVEMODELING, Policy.A_POSITIVEMODELING_PREINSTRUCTION,
                          Policy.A_PREINSTRUCTION_FIRSTNAME, Policy.A_PREINSTRUCTION_MANUALMANIPULATION,
                          Policy.A_PREINSTRUCTION_NEGATIVEMODELING, Policy.A_MANUALMANIPULATION_PREINSTRUCTION]
        else:
            check_list = [Policy.A_QUESTIONING, Policy. A_PREINSTRUCTION_QUESTIONING, Policy.A_QUESTIONING_FIRSTNAME,
                          Policy.A_QUESTIONING_POSITIVEMODELING, Policy.A_POSITIVEMODELING_QUESTIONING,
                          Policy.A_CONCURRENTINSTRUCTIONPOSITIVE_QUESTIONING, Policy.A_MANUALMANIPULATION_QUESTIONING,
                          Policy.A_POSTINSTRUCTIONNEGATIVE_QUESTIONING, Policy.A_POSTINSTRUCTIONPOSITIVE_QUESTIONING,
                          Policy.A_QUESTIONING_NEGATIVEMODELING]

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
        logging.debug("Configuring DisplayBehaviour: " + self._name)
        self.action = nodedata.get_data('action')
        self.set_start = nodedata.get_data('set_start', False)

    def run(self, nodedata):
        """
        Execute the specified action.
        :return: NodeStatus.SUCCESS if action sent successfully to robot, NodeStatus.FAIL otherwise.
        """
        logging.debug(str(self.action))
        output = {
            "utterance": str(self.action)
        }
        if controller.goal_level == 4:
            if controller.set_count >= 2:
                output = {
                    "utterance": "OK, play a final set of 30 shots to see if what you've been working on has improved!"
                }
                logging.info("Displaying action: OK, play a final set of 30 shots to see if what you've been working on has improved!")
            elif controller.set_count == 1:
                utterance1 = "your racket preparation for your forehand drive."
                utterance2 = "getting your racket up early"
                if controller.shot == 5:
                    utterance1 = "the angle of your racket face when you hit your forehand lob."
                    utterance2 = "keeping your racket face open"
                elif controller.shot == 0:
                    utterance1 = "the angle of your racket face when you hit your forehand drop."
                    utterance2 = "keeping your racket face open"
                elif controller.hand == "BH":
                    utterance1 = "your follow through timing for your backhand drive."
                    utterance2 = "your follow through"
                output = {
                    "utterance": "Based on that set of shots, I think you should work on " + utterance2 + " today. You will now have 5 minutes to try to improve " + utterance1 + " I'll let you know when 5 minutes has passed and we'll see if you have improved! You can start now."
                }

                logging.info(
                    "Displaying action: Based on that set of shots, I think you should work on " + utterance2 + " today. You will now have 5 minutes to try to improve " + utterance1 + " I'll let you know when 5 minutes has passed and we'll see if you have improved! You can start now.")
        elif controller.goal_level == 1:
            output = {
                "utterance": "Thank you for practicing with me today. Goodbye."
            }

        api_classes.expecting_action_goal = True
        # if self.action.demo is not None:
        #     output['demo'] = self.action.demo
        r = requests.post(post_address, json=output)
        controller.start_time = time()
        logging.debug("Returning SUCCESS from DisplayBehaviour")
        return NodeStatus(NodeStatus.SUCCESS, "Printed action message to output.")

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
        logging.debug("Running GetStats: " + self._name)

        output = {
            "start": str(1)
        }
        r = requests.post(post_address, json=output)

        # Will be ACTIVE when waiting for data and SUCCESS when got data and added to blackboard, FAIL when connection error.
        # logging.debug("In get stats")
        nodedata.motivation = controller.motivation
        nodedata.player_ability = controller.ability
        logging.info("Stats set, motivation = {motivation}, ability = {ability}".format(motivation=nodedata.motivation, ability=nodedata.player_ability))
        #nodedata.sessions = 6
        # logging.debug("After setting stats in GetStats: " + str(nodedata))
        logging.debug("Returning SUCCESS from GetStats, stats = " + str(nodedata))
        return NodeStatus(NodeStatus.SUCCESS, "Set stats to dummy values.")


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
            *args, **kwargs)

    def run(self, nodedata):
        """
        Display and obtain user input requesting the session duration in minutes.
        :param nodedata :type Blackboard: the blackboard on which we will store the obtained duration for access by
            other nodes.
        :return: NodeStatus.ACTIVE when waiting for user's input, NodeStatus.SUCCESS when user's input has been received
            and data has been stored in the blackboard, NodeStatus.FAIL otherwise.
        """
        logging.debug("Running GetDuration: " + self._name)
        # Will be ACTIVE when waiting for data and SUCCESS when got data and added to blackboard, FAIL when connection error.
        nodedata.session_duration = 1
        logging.info("Set session duration to: {duration}".format(duration=nodedata.session_duration))
        logging.debug("Returning SUCCESS from GetDuration, session duration = " + str(nodedata.session_duration))
        return NodeStatus(NodeStatus.SUCCESS, "Set session duration to dummy value 20.")


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
        # Will return SUCCESS once request sent to API, FAIL if called on ACTION_GOAL or connection error.
        if self.previous_goal_level == 6:
            nodedata.new_goal = 3
            logging.info("Created subgoal, new goal level = {}".format(nodedata.new_goal))
            logging.debug("Returning SUCCESS from CreateSubGoal, new goal level = " + str(nodedata.goal))
            return NodeStatus(NodeStatus.SUCCESS, "Created subgoal: 3 from BASELINE_GOAL")
        elif self.previous_goal_level > 6:
            logging.debug("Returning FAIL from CreateSubGoal, previous goal level = " + str(self.previous_goal_level))
            return NodeStatus(NodeStatus.FAIL, "Cannot create subgoal of ACTION_GOAL.")
        else:
            if self.previous_goal_level == PolicyWrapper.EXERCISE_GOAL and self.stat is None:
                nodedata.new_goal = 6
            else:
                nodedata.new_goal = self.previous_goal_level + 1
            logging.info("Created subgoal, new goal level = {}".format(nodedata.new_goal))
            logging.debug("Returning SUCCESS from CreateSubGoal, new goal level = " + str(nodedata.new_goal))
            return NodeStatus(NodeStatus.SUCCESS, "Created subgoal: " + str(self.previous_goal_level + 1))


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
    # TODO: Dummy class which will eventually communicate with guide via API
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
        logging.debug("Configuring EndSubgoal: " + self._name)
        self.goal_level = nodedata.get_data('goal', -1)

    def run(self, nodedata):
        """
        Send request to the API for the guide to create a subgoal.
        :param nodedata :type Blackboard: the blackboard on which we will update the goal level.
        :return: NodeStatus.SUCCESS when request is sent to API, NodeStatus.FAIL if current goal level is ACTION_GOAL
            or cannot connect to API.
        """
        # Will return SUCCESS once request sent to API, FAIL if called on goal > 6 or connection error.
        if self.goal_level > 6:
            logging.debug("Returning FAIL from EndSubgoal, goal_level = " + str(self.goal_level))
            return NodeStatus(NodeStatus.FAIL, "Cannot create subgoal of " + str(self.goal_level))
        else:
            if self.goal_level == PolicyWrapper.BASELINE_GOAL:
                nodedata.stat = 1
                nodedata.phase = PolicyWrapper.PHASE_END
                nodedata.new_goal = PolicyWrapper.STAT_GOAL
                controller.completed = controller.COMPLETED_STATUS_TRUE
            else:
                if (self.goal_level == PolicyWrapper.SET_GOAL and controller.set_count >= 3) or self.goal_level == PolicyWrapper.STAT_GOAL or self.goal_level == PolicyWrapper.EXERCISE_GOAL or self.goal_level == PolicyWrapper.SESSION_GOAL:
                    logging.debug("Ending subgoal, new controller.goal_level = " + str(controller.goal_level - 1))
                    controller.goal_level -= 1
                    controller.phase = PolicyWrapper.PHASE_END
                else:
                    controller.phase = PolicyWrapper.PHASE_START
                nodedata.new_goal = self.goal_level - 1
                nodedata.phase = PolicyWrapper.PHASE_START  # All behaviours have happened so its start of new goal.
                if self.goal_level == PolicyWrapper.STAT_GOAL:
                    controller.completed = controller.COMPLETED_STATUS_FALSE
                else:
                    controller.completed = controller.COMPLETED_STATUS_TRUE
                if self.goal_level == PolicyWrapper.EXERCISE_GOAL:
                    controller.session_time += 1
                    logging.debug("Exercise goal finished, added 1 to session_time. New time = " + str(controller.session_time))
            logging.info("Ended subgoal {old_goal}. New goal level = {new_goal}.".format(old_goal=self.goal_level, new_goal=nodedata.new_goal))
            logging.debug("Returning SUCCESS from EndSubgoal, new subgoal level = " + str(nodedata.new_goal))
            return NodeStatus(NodeStatus.SUCCESS, "Completed subgoal: " + str(self.goal_level - 1))


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
    # TODO: Dummy class which will eventually communicate with guide via API
    def __init__(self, name, *args, **kwargs):
        super(TimestepCue, self).__init__(
            name,
            run_cb=self.run,
            configure_cb=self.configure,
            *args, **kwargs)

    def configure(self, nodedata):
        logging.debug("Configuring TimestepCue: " + self._name)
        self.goal_level = nodedata.get_data('goal')
        self.phase = nodedata.get_data('phase')
        controller.completed = controller.COMPLETED_STATUS_FALSE

    def run(self, nodedata):
        """
        Check if the guide has requested an action be performed, and if so update the blackboard with the data about the
        current state given by the guide.

        All communication will be done through the API. A queue stack structure will be used to store timestepCue calls
        by the guide and the stack will be emptied each time this method is called (but only the top member acted upon).
        This will mean the robot never falls behind the interaction state (but may sometimes stay silent).
        :param nodedata :type Blackboard: the blackboard on which we will store the data provided by the guide.
        :return: NodeStatus.ACTIVE when waiting for data from the guide, NodeStatus.SUCCESS when data has been received
            and added to the blackboard, NodeStatus.FAIL otherwise.
        """
        # Will be ACTIVE when waiting for data and SUCCESS when got data and added to blackboard, FAIL when connection error.
        if self.goal_level == -1:  # Person goal created after receiving info from guide.
            if controller.goal_level == 0:  # For person goal should have name, ability and no. of sessions.
                nodedata.sessions = controller.sessions
                nodedata.player_ability = controller.ability
                nodedata.name = controller.name
                nodedata.phase = PolicyWrapper.PHASE_START
                logging.debug("Returning SUCCESS from TimestepCue player goal, stats = " + str(nodedata))
                return NodeStatus(NodeStatus.SUCCESS, "Data for person goal obtained from guide:" + str(nodedata))
            else:
                logging.debug("Returning ACTIVE from TimestepCue player goal")
                return NodeStatus(NodeStatus.ACTIVE, "Waiting for person goal data from guide.")

        elif self.goal_level == 1:  # For session goal should have performance from previous session.
            if controller.goal_level == 1:
                if controller.phase == PolicyWrapper.PHASE_END:  # Feedback sequence
                    nodedata.performance = round(mean(controller.set_performance_list))
                    nodedata.phase = PolicyWrapper.PHASE_END
                    logging.debug("Returning SUCCESS from TimestepCue session goal (end), stats = " + str(nodedata))
                    return NodeStatus(NodeStatus.SUCCESS, "Data for stat goal obtained from guide:" + str(nodedata))
                else:
                    nodedata.performance = controller.performance
                    nodedata.phase = PolicyWrapper.PHASE_START
                    logging.debug("Returning SUCCESS from TimestepCue session goal, stats = " + str(nodedata))
                    return NodeStatus(NodeStatus.SUCCESS, "Data for session goal obtained from guide:" + str(nodedata))
            else:
                logging.debug("Returning ACTIVE from TimestepCue session goal")
                return NodeStatus(NodeStatus.ACTIVE, "Waiting for session goal data from guide.")

        elif self.goal_level == 2:  # For shot goal should have performance from last time this shot was practiced.
            if controller.goal_level == 2:
                if controller.phase == PolicyWrapper.PHASE_END:
                    if controller.completed == controller.COMPLETED_STATUS_TRUE:  # This is actually the end of a baseline goal. Might need to update this so it's not as weirdly laid out.
                        nodedata.phase = PolicyWrapper.PHASE_END
                        nodedata.performance = controller.performance
                        logging.debug("Returning SUCCESS from TimestepCue shot goal (end), stats = " + str(nodedata))
                        return NodeStatus(NodeStatus.SUCCESS, "Data for shot goal obtained from guide:" + str(nodedata))
                    elif controller.completed == controller.COMPLETED_STATUS_FALSE:  # Feedback Sequence
                        nodedata.performance = round(mean(controller.set_performance_list))
                        nodedata.score = mean(controller.set_score_list)
                        nodedata.target = controller.target
                        nodedata.phase = PolicyWrapper.PHASE_END
                        logging.debug("Returning SUCCESS from TimestepCue shot goal (end), stats = " + str(nodedata))
                        return NodeStatus(NodeStatus.SUCCESS, "Data for shot goal obtained from guide:" + str(nodedata))
                    else:
                        logging.debug("Returning ACTIVE from TimestepCue shot goal, controller.completed = COMPLETED_STATUS_UNDEFINED")
                        return NodeStatus(NodeStatus.ACTIVE, "Waiting for shot goal data from guide.")
                else:
                    nodedata.performance = controller.performance
                    nodedata.phase = PolicyWrapper.PHASE_START
                    controller.goal_level = PolicyWrapper.SET_GOAL
                    logging.debug("Returning SUCCESS from TimestepCue shot goal, stats = " + str(nodedata))
                    return NodeStatus(NodeStatus.SUCCESS, "Data for shot goal obtained from guide:" + str(nodedata))
            else:
                logging.debug("Returning ACTIVE from TimestepCue shot goal, controller.goal_level != 2")
                return NodeStatus(NodeStatus.ACTIVE, "Waiting for shot goal data from guide.")

        elif self.goal_level == 3:  # For stat goal should have target and performance from last time this stat was practiced.
            if controller.goal_level == 3:
                if controller.phase == PolicyWrapper.PHASE_END:  # Feedback sequence
                    nodedata.performance = round(mean(controller.set_performance_list))
                    nodedata.phase = PolicyWrapper.PHASE_END
                    nodedata.score = mean(controller.set_score_list)
                    nodedata.target = controller.target
                    logging.debug("Returning SUCCESS from TimestepCue stat goal, stats = " + str(nodedata))
                    return NodeStatus(NodeStatus.SUCCESS, "Data for stat goal obtained from guide:" + str(nodedata))
                else:
                    nodedata.performance = controller.performance
                    nodedata.phase = PolicyWrapper.PHASE_START
                    logging.debug("Returning SUCCESS from TimestepCue stat goal, stats = " + str(nodedata))
                    return NodeStatus(NodeStatus.SUCCESS, "Data for stat goal obtained from guide:" + str(nodedata))
            else:
                logging.debug("Returning ACTIVE from TimestepCue stat goal")
                return NodeStatus(NodeStatus.ACTIVE, "Waiting for stat goal data from guide.")

        elif self.goal_level == 4:  # For set goal we don't need any information from guide up front, only for feedback.
            if controller.goal_level == 4:
                if controller.phase == PolicyWrapper.PHASE_END:  # Just finished previous goal level so into feedback sequence.
                    nodedata.phase = PolicyWrapper.PHASE_END
                    nodedata.performance = controller.performance
                    nodedata.score = controller.avg_score
                    nodedata.target = controller.target
                    logging.debug("Returning SUCCESS from TimestepCue set goal feedback, stats = " + str(nodedata))
                    return NodeStatus(NodeStatus.SUCCESS, "Data for set goal obtained from guide:" + str(nodedata))
                else:  # For set goal we don't need any information from guide up front, only for feedback.
                    nodedata.phase = PolicyWrapper.PHASE_START
                    nodedata.performance = controller.performance
                    controller.shot_count = 0
                    # controller.completed = controller.COMPLETED_STATUS_FALSE
                    logging.debug("Returning SUCCESS from TimestepCue set goal, stats = " + str(nodedata))
                    return NodeStatus(NodeStatus.SUCCESS, "Data for set goal obtained from guide:" + str(nodedata))
            else:
                logging.debug("Returning ACTIVE from TimestepCue set goal")
                return NodeStatus(NodeStatus.ACTIVE, "Waiting for set goal data from guide.")

        elif self.goal_level == 5:
            if controller.goal_level == 5:
                controller.goal_level = PolicyWrapper.SET_GOAL
                nodedata.phase = PolicyWrapper.PHASE_END
                nodedata.performance = controller.performance
                nodedata.score = controller.score
                nodedata.target = controller.target
                logging.debug("Returning SUCCESS from TimestepCue action goal, stats = " + str(nodedata))
                return NodeStatus(NodeStatus.SUCCESS, "Data for action goal obtained from guide:" + str(nodedata))
            else:
                logging.debug("Returning ACTIVE from TimestepCue action goal")
                return NodeStatus(NodeStatus.ACTIVE, "Waiting for action goal data from guide.")

        elif self.goal_level == 6:
            if controller.goal_level == 4:
                nodedata.phase = PolicyWrapper.PHASE_START
                controller.shot_count = 0
                controller.completed = controller.COMPLETED_STATUS_FALSE
                logging.debug("Returning SUCCESS from TimestepCue baseline goal, stats = " + str(nodedata))
                return NodeStatus(NodeStatus.SUCCESS, "Data for baseline goal obtained from guide:" + str(nodedata))
            else:
                logging.debug("Returning ACTIVE from TimestepCue baseline goal")
                return NodeStatus(NodeStatus.ACTIVE, "Waiting for baseline goal data from guide.")

        nodedata.performance = PolicyWrapper.MET
        nodedata.phase = PolicyWrapper.PHASE_START
        nodedata.target = 0.80
        nodedata.score = 0.79
        logging.debug("Returning SUCCESS from TimestepCue, stats = " + str(nodedata))
        return NodeStatus(NodeStatus.SUCCESS, "Set timestep cue values to dummy values MET, PHASE_START, 0.80, 0.79.")


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
        logging.debug("Configuring DurationCheck: " + self._name)
        self.start_time = nodedata.get_data('start_time')
        self.session_duration = nodedata.get_data('session_duration')
        # Only use until getting actual time:
        self.current_time = controller.session_time

    def run(self, nodedata):
        """
        Compare the requested session duration to the amount of time the session has been running.
        :return: NodeStatus.FAIL when session duration has not been reached, NodeStatus.SUCCESS otherwise.
        """
        # TODO update once getting actual time from user
        # Will return FAIL when when duration has not been reached. SUCCESS when it has.
        # self.current_time += 1
        if (self.current_time - self.start_time) < self.session_duration:
            logging.info("Session time limit NOT reached, current duration = {a}, session limit = {limit}.".format(a=self.current_time - self.start_time, limit=self.session_duration))
            logging.debug("Returning FAIL from DurationCheck - time limit not yet reached, current time = " + str(self.current_time) + ", start_time = " + str(self.start_time) + ", session_duration = " + str(self.session_duration))
            return NodeStatus(NodeStatus.FAIL, "Time limit not yet reached.")
        else:
            logging.info("Session time limit reached, current duration = {a}, session limit = {limit}.".format(
                a=self.current_time - self.start_time, limit=self.session_duration))
            logging.debug("Returning SUCCESS from DurationCheck - Time limit reached, current time = " + str(self.current_time))
            return NodeStatus(NodeStatus.SUCCESS, "Session time limit reached.")


class GetUserChoice(Node):
    """
    Ask for a choice from the user as to their preference on shot or stat to work on.
    ...
    Attributes
    ----------
    choice_type :type int
        Whether we are asking the user to choose a shot or a stat (SHOT_CHOICE or STAT_CHOICE).
    Methods
    -------
    run()
        Ask the user which shot/stat they would like to work on (display options on screen of Pepper).
    """

    def __init__(self, name, *args, **kwargs):
        super(GetUserChoice, self).__init__(
            name,
            run_cb=self.run,
            configure_cb=self.configure,
            *args, **kwargs)

    def configure(self, nodedata):
        logging.debug("Configuring GetUserChoice: " + self._name)
        self.choice_type = nodedata.get_data('choice_type')

    def run(self, nodedata):
        """
        Display available options on screen (sorted by guide's preferred order) and verbally ask user to pick.
        :return: NodeStatus.SUCCESS once options have been displayed to user.
        """
        # TODO Update once getting actual choice from user. Will probably need two nodes, one for requesting, one for
        #   waiting for user selection so that the tree doesn't grind to a halt.
        if self.choice_type == 0:  # controller.SHOT_CHOICE = 0
            nodedata.shot = 1
            controller.shot = 1
            nodedata.hand = 1  # Forehand
            controller.hand = 1
            logging.debug("Returning SUCCESS from GetUserChoice, shot = " + str(nodedata.shot))
        else:
            nodedata.stat = 1
            controller.stat = 1
            logging.debug("Returning SUCCESS from GetUserChoice, stat = " + str(nodedata.stat))
        return NodeStatus(NodeStatus.SUCCESS, "Set shot/stat to 1.")


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
        logging.debug("Configuring EndSetEvent: " + self._name + ", setting shotcount to " + str(controller.shot_count))
        self.shotcount = controller.shot_count

    def run(self, nodedata):
        """
        Check if at least 30 shots have been played and if so, check if the user has pressed the button.
        :return: NodeStatus.SUCCESS once the end set button has been pressed by the user, NodeStatus.FAIL otherwise.
        """
        # TODO Update once getting actual choice from user. Will probably need two nodes, one for displaying button,
        #   one for waiting for user selection so that the tree doesn't grind to a halt.
        # self.shotcount += 1  # TODO Set this to 0 when set starts.
        if controller.set_count == 1:
            if time() - controller.start_time >= 300:
                if controller.time_up_shots >= 2:
                    output = {
                        "utterance": "Time up! That's been 5 minutes. Time to see if all that hard work has paid off!"
                    }
                    logging.info("Stopping set: Time up! That's been 5 minutes. Time to see if all that hard work has paid off!")
                    r = requests.post(post_address, json=output)
                    logging.info("Training time completed. Total shots played = " + str(self.shotcount))
                    controller.set_count += 1
                    logging.debug("Returning SUCCESS from EndSetEvent, shot count = " + str(self.shotcount))
                    return NodeStatus(NodeStatus.SUCCESS, "Shot set ended.")
                if controller.time_up_shots == 0:
                    controller.time_up = True
                logging.debug("Returning FAIL from EndSetEvent in training set, time up shot count = " + str(controller.time_up_shots))
                return NodeStatus(NodeStatus.FAIL, "Shot set at " + str(self.shotcount) + ". Not ended yet.")
            else:
                logging.debug("Returning FAIL from EndSetEvent in training set, shot count = " + str(self.shotcount))
                return NodeStatus(NodeStatus.FAIL, "Shot set at " + str(self.shotcount) + ". Not ended yet.")
        elif self.shotcount >= 30:
            api_classes.expecting_action_goal = False
            controller.completed = controller.COMPLETED_STATUS_TRUE
            controller.set_count += 1

            output = {
                "stop": str(1)
            }
            logging.info("Stopping set: That's 30, you can stop there.")
            r = requests.post(post_address, json=output)

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
        self.motivation = nodedata.get_data('motivation')
        self.ability = nodedata.get_data('player_ability')
        if self.ability < 3:
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

        belief_distribution = [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0] if self.experience == "high" else [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]
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
        nodedata.phase = PolicyWrapper.PHASE_START
        nodedata.bl = BehaviourLibraryFunctions("SquashDict", squash_behaviour_library)
        nodedata.start_time = 0  # TODO: update with actual time.
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
