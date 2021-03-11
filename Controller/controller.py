from Policy.policy_wrapper import PolicyWrapper


class Controller:

    def __init__(self):
        # Create API object
        self.API = get_api()

        self.standard = API.get_user_standard()
        self.relationship = API.get_user_sessions()
        self.goal_level = Policy.PERSON_GOAL

    def timestep_cue(self, state, goal_level, performance, phase, shot, stat, score, target):
        if not (goal_level == PolicyWrapper.ACTION_GOAL):
            while
