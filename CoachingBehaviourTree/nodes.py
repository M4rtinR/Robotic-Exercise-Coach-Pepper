from task_behavior_engine.node import Node
from task_behavior_engine.tree import NodeStatus

from CoachingBehaviourTree.action import Action
from Policy.policy_wrapper import PolicyWrapper


class GetBehaviour(Node):
    def __init__(self, name, *args, **kwargs):
        super(GetBehaviour, self).__init__(
            name,
            run_cb=self.run,
            configure_cb=self.configure,
            cleanup_cb=self.cleanup,
            *args, **kwargs)

    def configure(self, nodedata):
        self.belief = nodedata.get_data('belief')            # Belief distribution over policies.
        self.state = nodedata.get_data('state')              # Previous state based on observation.
        self.goal_level = nodedata.get_data('goal')          # Which level of goal we are currently in (e.g. SET_GOAL)
        self.performance = nodedata.get_data('performance')  # Which level of performance the player achieved (e.g. MET)
        self.phase = nodedata.get_data('phase')              # PHASE_START or PHASE_END
        nodedata.behaviour = -1
        nodedata.observation = self.state

    def run(self, nodedata):
        policy = PolicyWrapper(self.belief)
        nodedata.behaviour = policy.get_behaviour(self.state, self.goal_level, self.performance, self.phase)
        nodedata.observation = policy.get_observation(self.state, nodedata.behaviour)
        return NodeStatus(NodeStatus.SUCCESS, "Obtained behaviour " + nodedata.behaviour)

    def cleanup(self, nodedata):
        # This might delete the behaviour from the blackboard before it has been formatted into an action.
        nodedata.behaviour = -1
        nodedata.observation = self.state


class FormatAction(Node):
    def __init__(self, name, *args, **kwargs):
        super(FormatAction, self).__init__(
            name,
            run_cb=self.run,
            configure_cb=self.configure,
            cleanup_cb=self.cleanup,
            *args, **kwargs)

    def configure(self, nodedata):
        self.goal_level = nodedata.get_data('goal')          # Which level of goal we are currently in (e.g. SET_GOAL)
        self.performance = nodedata.get_data('performance')  # Which level of performance the player achieved (e.g. MET)
        self.phase = nodedata.get_data('phase')              # PHASE_START or PHASE_END
        self.score = nodedata.get_data('score')              # Numerical score from sensor relating to a stat (can be None)
        self.target = nodedata.get_data('target')            # Numerical target score for stat (can be None)

    def run(self, nodedata):
        pre_msg = get_pre_msg(nodedata.get_data('behaviour'), self.goal_level, self.performance, self.phase)
        post_msg = get_post_msg(nodedata.get_data('behaviour'), self.goal_level, self.performance, self.phase)
        nodedata.action = Action(pre_msg, self.score, self.target, post_msg)
        return NodeStatus(NodeStatus.SUCCESS, "Created action from given behaviour.")

    def cleanup(self, nodedata):


class CheckForBehaviour(Node):
    def __init__(self, name, *args, **kwargs):
        super(CheckForBehaviour, self).__init__(
            name,
            run_cb=self.run,
            configure_cb=self.configure,
            cleanup_cb=self.cleanup,
            *args, **kwargs)

    def configure(self, nodedata):

    def run(self, nodedata):

    def cleanup(self, nodedata):


class DisplayBehaviour(Node):
    def __init__(self, name, *args, **kwargs):
        super(DisplayBehaviour, self).__init__(
            name,
            run_cb=self.run,
            configure_cb=self.configure,
            cleanup_cb=self.cleanup,
            *args, **kwargs)

    def configure(self, nodedata):

    def run(self, nodedata):

    def cleanup(self, nodedata):
