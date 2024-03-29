SHOT_CHOICE = 0
STAT_CHOICE = 1

CHOICE_BY_PERSON = 0
CHOICE_BY_SYSTEM = 1

MAX_SESSION_TIME = 1680  # 1800 seconds is 30 minutes so set to 2 minutes left to give time for tidying up.

COMPLETED_STATUS_UNDEFINED = -1
COMPLETED_STATUS_FALSE = 0
COMPLETED_STATUS_TRUE = 1

Q_RESPONSE_POSITIVE = 1
Q_RESPONSE_NEGATIVE = 0

# Goal Levels
PERSON_GOAL = 0
SESSION_GOAL = 1
EXERCISE_GOAL = 2
STAT_GOAL = 3
SET_GOAL = 4
ACTION_GOAL = 5
BASELINE_GOAL = 6

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

# ACTIONS
A_START = 0
A_PREINSTRUCTION = 1
A_CONCURRENTINSTRUCTIONPOSITIVE = 2
A_CONCURRENTINSTRUCTIONNEGATIVE = 3
A_POSTINSTRUCTIONPOSITIVE = 4
A_POSTINSTRUCTIONNEGATIVE = 5
A_MANUALMANIPULATION = 6
A_QUESTIONING = 7
A_POSITIVEMODELING = 8
A_NEGATIVEMODELING = 9
A_FIRSTNAME = 10
A_HUSTLE = 11
A_PRAISE = 12
A_SCOLD = 13
A_CONSOLE = 14
A_PREINSTRUCTION_MANUALMANIPULATION = 15
A_PREINSTRUCTION_QUESTIONING = 16
A_PREINSTRUCTION_POSITIVEMODELING = 17
A_PREINSTRUCTION_NEGATIVEMODELING = 18
A_PREINSTRUCTION_PRAISE = 19
A_CONCURRENTINSTRUCTIONPOSITIVE_QUESTIONING = 20
A_CONCURRENTINSTRUCTIONPOSITIVE_FIRSTNAME = 21
A_POSTINSTRUCTIONPOSITIVE_MANUALMANIPULATION = 22
A_POSTINSTRUCTIONPOSITIVE_QUESTIONING = 23
A_POSTINSTRUCTIONPOSITIVE_POSITIVE_MODELING = 24
A_POSTINSTRUCTIONPOSITIVE_NEGATIVE_MODELING = 25
A_POSTINSTRUCTIONPOSITIVE_FIRSTNAME = 26
A_POSTINSTRUCTIONNEGATIVE_MANUALMANIPULATION = 27
A_POSTINSTRUCTIONNEGATIVE_QUESTIONING = 28
A_POSTINSTRUCTIONNEGATIVE_POSITIVEMODELING = 29
A_POSTINSTRUCTIONNEGATIVE_NEGATIVEMODELING = 30
A_POSTINSTRUCTIONNEGATIVE_PRAISE = 31
A_MANUALMANIPULATION_POSTINSTRUCTIONPOSITIVE = 32
A_MANUALMANIPULATION_POSTINSTRUCTIONNEGATIVE = 33
A_QUESTIONING_NEGATIVEMODELING = 34
A_QUESTIONING_FIRSTNAME = 35
A_POSITIVEMODELING_PREINSTRUCTION = 36
A_POSITIVEMODELING_POSTINSTRUCTIONPOSITIVE = 37
A_NEGATIVEMODELING_POSTINSTRUCTIONNEGATIVE = 38
A_HUSTLE_FIRSTNAME = 39
A_PRAISE_FIRSTNAME = 40
A_SCOLD_POSITIVEMODELING = 41
A_SCOLD_FIRSTNAME = 42
A_CONSOLE_FIRSTNAME = 43
A_PREINSTRUCTION_FIRSTNAME = 44
A_CONCURRENTINSTRUCTIONPOSITIVE_CONCURRENTINSTRUCTIONPOSITIVE = 45
A_CONCURRENTINSTRUCTIONPOSITIVE_MANUALMANIPULATION = 46
A_CONCURRENTINSTRUCTIONPOSITIVE_POSITIVEMODELING = 47
A_CONCURRENTINSTRUCTIONPOSITIVE_PRAISE = 48
A_CONCURRENTINSTRUCTIONNEGATIVE_MANUALMANIPULATION = 49
A_CONCURRENTINSTRUCTIONNEGATIVE_NEGATIVEMODELING = 50
A_CONCURRENTINSTRUCTIONNEGATIVE_FIRSTNAME = 51
A_POSTINSTRUCTIONNEGATIVE_FIRSTNAME = 52
A_MANUALMANIPULATION_PREINSTRUCTION = 53
A_MANUALMANIPULATION_CONCURRENTINSTRUCTIONPOSITIVE = 54
A_MANUALMANIPULATION_CONCURRENTINSTRUCTIONNEGATIVE = 55
A_MANUALMANIPULATION_QUESTIONING = 56
A_MANUALMANIPULATION_POSITIVEMODELING = 57
A_MANUALMANIPULATION_FIRSTNAME = 58
A_MANUALMANIPULATION_HUSTLE = 59
A_MANUALMANIPULATION_PRAISE = 60
A_MANUALMANIPULATION_CONSOLE = 61
A_QUESTIONING_POSITIVEMODELING = 62
A_POSITIVEMODELING_CONCURRENTINSTRUCTIONPOSITIVE = 63
A_POSITIVEMODELING_QUESTIONING = 64
A_POSITIVEMODELING_HUSTLE = 65
A_POSITIVEMODELING_PRAISE = 66
A_END = 67
A_SILENCE = 68

SHOTS_PER_SET = 30
SETS_PER_STAT = 2
STATS_PER_SHOT = 2

shot_list_master = {"drop": 0,
                    "drive": 1,
                    "cross court lob": 14,
                    "two wall boast": 7,
                    "straight kill": 16,
                    "volley kill": 17,
                    "volley drop": 18}
shot_list_importance = {
    "drop": 4.0,
    "drive": 3.75,
    "cross court lob": 3.0,
    "two wall boast": 2.5,
    "straight kill": 2.0,
    "volley kill": 2.0,
    "volley drop": 1.75
}
stat_list = {}

# Initial values which will be updated when the API gets called by the guide.
goal_level = -1
sessions = -1
score = -1
target = -1
avg_score = -1
performance = None
completed = COMPLETED_STATUS_UNDEFINED
shot_count = 0
action_score = -1
prev_behav = -1
matching_behav = 0
phase = PHASE_START
session_time = 0
used_behaviours = []
set_performance_list = []  # 1 entry for each rep performed
set_score_list = []  # 1 entry for each rep performed
stat_performance_list = []  # 1 entry for each set performed for that stat
stat_score_list = []  # 1 entry for each set performed for that stat
shot_performance_list = []  # 1 entry for each stat worked on
shot_score_list = []  # 1 entry for each stat worked on
session_performance_list = []  # 1 entry for each shot performed
session_score_list = []  # 1 entry for each shot performed
set_count = 0
stat_count = 0
given_score = 0
# shot_list_session = ["Forehand Drive", "Backhand Drive", "Forehand Drop"]  # Delete from this list once the exercise has been completed in the session.
used_shots = []
used_stats = []
start_time = None
observation = -1
has_score_been_provided = True  # True if Pepper has already said e.g. "Your average score was 3.02 and your were aiming for 2.0" and False otherwise.
scores_provided = 0  # Add 1 each time a score is given in feedback. Reset to 0 at the completion of each goal.
behaviour_displayed = False  # Set to true in DisplayBehaviour node to indicate to the environment that a new action is needed from the policy.
repetitions = -1
stop_session = False
stop_set = False
metric_score_list = {}  # The scores for each of the 6 stats we are measuring in the baseline set.
metric_performance_list = []  # The performances of the 6 stats we are measuring in the baseline set.
override = None  # Will be True if user decides to override the policy's decision to choose/question about shot/stat options. False if they decide not to.
overriden = False  # Indicates whether an override has already occured at this goal level (no point asking if the user wants to override again).
overridePreInstructionOption = False  # Will be set to True when user is being given the option to override a pre-instruction
overrideQuestioningOption = False     # so that the correct screen can be displayed.
getBehaviourGoalLevel = -1  # To keep track of which level the controller is in when getting a new behaviour from the policy.
question_response = None
feedback_question = False
action_score_given = False
cumulative_reward = 0

# Variables to deal with rewards:
set_level_behaviours = []
stat_level_behaviours = []
shot_level_behaviours = []
session_level_behaviours = []
person_level_behaviours = []
set_finished = False
stat_finished = False
shot_finished = False
session_finished = False
person_finished = False

# Initial values which will be updated when the API gets called by the guide.
expecting_action_goal = False
stat_confirmed = False  # Becomes true when stat goal is created with chosen stat, reset to false on end stat goal.
shot_confirmed = False  # Becomes true when shot goal is created with chosen shot, reset to false on end shot goal.
dont_send_action_response = False  # Whether or not to send the response to the action goal (i.e. if we have completed the set, do not send it).
given_stat_explanation = False  # We don't want to keep giving an explanation of what the same stat means. This will prevent that.
session_goal_created = False  # Used to keep track of whether or not we have already created the session/shot goal when we choose a new shot/stat
shot_goal_created = False
shots_dealt_with = []  # Add element to list every time a shot comes through from the app. Remove from the list when we send a response to the shot. Cannot send any other response to another goal level while this list has elements in it.
tidied_up = False  # Variable to check whether we are ready to end the session (i.e. have given feedback for all completed sets/stats/shots and written all appropriate data to file.
tidying = False
session_stop_utterance_given = False  # Used to track whether we have already told the user that's the end of the session.
finished_stat = False  # Used to track whether we can safely end the session because the stat goal will have been finished.
# TODO: ^ May need to do the same for sets ^
pause_display = False  # Set to True when the user has selected to end the session early. At this point we will skip to session goal before displaying any more behaviours.
# pre_instr_recursion_counter = 0  # Used when dealing with override
# questioning_recursion_counter = 0
targetList = {}
accuracy = None  # Stores accuracy for a stat from sensor data, to update the baseline file at the end of each stat.
doneBaselineGoal = False
stop_on_baseline = False
stop_session_on_baseline = False
during_baseline_goal = False
finish_session_baseline_stop = False
end_session_stat = None
expecting_double_set = False
double_set_count_feedback = 0
double_set_count_start = 0

# Initial values to be changed at the beginning of each session:
name = "Pepper"
participantNo = "Default."
participant_filename = participantNo + "_history.txt"
ability = 2
motivation = 8
# 1 = DRIVE, 5 = LOB, 0 = DROP
shot = None
# "FH" or "BH"
hand = None
# "racketPreparation" = RACKET_PREP, "impactCutAngle" = IMPACT_CUT_ANGLE, "followThroughTime" = FOLLOW_THROUGH_TIME
stat = None
policy = 11
leftHand = False

# Values for RL
alpha = 0.3
gamma = 0.7
lambdaValue = 0.6
epsilon = -1
policy_matrix = None

# Robot through Peppernet router\:
# post_address = 'http://192.168.1.237:4999/output'

# Simulation on 4G:
# post_address = 'http://192.168.43.19:4999/output'

# Simulation on home wifi:
# post_address = 'http://192.168.1.174:4999/output'
# screen_post_address = "http://192.168.1.174:8000/"

# Robot through ITT Pepper router:
post_address = "http://192.168.1.207:4999/output"
screen_post_address = "http://192.168.1.207:8000/"

# Robot through hotspot:
# post_address = "http://192.168.43.19:4999/output"

# Dusty on HRI lab 5G:
# post_address = "http://192.168.1.115:4999/output"
# screen_post_address = "http://192.168.1.115:8000/"

behaviour = -1
need_new_behaviour = False
