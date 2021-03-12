from task_behavior_engine.node import Node
from Policy.policy import Policy


class CoachingTree(Node):
    def __init__(self, name, *args, **kwargs):
        run_cb = self.run
        configure_cb = self.configure
        cleanup_cb = self.cleanup

    def configure(self):
        # Create API object
        self.API = get_api()

        self.standard = API.get_user_standard()
        self.relationship = API.get_user_sessions()
        self.goal_level = Policy.PERSON_GOAL

    def run(self):

        return -1

    def cleanup(self):

        self.goal_level = Policy.PERSON_GOAL
