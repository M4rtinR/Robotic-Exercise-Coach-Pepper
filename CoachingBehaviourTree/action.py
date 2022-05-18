from dataclasses import dataclass

from CoachingBehaviourTree import controller
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
    demo: str = None
    question: str = None
    goal: int = None

    def __str__(self):
        """
        Format the output of the data stored in this instance of Action.
        :return:type str: the complete formatted utterance.
        """
        if self.score is not None and controller.has_score_been_provided is False:
            if self.goal is not PolicyWrapper.ACTION_GOAL:
                return f'{self.pre_msg} You got an average time of {round(self.score, 2)} seconds and were aiming for {round(self.target, 2)} seconds.'

        return f'{self.pre_msg}'
