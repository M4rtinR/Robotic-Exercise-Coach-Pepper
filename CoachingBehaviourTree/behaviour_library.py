"""Behaviour Library

This script is where all of the different utterance options for the robot are stored and can be accessed using the
BehaviourLibraryFunctions class.
...
Attributes
----------
squash_behaviour_library :type dict
    Dictionary structure containing all options for utterances during a squash coaching session. Keys have the format
    <behaviour code>_?<goal level code>_?<performance code>_?<phase code>_?<post code> where ? means optional.

Classes
-------
BehaviourLibraryFunctions :dataclass
    A data class to access the dictionary of behaviour utterances.
"""

from dataclasses import dataclass, field
import random
from Policy.policy import Policy
from Policy.policy_wrapper import PolicyWrapper

squash_behaviour_library = {
    # Keys have format <behaviour code>_?<goal level code>_?<performance code>_?<phase code>_?<post code>
    '1_1': {0: 'pre_instruction_session_0', 1: 'pre_instruction_session_1', 2: 'pre_instruction_session_2',
            3: 'pre_instruction_session_3'},
    '1_2': {0: 'pre_instruction_stat_0', 1: 'pre_instruction_stat_1', 2: 'pre_instruction_stat_2',
            3: 'pre_instruction_stat_3'},
    '1_3': {0: 'pre_instruction_stat_0', 1: 'pre_instruction_stat_1', 2: 'pre_instruction_stat_2',
            3: 'pre_instruction_stat_3'},
    '1_4': {0: 'pre_instruction_set_0', 1: 'pre_instruction_set_1', 2: 'pre_instruction_set_2',
            3: 'pre_instruction_set_3'},
    '4_1_0_0': {0: 'postinstructionpositive_session_met_start_0',
                1: 'postinstructionpositive_session_met_start_1',
                2: 'postinstructionpositive_session_met_start_2',
                3: 'postinstructionpositive_session_met_start_3'},
    '4_1_0_1': {0: 'postinstructionpositive_session_met_end_0',
                1: 'postinstructionpositive_session_met_end_1',
                2: 'postinstructionpositive_session_met_end_2',
                3: 'postinstructionpositive_session_met_end_3'},
    '4_1_0_0_0': {0: 'postinstructionpositive_session_met_start_post_0',
                  1: 'postinstructionpositive_session_met_start_post_1',
                  2: 'postinstructionpositive_session_met_start_post_2',
                  3: 'postinstructionpositive_session_met_start_post_3'},
    '12': {0: 'Good', 1: 'Nice', 2: 'That\'s it', 3: 'Awesome'}}


@dataclass
class BehaviourLibraryFunctions:
    """
    A data class to access the dictionary of behaviour utterances.
    ...
    Attributes
    ----------
    name :type str
        The name of the class.
    behaviours :type dict
        The dictionary of behaviour utterances to access.
    POST_MSG :type int
        Final value 0 representing that we want to access the post message (after displaying score and target).

    Methods
    -------
    get_pre_msg(behaviour, goal_level, performance, phase)
        Accesses the behaviour library dictionary and returns a random utterance appropriate to the parameters.
    get_post_msg(behaviour, goal)level, performance, phase)
        Accesses the behaviour library dictionary and returns a random utterance appropriate to the parameters.
    """

    name: str
    behaviours: dict
    POST_MSG: int = 0

    def get_pre_msg(self, behaviour, goal_level, performance, phase):
        """
        Accesses the behaviour library dictionary and returns a random pre utterance appropriate to the parameters.
        :param behaviour :type int: the behaviour code e.g. A_PREINSTRUCTION = 1
        :param goal_level :type int: the current level of goal e.g. SESSION_GOAL = 1
        :param performance :type int: whether the user met their target score or not e.g. MET = 0
        :param phase :type int: whether we are in the intro (PHASE_START = 0) or feedback (PHASE_END = 1) phase
        :return: msg :type str: random utterance corresponding to the given parameters
        """

        # TODO: Expand with full list of behaviours etc.
        r = random.randint(0, 3)

        # Check which behaviour we have and randomly select from that dict.
        if behaviour == Policy.A_PREINSTRUCTION:
            msg = self.behaviours[str(behaviour) + '_' + str(goal_level)][r]
        elif behaviour == Policy.A_PRAISE:
            msg = self.behaviours[str(behaviour) + ''][r]

        return msg

    def get_post_msg(self, behaviour, goal_level, performance, phase):
        """
        Accesses the behaviour library dictionary and returns a random post utterance appropriate to the parameters.
        :param behaviour :type int: the behaviour code e.g. A_PREINSTRUCTION = 1
        :param goal_level :type int: the current level of goal e.g. SESSION_GOAL = 1
        :param performance :type int: whether the user met their target score or not e.g. MET = 0
        :param phase :type int: whether we are in the intro (PHASE_START = 0) or feedback (PHASE_END = 1) phase
        :return: msg :type str: random utterance corresponding to the given parameters
        """

        # TODO: Expand with full list of behaviours etc.
        # TODO: May need to create random in constructor to avoid the same order of selections all the time.
        r = random.randint(0, 3)

        # Check which behaviour we have and randomly select from that dict.
        if behaviour == Policy.A_PREINSTRUCTION:
            msg = None
        elif behaviour == Policy.A_POSTINSTRUCTIONPOSITIVE:
            msg = self.behaviours[str(behaviour) + '_' + str(goal_level) + '_' + str(performance) + '_' + str(phase) + '_' + str(self.POST_MSG)][r]
        elif behaviour == Policy.A_PRAISE:
            msg = None

        return msg
