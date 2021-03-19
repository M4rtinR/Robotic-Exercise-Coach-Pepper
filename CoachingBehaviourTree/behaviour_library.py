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
    name: str
    behaviours: dict
    POST_MSG: int = 0

    def get_pre_msg(self, behaviour, goal_level, performance, phase):
        # TODO: Expand with full list of behaviours etc.
        r = random.randint(0, 3)

        # Check which behaviour we have and randomly select from that dict.
        if behaviour == Policy.A_PREINSTRUCTION:
            msg = self.behaviours[str(behaviour) + '_' + str(goal_level)][r]
        elif behaviour == Policy.A_PRAISE:
            msg = self.behaviours[str(behaviour) + ''][r]

        return msg

    def get_post_msg(self, behaviour, goal_level, performance, phase):
        # TODO: Expand with full list of behaviours etc.
        r = random.randint(0, 3)

        # Check which behaviour we have and randomly select from that dict.
        if behaviour == Policy.A_PREINSTRUCTION:
            msg = None
        elif behaviour == Policy.A_POSTINSTRUCTIONPOSITIVE:
            msg = self.behaviours[str(behaviour) + '_' + str(goal_level) + '_' + str(performance) + '_' + str(phase) + '_' + str(self.POST_MSG)][r]
        elif behaviour == Policy.A_PRAISE:
            msg = None

        return msg
