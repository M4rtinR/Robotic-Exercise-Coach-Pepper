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
    # Keys have format <goal level code>_?<behaviour code>_?<performance code>_?<phase code>_?<post code>
    #
    #
    # Person Goal
    #
    #
    '0_1_-1_0_0': {0: 'pre_instruction_person_start_pre_0', 1: 'pre_instruction_person_start_pre_1',
                   2: 'pre_instruction_person_start_pre_2', 3: 'pre_instruction_person_start_pre_3'},
    '0_1_-1_1_0': {0: 'pre_instruction_person_end_pre_0', 1: 'pre_instruction_person_end_pre_1',
                   2: 'pre_instruction_person_end_pre_2', 3: 'pre_instruction_person_end_pre_3'},
    '0_44_-1_0_0': {0: 'pre_instruction_firstname_person_start_pre_0',
                    1: 'pre_instruction_firstname_person_start_pre_1',
                    2: 'pre_instruction_firstname_person_start_pre_2',
                    3: 'pre_instruction_firstname_person_start_pre_3'},
    '0_44_-1_1_0': {0: 'pre_instruction_firstname_person_end_pre_0', 1: 'pre_instruction_firstname_person_end_pre_1',
                    2: 'pre_instruction_firstname_person_end_pre_2', 3: 'pre_instruction_firstname_person_end_pre_3'},

    #
    #
    # Session Goal
    #
    #
    #
    # Pre-instruction
    #
    '1_1_-1_0_0': {0: 'pre_instruction_session_start_pre_0', 1: 'pre_instruction_session_start_pre_1',
                   2: 'pre_instruction_session_start_pre_2', 3: 'pre_instruction_session_start_pre_3'},
    '1_1_0_0_0': {0: 'pre_instruction_session_met_start_pre_0', 1: 'pre_instruction_session_met_start_pre_1',
                  2: 'pre_instruction_session_met_start_pre_2', 3: 'pre_instruction_session_met_start_pre_3'},
    '1_1_0_0_1': {0: 'pre_instruction_session_met_start_post_0', 1: 'pre_instruction_session_met_start_post_1',
                  2: 'pre_instruction_session_met_start_post_2', 3: 'pre_instruction_session_met_start_post_3'},
    '1_1_1_0_0': {0: 'pre_instruction_session_muchimproved_start_pre_0',
                  1: 'pre_instruction_session_muchimproved_start_pre_1',
                  2: 'pre_instruction_session_muchimproved_start_pre_2',
                  3: 'pre_instruction_session_muchimproved_start_pre_3'},
    '1_1_1_0_1': {0: 'pre_instruction_session_muchimproved_start_post_0',
                  1: 'pre_instruction_session_muchimproved_start_post_1',
                  2: 'pre_instruction_session_muchimproved_start_post_2',
                  3: 'pre_instruction_session_muchimproved_start_post_3'},
    '1_1_2_0_0': {0: 'pre_instruction_session_improved_start_pre_0', 1: 'pre_instruction_session_improved_start_pre_1',
                  2: 'pre_instruction_session_improved_start_pre_2', 3: 'pre_instruction_session_improved_start_pre_3'},
    '1_1_2_0_1': {0: 'pre_instruction_session_improved_start_post_0',
                  1: 'pre_instruction_session_improved_start_post_1',
                  2: 'pre_instruction_session_improved_start_post_2',
                  3: 'pre_instruction_session_improved_start_post_3'},
    '1_1_3_0_0': {0: 'pre_instruction_session_improvedswap_start_pre_0',
                  1: 'pre_instruction_session_improvedswap_start_pre_1',
                  2: 'pre_instruction_session_improvedswap_start_pre_2',
                  3: 'pre_instruction_session_improvedswap_start_pre_3'},
    '1_1_3_0_1': {0: 'pre_instruction_session_improvedswap_start_post_0',
                  1: 'pre_instruction_session_improvedswap_start_post_1',
                  2: 'pre_instruction_session_improvedswap_start_post_2',
                  3: 'pre_instruction_session_improvedswap_start_post_3'},
    '1_1_4_0_0': {0: 'pre_instruction_session_steady_start_pre_0', 1: 'pre_instruction_session_steady_start_pre_1',
                  2: 'pre_instruction_session_steady_start_pre_2', 3: 'pre_instruction_session_steady_start_pre_3'},
    '1_1_4_0_1': {0: 'pre_instruction_session_steady_start_post_0', 1: 'pre_instruction_session_steady_start_post_1',
                  2: 'pre_instruction_session_steady_start_post_2', 3: 'pre_instruction_session_steady_start_post_3'},
    '1_1_5_0_0': {0: 'pre_instruction_session_regressed_start_pre_0',
                  1: 'pre_instruction_session_regressed_start_pre_1',
                  2: 'pre_instruction_session_regressed_start_pre_2',
                  3: 'pre_instruction_session_regressed_start_pre_3'},
    '1_1_5_0_1': {0: 'pre_instruction_session_regressed_start_post_0',
                  1: 'pre_instruction_session_regressed_start_post_1',
                  2: 'pre_instruction_session_regressed_start_post_2',
                  3: 'pre_instruction_session_regressed_start_post_3'},
    '1_1_6_0_0': {0: 'pre_instruction_session_regressedswap_start_pre_0',
                  1: 'pre_instruction_session_regressedswap_start_pre_1',
                  2: 'pre_instruction_session_regressedswap_start_pre_2',
                  3: 'pre_instruction_session_regressedswap_start_pre_3'},
    '1_1_6_0_1': {0: 'pre_instruction_session_regressedswap_start_post_0',
                  1: 'pre_instruction_session_regressedswap_start_post_1',
                  2: 'pre_instruction_session_regressedswap_start_post_2',
                  3: 'pre_instruction_session_regressedswap_start_post_3'},
    '1_1_7_0_0': {0: 'pre_instruction_session_muchregressed_start_pre_0',
                  1: 'pre_instruction_session_muchregressed_start_pre_1',
                  2: 'pre_instruction_session_muchregressed_start_pre_2',
                  3: 'pre_instruction_session_muchregressed_start_pre_3'},
    '1_1_7_0_1': {0: 'pre_instruction_session_muchregressed_start_post_0',
                  1: 'pre_instruction_session_muchregressed_start_post_1',
                  2: 'pre_instruction_session_muchregressed_start_post_2',
                  3: 'pre_instruction_session_muchregressed_start_post_3'},

    #
    # Post Instruction (Positive)
    #
    '1_4_-1_0_0': {0: 'postinstructionpos_session_start_pre_0', 1: 'postinstructionpos_session_start_pre_1',
                   2: 'postinstructionpos_session_start_pre_2', 3: 'postinstructionpos_session_start_pre_3'},
    '1_4_0_0_0': {0: 'postinstructionpos_session_met_start_pre_0', 1: 'postinstructionpos_session_met_start_pre_1',
                  2: 'postinstructionpos_session_met_start_pre_2', 3: 'postinstructionpos_session_met_start_pre_3'},
    '1_4_0_0_1': {0: 'postinstructionpos_session_met_start_post_0', 1: 'postinstructionpos_session_met_start_post_1',
                  2: 'postinstructionpos_session_met_start_post_2', 3: 'postinstructionpos_session_met_start_post_3'},
    '1_4_0_1_0': {0: 'postinstructionpos_session_met_end_pre_0', 1: 'postinstructionpos_session_met_end_pre_1',
                  2: 'postinstructionpos_session_met_end_pre_2', 3: 'postinstructionpos_session_met_end_pre_3'},
    '1_4_0_1_1': {0: 'postinstructionpos_session_met_end_post_0', 1: 'postinstructionpos_session_met_end_post_1',
                  2: 'postinstructionpos_session_met_end_post_2', 3: 'postinstructionpos_session_met_end_post_3'},
    '1_4_1_0_0': {0: 'postinstructionpos_session_muchimproved_start_pre_0',
                  1: 'postinstructionpos_session_muchimproved_start_pre_1',
                  2: 'postinstructionpos_session_muchimproved_start_pre_2',
                  3: 'postinstructionpos_session_muchimproved_start_pre_3'},
    '1_4_1_0_1': {0: 'postinstructionpos_session_muchimproved_start_post_0',
                  1: 'postinstructionpos_session_muchimproved_start_post_1',
                  2: 'postinstructionpos_session_muchimproved_start_post_2',
                  3: 'postinstructionpos_session_muchimproved_start_post_3'},
    '1_4_1_1_0': {0: 'postinstructionpos_session_muchimproved_end_pre_0',
                  1: 'postinstructionpos_session_muchimproved_end_pre_1',
                  2: 'postinstructionpos_session_muchimproved_end_pre_2',
                  3: 'postinstructionpos_session_muchimproved_end_pre_3'},
    '1_4_1_1_1': {0: 'postinstructionpos_session_muchimproved_end_post_0',
                  1: 'postinstructionpos_session_muchimproved_end_post_1',
                  2: 'postinstructionpos_session_muchimproved_end_post_2',
                  3: 'postinstructionpos_session_muchimproved_end_post_3'},
    '1_4_2_0_0': {0: 'postinstructionpos_session_improved_start_pre_0',
                  1: 'postinstructionpos_session_improved_start_pre_1',
                  2: 'postinstructionpos_session_improved_start_pre_2',
                  3: 'postinstructionpos_session_improved_start_pre_3'},
    '1_4_2_0_1': {0: 'postinstructionpos_session_improved_start_post_0',
                  1: 'postinstructionpos_session_improved_start_post_1',
                  2: 'postinstructionpos_session_improved_start_post_2',
                  3: 'postinstructionpos_session_improved_start_post_3'},
    '1_4_2_1_0': {0: 'postinstructionpos_session_improved_end_pre_0',
                  1: 'postinstructionpos_session_improved_end_pre_1',
                  2: 'postinstructionpos_session_improved_end_pre_2',
                  3: 'postinstructionpos_session_improved_end_pre_3'},
    '1_4_2_1_1': {0: 'postinstructionpos_session_improved_end_post_0',
                  1: 'postinstructionpos_session_improved_end_post_1',
                  2: 'postinstructionpos_session_improved_end_post_2',
                  3: 'postinstructionpos_session_improved_end_post_3'},
    '1_4_3_0_0': {0: 'postinstructionpos_session_improvedswap_start_pre_0',
                  1: 'postinstructionpos_session_improvedswap_start_pre_1',
                  2: 'postinstructionpos_session_improvedswap_start_pre_2',
                  3: 'postinstructionpos_session_improvedswap_start_pre_3'},
    '1_4_3_0_1': {0: 'postinstructionpos_session_improvedswap_start_post_0',
                  1: 'postinstructionpos_session_improvedswap_start_post_1',
                  2: 'postinstructionpos_session_improvedswap_start_post_2',
                  3: 'postinstructionpos_session_improvedswap_start_post_3'},
    '1_4_3_1_0': {0: 'postinstructionpos_session_improvedswap_end_pre_0',
                  1: 'postinstructionpos_session_improvedswap_end_pre_1',
                  2: 'postinstructionpos_session_improvedswap_end_pre_2',
                  3: 'postinstructionpos_session_improvedswap_end_pre_3'},
    '1_4_3_1_1': {0: 'postinstructionpos_session_improvedswap_end_post_0',
                  1: 'postinstructionpos_session_improvedswap_end_post_1',
                  2: 'postinstructionpos_session_improvedswap_end_post_2',
                  3: 'postinstructionpos_session_improvedswap_end_post_3'},
    '1_4_4_0_0': {0: 'postinstructionpos_session_steady_start_pre_0',
                  1: 'postinstructionpos_session_steady_start_pre_1',
                  2: 'postinstructionpos_session_steady_start_pre_2',
                  3: 'postinstructionpos_session_steady_start_pre_3'},
    '1_4_4_0_1': {0: 'postinstructionpos_session_steady_start_post_0',
                  1: 'postinstructionpos_session_steady_start_post_1',
                  2: 'postinstructionpos_session_steady_start_post_2',
                  3: 'postinstructionpos_session_steady_start_post_3'},
    '1_4_4_1_0': {0: 'postinstructionpos_session_steady_end_pre_0',
                  1: 'postinstructionpos_session_steady_end_pre_1',
                  2: 'postinstructionpos_session_steady_end_pre_2',
                  3: 'postinstructionpos_session_steady_end_pre_3'},
    '1_4_4_1_1': {0: 'postinstructionpos_session_steady_end_post_0',
                  1: 'postinstructionpos_session_steady_end_post_1',
                  2: 'postinstructionpos_session_steady_end_post_2',
                  3: 'postinstructionpos_session_steady_end_post_3'},
    '1_4_5_0_0': {0: 'postinstructionpos_session_regressed_start_pre_0',
                  1: 'postinstructionpos_session_regressed_start_pre_1',
                  2: 'postinstructionpos_session_regressed_start_pre_2',
                  3: 'postinstructionpos_session_regressed_start_pre_3'},
    '1_4_5_0_1': {0: 'postinstructionpos_session_regressed_start_post_0',
                  1: 'postinstructionpos_session_regressed_start_post_1',
                  2: 'postinstructionpos_session_regressed_start_post_2',
                  3: 'postinstructionpos_session_regressed_start_post_3'},
    '1_4_5_1_0': {0: 'postinstructionpos_session_regressed_end_pre_0',
                  1: 'postinstructionpos_session_regressed_end_pre_1',
                  2: 'postinstructionpos_session_regressed_end_pre_2',
                  3: 'postinstructionpos_session_regressed_end_pre_3'},
    '1_4_5_1_1': {0: 'postinstructionpos_session_regressed_end_post_0',
                  1: 'postinstructionpos_session_regressed_end_post_1',
                  2: 'postinstructionpos_session_regressed_end_post_2',
                  3: 'postinstructionpos_session_regressed_end_post_3'},
    '1_4_6_0_0': {0: 'postinstructionpos_session_regressedswap_start_pre_0',
                  1: 'postinstructionpos_session_regressedswap_start_pre_1',
                  2: 'postinstructionpos_session_regressedswap_start_pre_2',
                  3: 'postinstructionpos_session_regressedswap_start_pre_3'},
    '1_4_6_0_1': {0: 'postinstructionpos_session_regressedswap_start_post_0',
                  1: 'postinstructionpos_session_regressedswap_start_post_1',
                  2: 'postinstructionpos_session_regressedswap_start_post_2',
                  3: 'postinstructionpos_session_regressedswap_start_post_3'},
    '1_4_6_1_0': {0: 'postinstructionpos_session_regressedswap_end_pre_0',
                  1: 'postinstructionpos_session_regressedswap_end_pre_1',
                  2: 'postinstructionpos_session_regressedswap_end_pre_2',
                  3: 'postinstructionpos_session_regressedswap_end_pre_3'},
    '1_4_6_1_1': {0: 'postinstructionpos_session_regressedswap_end_post_0',
                  1: 'postinstructionpos_session_regressedswap_end_post_1',
                  2: 'postinstructionpos_session_regressedswap_end_post_2',
                  3: 'postinstructionpos_session_regressedswap_end_post_3'},
    '1_4_7_0_0': {0: 'postinstructionpos_session_muchregressed_start_pre_0',
                  1: 'postinstructionpos_session_muchregressed_start_pre_1',
                  2: 'postinstructionpos_session_muchregressed_start_pre_2',
                  3: 'postinstructionpos_session_muchregressed_start_pre_3'},
    '1_4_7_0_1': {0: 'postinstructionpos_session_muchregressed_start_post_0',
                  1: 'postinstructionpos_session_muchregressed_start_post_1',
                  2: 'postinstructionpos_session_muchregressed_start_post_2',
                  3: 'postinstructionpos_session_muchregressed_start_post_3'},
    '1_4_7_1_0': {0: 'postinstructionpos_session_muchregressed_end_pre_0',
                  1: 'postinstructionpos_session_muchregressed_end_pre_1',
                  2: 'postinstructionpos_session_muchregressed_end_pre_2',
                  3: 'postinstructionpos_session_muchregressed_end_pre_3'},
    '1_4_7_1_1': {0: 'postinstructionpos_session_muchregressed_end_post_0',
                  1: 'postinstructionpos_session_muchregressed_end_post_1',
                  2: 'postinstructionpos_session_muchregressed_end_post_2',
                  3: 'postinstructionpos_session_muchregressed_end_post_3'},

    #
    # Post Instruction (Negative)
    #
    '1_5_-1_0_0': {0: 'postinstructionneg_session_start_pre_0', 1: 'postinstructionneg_session_start_pre_1',
                   2: 'postinstructionneg_session_start_pre_2', 3: 'postinstructionneg_session_start_pre_3'},
    '1_5_0_0_0': {0: 'postinstructionneg_session_met_start_pre_0', 1: 'postinstructionneg_session_met_start_pre_1',
                  2: 'postinstructionneg_session_met_start_pre_2', 3: 'postinstructionneg_session_met_start_pre_3'},
    '1_5_0_0_1': {0: 'postinstructionneg_session_met_start_post_0', 1: 'postinstructionneg_session_met_start_post_1',
                  2: 'postinstructionneg_session_met_start_post_2', 3: 'postinstructionneg_session_met_start_post_3'},
    '1_5_0_1_0': {0: 'postinstructionneg_session_met_end_pre_0', 1: 'postinstructionneg_session_met_end_pre_1',
                  2: 'postinstructionneg_session_met_end_pre_2', 3: 'postinstructionneg_session_met_end_pre_3'},
    '1_5_0_1_1': {0: 'postinstructionneg_session_met_end_post_0', 1: 'postinstructionneg_session_met_end_post_1',
                  2: 'postinstructionneg_session_met_end_post_2', 3: 'postinstructionneg_session_met_end_post_3'},
    '1_5_1_0_0': {0: 'postinstructionneg_session_muchimproved_start_pre_0',
                  1: 'postinstructionneg_session_muchimproved_start_pre_1',
                  2: 'postinstructionneg_session_muchimproved_start_pre_2',
                  3: 'postinstructionneg_session_muchimproved_start_pre_3'},
    '1_5_1_0_1': {0: 'postinstructionneg_session_muchimproved_start_post_0',
                  1: 'postinstructionneg_session_muchimproved_start_post_1',
                  2: 'postinstructionneg_session_muchimproved_start_post_2',
                  3: 'postinstructionneg_session_muchimproved_start_post_3'},
    '1_5_1_1_0': {0: 'postinstructionneg_session_muchimproved_end_pre_0',
                  1: 'postinstructionneg_session_muchimproved_end_pre_1',
                  2: 'postinstructionneg_session_muchimproved_end_pre_2',
                  3: 'postinstructionneg_session_muchimproved_end_pre_3'},
    '1_5_1_1_1': {0: 'postinstructionneg_session_muchimproved_end_post_0',
                  1: 'postinstructionneg_session_muchimproved_end_post_1',
                  2: 'postinstructionneg_session_muchimproved_end_post_2',
                  3: 'postinstructionneg_session_muchimproved_end_post_3'},
    '1_5_2_0_0': {0: 'postinstructionneg_session_improved_start_pre_0',
                  1: 'postinstructionneg_session_improved_start_pre_1',
                  2: 'postinstructionneg_session_improved_start_pre_2',
                  3: 'postinstructionneg_session_improved_start_pre_3'},
    '1_5_2_0_1': {0: 'postinstructionneg_session_improved_start_post_0',
                  1: 'postinstructionneg_session_improved_start_post_1',
                  2: 'postinstructionneg_session_improved_start_post_2',
                  3: 'postinstructionneg_session_improved_start_post_3'},
    '1_5_2_1_0': {0: 'postinstructionneg_session_improved_end_pre_0',
                  1: 'postinstructionneg_session_improved_end_pre_1',
                  2: 'postinstructionneg_session_improved_end_pre_2',
                  3: 'postinstructionneg_session_improved_end_pre_3'},
    '1_5_2_1_1': {0: 'postinstructionneg_session_improved_end_post_0',
                  1: 'postinstructionneg_session_improved_end_post_1',
                  2: 'postinstructionneg_session_improved_end_post_2',
                  3: 'postinstructionneg_session_improved_end_post_3'},
    '1_5_3_0_0': {0: 'postinstructionneg_session_improvedswap_start_pre_0',
                  1: 'postinstructionneg_session_improvedswap_start_pre_1',
                  2: 'postinstructionneg_session_improvedswap_start_pre_2',
                  3: 'postinstructionneg_session_improvedswap_start_pre_3'},
    '1_5_3_0_1': {0: 'postinstructionneg_session_improvedswap_start_post_0',
                  1: 'postinstructionneg_session_improvedswap_start_post_1',
                  2: 'postinstructionneg_session_improvedswap_start_post_2',
                  3: 'postinstructionneg_session_improvedswap_start_post_3'},
    '1_5_3_1_0': {0: 'postinstructionneg_session_improvedswap_end_pre_0',
                  1: 'postinstructionneg_session_improvedswap_end_pre_1',
                  2: 'postinstructionneg_session_improvedswap_end_pre_2',
                  3: 'postinstructionneg_session_improvedswap_end_pre_3'},
    '1_5_3_1_1': {0: 'postinstructionneg_session_improvedswap_end_post_0',
                  1: 'postinstructionneg_session_improvedswap_end_post_1',
                  2: 'postinstructionneg_session_improvedswap_end_post_2',
                  3: 'postinstructionneg_session_improvedswap_end_post_3'},
    '1_5_4_0_0': {0: 'postinstructionneg_session_steady_start_pre_0',
                  1: 'postinstructionneg_session_steady_start_pre_1',
                  2: 'postinstructionneg_session_steady_start_pre_2',
                  3: 'postinstructionneg_session_steady_start_pre_3'},
    '1_5_4_0_1': {0: 'postinstructionneg_session_steady_start_post_0',
                  1: 'postinstructionneg_session_steady_start_post_1',
                  2: 'postinstructionneg_session_steady_start_post_2',
                  3: 'postinstructionneg_session_steady_start_post_3'},
    '1_5_4_1_0': {0: 'postinstructionneg_session_steady_end_pre_0',
                  1: 'postinstructionneg_session_steady_end_pre_1',
                  2: 'postinstructionneg_session_steady_end_pre_2',
                  3: 'postinstructionneg_session_steady_end_pre_3'},
    '1_5_4_1_1': {0: 'postinstructionneg_session_steady_end_post_0',
                  1: 'postinstructionneg_session_steady_end_post_1',
                  2: 'postinstructionneg_session_steady_end_post_2',
                  3: 'postinstructionneg_session_steady_end_post_3'},
    '1_5_5_0_0': {0: 'postinstructionneg_session_regressed_start_pre_0',
                  1: 'postinstructionneg_session_regressed_start_pre_1',
                  2: 'postinstructionneg_session_regressed_start_pre_2',
                  3: 'postinstructionneg_session_regressed_start_pre_3'},
    '1_5_5_0_1': {0: 'postinstructionneg_session_regressed_start_post_0',
                  1: 'postinstructionneg_session_regressed_start_post_1',
                  2: 'postinstructionneg_session_regressed_start_post_2',
                  3: 'postinstructionneg_session_regressed_start_post_3'},
    '1_5_5_1_0': {0: 'postinstructionneg_session_regressed_end_pre_0',
                  1: 'postinstructionneg_session_regressed_end_pre_1',
                  2: 'postinstructionneg_session_regressed_end_pre_2',
                  3: 'postinstructionneg_session_regressed_end_pre_3'},
    '1_5_5_1_1': {0: 'postinstructionneg_session_regressed_end_post_0',
                  1: 'postinstructionneg_session_regressed_end_post_1',
                  2: 'postinstructionneg_session_regressed_end_post_2',
                  3: 'postinstructionneg_session_regressed_end_post_3'},
    '1_5_6_0_0': {0: 'postinstructionneg_session_regressedswap_start_pre_0',
                  1: 'postinstructionneg_session_regressedswap_start_pre_1',
                  2: 'postinstructionneg_session_regressedswap_start_pre_2',
                  3: 'postinstructionneg_session_regressedswap_start_pre_3'},
    '1_5_6_0_1': {0: 'postinstructionneg_session_regressedswap_start_post_0',
                  1: 'postinstructionneg_session_regressedswap_start_post_1',
                  2: 'postinstructionneg_session_regressedswap_start_post_2',
                  3: 'postinstructionneg_session_regressedswap_start_post_3'},
    '1_5_6_1_0': {0: 'postinstructionneg_session_regressedswap_end_pre_0',
                  1: 'postinstructionneg_session_regressedswap_end_pre_1',
                  2: 'postinstructionneg_session_regressedswap_end_pre_2',
                  3: 'postinstructionneg_session_regressedswap_end_pre_3'},
    '1_5_6_1_1': {0: 'postinstructionneg_session_regressedswap_end_post_0',
                  1: 'postinstructionneg_session_regressedswap_end_post_1',
                  2: 'postinstructionneg_session_regressedswap_end_post_2',
                  3: 'postinstructionneg_session_regressedswap_end_post_3'},
    '1_5_7_0_0': {0: 'postinstructionneg_session_muchregressed_start_pre_0',
                  1: 'postinstructionneg_session_muchregressed_start_pre_1',
                  2: 'postinstructionneg_session_muchregressed_start_pre_2',
                  3: 'postinstructionneg_session_muchregressed_start_pre_3'},
    '1_5_7_0_1': {0: 'postinstructionneg_session_muchregressed_start_post_0',
                  1: 'postinstructionneg_session_muchregressed_start_post_1',
                  2: 'postinstructionneg_session_muchregressed_start_post_2',
                  3: 'postinstructionneg_session_muchregressed_start_post_3'},
    '1_5_7_1_0': {0: 'postinstructionneg_session_muchregressed_end_pre_0',
                  1: 'postinstructionneg_session_muchregressed_end_pre_1',
                  2: 'postinstructionneg_session_muchregressed_end_pre_2',
                  3: 'postinstructionneg_session_muchregressed_end_pre_3'},
    '1_5_7_1_1': {0: 'postinstructionneg_session_muchregressed_end_post_0',
                  1: 'postinstructionneg_session_muchregressed_end_post_1',
                  2: 'postinstructionneg_session_muchregressed_end_post_2',
                  3: 'postinstructionneg_session_muchregressed_end_post_3'},

    #
    # Questioning
    #
    '1_7_-1_0_0': {0: 'questioning_session_start_pre_0', 1: 'questioning_session_start_pre_1',
                   2: 'questioning_session_start_pre_2', 3: 'questioning_session_start_pre_3'},
    '1_7_0_0_0': {0: 'questioning_session_met_start_pre_0', 1: 'questioning_session_met_start_pre_1',
                  2: 'questioning_session_met_start_pre_2', 3: 'questioning_session_met_start_pre_3'},
    '1_7_0_0_1': {0: 'questioning_session_met_start_post_0', 1: 'questioning_session_met_start_post_1',
                  2: 'questioning_session_met_start_post_2', 3: 'questioning_session_met_start_post_3'},
    '1_7_0_1_0': {0: 'questioning_session_met_end_pre_0', 1: 'questioning_session_met_end_pre_1',
                  2: 'questioning_session_met_end_pre_2', 3: 'questioning_session_met_end_pre_3'},
    '1_7_0_1_1': {0: 'questioning_session_met_end_post_0', 1: 'questioning_session_met_end_post_1',
                  2: 'questioning_session_met_end_post_2', 3: 'questioning_session_met_end_post_3'},
    '1_7_1_0_0': {0: 'questioning_session_muchimproved_start_pre_0',
                  1: 'questioning_session_muchimproved_start_pre_1',
                  2: 'questioning_session_muchimproved_start_pre_2',
                  3: 'questioning_session_muchimproved_start_pre_3'},
    '1_7_1_0_1': {0: 'questioning_session_muchimproved_start_post_0',
                  1: 'questioning_session_muchimproved_start_post_1',
                  2: 'questioning_session_muchimproved_start_post_2',
                  3: 'questioning_session_muchimproved_start_post_3'},
    '1_7_1_1_0': {0: 'questioning_session_muchimproved_end_pre_0',
                  1: 'questioning_session_muchimproved_end_pre_1',
                  2: 'questioning_session_muchimproved_end_pre_2',
                  3: 'questioning_session_muchimproved_end_pre_3'},
    '1_7_1_1_1': {0: 'questioning_session_muchimproved_end_post_0',
                  1: 'questioning_session_muchimproved_end_post_1',
                  2: 'questioning_session_muchimproved_end_post_2',
                  3: 'questioning_session_muchimproved_end_post_3'},
    '1_7_2_0_0': {0: 'questioning_session_improved_start_pre_0',
                  1: 'questioning_session_improved_start_pre_1',
                  2: 'questioning_session_improved_start_pre_2',
                  3: 'questioning_session_improved_start_pre_3'},
    '1_7_2_0_1': {0: 'questioning_session_improved_start_post_0',
                  1: 'questioning_session_improved_start_post_1',
                  2: 'questioning_session_improved_start_post_2',
                  3: 'questioning_session_improved_start_post_3'},
    '1_7_2_1_0': {0: 'questioning_session_improved_end_pre_0',
                  1: 'questioning_session_improved_end_pre_1',
                  2: 'questioning_session_improved_end_pre_2',
                  3: 'questioning_session_improved_end_pre_3'},
    '1_7_2_1_1': {0: 'questioning_session_improved_end_post_0',
                  1: 'questioning_session_improved_end_post_1',
                  2: 'questioning_session_improved_end_post_2',
                  3: 'questioning_session_improved_end_post_3'},
    '1_7_3_0_0': {0: 'questioning_session_improvedswap_start_pre_0',
                  1: 'questioning_session_improvedswap_start_pre_1',
                  2: 'questioning_session_improvedswap_start_pre_2',
                  3: 'questioning_session_improvedswap_start_pre_3'},
    '1_7_3_0_1': {0: 'questioning_session_improvedswap_start_post_0',
                  1: 'questioning_session_improvedswap_start_post_1',
                  2: 'questioning_session_improvedswap_start_post_2',
                  3: 'questioning_session_improvedswap_start_post_3'},
    '1_7_3_1_0': {0: 'questioning_session_improvedswap_end_pre_0',
                  1: 'questioning_session_improvedswap_end_pre_1',
                  2: 'questioning_session_improvedswap_end_pre_2',
                  3: 'questioning_session_improvedswap_end_pre_3'},
    '1_7_3_1_1': {0: 'questioning_session_improvedswap_end_post_0',
                  1: 'questioning_session_improvedswap_end_post_1',
                  2: 'questioning_session_improvedswap_end_post_2',
                  3: 'questioning_session_improvedswap_end_post_3'},
    '1_7_4_0_0': {0: 'questioning_session_steady_start_pre_0',
                  1: 'questioning_session_steady_start_pre_1',
                  2: 'questioning_session_steady_start_pre_2',
                  3: 'questioning_session_steady_start_pre_3'},
    '1_7_4_0_1': {0: 'questioning_session_steady_start_post_0',
                  1: 'questioning_session_steady_start_post_1',
                  2: 'questioning_session_steady_start_post_2',
                  3: 'questioning_session_steady_start_post_3'},
    '1_7_4_1_0': {0: 'questioning_session_steady_end_pre_0',
                  1: 'questioning_session_steady_end_pre_1',
                  2: 'questioning_session_steady_end_pre_2',
                  3: 'questioning_session_steady_end_pre_3'},
    '1_7_4_1_1': {0: 'questioning_session_steady_end_post_0',
                  1: 'questioning_session_steady_end_post_1',
                  2: 'questioning_session_steady_end_post_2',
                  3: 'questioning_session_steady_end_post_3'},
    '1_7_5_0_0': {0: 'questioning_session_regressed_start_pre_0',
                  1: 'questioning_session_regressed_start_pre_1',
                  2: 'questioning_session_regressed_start_pre_2',
                  3: 'questioning_session_regressed_start_pre_3'},
    '1_7_5_0_1': {0: 'questioning_session_regressed_start_post_0',
                  1: 'questioning_session_regressed_start_post_1',
                  2: 'questioning_session_regressed_start_post_2',
                  3: 'questioning_session_regressed_start_post_3'},
    '1_7_5_1_0': {0: 'questioning_session_regressed_end_pre_0',
                  1: 'questioning_session_regressed_end_pre_1',
                  2: 'questioning_session_regressed_end_pre_2',
                  3: 'questioning_session_regressed_end_pre_3'},
    '1_7_5_1_1': {0: 'questioning_session_regressed_end_post_0',
                  1: 'questioning_session_regressed_end_post_1',
                  2: 'questioning_session_regressed_end_post_2',
                  3: 'questioning_session_regressed_end_post_3'},
    '1_7_6_0_0': {0: 'questioning_session_regressedswap_start_pre_0',
                  1: 'questioning_session_regressedswap_start_pre_1',
                  2: 'questioning_session_regressedswap_start_pre_2',
                  3: 'questioning_session_regressedswap_start_pre_3'},
    '1_7_6_0_1': {0: 'questioning_session_regressedswap_start_post_0',
                  1: 'questioning_session_regressedswap_start_post_1',
                  2: 'questioning_session_regressedswap_start_post_2',
                  3: 'questioning_session_regressedswap_start_post_3'},
    '1_7_6_1_0': {0: 'questioning_session_regressedswap_end_pre_0',
                  1: 'questioning_session_regressedswap_end_pre_1',
                  2: 'questioning_session_regressedswap_end_pre_2',
                  3: 'questioning_session_regressedswap_end_pre_3'},
    '1_7_6_1_1': {0: 'questioning_session_regressedswap_end_post_0',
                  1: 'questioning_session_regressedswap_end_post_1',
                  2: 'questioning_session_regressedswap_end_post_2',
                  3: 'questioning_session_regressedswap_end_post_3'},
    '1_7_7_0_0': {0: 'questioning_session_muchregressed_start_pre_0',
                  1: 'questioning_session_muchregressed_start_pre_1',
                  2: 'questioning_session_muchregressed_start_pre_2',
                  3: 'questioning_session_muchregressed_start_pre_3'},
    '1_7_7_0_1': {0: 'questioning_session_muchregressed_start_post_0',
                  1: 'questioning_session_muchregressed_start_post_1',
                  2: 'questioning_session_muchregressed_start_post_2',
                  3: 'questioning_session_muchregressed_start_post_3'},
    '1_7_7_1_0': {0: 'questioning_session_muchregressed_end_pre_0',
                  1: 'questioning_session_muchregressed_end_pre_1',
                  2: 'questioning_session_muchregressed_end_pre_2',
                  3: 'questioning_session_muchregressed_end_pre_3'},
    '1_7_7_1_1': {0: 'questioning_session_muchregressed_end_post_0',
                  1: 'questioning_session_muchregressed_end_post_1',
                  2: 'questioning_session_muchregressed_end_post_2',
                  3: 'questioning_session_muchregressed_end_post_3'},

    #
    # Praise
    #
    '1_12_0_0_0': {0: 'praise_session_met_start_pre_0', 1: 'praise_session_met_start_pre_1',
                   2: 'praise_session_met_start_pre_2', 3: 'praise_session_met_start_pre_3'},
    '1_12_0_0_1': {0: 'praise_session_met_start_post_0', 1: 'praise_session_met_start_post_1',
                   2: 'praise_session_met_start_post_2', 3: 'praise_session_met_start_post_3'},
    '1_12_0_1_0': {0: 'praise_session_met_end_pre_0', 1: 'praise_session_met_end_pre_1',
                   2: 'praise_session_met_end_pre_2', 3: 'praise_session_met_end_pre_3'},
    '1_12_0_1_1': {0: 'praise_session_met_end_post_0', 1: 'praise_session_met_end_post_1',
                   2: 'praise_session_met_end_post_2', 3: 'praise_session_met_end_post_3'},
    '1_12_1_0_0': {0: 'praise_session_muchimproved_start_pre_0', 1: 'praise_session_muchimproved_start_pre_1',
                   2: 'praise_session_muchimproved_start_pre_2', 3: 'praise_session_muchimproved_start_pre_3'},
    '1_12_1_0_1': {0: 'praise_session_muchimproved_start_post_0', 1: 'praise_session_muchimproved_start_post_1',
                   2: 'praise_session_muchimproved_start_post_2', 3: 'praise_session_muchimproved_start_post_3'},
    '1_12_1_1_0': {0: 'praise_session_muchimproved_end_pre_0', 1: 'praise_session_muchimproved_end_pre_1',
                   2: 'praise_session_muchimproved_end_pre_2', 3: 'praise_session_muchimproved_end_pre_3'},
    '1_12_1_1_1': {0: 'praise_session_muchimproved_end_post_0', 1: 'praise_session_muchimproved_end_post_1',
                   2: 'praise_session_muchimproved_end_post_2', 3: 'praise_session_muchimproved_end_post_3'},
    '1_12_2_0_0': {0: 'praise_session_improved_start_pre_0', 1: 'praise_session_improved_start_pre_1',
                   2: 'praise_session_improved_start_pre_2', 3: 'praise_session_improved_start_pre_3'},
    '1_12_2_0_1': {0: 'praise_session_improved_start_post_0', 1: 'praise_session_improved_start_post_1',
                   2: 'praise_session_improved_start_post_2', 3: 'praise_session_improved_start_post_3'},
    '1_12_2_1_0': {0: 'praise_session_improved_end_pre_0', 1: 'praise_session_improved_end_pre_1',
                   2: 'praise_session_improved_end_pre_2', 3: 'praise_session_improved_end_pre_3'},
    '1_12_2_1_1': {0: 'praise_session_improved_end_post_0', 1: 'praise_session_improved_end_post_1',
                   2: 'praise_session_improved_end_post_2', 3: 'praise_session_improved_end_post_3'},
    '1_12_3_0_0': {0: 'praise_session_improvedswap_start_pre_0', 1: 'praise_session_improvedswap_start_pre_1',
                   2: 'praise_session_improvedswap_start_pre_2', 3: 'praise_session_improvedswap_start_pre_3'},
    '1_12_3_0_1': {0: 'praise_session_improvedswap_start_post_0', 1: 'praise_session_improvedswap_start_post_1',
                   2: 'praise_session_improvedswap_start_post_2', 3: 'praise_session_improvedswap_start_post_3'},
    '1_12_3_1_0': {0: 'praise_session_improvedswap_end_pre_0', 1: 'praise_session_improvedswap_end_pre_1',
                   2: 'praise_session_improvedswap_end_pre_2', 3: 'praise_session_improvedswap_end_pre_3'},
    '1_12_3_1_1': {0: 'praise_session_improvedswap_end_post_0', 1: 'praise_session_improvedswap_end_post_1',
                   2: 'praise_session_improvedswap_end_post_2', 3: 'praise_session_improvedswap_end_post_3'},
    '1_12_4_0_0': {0: 'praise_session_steady_start_pre_0', 1: 'praise_session_steady_start_pre_1',
                   2: 'praise_session_steady_start_pre_2', 3: 'praise_session_steady_start_pre_3'},
    '1_12_4_0_1': {0: 'praise_session_steady_start_post_0', 1: 'praise_session_steady_start_post_1',
                   2: 'praise_session_steady_start_post_2', 3: 'praise_session_steady_start_post_3'},
    '1_12_4_1_0': {0: 'praise_session_steady_end_pre_0', 1: 'praise_session_steady_end_pre_1',
                   2: 'praise_session_steady_end_pre_2', 3: 'praise_session_steady_end_pre_3'},
    '1_12_4_1_1': {0: 'praise_session_steady_end_post_0', 1: 'praise_session_steady_end_post_1',
                   2: 'praise_session_steady_end_post_2', 3: 'praise_session_steady_end_post_3'},

    #
    # Scold
    #
    '1_13_5_0_0': {0: 'scold_session_regressed_start_pre_0',
                  1: 'scold_session_regressed_start_pre_1',
                  2: 'scold_session_regressed_start_pre_2',
                  3: 'scold_session_regressed_start_pre_3'},
    '1_13_5_0_1': {0: 'scold_session_regressed_start_post_0',
                  1: 'scold_session_regressed_start_post_1',
                  2: 'scold_session_regressed_start_post_2',
                  3: 'scold_session_regressed_start_post_3'},
    '1_13_5_1_0': {0: 'scold_session_regressed_end_pre_0',
                  1: 'scold_session_regressed_end_pre_1',
                  2: 'scold_session_regressed_end_pre_2',
                  3: 'scold_session_regressed_end_pre_3'},
    '1_13_5_1_1': {0: 'scold_session_regressed_end_post_0',
                  1: 'scold_session_regressed_end_post_1',
                  2: 'scold_session_regressed_end_post_2',
                  3: 'scold_session_regressed_end_post_3'},
    '1_13_6_0_0': {0: 'scold_session_regressedswap_start_pre_0',
                  1: 'scold_session_regressedswap_start_pre_1',
                  2: 'scold_session_regressedswap_start_pre_2',
                  3: 'scold_session_regressedswap_start_pre_3'},
    '1_13_6_0_1': {0: 'scold_session_regressedswap_start_post_0',
                  1: 'scold_session_regressedswap_start_post_1',
                  2: 'scold_session_regressedswap_start_post_2',
                  3: 'scold_session_regressedswap_start_post_3'},
    '1_13_6_1_0': {0: 'scold_session_regressedswap_end_pre_0',
                  1: 'scold_session_regressedswap_end_pre_1',
                  2: 'scold_session_regressedswap_end_pre_2',
                  3: 'scold_session_regressedswap_end_pre_3'},
    '1_13_6_1_1': {0: 'scold_session_regressedswap_end_post_0',
                  1: 'scold_session_regressedswap_end_post_1',
                  2: 'scold_session_regressedswap_end_post_2',
                  3: 'scold_session_regressedswap_end_post_3'},
    '1_13_7_0_0': {0: 'scold_session_muchregressed_start_pre_0',
                  1: 'scold_session_muchregressed_start_pre_1',
                  2: 'scold_session_muchregressed_start_pre_2',
                  3: 'scold_session_muchregressed_start_pre_3'},
    '1_13_7_0_1': {0: 'scold_session_muchregressed_start_post_0',
                  1: 'scold_session_muchregressed_start_post_1',
                  2: 'scold_session_muchregressed_start_post_2',
                  3: 'scold_session_muchregressed_start_post_3'},
    '1_13_7_1_0': {0: 'scold_session_muchregressed_end_pre_0',
                  1: 'scold_session_muchregressed_end_pre_1',
                  2: 'scold_session_muchregressed_end_pre_2',
                  3: 'scold_session_muchregressed_end_pre_3'},
    '1_13_7_1_1': {0: 'scold_session_muchregressed_end_post_0',
                  1: 'scold_session_muchregressed_end_post_1',
                  2: 'scold_session_muchregressed_end_post_2',
                  3: 'scold_session_muchregressed_end_post_3'},

    #
    # Console
    #
    '1_14_5_0_0': {0: 'console_session_regressed_start_pre_0',
                   1: 'console_session_regressed_start_pre_1',
                   2: 'console_session_regressed_start_pre_2',
                   3: 'console_session_regressed_start_pre_3'},
    '1_14_5_0_1': {0: 'console_session_regressed_start_post_0',
                   1: 'console_session_regressed_start_post_1',
                   2: 'console_session_regressed_start_post_2',
                   3: 'console_session_regressed_start_post_3'},
    '1_14_5_1_0': {0: 'console_session_regressed_end_pre_0',
                   1: 'console_session_regressed_end_pre_1',
                   2: 'console_session_regressed_end_pre_2',
                   3: 'console_session_regressed_end_pre_3'},
    '1_14_5_1_1': {0: 'console_session_regressed_end_post_0',
                   1: 'console_session_regressed_end_post_1',
                   2: 'console_session_regressed_end_post_2',
                   3: 'console_session_regressed_end_post_3'},
    '1_14_6_0_0': {0: 'console_session_regressedswap_start_pre_0',
                   1: 'console_session_regressedswap_start_pre_1',
                   2: 'console_session_regressedswap_start_pre_2',
                   3: 'console_session_regressedswap_start_pre_3'},
    '1_14_6_0_1': {0: 'console_session_regressedswap_start_post_0',
                   1: 'console_session_regressedswap_start_post_1',
                   2: 'console_session_regressedswap_start_post_2',
                   3: 'console_session_regressedswap_start_post_3'},
    '1_14_6_1_0': {0: 'console_session_regressedswap_end_pre_0',
                   1: 'console_session_regressedswap_end_pre_1',
                   2: 'console_session_regressedswap_end_pre_2',
                   3: 'console_session_regressedswap_end_pre_3'},
    '1_14_6_1_1': {0: 'console_session_regressedswap_end_post_0',
                   1: 'console_session_regressedswap_end_post_1',
                   2: 'console_session_regressedswap_end_post_2',
                   3: 'console_session_regressedswap_end_post_3'},
    '1_14_7_0_0': {0: 'console_session_muchregressed_start_pre_0',
                   1: 'console_session_muchregressed_start_pre_1',
                   2: 'console_session_muchregressed_start_pre_2',
                   3: 'console_session_muchregressed_start_pre_3'},
    '1_14_7_0_1': {0: 'console_session_muchregressed_start_post_0',
                   1: 'console_session_muchregressed_start_post_1',
                   2: 'console_session_muchregressed_start_post_2',
                   3: 'console_session_muchregressed_start_post_3'},
    '1_14_7_1_0': {0: 'console_session_muchregressed_end_pre_0',
                   1: 'console_session_muchregressed_end_pre_1',
                   2: 'console_session_muchregressed_end_pre_2',
                   3: 'console_session_muchregressed_end_pre_3'},
    '1_14_7_1_1': {0: 'console_session_muchregressed_end_post_0',
                   1: 'console_session_muchregressed_end_post_1',
                   2: 'console_session_muchregressed_end_post_2',
                   3: 'console_session_muchregressed_end_post_3'},

    #
    #
    # Shot Goal
    #
    #
    #
    # Pre-instruction
    #
    '1_2': {0: 'pre_instruction_shot_0', 1: 'pre_instruction_shot_1', 2: 'pre_instruction_shot_2',
            3: 'pre_instruction_shot_3'},

    #
    #
    # Stat Goal
    #
    #
    #
    # Pre-instruction
    #
    '1_3': {0: 'pre_instruction_stat_0', 1: 'pre_instruction_stat_1', 2: 'pre_instruction_stat_2',
            3: 'pre_instruction_stat_3'},

    #
    #
    # Set Goal
    #
    #
    #
    # Pre-instruction
    #
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
