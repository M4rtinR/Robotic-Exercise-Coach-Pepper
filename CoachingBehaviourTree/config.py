SHOT_CHOICE = 0
MAX_SESSION_TIME = 4

COMPLETED_STATUS_UNDEFINED = -1
COMPLETED_STATUS_FALSE = 0
COMPLETED_STATUS_TRUE = 1

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

shot_list_master = ["Forehand Drive", "Backhand Drive", "Forehand Drop"]

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
given_score = 0
shot_list_session = ["Forehand Drive", "Backhand Drive", "Forehand Drop"]  # Delete from this list once the exercise has been completed in the session.
used_shots = []
start_time = None
observation = -1
has_score_been_provided = True  # True if Pepper has already said e.g. "Your average score was 3.02 and your were aiming for 2.0" and False otherwise.
scores_provided = 0  # Add 1 each time a score is given in feedback. Reset to 0 at the completion of each goal.
behaviour_displayed = False  # Set to true in DisplayBehaviour node to indicate to the environment that a new action is needed from the policy.
repetitions = -1
stop_session = False
stop_set = False

# Initial values to be changed at the beginning of each session:
name = "Martin"
participantNo = "Testing.0"
participant_filename = participantNo + "_history.txt"
ability = 4
motivation = 8
# 1 = DRIVE, 5 = LOB, 0 = DROP
shot = 0
# "FH" or "BH"
hand = "FH"
# "racketPreparation" = RACKET_PREP, "impactCutAngle" = IMPACT_CUT_ANGLE, "followThroughTime" = FOLLOW_THROUGH_TIME
stat = "impactCutAngle"
policy = 11
leftHand = True

# Values for RL
alpha = 0.85
gamma = 0.95
policy_matrix = None

# Robot through Peppernet router:
# post_address = 'http://192.168.1.237:4999/output'

# Simulation on 4G:
# post_address = 'http://192.168.43.19:4999/output'
# post_address = 'http://192.168.1.174:4999/output'

# Robot through ITT Pepper router:
post_address = "http://192.168.1.207:4999/output"
screen_post_address = "http://192.168.1.207:8000/"

# Robot through hotspot:
# post_address = "http://192.168.43.19:4999/output"

behaviour = -1
need_new_behaviour = False
