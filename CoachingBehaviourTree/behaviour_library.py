from dataclasses import dataclass, field
from random import random
from Policy.policy import Policy
from Policy.policy_wrapper import PolicyWrapper


@dataclass
class BehaviourLibrary:

    behaviours: dict = field(default_factory={
        '1_session': {0: 'pre_instruction_session_0', 1: 'pre_instruction_session_1', 2: 'pre_instruction_session_2',
                      3: 'pre_instruction_session_3'},
        '1_exercise': {0: 'pre_instruction_stat_0', 1: 'pre_instruction_stat_1', 2: 'pre_instruction_stat_2',
                       3: 'pre_instruction_stat_3'},
        '1_stat': {0: 'pre_instruction_stat_0', 1: 'pre_instruction_stat_1', 2: 'pre_instruction_stat_2',
                   3: 'pre_instruction_stat_3'},
        '1_set': {0: 'pre_instruction_set_0', 1: 'pre_instruction_set_1', 2: 'pre_instruction_set_2',
                  3: 'pre_instruction_set_3'},
        '4_session_met_start': {0: 'postinstructionpositive_session_met_start_0',
                                1: 'postinstructionpositive_session_met_start_1',
                                2: 'postinstructionpositive_session_met_start_2',
                                3: 'postinstructionpositive_session_met_start_3'},
        '4_session_met_end': {0: 'postinstructionpositive_session_met_end_0',
                              1: 'postinstructionpositive_session_met_end_1',
                              2: 'postinstructionpositive_session_met_end_2',
                              3: 'postinstructionpositive_session_met_end_3'},
        '12': {0: 'Good', 1: 'Nice', 2: 'That\'s it', 3: 'Awesome'}
    })












    #
    #
    #
    #
    # Test BehaviourLibrary before doing anymore implementation
    #
    #
    #
    #














    def get_pre_msg(self, behaviour, goal_level, performance, phase):
        # behaviour = praise
        # goal_level = ACTION_GOAL
        # performance = MET
        # phase = start

        r = random.randint(0, 3)

        # Check which behaviour we have and randomly select from that dict.
        if behaviour == Policy.A_PREINSTRUCTION:
            msg = self.behaviours[behaviour + 'goal_level'][r]
        elif behaviour == Policy.A_PRAISE:
            msg = self.behaviours[behaviour + ''][r]

        return msg
