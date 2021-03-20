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
"""

from time import time

from task_behavior_engine.node import Node
from task_behavior_engine.tree import NodeStatus

from CoachingBehaviourTree.action import Action
from CoachingBehaviourTree.behaviour_library import BehaviourLibraryFunctions
from Policy.policy_wrapper import PolicyWrapper


class GetBehaviour(Node):
    """
    Query the policy wrapper for the next behaviour to confirm given the current state of the interaction.
    ...
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

        self.belief = nodedata.get_data('belief')            # Belief distribution over policies.
        self.state = nodedata.get_data('state')              # Previous state based on observation.
        self.goal_level = nodedata.get_data('goal')          # Which level of goal we are currently in (e.g. SET_GOAL)
        self.performance = nodedata.get_data('performance')  # Which level of performance the player achieved (e.g. MET)
        self.phase = nodedata.get_data('phase')              # PHASE_START or PHASE_END
        nodedata.behaviour = -1
        nodedata.observation = self.state

    def run(self, nodedata):
        """
        Query the policy wrapper for a behaviour based on the state, goal_level, performance and phase of interaction.
        :param nodedata :type Blackboard: the blackboard on which we will store the obtained behaviour and observation
            for accesses by other nodes.
        :return: NodeStatus.SUCCESS when a behaviour and observation has been obtained from the policy wrapper.
        """
        policy = PolicyWrapper(self.belief)  # TODO: generate this at start of interaction and store on blackboard.
        nodedata.behaviour = policy.get_behaviour(self.state, self.goal_level, self.performance, self.phase)
        nodedata.observation = policy.get_observation(self.state, nodedata.behaviour)
        return NodeStatus(NodeStatus.SUCCESS, "Obtained behaviour " + str(nodedata.behaviour))

    def cleanup(self, nodedata):
        """
        Reset values in the blackboard so as not to interfere with the next behaviour selection.
        :param nodedata :type Blackboard: the blackboard associated with this Behaviour Tree containing all relevant
            state information.
        :return: None
        """
        # This might delete the behaviour from the blackboard before it has been formatted into an action.
        nodedata.behaviour = -1
        nodedata.observation = self.state


class FormatAction(Node):
    """
    Create an instance of the Action class using the given behaviour.
    ...
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
        self.goal_level = nodedata.get_data('goal')          # Which level of goal we are currently in (e.g. SET_GOAL)
        self.performance = nodedata.get_data('performance')  # Which level of performance the player achieved (e.g. MET)
        self.phase = nodedata.get_data('phase')              # PHASE_START or PHASE_END
        self.score = nodedata.get_data('score')              # Numerical score from sensor relating to a stat (can be None)
        self.target = nodedata.get_data('target')            # Numerical target score for stat (can be None)
        self.behaviour_lib = nodedata.get_data('bl')         # The behaviour library to be used in generating actions

    def run(self, nodedata):
        """
        Generate pre_ and post_ messages suitable for the given behaviour using Behaviour Library functions.
        :param nodedata :type Blackboard: the blackboard on which we will store the created action for accesses by other
            nodes.
        :return: NodeStatus.SUCCESS when an action has been created.
        """
        pre_msg = self.behaviour_lib.get_pre_msg(nodedata.get_data('behaviour'), self.goal_level, self.performance, self.phase)
        post_msg = self.behaviour_lib.get_post_msg(nodedata.get_data('behaviour'), self.goal_level, self.performance, self.phase)
        if post_msg is not None:
            nodedata.action = Action(pre_msg, self.score, self.target, post_msg)
        else:
            nodedata.action = Action(pre_msg)

        return NodeStatus(NodeStatus.SUCCESS, "Created action from given behaviour.")


class CheckForBehaviour(Node):
    """
    Compare the currently selected behaviour to a given behaviour category.
    ...
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
        self.behaviour = nodedata.get_data('behaviour')              # The behaviour selected from the policy
        self.check_behaviour = nodedata.get_data('check_behaviour')  # The behaviour to check against

    def run(self):
        """
        Check if the current behaviour is a member of the given check_behaviour category
        e.g. A_PREINSTRUCTION_POSITIVEMODELLING is a member of the A_PREINSTRUCTION category.

        Behaviour categories are defined as the 16 unique behaviours on the original observation instrument. Most likely
        categories are A_PREINSTRUCTION, A_POSTINSTRUCTIONPOSITIVE and A_POSTINSTRUCTIONNEGATIVE.
        :return: NodeStatus.SUCCESS if the behaviour is a member of the given category, NodeStatus.FAIL otherwise.
        """
        # TODO: Update for variants of check_behaviour.
        # SUCCESS if next behaviour is given behaviour, else FAIL
        if self.behaviour == self.check_behaviour:
            return NodeStatus(NodeStatus.SUCCESS, "Behaviour " + str(self.check_behaviour) + " found in the form " + str(self.behaviour))
        else:
            return NodeStatus(NodeStatus.FAIL, "Behaviour " + str(self.check_behaviour) + " not found.")


class DisplayBehaviour(Node):
    """
    Have the robot perform the formatted action.
    ...
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
        self.action = nodedata.get_data('action')

    def run(self):
        """
        Execute the specified action.
        :return: NodeStatus.SUCCESS if action sent successfully to robot, NodeStatus.FAIL otherwise.
        """
        print(str(self.action))
        return NodeStatus(NodeStatus.SUCCESS, "Printed action message to output.")


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
        Set the player's motivation, ability and no. of sessions on the blackboard.

        The ability and no. of sessions will be given by the guide. The motivation will vary each session and will have
        to be obtained from the user.
        :param nodedata :type Blackboard: the blackboard on which we will store the obtained stats for access by other
            nodes.
        :return: NodeStatus.ACTIVE when waiting for data, NodeStatus.SUCCESS when got data and added to blackboard,
            NodeStatus.FAIL otherwise.
        """
        # Will be ACTIVE when waiting for data and SUCCESS when got data and added to blackboard, FAIL when connection error.
        nodedata.motivation = 8
        nodedata.player_ability = 2
        nodedata.sessions = 6
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
        # Will be ACTIVE when waiting for data and SUCCESS when got data and added to blackboard, FAIL when connection error.
        nodedata.session_duration = 20
        return NodeStatus(NodeStatus.SUCCESS, "Set session duration to dummy value 20.")


class CreateSubgoal(Node):
    """
    Tell the guide via the API that a new subgoal is required.
    ...
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
        Obtain the current goal level (e.g. SESSION_GOAL) from the blackboard.
        :param nodedata :type Blackboard: the blackboard associated with this Behaviour Tree containing the goal level.
        :return: None
        """
        self.previous_goal_level = nodedata.get_data('goal')

    def run(self, nodedata):
        """
        Send request to the API for the guide to create a subgoal.
        :param nodedata :type Blackboard: the blackboard on which we will update the goal level.
        :return: NodeStatus.SUCCESS when request is sent to API, NodeStatus.FAIL if current goal level is ACTION_GOAL
            or cannot connect to API.
        """
        # Will return SUCCESS once request sent to API, FAIL if called on ACTION_GOAL or connection error.
        if self.previous_goal_level == 5:
            return NodeStatus(NodeStatus.FAIL, "Cannot create subgoal of ACTION_GOAL.")
        else:
            nodedata.goal = self.previous_goal_level + 1
            return NodeStatus(NodeStatus.SUCCESS, "Created subgoal: " + str(self.previous_goal_level + 1))


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
            *args, **kwargs)

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
        nodedata.performance = PolicyWrapper.MET
        nodedata.phase = PolicyWrapper.PHASE_START
        nodedata.target = 0.80
        nodedata.score = 0.79
        return NodeStatus(NodeStatus.SUCCESS, "Set timestep cue values to dummy values MET, PHASE_START, 0.80, 0.79.")


class DurationCheck(Node):
    """
    Check if the session has reached the time limit selected by the user.
    ...
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
        self.start_time = nodedata.get_data('start_time')
        self.session_duration = nodedata.get_data('session_duration')

    def run(self):
        """
        Compare the requested session duration to the amount of time the session has been running.
        :return: NodeStatus.FAIL when session duration has not been reached, NodeStatus.SUCCESS otherwise.
        """
        # TODO update once getting actual time from user
        # Will return FAIL when when duration has not been reached. SUCCESS when it has.
        current_time = time()
        if (current_time - self.start_time) < self.session_duration:
            return NodeStatus(NodeStatus.FAIL, "Time limit not yet reached.")
        else:
            return NodeStatus(NodeStatus.SUCCESS, "Session time limit reached.")
