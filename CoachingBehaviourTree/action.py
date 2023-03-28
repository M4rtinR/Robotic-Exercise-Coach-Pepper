from dataclasses import dataclass

from CoachingBehaviourTree import controller, config
from Policy.policy_wrapper import PolicyWrapper


@dataclass
class Action:
    """
    Data class for storing information about an action which will be performed by the robot.
    ...
    Attributes
    ----------
    pre_msg :type str
        The utterance to be spoken by the robot before giving the score information.
    score :type float
        The score given by the guide for the action just performed by the user.
    target :type float
        The target score the user was aiming for in the last action they performed.
    post_msg :type str
        The utterance to be spoken by the robot after giving the score information.

    Methods
    -------
    __str__()
        Format the output of the data stored in this instance of Action.
    """
    pre_msg: str
    score: float = None
    target: float = None
    post_msg: str = None
    # has_score_been_provided: bool = False
    demo: str = None
    question: str = None
    goal: int = None
    stat_measure: str = None
    stat_explanation: str = None
    shot: str = None
    hand: str = None
    stat_count: int = 0
    ending: bool = False

    def __str__(self):
        """
        Format the output of the data stored in this instance of Action.
        :return:type str: the complete formatted utterance.
        """
        if self.score is not None and isinstance(self.score, float) and not self.goal == config.ACTION_GOAL:
            if self.goal > config.EXERCISE_GOAL:
                if self.stat_explanation is not None:
                    return f'{self.pre_msg}. Your baseline score is {round(self.score, 2)}' + self.stat_measure + f' and you are aiming for {round(self.target, 2)}' + self.stat_measure + '. ' + self.stat_explanation
                else:
                    return f'{self.pre_msg}. You got an average score of {round(self.score, 2)}' + self.stat_measure + f' and were aiming for {round(self.target, 2)}' + self.stat_measure + '.'
            else:
                if self.goal == config.EXERCISE_GOAL:
                    if self.stat_count < config.STATS_PER_SHOT:
                        return f'{self.pre_msg}. You\'ve got an average accuracy of {round(self.score, 2)} out of 5 so far for your {"backhand" if self.hand == "BH" else "forehand"} {self.shot}s today.'
                    else:
                        return f'{self.pre_msg}. You got an average accuracy of {round(self.score, 2)} out of 5 for your {"backhand" if self.hand == "BH" else "forehand"} {self.shot}s today.'
                else:
                    if not self.ending:
                        return f'{self.pre_msg}. So far, you\'ve had an average accuracy of {round(self.score, 2)} out of 5 for all of your shots combined today.'
                    else:
                        return f'{self.pre_msg}. You got an average accuracy of {round(self.score, 2)} out of 5 for all of your shots combined today.'

            '''if self.goal is not config.ACTION_GOAL:
                # TODO: add score-specific utterance (e.g. seconds, degrees) to explain the score better to the user.
                logging.debug("ACTION, self.score = " + str(self.score))
                logging.debug("ACTION, self.target = " + str(self.target))
                if self.stat == "racketPreparation" or self.stat == "approachTiming":
                    stat_measure = "%"
                    if self.stat == "racketPreparation":
                        stat_explanation = "The % relates to how high your racket gets before you hit the ball. Generally, the higher the better!"
                    else:
                        stat_explanation = "The % relates to how well you have timed your swing to the ball. Generally, the higher the percentage, the better!"
                elif self.stat == "impactCutAngle" or self.stat == "followThroughRoll":
                    stat_measure = " degrees"
                    if self.stat == "impactCutAngle":
                        stat_explanation = "This is the angle of your racket face at contact."
                    else:
                        stat_explanation = "This relates to how much you roll your wrist over after hitting the ball."
                elif self.stat == "impactSpeed":
                    stat_measure = ""
                    stat_explanation = "This is the velocity of your racket as your strike the ball."
                else:  # followThroughTime
                    stat_measure = " seconds"
                    stat_explanation = "This is a measure of how long it takes between hitting the ball and your swing stopping."

                if self.phase == config.PHASE_START:
                    returnString = f'{self.pre_msg}. In the last set you got an average score of {round(self.score, 2)}' + stat_measure + f' and were aiming for {round(self.target, 2)}' + stat_measure + '. '
                    if config.given_stat_explanation:
                        logging.debug("ACTION, Phase Start, already given stat explanation")
                        return returnString
                    else:
                        logging.debug("ACTION, Phase Start, giving stat explanation now")
                        return returnString + stat_explanation
                else:
                    returnString = f'{self.pre_msg}. You got an average score of {round(self.score, 2)}' + stat_measure + f' and were aiming for {round(self.target, 2)}' + stat_measure + '. '
                    if config.given_stat_explanation:
                        logging.debug("ACTION, Phase End, already given stat explanation")
                        return returnString
                    else:
                        logging.debug("ACTION, Phase End, giving stat explanation now")
                        config.given_stat_explanation = True
                        return returnString + stat_explanation'''
        else:

            return f'{self.pre_msg}'
