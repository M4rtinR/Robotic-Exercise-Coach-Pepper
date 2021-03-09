from policy import Policy


class PolicyWrapper:

    def __init__(self, belief):
        self.policy = Policy(belief)

    # Goal Levels
    PERSON_GOAL = 0
    SESSION_GOAL = 1
    EXERCISE_GOAL = 2
    STAT_GOAL = 3
    SET_GOAL = 4
    ACTION_GOAL = 5

    # Phases
    PHASE_START = 0
    PHASE_END = 1

    # Performance Levels
    MET = 0             # Met the target
    MUCH_IMPROVED = 1   # Moved a lot closer to the target
    IMPROVED = 2        # Moved closer to the target
    IMPROVED_SWAP = 3   # Moved closer to the target but passed it
    STEADY = 4          # Stayed the same
    REGRESSED = 5       # Moved further away from the target
    REGRESSED_SWAP = 6  # Moved past the target and further from it
    MUCH_REGRESSED = 7  # Moved a lot further away from the target

    def get_action(self, state, goal_level, performance, phase):
        valid_behaviours = self._get_valid_list(goal_level, performance, phase)
        behaviour = self.policy.sample_action(state)
        while not(behaviour in valid_behaviours):
            if goal_level == self.ACTION_GOAL:     # If between shots, silence is an appropriate action so each time a
                behaviour = self.policy.A_SILENCE  # non-valid action is proposed, just use silence.
            else:
                behaviour = self.policy.sample_action(state)

        return behaviour

    def _get_valid_list(self, goal_level, performance, phase):
        valid_list = []

        # Person Goal
        if goal_level == self.PERSON_GOAL:
            valid_list.extend([self.policy.A_PREINSTRUCTION, self.policy.A_PREINSTRUCTION_FIRSTNAME])

        # Session Goal
        elif goal_level == self.SESSION_GOAL:
            valid_list.extend([self.policy.A_POSTINSTRUCTIONPOSITIVE, self.policy.A_POSTINSTRUCTIONNEGATIVE,
                               self.policy.A_QUESTIONING, self.policy.A_POSTINSTRUCTIONPOSITIVE_QUESTIONING,
                               self.policy.A_POSTINSTRUCTIONPOSITIVE_FIRSTNAME,
                               self.policy.A_POSTINSTRUCTIONNEGATIVE_QUESTIONING, self.policy.A_QUESTIONING_FIRSTNAME,
                               self.policy.A_POSTINSTRUCTIONNEGATIVE_FIRSTNAME,
                               self.policy.A_QUESTIONING_POSITIVEMODELING, self.policy.A_POSITIVEMODELING_QUESTIONING,
                               self.policy.A_POSTINSTRUCTIONPOSITIVE_POSITIVE_MODELING,
                               self.policy.A_POSTINSTRUCTIONPOSITIVE_NEGATIVE_MODELING,
                               self.policy.A_POSTINSTRUCTIONNEGATIVE_POSITIVEMODELING,
                               self.policy.A_POSTINSTRUCTIONNEGATIVE_NEGATIVEMODELING,
                               self.policy.A_QUESTIONING_NEGATIVEMODELING,
                               self.policy.A_POSITIVEMODELING_POSTINSTRUCTIONPOSITIVE,
                               self.policy.A_NEGATIVEMODELING_POSTINSTRUCTIONNEGATIVE])
            if phase == self.PHASE_START:
                valid_list.extend([self.policy.A_PREINSTRUCTION, self.policy.A_PREINSTRUCTION_QUESTIONING,
                                   self.policy.A_PREINSTRUCTION_FIRSTNAME,
                                   self.policy.A_PREINSTRUCTION_POSITIVEMODELING,
                                   self.policy.A_PREINSTRUCTION_NEGATIVEMODELING,
                                   self.policy.A_POSITIVEMODELING_PREINSTRUCTION])
                if performance == self.MET:
                    valid_list.extend([self.policy.A_PRAISE, self.policy.A_PRAISE_FIRSTNAME,
                                       self.policy.A_POSITIVEMODELING_PRAISE])
                elif performance == self.MUCH_IMPROVED:
                    valid_list.extend([self.policy.A_PRAISE, self.policy.A_PRAISE_FIRSTNAME,
                                       self.policy.A_POSITIVEMODELING_PRAISE])
                elif performance == self.IMPROVED:
                    valid_list.extend([self.policy.A_PRAISE, self.policy.A_PRAISE_FIRSTNAME,
                                       self.policy.A_POSITIVEMODELING_PRAISE])
                elif performance == self.IMPROVED_SWAP:
                    valid_list.extend([self.policy.A_PRAISE, self.policy.A_PRAISE_FIRSTNAME,
                                       self.policy.A_POSITIVEMODELING_PRAISE])
                elif performance == self.STEADY:
                    valid_list.extend([self.policy.A_PRAISE, self.policy.A_PRAISE_FIRSTNAME,
                                       self.policy.A_POSITIVEMODELING_PRAISE])
                elif performance == self.REGRESSED:
                    valid_list.extend([self.policy.A_SCOLD, self.policy.A_CONSOLE, self.policy.A_SCOLD_FIRSTNAME,
                                       self.policy.A_CONSOLE_FIRSTNAME])
                elif performance == self.REGRESSED_SWAP:
                    valid_list.extend([self.policy.A_SCOLD, self.policy.A_CONSOLE, self.policy.A_SCOLD_FIRSTNAME,
                                       self.policy.A_CONSOLE_FIRSTNAME])
                else:  # performance == self.MUCH_REGRESSED
                    valid_list.extend([self.policy.A_SCOLD, self.policy.A_CONSOLE, self.policy.A_SCOLD_FIRSTNAME,
                                       self.policy.A_CONSOLE_FIRSTNAME])
            else:  # phase == self.PHASE_END
                valid_list.append(self.policy.A_END)
                if performance == self.MET:
                    valid_list.extend([self.policy.A_PRAISE, self.policy.A_PRAISE_FIRSTNAME,
                                       self.policy.A_POSITIVEMODELING_PRAISE])
                elif performance == self.MUCH_IMPROVED:
                    valid_list.extend([self.policy.A_PRAISE, self.policy.A_PRAISE_FIRSTNAME,
                                       self.policy.A_POSITIVEMODELING_PRAISE])
                elif performance == self.IMPROVED:
                    valid_list.extend([self.policy.A_PRAISE, self.policy.A_PRAISE_FIRSTNAME,
                                       self.policy.A_POSITIVEMODELING_PRAISE])
                elif performance == self.IMPROVED_SWAP:
                    valid_list.extend([self.policy.A_PRAISE, self.policy.A_PRAISE_FIRSTNAME,
                                       self.policy.A_POSITIVEMODELING_PRAISE])
                elif performance == self.STEADY:
                    valid_list.extend([self.policy.A_PRAISE, self.policy.A_PRAISE_FIRSTNAME,
                                       self.policy.A_POSITIVEMODELING_PRAISE])
                elif performance == self.REGRESSED:
                    valid_list.extend([self.policy.A_SCOLD, self.policy.A_CONSOLE, self.policy.A_SCOLD_FIRSTNAME,
                                       self.policy.A_CONSOLE_FIRSTNAME])
                elif performance == self.REGRESSED_SWAP:
                    valid_list.extend([self.policy.A_SCOLD, self.policy.A_CONSOLE, self.policy.A_SCOLD_FIRSTNAME,
                                       self.policy.A_CONSOLE_FIRSTNAME])
                else:  # performance == self.MUCH_REGRESSED
                    valid_list.extend([self.policy.A_SCOLD, self.policy.A_CONSOLE, self.policy.A_SCOLD_FIRSTNAME,
                                       self.policy.A_CONSOLE_FIRSTNAME])

        # Exercise (shot in squash) Goal
        elif goal_level == self.EXERCISE_GOAL:
            
        # Stat Goal
        elif goal_level == self.STAT_GOAL:
            return [self.policy.A_PREINSTRUCTION, self.policy.A_POSTINSTRUCTIONPOSITIVE,
                    self.policy.A_POSTINSTRUCTIONNEGATIVE, self.policy.A_QUESTIONING]

        # Set Goal
        elif goal_level == self.SET_GOAL:
            return [self.policy.A_PREINSTRUCTION, self.policy.A_POSTINSTRUCTIONPOSITIVE,
                    self.policy.A_POSTINSTRUCTIONNEGATIVE, self.policy.A_QUESTIONING]

        # Action Goal (each shot in squash or movement in rehab)
        else:  # goal_level == self.ACTION_GOAL:
            return [self.policy.A_SILENCE, self.policy.A_PRAISE, self.policy.A_CONCURRENTINSTRUCTIONNEGATIVE,
                    self.policy.A_CONCURRENTINSTRUCTIONPOSITIVE, self.policy.A_SCOLD, self.policy.A_HUSTLE,
                    self.policy.A_CONSOLE]

        return valid_list
