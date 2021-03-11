from dataclasses import dataclass


@dataclass
class Action:
    pre_msg: str
    score: float
    target: float
    post_msg: str

    def __str__(self):
        if self.score is not None:
            return f'{self.pre_msg} You got a score of {self.score} and were aiming for {self.target}. {self.post_msg}'
        else:
            return f'{self.pre_msg}'
