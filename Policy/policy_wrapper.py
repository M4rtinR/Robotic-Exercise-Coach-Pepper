import logging

from Policy.policy import Policy


class PolicyWrapper:
    """
    A class which acts as an interface between the raw policy and the behaviour tree. It can give the tree a behaviour
    or observation generated by the policy which is within a set of defined valid behaviours for a given state.
    ...
    Attributes
    ----------
    Goal Levels :type int
        6 different goal levels which correspond to stages in the interaction and the goal hierarchy of the racketware
        guide.
    Phases :type int
        2 different phases (start and end) which correspond respectively to either an intro or feedback sequence.
    Performance Levels :type int
        8 different performance levels which represent how the user did in their previous action.
    policy
        The policy we will query to obtain behaviours and observations.

    Methods
    -------
    get_behaviour(state, goal_level, performance, phase)
        Obtain a behaviour from the underlying policy and check it is valid in the current state of interaction.
    _get_valid_list(goal_level, performance, phase)
        Local method which creates the list of valid for each state of interaction.
    get_observation(state, behaviour)
        Obtain an observation from the underlying policy.
    """
    def __init__(self, belief):
        self.policy = Policy(belief)

    # Goal Levels
    PERSON_GOAL = 0
    SESSION_GOAL = 1
    EXERCISE_GOAL = 2
    SET_GOAL = 3
    ACTION_GOAL = 4

    # Phases
    PHASE_START = 0
    PHASE_END = 1

    # Performance Levels
    GOOD = 0            # Timing was within 0.5 secs either side of optimal
    FAST = 1            # Timing was <= optimal - 0.5secs
    SLOW = 2            # Timing was >= optimal + 0.5secs

    def get_behaviour(self, state, goal_level, performance, phase):
        """
        Obtain a behaviour from the underlying policy and check it is valid in the current state of interaction.
        :param state :type int: the previously observed state.
        :param goal_level :type int: the current goal level of the interaction.
        :param performance :type int: the performance of the user on their last action.
        :param phase :type int: the phase of the current goal level (either intro or feedback).
        :return behaviour :type int: the behaviour generated by the policy.
        """
        if goal_level == self.ACTION_GOAL:
            logging.debug("Action goal")
            logging.debug("performance = ", performance)

        valid_behaviours = self._get_valid_list(goal_level, performance, phase)
        behaviour = self.policy.sample_action(state)
        # obs_behaviour = behaviour
        count = 0
        if goal_level == self.ACTION_GOAL:
            logging.debug("behaviour = ", behaviour, ". valid_behaviours: ", valid_behaviours)

        while not(behaviour in valid_behaviours):
            logging.debug("Not valid behaviour")
            if goal_level == self.ACTION_GOAL:     # If between shots, silence is an appropriate action so each time a
                behaviour = self.policy.A_SILENCE  # non-valid action is proposed, just use silence.
            else:
                if count <= 10:  # Only try this 10 times and if still no valid behaviour, try the next behaviour in the action sequence.
                    logging.debug("PolicyWrapper <= 10")
                    behaviour = self.policy.sample_action(state)
                else:
                    logging.debug("PolicyWrapper > 10")
                    # TODO: Remove this if else and figure out what's going on with centroids.
                    if behaviour == self.policy.A_MANUALMANIPULATION_QUESTIONING:
                        behaviour = self.policy.A_QUESTIONING
                    elif behaviour == self.policy.A_MANUALMANIPULATION_PREINSTRUCTION \
                            or behaviour == self.policy.A_PREINSTRUCTION_MANUALMANIPULATION:
                        behaviour = self.policy.A_PREINSTRUCTION
                    elif behaviour == self.policy.A_MANUALMANIPULATION_POSITIVEMODELING:
                        behaviour = self.policy.A_POSITIVEMODELING
                    elif behaviour == self.policy.A_MANUALMANIPULATION_CONCURRENTINSTRUCTIONNEGATIVE \
                            or behaviour == self.policy.A_CONCURRENTINSTRUCTIONNEGATIVE_MANUALMANIPULATION:
                        behaviour = self.policy.A_CONCURRENTINSTRUCTIONNEGATIVE
                    elif behaviour == self.policy.A_MANUALMANIPULATION_CONCURRENTINSTRUCTIONPOSITIVE \
                            or behaviour == self.policy.A_CONCURRENTINSTRUCTIONPOSITIVE_MANUALMANIPULATION:
                        behaviour = self.policy.A_CONCURRENTINSTRUCTIONPOSITIVE
                    elif behaviour == self.policy.A_MANUALMANIPULATION_CONSOLE:
                        behaviour = self.policy.A_CONSOLE
                    elif behaviour == self.policy.A_MANUALMANIPULATION_FIRSTNAME:
                        behaviour = self.policy.A_FIRSTNAME
                    elif behaviour == self.policy.A_MANUALMANIPULATION_HUSTLE:
                        behaviour = self.policy.A_HUSTLE
                    elif behaviour == self.policy.A_MANUALMANIPULATION_POSTINSTRUCTIONNEGATIVE \
                            or behaviour == self.policy.A_POSTINSTRUCTIONNEGATIVE_MANUALMANIPULATION:
                        behaviour = self.policy.A_POSTINSTRUCTIONNEGATIVE
                    elif behaviour == self.policy.A_MANUALMANIPULATION_POSTINSTRUCTIONPOSITIVE \
                            or behaviour == self.policy.A_POSTINSTRUCTIONPOSITIVE_MANUALMANIPULATION:
                        behaviour = self.policy.A_POSTINSTRUCTIONPOSITIVE
                    elif behaviour == self.policy.A_MANUALMANIPULATION_PRAISE:
                        behaviour = self.policy.A_PRAISE
                    else:
                        if behaviour == self.policy.A_END:  # If behaviour == end then start from start again.
                            behaviour = self.policy.A_START
                        state = self.policy.sample_observation(action=behaviour, state=state)
                        behaviour = self.policy.sample_action(state)
                        count = 0
                count += 1

        return behaviour  #, obs_behaviour

    def _get_valid_list(self, goal_level, performance, phase):
        """
        Local method which creates the list of valid for each state of interaction.
        :param goal_level :type int: the current goal level of the interaction.
        :param performance :type int: the performance of the user on their last action.
        :param phase :type int: the phase of the current goal level (either intro or feedback).
        :return valid_list :type list[int]: a list of valid behaviours in the current interaction state.
        """
        valid_list = []

        logging.debug('goal_level = ' + str(goal_level))
        # Person Goal
        if goal_level == self.PERSON_GOAL:
            logging.debug('Creating list for person goal')
            valid_list.extend([self.policy.A_PREINSTRUCTION, self.policy.A_PREINSTRUCTION_FIRSTNAME])

        # Session, Exercise and Set Goals will all have the same action categories (different individual actions)
        elif goal_level == self.SESSION_GOAL or goal_level == self.EXERCISE_GOAL or goal_level == self.SET_GOAL:
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
                if performance == self.GOOD:
                    valid_list.extend([self.policy.A_PRAISE, self.policy.A_PRAISE_FIRSTNAME,
                                       self.policy.A_POSITIVEMODELING_PRAISE])
                    valid_list.extend([self.policy.A_PRAISE, self.policy.A_PRAISE_FIRSTNAME,
                                       self.policy.A_POSITIVEMODELING_PRAISE])
                elif performance == self.SLOW or performance == self.FAST:
                    valid_list.extend([self.policy.A_SCOLD, self.policy.A_CONSOLE, self.policy.A_SCOLD_FIRSTNAME,
                                       self.policy.A_CONSOLE_FIRSTNAME])
            else:  # phase == self.PHASE_END
                if goal_level == self.SESSION_GOAL:
                    valid_list.append(self.policy.A_END)
                if performance == self.GOOD:
                    valid_list.extend([self.policy.A_PRAISE, self.policy.A_PRAISE_FIRSTNAME,
                                       self.policy.A_POSITIVEMODELING_PRAISE])
                elif performance == self.SLOW or performance == self.FAST:
                    valid_list.extend([self.policy.A_SCOLD, self.policy.A_CONSOLE, self.policy.A_SCOLD_FIRSTNAME,
                                       self.policy.A_CONSOLE_FIRSTNAME])

        # Action Goal (each shot in squash or repetition of exercise in rehab)
        else:  # goal_level == self.ACTION_GOAL:
            valid_list.extend([self.policy.A_SILENCE, self.policy.A_CONCURRENTINSTRUCTIONPOSITIVE,
                               self.policy.A_QUESTIONING, self.policy.A_POSITIVEMODELING, self.policy.A_HUSTLE,
                               self.policy.A_CONCURRENTINSTRUCTIONPOSITIVE_QUESTIONING,
                               self.policy.A_CONCURRENTINSTRUCTIONPOSITIVE_FIRSTNAME,
                               self.policy.A_QUESTIONING_FIRSTNAME, self.policy.A_HUSTLE_FIRSTNAME,
                               self.policy.A_CONCURRENTINSTRUCTIONPOSITIVE_POSITIVEMODELING,
                               self.policy.A_POSITIVEMODELING_HUSTLE,
                               self.policy.A_POSITIVEMODELING_CONCURRENTINSTRUCTIONPOSITIVE])
            # No phases in action goals, just a behaviour after each shot.
            if performance == self.GOOD:
                valid_list.extend([self.policy.A_PRAISE, self.policy.A_PRAISE_FIRSTNAME,
                                   self.policy.A_CONCURRENTINSTRUCTIONPOSITIVE_PRAISE,
                                   self.policy.A_POSITIVEMODELING_PRAISE])
            elif performance == self.SLOW or performance == self.FAST:
                valid_list.extend([self.policy.A_CONCURRENTINSTRUCTIONNEGATIVE, self.policy.A_NEGATIVEMODELING,
                                   self.policy.A_SCOLD, self.policy.A_CONSOLE,
                                   self.policy.A_QUESTIONING_NEGATIVEMODELING, self.policy.A_SCOLD_POSITIVEMODELING,
                                   self.policy.A_SCOLD_FIRSTNAME, self.policy.A_CONSOLE_FIRSTNAME,
                                   self.policy.A_CONCURRENTINSTRUCTIONNEGATIVE_NEGATIVEMODELING,
                                   self.policy.A_CONCURRENTINSTRUCTIONNEGATIVE_FIRSTNAME,])

        return valid_list

    def get_observation(self, state, behaviour):
        """
        Obtain an observation from the underlying policy.
        :param state :type int: the previously observed state.
        :param behaviour :type int: the previous behaviour generated by the policy.
        :return:type int: the observation of which state we have moved to, generated by the policy.
        """
        return self.policy.sample_observation(state, behaviour)
