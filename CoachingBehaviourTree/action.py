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

    def __str__(self):
        """
        Format the output of the data stored in this instance of Action.
        :return:type str: the complete formatted utterance.
        """
        if self.score is not None and not self.goal == config.ACTION_GOAL:
            if self.stat_explanation is not None:
                return f'{self.pre_msg}. You got an average score of {round(self.score, 2)}' + self.stat_measure + f' and were aiming for {round(self.target, 2)}' + self.stat_measure + '. ' + self.stat_explanation
            else:
                return f'{self.pre_msg}. You got an average score of {round(self.score, 2)}' + self.stat_measure + f' and were aiming for {round(self.target, 2)}' + self.stat_measure + '.'
            '''if self.goal is not config.ACTION_GOAL:
                # TODO: add score-specific utterance (e.g. seconds, degrees) to explain the score better to the user.
                print("ACTION, self.score = " + str(self.score))
                print("ACTION, self.target = " + str(self.target))
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
                        print("ACTION, Phase Start, already given stat explanation")
                        return returnString
                    else:
                        print("ACTION, Phase Start, giving stat explanation now")
                        return returnString + stat_explanation
                else:
                    returnString = f'{self.pre_msg}. You got an average score of {round(self.score, 2)}' + stat_measure + f' and were aiming for {round(self.target, 2)}' + stat_measure + '. '
                    if config.given_stat_explanation:
                        print("ACTION, Phase End, already given stat explanation")
                        return returnString
                    else:
                        print("ACTION, Phase End, giving stat explanation now")
                        config.given_stat_explanation = True
                        return returnString + stat_explanation'''
        else:

            return f'{self.pre_msg}'
