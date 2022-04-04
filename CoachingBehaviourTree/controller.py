"""Controller

This script is where the main behaviour tree skeleton is created and where the main method which ticks through the tree
can be found.
...
Methods
-------
create_coaching_tree()
    Responsible for creating the main Behaviour Tree structure.
get_feedback_loop(name, behav)
    Creates a subtree which gives feedback at a given goal level.
__main__()
    Creates the behaviour tree and ticks through it until it completes.
"""
import threading
import time
import logging

from task_behavior_engine.branch import Sequencer, Selector, Progressor, Runner
from task_behavior_engine.decorator import Until, While, Negate, Repeat, UntilCount, Succeed
from task_behavior_engine.tree import NodeStatus, Blackboard

from API import api_classes
from CoachingBehaviourTree.nodes import FormatAction, DisplayBehaviour, CheckForBehaviour, GetBehaviour, GetStats, \
    GetDuration, CreateSubgoal, TimestepCue, DurationCheck, GetUserChoice, EndSetEvent, InitialiseBlackboard, \
    EndSubgoal, OperatorInput
from Policy.policy import Policy
from Policy.policy_wrapper import PolicyWrapper

SHOT_CHOICE = 0

COMPLETED_STATUS_UNDEFINED = -1
COMPLETED_STATUS_FALSE = 0
COMPLETED_STATUS_TRUE = 1

exercise_list_master = ["Table top circles", "Towel slide", "External rotation with cane", "Shoulder openers"]

# Initial values which will be updated when the API gets called by the guide.
goal_level = 0
sessions = -1
score = -1
target = -1
avg_score = -1
performance = None
completed = COMPLETED_STATUS_UNDEFINED
exercise_count = 0
action_score = -1
prev_behav = -1
matching_behav = 0
phase = PolicyWrapper.PHASE_START
session_time = 0
used_behaviours = []
set_performance_list = []  # 1 entry for each rep performed
set_score_list = []  # 1 entry for each rep performed
exercise_performance_list = []  # 1 entry for each set performed of that exercise
exercise_score_list = []  # 1 entry for each set performed of that exercise
session_performance_list = []  # 1 entry for each exercise performed
session_score_list = []  # 1 entry for each exercise performed
set_count = 0
given_score = 0
exercise_list_session = ["Table top circles", "Towel slide", "External rotation with cane", "Shoulder openers"]  # Delete from this list once the exercise has been completed in the session.
start_time = None

# Initial values to be changed at the beginning of each session:
name = "Martin"
participantNo = "Testing.0"
participant_filename = participantNo + "_history"
impairment = 0
motivation = 8
exercise = -1
policy = 2

def create_coaching_tree():
    """
    Responsible for creating the main Behaviour Tree structure.
    :return:type: Progressor: the root node of the created behaviour tree.
    """
    # global performance
    b = Blackboard()
    root = Progressor("coaching root", blackboard=b)

    # Player stats
    user_stats = GetStats(name="user_stats", blackboard=b)
    player_stats_until = Until(name="player_stats_until", child=user_stats)
    root.add_child(player_stats_until)

    user_start = TimestepCue(name="user_start", blackboard=b)
    root.add_child(user_start)
    b.save('goal', -1, user_start._id)

    initialise = InitialiseBlackboard(name="initialise_blackboard", blackboard=b)
    root.add_child(initialise)

    # Share data between user_stats and initialise nodes.
    b.save('name', name, initialise._id)
    b.add_remapping(user_stats._id, 'motivation', initialise._id, 'motivation')
    b.save('user_impairment', impairment, initialise._id)
    b.add_remapping(user_start._id, 'sessions', initialise._id, 'sessions')

    # Session duration
    #TODO: needs updated when the user will choose actual time rather than just once through the exercises for the purposes of study 1.
    duration = GetDuration(name="duration", blackboard=b)
    root.add_child(duration)
    b.save('session_duration', 4, duration._id)  # Set session duration to 4 so that 4 exercises happen.
    b.save('start_time', 0, duration._id)

    # Add an intro and feedback loop for player goal.
    gen_person_goal = Progressor(name="gen_person_goal")
    #
    #
    # Create session goal in guide
    #
    #
    person_goal = CreateSubgoal(name="create_person_goal", blackboard=b)
    gen_person_goal.add_child(person_goal)

    #
    #
    # Display pre-instruction behaviour
    #
    #
    person_goal_intro_sequence = Progressor(name="person_goal_intro_sequence")  # Different from other intro sequences so don't use abstracted method.

    # Get behaviour from policy
    person_goal_intro_behav = GetBehaviour(name="person_goal_intro_behaviour", blackboard=b)
    person_goal_intro_sequence.add_child(person_goal_intro_behav)

    # Share data between initialise, session_goal_start, and session_goal_intro_behav.
    b.add_remapping(initialise._id, 'belief', person_goal_intro_behav._id, 'belief')
    b.add_remapping(initialise._id, 'state', person_goal_intro_behav._id, 'state')
    b.save('performance', performance, person_goal_intro_behav._id)
    b.add_remapping(user_start._id, 'phase', person_goal_intro_behav._id, 'phase')
    b.add_remapping(person_goal._id, 'new_goal', person_goal_intro_behav._id, 'goal')

    person_goal_intro_check_for_pre = CheckForBehaviour(name="person_goal_intro_check_for_pre", blackboard=b)
    b.save('check_behaviour', Policy.A_PREINSTRUCTION, person_goal_intro_check_for_pre._id)
    # Share behaviour between session_goal_intro_behav and session_goal_intro_check_for_pre.
    b.add_remapping(person_goal_intro_behav._id, 'behaviour', person_goal_intro_check_for_pre._id, 'behaviour')
    person_goal_intro_sequence.add_child(person_goal_intro_check_for_pre)

    # Format selected behaviour (i.e. create the output action)
    person_goal_intro_action = FormatAction(name="person_goal_intro_action", blackboard=b)
    person_goal_intro_sequence.add_child(person_goal_intro_action)

    # Share data between initialise, person_goal_start, person_goal, person_goal_intro_behav and person_goal_intro_action.
    b.add_remapping(initialise._id, 'bl', person_goal_intro_action._id, 'bl')
    b.save('performance', performance, person_goal_intro_action._id)
    b.add_remapping(user_start._id, 'phase', person_goal_intro_action._id, 'phase')
    b.add_remapping(person_goal._id, 'new_goal', person_goal_intro_action._id, 'goal')
    b.add_remapping(person_goal_intro_behav._id, 'behaviour', person_goal_intro_action._id, 'behaviour')
    b.add_remapping(user_start._id, 'name', person_goal_intro_action._id, 'name')

    # Display pre-instruction behaviour
    person_goal_intro_output = DisplayBehaviour(name="person_goal_intro_output", blackboard=b)
    person_goal_intro_sequence.add_child(person_goal_intro_output)
    # Share action between person_goal_intro_action and person_goal_intro_output.
    b.add_remapping(person_goal_intro_action._id, 'action', person_goal_intro_output._id, 'action')

    gen_person_goal.add_child(person_goal_intro_sequence)

    #
    #
    #
    # Conduct session
    #
    #
    #
    gen_session_goal, session_goal, session_goal_start, session_goal_exercise_choice, session_goal_intro_behav = get_intro_loop(name="session_goal_intro_loop", blackboard=b, prev_goal_node=person_goal._id, initialise_node=initialise._id, person_node=user_start._id)

    '''
    #
    #
    # Create session goal in guide
    #
    #
    session_goal = CreateSubgoal(name="create_session_goal", blackboard=b)
    gen_session_goal.add_child(session_goal)

    # Share data between person_goal and session_goal.
    b.add_remapping(person_goal._id, 'new_goal', session_goal._id, 'goal')

    #
    #
    # Wait for timestep cue (i.e. session goal has been created by guide and we are ready for intro.
    #
    #
    session_goal_start = TimestepCue(name="session_goal_started_timestep", blackboard=b)
    session_goal_start_until = Until(name="session_goal_start_until", child=session_goal_start)
    gen_session_goal.add_child(session_goal_start_until)
    b.add_remapping(session_goal._id, 'new_goal', session_goal_start._id, 'goal')

    #
    #
    # Display behaviours until pre-instruction or questioning
    #
    #
    session_goal_intro_sequence = Progressor(name="session_goal_intro_sequence")

    # Get behaviour from policy
    session_goal_intro_behav = GetBehaviour(name="session_goal_intro_behaviour", blackboard=b)
    session_goal_intro_sequence.add_child(session_goal_intro_behav)

    # Share data between initialise, session_goal_start, and session_goal_intro_behav.
    b.add_remapping(initialise._id, 'belief', session_goal_intro_behav._id, 'belief')
    b.add_remapping(initialise._id, 'state', session_goal_intro_behav._id, 'state')
    b.add_remapping(session_goal_start._id, 'performance', session_goal_intro_behav._id, 'performance')
    b.add_remapping(session_goal_start._id, 'phase', session_goal_intro_behav._id, 'phase')
    b.add_remapping(session_goal._id, 'new_goal', session_goal_intro_behav._id, 'goal')

    # Check if pre-instruction
    session_goal_intro_pre_instr_sequence = Progressor(name="session_goal_intro_pre_instruction_sequence")
    session_goal_intro_check_for_pre = CheckForBehaviour(name="session_goal_intro_check_for_pre", blackboard=b)
    b.save('check_behaviour', Policy.A_PREINSTRUCTION, session_goal_intro_check_for_pre._id)
    # Share behaviour between session_goal_intro_behav and session_goal_intro_check_for_pre.
    b.add_remapping(session_goal_intro_behav._id, 'behaviour', session_goal_intro_check_for_pre._id, 'behaviour')
    session_goal_intro_pre_instr_sequence.add_child(session_goal_intro_check_for_pre)
    # Format and display pre-instruction action.
    session_goal_intro_pre_instr_action = FormatAction(name="session_goal_intro_pre_instruction_action", blackboard=b)
    session_goal_intro_pre_instr_sequence.add_child(session_goal_intro_pre_instr_action)
    # Share data between initialise, session_goal_start, session_goal, session_goal_intro_behav and session_goal_intro_action.
    b.add_remapping(initialise._id, 'bl', session_goal_intro_pre_instr_action._id, 'bl')
    b.add_remapping(session_goal_start._id, 'performance', session_goal_intro_pre_instr_action._id, 'performance')
    b.add_remapping(session_goal_start._id, 'phase', session_goal_intro_pre_instr_action._id, 'phase')
    b.add_remapping(session_goal_start._id, 'score', session_goal_intro_pre_instr_action._id, 'score')
    b.add_remapping(session_goal_start._id, 'target', session_goal_intro_pre_instr_action._id, 'target')
    b.add_remapping(session_goal._id, 'new_goal', session_goal_intro_pre_instr_action._id, 'goal')
    b.add_remapping(session_goal_intro_behav._id, 'behaviour', session_goal_intro_pre_instr_action._id, 'behaviour')
    b.add_remapping(user_start._id, 'name', session_goal_intro_pre_instr_action._id, 'name')
    b.save('exercise', exercise, session_goal_intro_pre_instr_action._id)
    session_goal_intro_pre_instr_output = DisplayBehaviour(name="session_goal_intro_pre_instruction_output", blackboard=b)
    session_goal_intro_pre_instr_sequence.add_child(session_goal_intro_pre_instr_output)
    # Share action between session_goal_intro_action and session_goal_intro_output.
    b.add_remapping(session_goal_intro_pre_instr_action._id, 'action', session_goal_intro_pre_instr_output._id, 'action')
    session_goal_intro_pre_instr_negate = Negate(name="session_goal_intro_pre_instr_negate", child=session_goal_intro_pre_instr_sequence)
    session_goal_intro_sequence.add_child(session_goal_intro_pre_instr_negate)

    # Check if questioning
    session_goal_intro_questioning_sequence = Progressor(name="session_goal_intro_questioning_sequence")
    session_goal_intro_check_for_questioning = CheckForBehaviour(name="session_goal_intro_check_for_questioning", blackboard=b)
    b.save('check_behaviour', Policy.A_QUESTIONING, session_goal_intro_check_for_questioning._id)
    # Share behaviour between session_goal_intro_behav and session_goal_intro_check_for_questioning.
    b.add_remapping(session_goal_intro_behav._id, 'behaviour', session_goal_intro_check_for_questioning._id, 'behaviour')
    session_goal_intro_questioning_sequence.add_child(session_goal_intro_check_for_questioning)
    session_goal_shot_choice = GetUserChoice(name="session_goal_shot_choice", blackboard=b)
    b.save('choice_type', SHOT_CHOICE, session_goal_shot_choice._id)
    session_goal_intro_questioning_sequence.add_child(session_goal_shot_choice)
    session_goal_intro_questioning_negate = Negate(name="session_goal_intro_questioning_negate", child=session_goal_intro_questioning_sequence)
    session_goal_intro_sequence.add_child(session_goal_intro_questioning_negate)

    # Format selected behaviour if not pre-instruction or questioning (i.e. create the output action)
    session_goal_intro_action = FormatAction(name="session_goal_intro_action", blackboard=b)
    session_goal_intro_sequence.add_child(session_goal_intro_action)

    # Share data between initialise, session_goal_start, session_goal, session_goal_intro_behav and session_goal_intro_action.
    b.add_remapping(initialise._id, 'bl', session_goal_intro_action._id, 'bl')
    b.add_remapping(session_goal_start._id, 'performance', session_goal_intro_action._id, 'performance')
    b.add_remapping(session_goal_start._id, 'phase', session_goal_intro_action._id, 'phase')
    b.add_remapping(session_goal_start._id, 'score', session_goal_intro_action._id, 'score')
    b.add_remapping(session_goal_start._id, 'target', session_goal_intro_action._id, 'target')
    b.add_remapping(session_goal._id, 'new_goal', session_goal_intro_action._id, 'goal')
    b.add_remapping(session_goal_intro_behav._id, 'behaviour', session_goal_intro_action._id, 'behaviour')
    b.add_remapping(user_start._id, 'name', session_goal_intro_action._id, 'name')
    b.save('exercise', exercise, session_goal_intro_action._id)


    # Display selected behaviour if not pre-instruction or questioning
    session_goal_intro_output = DisplayBehaviour(name="session_goal_intro_output", blackboard=b)
    session_goal_intro_sequence.add_child(session_goal_intro_output)
    # Share action between session_goal_intro_action and session_goal_intro_output.
    b.add_remapping(session_goal_intro_action._id, 'action', session_goal_intro_output._id, 'action')

    session_goal_intro_while = While(name="session_goal_intro_while", child=session_goal_intro_sequence)
    session_goal_intro_while_negate = Negate(name="session_goal_intro_while_negate", child=session_goal_intro_while)
    gen_session_goal.add_child(session_goal_intro_while_negate)
    '''

    #
    #
    # Session loop until chosen session duration is reached (i.e. in this case 4 exercises completed)
    #
    #
    session_goal_selector = Selector(name="session_goal_selector")

    # Check if session duration has been reached
    session_time_reached = DurationCheck(name="session_time_reached", blackboard=b)
    session_goal_selector.add_child(session_time_reached)

    # Share data between initialise, duration and session_time_reached.
    b.add_remapping(initialise._id, 'start_time', session_time_reached._id, 'start_time')
    b.add_remapping(duration._id, 'session_duration', session_time_reached._id, 'session_duration')

    #
    # Conduct coaching for a shot
    #
    gen_exercise_goal, exercise_goal, exercise_goal_start, exercise_goal_exercise_choice, exercise_goal_intro_behav = get_intro_loop(
        name="exercise_goal_intro_loop", blackboard=b, prev_goal_node=session_goal._id, initialise_node=initialise._id,
        person_node=user_start._id)

    '''
    # Create shot goal in guide
    shot_goal = CreateSubgoal(name="create_shot_goal", blackboard=b)
    gen_shot_goal.add_child(shot_goal)

    # Share data between session_goal, session_goal_shot_choice and shot_goal.
    b.add_remapping(session_goal._id, 'new_goal', shot_goal._id, 'goal')
    b.add_remapping(session_goal_exercise_choice._id, 'shot', shot_goal._id, 'shot')

    # Wait for timestep cue (i.e. shot goal has been created by guide and we are ready for intro.
    shot_goal_start = TimestepCue(name="shot_goal_started_timestep", blackboard=b)
    shot_goal_start_until = Until(name="shot_goal_start_until", child=shot_goal_start)
    gen_shot_goal.add_child(shot_goal_start_until)
    b.add_remapping(shot_goal._id, 'new_goal', shot_goal_start._id, 'goal')
    b.save('phase', phase, shot_goal_start._id)

    #
    # Display intro shot behaviours until pre-instruction or questioning
    #
    shot_goal_intro_sequence = Progressor(name="shot_goal_intro_sequence")

    # Get behaviour from policy
    shot_goal_intro_behav = GetBehaviour(name="shot_goal_intro_behaviour", blackboard=b)
    shot_goal_intro_sequence.add_child(shot_goal_intro_behav)

    # Share data between initialise, session_goal_intro_behav, shot_goal_start and shot_goal_intro_behav.
    b.add_remapping(initialise._id, 'belief', shot_goal_intro_behav._id, 'belief')
    b.add_remapping(session_goal_intro_behav._id, 'observation', shot_goal_intro_behav._id, 'state')
    b.add_remapping(shot_goal._id, 'new_goal', shot_goal_intro_behav._id, 'goal')
    b.add_remapping(shot_goal_start._id, 'performance', shot_goal_intro_behav._id, 'performance')
    b.add_remapping(shot_goal_start._id, 'phase', shot_goal_intro_behav._id, 'phase')

    # Check if pre-instruction
    shot_goal_intro_pre_instr_sequence = Progressor(name="shot_goal_intro_pre_instr_sequence")
    shot_goal_intro_check_for_pre = CheckForBehaviour(name="shot_goal_intro_check_for_pre", blackboard=b)
    b.save('check_behaviour', Policy.A_PREINSTRUCTION, shot_goal_intro_check_for_pre._id)
    shot_goal_intro_pre_instr_sequence.add_child(shot_goal_intro_check_for_pre)
    # Share behaviour between shot_goal_intro_behav and shot_goal_intro_check_for_pre.
    b.add_remapping(shot_goal_intro_behav._id, 'behaviour', shot_goal_intro_check_for_pre._id, 'behaviour')
    # If pre-instruction is selected run baseline set to make decision of stat choice
    gen_baseline_goal = Progressor(name="gen_baseline_goal")
    # Create baseline goal
    baseline_goal = CreateSubgoal(name="create_baseline_goal", blackboard=b)
    gen_baseline_goal.add_child(baseline_goal)
    # Share data between shot_goal and baseline_goal.
    b.add_remapping(shot_goal._id, 'new_goal', baseline_goal._id, 'goal')
    # Wait for timestep cue (i.e. baseline goal has been created by guide and we are ready for intro.
    baseline_goal_start = TimestepCue(name="baseline_goal_started_timestep", blackboard=b)
    baseline_goal_start_until = Until(name="baseline_goal_start_until", child=baseline_goal_start)
    gen_baseline_goal.add_child(baseline_goal_start_until)
    b.add_remapping(baseline_goal._id, 'new_goal', baseline_goal_start._id, 'goal')
    # Get behaviour from policy (will always be pre-instruction for baseline goal.
    baseline_goal_intro_behav = GetBehaviour(name="baseline_goal_intro_behaviour", blackboard=b)
    gen_baseline_goal.add_child(baseline_goal_intro_behav)
    # Share data between initialise, session_goal_intro_behav, shot_goal_start and baseline_goal_intro_behav.
    b.add_remapping(initialise._id, 'belief', baseline_goal_intro_behav._id, 'belief')
    b.add_remapping(session_goal_intro_behav._id, 'observation', baseline_goal_intro_behav._id, 'state')
    b.add_remapping(baseline_goal._id, 'new_goal', baseline_goal_intro_behav._id, 'goal')
    b.add_remapping(baseline_goal_start._id, 'performance', baseline_goal_intro_behav._id, 'performance')
    b.add_remapping(baseline_goal_start._id, 'phase', baseline_goal_intro_behav._id, 'phase')
    # Format baseline pre-instruction behaviour
    baseline_goal_intro_action = FormatAction(name="baseline_goal_intro_action", blackboard=b)
    gen_baseline_goal.add_child(baseline_goal_intro_action)
    # Share data between initialise, baseline_goal_start, baseline_goal and baseline_goal_intro_action.
    b.add_remapping(initialise._id, 'bl', baseline_goal_intro_action._id, 'bl')
    b.add_remapping(baseline_goal_start._id, 'performance', baseline_goal_intro_action._id, 'performance')
    b.add_remapping(baseline_goal_start._id, 'phase', baseline_goal_intro_action._id, 'phase')
    b.add_remapping(baseline_goal_start._id, 'score', baseline_goal_intro_action._id, 'score')
    b.add_remapping(baseline_goal_start._id, 'target', baseline_goal_intro_action._id, 'target')
    b.add_remapping(baseline_goal._id, 'new_goal', baseline_goal_intro_action._id, 'goal')
    b.add_remapping(baseline_goal_intro_behav._id, 'behaviour', baseline_goal_intro_action._id, 'behaviour')
    b.add_remapping(user_start._id, 'name', baseline_goal_intro_action._id, 'name')
    b.save('shot', exercise, baseline_goal_intro_action._id)
    b.save('hand', hand, baseline_goal_intro_action._id)
    # Display baseline pre-instruction behaviour
    baseline_goal_intro = DisplayBehaviour(name="baseline_goal_intro", blackboard=b)
    gen_baseline_goal.add_child(baseline_goal_intro)
    # Share action between baseline_goal_intro_action and baseline_goal_intro.
    b.add_remapping(baseline_goal_intro_action._id, 'action', baseline_goal_intro._id, 'action')
    b.save('set_start', True, baseline_goal_intro._id)
    # Wait for user to finish set
    baseline_goal_end_set_event = EndSetEvent(name="baseline_goal_end_set_event", blackboard=b)
    baseline_goal_end_set_until = Until(name="baseline_goal_end_set_until", child=baseline_goal_end_set_event)
    gen_baseline_goal.add_child(baseline_goal_end_set_until)
    # End baseline goal
    baseline_goal_end = EndSubgoal(name="baseline_goal_end", blackboard=b)
    gen_baseline_goal.add_child(baseline_goal_end)
    b.add_remapping(baseline_goal._id, 'new_goal', baseline_goal_end._id, 'goal')
    # Wait for timestep cue with stats for baseline set just played.
    baseline_goal_end_cue = TimestepCue(name="baseline_goal_end_cue", blackboard=b)
    baseline_goal_end_cue_until = Until(name="baseline_goal_end_cue_until", child=baseline_goal_end_cue)
    gen_baseline_goal.add_child(baseline_goal_end_cue_until)
    b.add_remapping(baseline_goal_end._id, 'new_goal', baseline_goal_end_cue._id, 'goal')
    b.add_remapping(baseline_goal_end._id, 'phase', baseline_goal_end_cue._id, 'phase')
    shot_goal_intro_pre_instr_sequence.add_child(gen_baseline_goal)
    shot_goal_intro_pre_instr_negate = Negate(name="shot_goal_intro_pre_instr_negate", child=shot_goal_intro_pre_instr_sequence)
    shot_goal_intro_sequence.add_child(shot_goal_intro_pre_instr_negate)

    # Check if questioning
    shot_goal_intro_questioning_sequence = Progressor(name="shot_goal_intro_questioning_sequence")
    shot_goal_intro_check_for_questioning = CheckForBehaviour(name="shot_goal_intro_check_for_questioning", blackboard=b)
    b.save('check_behaviour', Policy.A_QUESTIONING, shot_goal_intro_check_for_questioning._id)
    shot_goal_intro_questioning_sequence.add_child(shot_goal_intro_check_for_questioning)
    # Share behaviour between shot_goal_intro_behav and shot_goal_intro_check_for_questioning.
    b.add_remapping(shot_goal_intro_behav._id, 'behaviour', shot_goal_intro_check_for_questioning._id, 'behaviour')
    shot_goal_stat_choice = GetUserChoice(name="shot_goal_stat_choice", blackboard=b)
    b.save('choice_type', STAT_CHOICE, shot_goal_stat_choice._id)
    shot_goal_intro_questioning_sequence.add_child(shot_goal_stat_choice)
    shot_goal_intro_questioning_negate = Negate(name="shot_goal_intro_questioning_negate", child=shot_goal_intro_questioning_sequence)
    # shot_goal_intro_sequence.add_child(shot_goal_intro_questioning_negate)

    # Format selected behaviour if not pre-instruction or questioning (i.e. create the output action)
    shot_goal_intro_action = FormatAction(name="shot_goal_intro_action", blackboard=b)
    shot_goal_intro_sequence.add_child(shot_goal_intro_action)
    # Share data between initialise, shot_goal_start, shot_goal, shot_goal_intro_behav and shot_goal_intro_action.
    b.add_remapping(initialise._id, 'bl', shot_goal_intro_action._id, 'bl')
    b.add_remapping(shot_goal_start._id, 'performance', shot_goal_intro_action._id, 'performance')
    b.add_remapping(shot_goal_start._id, 'phase', shot_goal_intro_action._id, 'phase')
    b.add_remapping(shot_goal_start._id, 'score', shot_goal_intro_action._id, 'score')
    b.add_remapping(shot_goal_start._id, 'target', shot_goal_intro_action._id, 'target')
    b.add_remapping(shot_goal._id, 'new_goal', shot_goal_intro_action._id, 'goal')
    b.add_remapping(shot_goal_intro_behav._id, 'behaviour', shot_goal_intro_action._id, 'behaviour')
    b.add_remapping(user_start._id, 'name', shot_goal_intro_action._id, 'name')
    b.save('shot', exercise, shot_goal_intro_action._id)
    b.save('hand', hand, shot_goal_intro_action._id)

    # Display selected behaviour if not pre-instruction or questioning
    shot_goal_intro_output = DisplayBehaviour(name="shot_goal_intro_output", blackboard=b)
    shot_goal_intro_sequence.add_child(shot_goal_intro_output)
    # Share action between shot_goal_intro_action and shot_goal_intro_output.
    b.add_remapping(shot_goal_intro_action._id, 'action', shot_goal_intro_output._id, 'action')

    shot_goal_intro_while = While(name="shot_goal_intro_while", child=shot_goal_intro_sequence)
    shot_goal_intro_while_negate = Negate(name="shot_goal_intro_while_negate", child=shot_goal_intro_while)
    gen_shot_goal.add_child(shot_goal_intro_while_negate)

    #
    # Conduct coaching for stat
    #
    gen_stat_goal = Progressor(name="gen_stat_goal")

    # Create stat goal in guide
    stat_goal = CreateSubgoal(name="create_stat_goal", blackboard=b)
    gen_stat_goal.add_child(stat_goal)

    # Share data between shot_goal and stat_goal.
    b.add_remapping(shot_goal._id, 'new_goal', stat_goal._id, 'goal')
    b.save('stat', stat, stat_goal._id)

    # Wait for timestep cue (i.e. stat goal has been created by guide and we are ready for intro.
    stat_goal_start = TimestepCue(name="stat_goal_started_timestep", blackboard=b)
    stat_goal_start_until = Until(name="stat_goal_start_until", child=stat_goal_start)
    gen_stat_goal.add_child(stat_goal_start_until)
    b.add_remapping(stat_goal._id, 'new_goal', stat_goal_start._id, 'goal')

    # Display intro stat behaviours until pre-instruction
    stat_goal_intro_sequence = Progressor(name="stat_goal_intro_sequence")

    # Get behaviour from policy
    stat_goal_intro_behav = GetBehaviour(name="stat_goal_intro_behaviour", blackboard=b)
    stat_goal_intro_sequence.add_child(stat_goal_intro_behav)

    # Share data between initialise, shot_goal_intro_behav, stat_goal_start and stat_goal_intro_behav.
    b.add_remapping(initialise._id, 'belief', stat_goal_intro_behav._id, 'belief')
    b.add_remapping(shot_goal_intro_behav._id, 'observation', stat_goal_intro_behav._id, 'state')
    b.add_remapping(stat_goal._id, 'new_goal', stat_goal_intro_behav._id, 'goal')
    b.add_remapping(stat_goal_start._id, 'performance', stat_goal_intro_behav._id, 'performance')
    b.add_remapping(stat_goal_start._id, 'phase', stat_goal_intro_behav._id, 'phase')

    # Check if pre-instruction
    stat_goal_intro_check_for_pre_instr = CheckForBehaviour(name="stat_goal_intro_check_for_pre_instr", blackboard=b)
    b.save('check_behaviour', Policy.A_PREINSTRUCTION, stat_goal_intro_check_for_pre_instr._id)
    stat_goal_intro_pre_instr_negate = Negate(name="stat_goal_intro_pre_instr_negate", child=stat_goal_intro_check_for_pre_instr)
    stat_goal_intro_sequence.add_child(stat_goal_intro_pre_instr_negate)
    # Share behaviour between stat_goal_intro_behav and stat_goal_intro_check_for_pre_instr.
    b.add_remapping(stat_goal_intro_behav._id, 'behaviour', stat_goal_intro_check_for_pre_instr._id, 'behaviour')

    # Format selected behaviour if not pre-instruction (i.e. create the output action)
    stat_goal_intro_action = FormatAction(name="stat_goal_intro_action", blackboard=b)
    stat_goal_intro_sequence.add_child(stat_goal_intro_action)
    # Share data between initialise, stat_goal_start, stat_goal, stat_goal_intro_behav and stat_goal_intro_action.
    b.add_remapping(initialise._id, 'bl', stat_goal_intro_action._id, 'bl')
    b.add_remapping(stat_goal_start._id, 'performance', stat_goal_intro_action._id, 'performance')
    b.add_remapping(stat_goal_start._id, 'phase', stat_goal_intro_action._id, 'phase')
    b.add_remapping(stat_goal_start._id, 'score', stat_goal_intro_action._id, 'score')
    b.add_remapping(stat_goal_start._id, 'target', stat_goal_intro_action._id, 'target')
    b.add_remapping(stat_goal._id, 'new_goal', stat_goal_intro_action._id, 'goal')
    b.add_remapping(stat_goal_intro_behav._id, 'behaviour', stat_goal_intro_action._id, 'behaviour')
    b.add_remapping(user_start._id, 'name', stat_goal_intro_action._id, 'name')
    b.save('stat', stat, stat_goal_intro_action._id)

    # Display selected behaviour if not pre-instruction
    stat_goal_intro_output = DisplayBehaviour(name="stat_goal_intro_output", blackboard=b)
    stat_goal_intro_sequence.add_child(stat_goal_intro_output)
    # Share action between stat_goal_intro_action and stat_goal_intro_output.
    b.add_remapping(stat_goal_intro_action._id, 'action', stat_goal_intro_output._id, 'action')

    stat_goal_intro_while = While(name="stat_goal_intro_while", child=stat_goal_intro_sequence)
    stat_goal_intro_while_negate = Negate(name="stat_goal_intro_while_negate", child=stat_goal_intro_while)
    gen_stat_goal.add_child(stat_goal_intro_while_negate)

    # Format pre-instruction behaviour (i.e. create the output action)
    stat_goal_pre_instr_intro_action = FormatAction(name="stat_goal_pre_instr_intro_action", blackboard=b)
    gen_stat_goal.add_child(stat_goal_pre_instr_intro_action)
    # Share data between initialise, stat_goal_start, stat_goal, stat_goal_intro_behav and stat_goal_pre_instr_intro_action.
    b.add_remapping(initialise._id, 'bl', stat_goal_pre_instr_intro_action._id, 'bl')
    b.add_remapping(stat_goal_start._id, 'performance', stat_goal_pre_instr_intro_action._id, 'performance')
    b.add_remapping(stat_goal_start._id, 'phase', stat_goal_pre_instr_intro_action._id, 'phase')
    b.add_remapping(stat_goal_start._id, 'score', stat_goal_pre_instr_intro_action._id, 'score')
    b.add_remapping(stat_goal_start._id, 'target', stat_goal_pre_instr_intro_action._id, 'target')
    b.add_remapping(stat_goal._id, 'new_goal', stat_goal_pre_instr_intro_action._id, 'goal')
    b.add_remapping(stat_goal_intro_behav._id, 'behaviour', stat_goal_pre_instr_intro_action._id, 'behaviour')
    b.add_remapping(user_start._id, 'name', stat_goal_pre_instr_intro_action._id, 'name')
    b.save('stat', stat, stat_goal_pre_instr_intro_action._id)

    # Display pre-instruction behaviour for stat
    stat_goal_pre_instr_intro_output = DisplayBehaviour(name="stat_goal_pre_instr_intro_output", blackboard=b)
    gen_stat_goal.add_child(stat_goal_pre_instr_intro_output)
    # Share action between stat_goal_pre_instr_intro_action and stat_goal_pre_instr_intro_output.
    b.add_remapping(stat_goal_pre_instr_intro_action._id, 'action', stat_goal_pre_instr_intro_output._id, 'action')
    '''

    # Loop through 2 sets of exercises
    exercise_goal_coaching = Progressor(name="exercise_goal_coaching")

    #
    # Conduct coaching for set
    #
    gen_set_goal, set_goal, set_goal_start, set_goal_choice, set_goal_intro_behav = get_intro_loop(
        name="set_goal_intro_loop", blackboard=b, prev_goal_node=exercise_goal._id, initialise_node=initialise._id,
        person_node=user_start._id)

    '''
    # Create set goal in guide
    set_goal = CreateSubgoal(name="create_set_goal", blackboard=b)
    gen_set_goal.add_child(set_goal)
    # Share data between stat_goal and set_goal.
    b.add_remapping(stat_goal._id, 'new_goal', set_goal._id, 'goal')

    # Wait for timestep cue (i.e. set goal has been created by guide and we are ready for intro.
    set_goal_start = TimestepCue(name="set_goal_started_timestep", blackboard=b)
    set_goal_start_until = Until(name="set_goal_start_until", child=set_goal_start)
    gen_set_goal.add_child(set_goal_start_until)
    b.add_remapping(set_goal._id, 'new_goal', set_goal_start._id, 'goal')
    b.save('phase', phase, set_goal_start._id)

    # Display intro set behaviours until pre-instruction
    set_goal_intro_sequence = Progressor(name="set_goal_intro_sequence")

    # Get behaviour from policy
    set_goal_intro_behav = GetBehaviour(name="set_goal_intro_behaviour", blackboard=b)
    set_goal_intro_sequence.add_child(set_goal_intro_behav)

    # Share data between initialise, stat_goal_intro_behav, set_goal_start and set_goal_intro_behav.
    b.add_remapping(initialise._id, 'belief', set_goal_intro_behav._id, 'belief')
    b.add_remapping(stat_goal_intro_behav._id, 'observation', set_goal_intro_behav._id, 'state')
    b.add_remapping(set_goal._id, 'new_goal', set_goal_intro_behav._id, 'goal')
    b.add_remapping(set_goal_start._id, 'performance', set_goal_intro_behav._id, 'performance')
    b.add_remapping(set_goal_start._id, 'phase', set_goal_intro_behav._id, 'phase')

    # Check if pre-instruction
    set_goal_intro_check_for_pre_instr = CheckForBehaviour(name="set_goal_intro_check_for_pre_instr", blackboard=b)
    b.save('check_behaviour', Policy.A_PREINSTRUCTION, set_goal_intro_check_for_pre_instr._id)
    set_goal_intro_pre_instr_negate = Negate(name="set_goal_intro_pre_instr_negate", child=set_goal_intro_check_for_pre_instr)
    set_goal_intro_sequence.add_child(set_goal_intro_pre_instr_negate)
    # Share behaviour between set_goal_intro_behav and set_goal_intro_check_for_pre_instr.
    b.add_remapping(set_goal_intro_behav._id, 'behaviour', set_goal_intro_check_for_pre_instr._id, 'behaviour')

    # Format selected behaviour if not pre-instruction (i.e. create the output action)
    set_goal_intro_action = FormatAction(name="set_goal_intro_action", blackboard=b)
    set_goal_intro_sequence.add_child(set_goal_intro_action)
    # Share data between initialise, set_goal_start, set_goal, set_goal_intro_behav and set_goal_intro_action.
    b.add_remapping(initialise._id, 'bl', set_goal_intro_action._id, 'bl')
    b.add_remapping(set_goal_start._id, 'performance', set_goal_intro_action._id, 'performance')
    b.add_remapping(set_goal_start._id, 'phase', set_goal_intro_action._id, 'phase')
    b.add_remapping(stat_goal_start._id, 'score', set_goal_intro_action._id, 'score')
    b.add_remapping(stat_goal_start._id, 'target', set_goal_intro_action._id, 'target')
    b.add_remapping(set_goal._id, 'new_goal', set_goal_intro_action._id, 'goal')
    b.add_remapping(set_goal_intro_behav._id, 'behaviour', set_goal_intro_action._id, 'behaviour')
    b.add_remapping(user_start._id, 'name', set_goal_intro_action._id, 'name')
    b.save('shot', exercise, set_goal_intro_action._id)
    b.save('hand', hand, set_goal_intro_action._id)
    b.save('stat', stat, set_goal_intro_action._id)

    # Display selected behaviour if not pre-instruction
    set_goal_intro_output = DisplayBehaviour(name="set_goal_intro_output", blackboard=b)
    set_goal_intro_sequence.add_child(set_goal_intro_output)
    # Share action between set_goal_intro_action and set_goal_intro_output.
    b.add_remapping(set_goal_intro_action._id, 'action', set_goal_intro_output._id, 'action')

    set_goal_intro_while = While(name="set_goal_intro_while", child=set_goal_intro_sequence)
    set_goal_intro_while_negate = Negate(name="set_goal_intro_while_negate", child=set_goal_intro_while)
    gen_set_goal.add_child(set_goal_intro_while_negate)

    # Format pre-instruction behaviour (i.e. create the output action)
    set_goal_pre_instr_intro_action = FormatAction(name="set_goal_pre_instr_intro_action", blackboard=b)
    gen_set_goal.add_child(set_goal_pre_instr_intro_action)
    # Share data between initialise, set_goal_start, set_goal, set_goal_intro_behav and set_goal_pre_instr_intro_action.
    b.add_remapping(initialise._id, 'bl', set_goal_pre_instr_intro_action._id, 'bl')
    b.add_remapping(set_goal_start._id, 'performance', set_goal_pre_instr_intro_action._id, 'performance')
    b.add_remapping(set_goal_start._id, 'phase', set_goal_pre_instr_intro_action._id, 'phase')
    b.add_remapping(set_goal_start._id, 'score', set_goal_pre_instr_intro_action._id, 'score')
    b.add_remapping(set_goal_start._id, 'target', set_goal_pre_instr_intro_action._id, 'target')
    b.add_remapping(set_goal._id, 'new_goal', set_goal_pre_instr_intro_action._id, 'goal')
    b.add_remapping(set_goal_intro_behav._id, 'behaviour', set_goal_pre_instr_intro_action._id, 'behaviour')
    b.add_remapping(user_start._id, 'name', set_goal_pre_instr_intro_action._id, 'name')
    b.save('shot', exercise, set_goal_pre_instr_intro_action._id)
    b.save('hand', hand, set_goal_pre_instr_intro_action._id)
    b.save('stat', stat, set_goal_pre_instr_intro_action._id)

    # Display pre-instruction behaviour for set
    set_goal_pre_instr_intro_output = DisplayBehaviour(name="set_goal_pre_instr_intro_output", blackboard=b)
    gen_set_goal.add_child(set_goal_pre_instr_intro_output)
    # Share action between set_goal_pre_instr_intro_action and set_goal_pre_instr_intro_output.
    b.add_remapping(set_goal_pre_instr_intro_action._id, 'action', set_goal_pre_instr_intro_output._id, 'action')
    b.save('set_start', True, set_goal_pre_instr_intro_output._id)
    '''

    # Coaching loop for set until end of set event (i.e. all reps have been done or user has ended the set early)
    set_goal_coaching_selector = Selector(name="set_goal_coaching_selector")

    # Check for user ending set event
    set_goal_end_set_event = EndSetEvent(name="set_goal_end_set_event", blackboard=b)
    set_goal_coaching_selector.add_child(set_goal_end_set_event)

    # Individual action coaching loop
    set_goal_individual_action_sequence = Progressor(name="set_goal_individual_action_Progressor")
    # Create action goal
    action_goal = CreateSubgoal(name="create_action_goal", blackboard=b)
    set_goal_individual_action_sequence.add_child(action_goal)
    # Share data between stat_goal and set_goal.
    b.add_remapping(set_goal._id, 'new_goal', action_goal._id, 'goal')
    # Wait for operator input, and then call timestep cue (i.e. the user has completed a rep of the given exercise)
    set_goal_individual_action_rep = OperatorInput(name="set_goal_individual_action_rep", blackboard=b)
    set_goal_individual_action_cue = TimestepCue(name="set_goal_individual_action_cue", blackboard=b)
    set_goal_individual_action_until = Until(name="set_goal_individual_action_until", child=set_goal_individual_action_rep)
    set_goal_individual_action_sequence.add_child(set_goal_individual_action_until)
    set_goal_individual_action_sequence.add_child(set_goal_individual_action_cue)
    b.add_remapping(action_goal._id, 'new_goal', set_goal_individual_action_cue._id, 'goal')
    b.add_remapping(exercise_goal_start._id, 'target', set_goal_individual_action_rep._id, 'target')
    set_goal_individual_action_behav_sequence = Progressor(name="set_goal_individual_behav_Progressor")
    # Get coaching behaviour from policy for individual action/shot
    set_goal_individual_action_behav = GetBehaviour(name="set_goal_individual_action_behaviour", blackboard=b)
    set_goal_individual_action_behav_sequence.add_child(set_goal_individual_action_behav)
    # Share data between initialise, set_goal_intro_behav, set_goal_individual_action_cue and set_goal_individual_action_behav.
    b.add_remapping(initialise._id, 'belief', set_goal_individual_action_behav._id, 'belief')
    b.add_remapping(set_goal_intro_behav._id, 'observation', set_goal_individual_action_behav._id, 'state')
    b.add_remapping(action_goal._id, 'new_goal', set_goal_individual_action_behav._id, 'goal')
    b.add_remapping(set_goal_individual_action_cue._id, 'performance', set_goal_individual_action_behav._id, 'performance')
    b.add_remapping(set_goal_individual_action_cue._id, 'phase', set_goal_individual_action_behav._id, 'phase')
    # Format individual action coaching behaviour
    set_goal_individual_action = FormatAction(name="set_goal_individual_action", blackboard=b)
    set_goal_individual_action_behav_sequence.add_child(set_goal_individual_action)
    # Share data between initialise, set_goal_individual_action_cue, action_goal, set_goal_individual_action_behav and set_goal_individual_action.
    b.add_remapping(initialise._id, 'bl', set_goal_individual_action._id, 'bl')
    b.add_remapping(set_goal_individual_action_cue._id, 'performance', set_goal_individual_action, 'performance')
    b.add_remapping(set_goal_individual_action_cue._id, 'phase', set_goal_individual_action._id, 'phase')
    b.add_remapping(set_goal_individual_action_cue._id, 'score', set_goal_individual_action._id, 'score')
    b.add_remapping(set_goal_individual_action_cue._id, 'target', set_goal_individual_action._id, 'target')
    b.add_remapping(action_goal._id, 'new_goal', set_goal_individual_action._id, 'goal')
    b.add_remapping(set_goal_individual_action_behav._id, 'behaviour', set_goal_individual_action._id, 'behaviour')
    b.add_remapping(user_start._id, 'name', set_goal_individual_action._id, 'name')
    b.add_remapping(exercise_goal._id, 'exercise', set_goal_individual_action._id, 'exercise')
    # Display individual action caoching behaviour
    set_goal_individual_action_output = DisplayBehaviour(name="set_goal_individual_action_output", blackboard=b)
    set_goal_individual_action_behav_sequence.add_child(set_goal_individual_action_output)
    # Share action between set_goal_pre_instr_intro_action and set_goal_pre_instr_intro_output.
    b.add_remapping(set_goal_individual_action._id, 'action', set_goal_individual_action_output._id, 'action')
    set_goal_individual_action_behav_succeed = Succeed(name="set_goal_individual_action_behav_succeed", child=set_goal_individual_action_behav_sequence)
    set_goal_individual_action_sequence.add_child(set_goal_individual_action_behav_succeed)
    # End the action goal
    end_action_goal = EndSubgoal(name="end_action_goal", blackboard=b)
    set_goal_individual_action_sequence.add_child(end_action_goal)
    # Share goal between action_goal and end_action_goal
    b.add_remapping(action_goal._id, 'new_goal', end_action_goal._id, 'goal')

    set_goal_individual_action_repeat = Repeat(name="set_goal_individual_action_repeat", child=set_goal_individual_action_sequence)
    set_goal_coaching_selector.add_child(set_goal_individual_action_repeat)

    set_goal_coaching_until = Until(name="set_goal_coaching_until", child=set_goal_coaching_selector)
    gen_set_goal.add_child(set_goal_coaching_until)

    # Set feedback loop until pre-instruction
    # Wait for timestep cue (i.e. set goal has been completed by guide and we are ready for feedback behaviours).
    set_goal_end = TimestepCue(name="set_goal_ended_timestep", blackboard=b)
    b.add_remapping(end_action_goal._id, 'new_goal', set_goal_end._id, 'goal')
    set_goal_end_until = Until(name="set_goal_end_until", child=set_goal_end)
    gen_set_goal.add_child(set_goal_end_until)
    exercise_goal_coaching.add_child(gen_set_goal)

    set_goal_feedback_loop, set_goal_feedback_behav, set_goal_feedback_end = get_feedback_loop(name="set_goal_feedback_loop", behav=Policy.A_PREINSTRUCTION, blackboard=b, goal_node=set_goal._id, initialise_node=initialise._id, previous_behav_node=set_goal_individual_action_behav._id, timestep_cue_node=set_goal_end._id, person_node=user_start._id)
    set_goal_feedback_negate = Negate(name="set_goal_feedback_loop_negate", child=set_goal_feedback_loop)
    exercise_goal_coaching.add_child(set_goal_feedback_negate)
    # Remap the observation from the feedback loop to be the new state when an intro behaviour is given for the next set.
    b.add_remapping(set_goal_end, 'phase', set_goal_intro_behav, 'previous_phase')
    b.add_remapping(set_goal_feedback_behav, 'observation', set_goal_intro_behav, 'feedback_state')

    '''
    stat_goal_coaching_until_count = UntilCount(name="stat_goal_coaching_until_count", max_count=5, child=stat_goal_coaching)
    stat_goal_coaching_until_negate = Negate(name="stat_goal_coaching_until_negate", child=stat_goal_coaching_until_count)
    gen_stat_goal.add_child(stat_goal_coaching_until_negate)

    # Stat feedback loop until pre-instruction
    # Wait for timestep cue (i.e. stat goal has been completed by guide and we are ready for feedback behaviours).
    stat_goal_end = TimestepCue(name="stat_goal_ended_timestep", blackboard=b)
    b.add_remapping(set_goal_feedback_end._id, 'new_goal', stat_goal_end._id, 'goal')
    stat_goal_end_until = Until(name="stat_goal_end_until", child=stat_goal_end)
    gen_stat_goal.add_child(stat_goal_end_until)
    stat_goal_feedback_loop, stat_goal_feedback_behav, stat_goal_feedback_end = get_feedback_loop(name="stat_goal_feedback_loop", behav=Policy.A_PREINSTRUCTION, blackboard=b, goal_node=stat_goal._id, initialise_node=initialise._id, previous_behav_node=set_goal_feedback_behav._id, timestep_cue_node=stat_goal_end._id, person_node=user_start._id)
    gen_stat_goal.add_child(stat_goal_feedback_loop)
    # Remap the observation from the feedback loop to be the new state when an intro behaviour is given for the next stat.
    b.add_remapping(stat_goal_end, 'phase', stat_goal_intro_behav, 'previous_phase')
    b.add_remapping(stat_goal_feedback_behav, 'observation', stat_goal_intro_behav, 'feedback_state')

    stat_goal_until_count = UntilCount(name="stat_goal_until_count", max_count=1, child=gen_stat_goal)
    gen_shot_goal.add_child(stat_goal_until_count)
    '''

    # Shot feedback loop until pre-instruction
    # Wait for timestep cue (i.e. shot goal has been completed by guide and we are ready for feedback behaviours).
    exercise_goal_end = TimestepCue(name="exercise_goal_ended_timestep", blackboard=b)
    b.add_remapping(set_goal_feedback_end._id, 'new_goal', exercise_goal_end._id, 'goal')
    b.add_remapping(exercise_goal, 'exercise', exercise_goal_end._id, 'exercise')
    exercise_goal_end_until = Until(name="shot_goal_end_until", child=exercise_goal_end)
    gen_exercise_goal.add_child(exercise_goal_end_until)
    exercise_goal_feedback_loop, exercise_goal_feedback_behav, exercise_goal_feedback_end = get_feedback_loop(name="exercise_goal_feedback_loop", behav=Policy.A_PREINSTRUCTION, blackboard=b, goal_node=exercise_goal._id, initialise_node=initialise._id, previous_behav_node=set_goal_feedback_behav._id, timestep_cue_node=exercise_goal_end._id, person_node=user_start._id)
    gen_exercise_goal.add_child(exercise_goal_feedback_loop)
    # Remap the observation from the feedback loop to be the new state when an intro behaviour is given for the next shot.
    b.add_remapping(exercise_goal_end, 'phase', exercise_goal_intro_behav, 'previous_phase')
    b.add_remapping(exercise_goal_feedback_behav, 'observation', exercise_goal_intro_behav, 'feedback_state')

    exercise_goal_negate = Repeat(name="exercise_goal_negate", child=gen_exercise_goal)
    session_goal_selector.add_child(exercise_goal_negate)

    session_goal_until = Until(name="session_goal_until", child=session_goal_selector)
    gen_session_goal.add_child(session_goal_until)

    #
    # Session goal feedback loop
    #
    # Wait for timestep cue (i.e. session goal has been completed by guide and we are ready for feedback behaviours).
    session_goal_end = TimestepCue(name="session_goal_ended_timestep", blackboard=b)
    b.add_remapping(exercise_goal_feedback_end._id, 'new_goal', session_goal_end._id, 'goal')
    session_goal_end_until = Until(name="session_goal_end_until", child=session_goal_end)
    gen_session_goal.add_child(session_goal_end_until)
    session_goal_feedback_loop, session_goal_feedback_behav, session_goal_feedback_end = get_feedback_loop(name="session_goal_feedback_loop", behav=Policy.A_END, blackboard=b, goal_node=session_goal._id, initialise_node=initialise._id, previous_behav_node=exercise_goal_feedback_behav._id, timestep_cue_node=session_goal_end._id, person_node=user_start._id)
    gen_session_goal.add_child(session_goal_feedback_loop)

    gen_person_goal.add_child(gen_session_goal)

    #
    # Person goal feedback loop
    #
    # Wait for timestep cue (i.e. session (person goal) has been completed by guide and we are ready for feedback behaviours).
    person_goal_end = TimestepCue(name="person_goal_ended_timestep", blackboard=b)
    b.add_remapping(session_goal_feedback_end._id, 'new_goal', person_goal_end._id, 'goal')
    person_goal_end_until = Until(name="person_goal_end_until", child=person_goal_end)
    gen_person_goal.add_child(person_goal_end_until)
    person_goal_feedback_loop, person_goal_feedback_behav, person_goal_feedback_end = get_feedback_loop(name="person_goal_feedback_loop",
                                                                                behav=Policy.A_END, blackboard=b,
                                                                                goal_node=person_goal._id,
                                                                                initialise_node=initialise._id,
                                                                                previous_behav_node=session_goal_feedback_behav._id,
                                                                                timestep_cue_node=person_goal_end._id, person_node=user_start._id)
    gen_person_goal.add_child(person_goal_feedback_loop)

    root.add_child(gen_person_goal)
    return root

def get_intro_loop(name, blackboard, prev_goal_node, initialise_node, person_node):
    """
    Creates a subtree which gives the introduction at a given goal level.
    :param name :type str: the name to be used when creating nodes of the tree.
    :param behav :type int: the behaviour (either A_QUESTIONING or A_PREINSTRUCTION) to check for which will end the
        intro loop.
    :param blackboard :type Blackboard: the Blackboard associated with this behaviour tree.
    :param goal_node :type CreateSubgoal: the goal node from which to share data about the current goal state.
    :return:type: Negate: the root While Node of the created feedback loop tree, negated to allow the tree to continue
        running.
    """
    # Create overall feedback Progressor
    overall_name = name + "_overall_sequence"
    overall_intro_sequence = Progressor(name=overall_name)  # Progressor because the Negate will make the While return SUCCESS when question or pre-instruction has been displayed.

    #
    #
    # Create goal in guide
    #
    #
    new_goal_name = "create_" + name + "_goal"
    new_goal = CreateSubgoal(name=new_goal_name, blackboard=blackboard)
    overall_intro_sequence.add_child(new_goal)

    # Share data between person_goal and session_goal.
    blackboard.add_remapping(prev_goal_node, 'new_goal', new_goal._id, 'goal')

    #
    #
    # Wait for timestep cue (i.e. the new goal has been created by guide and we are ready for intro.
    #
    #
    new_goal_start_name = name + "_timestep"
    new_goal_start = TimestepCue(name=new_goal_start_name, blackboard=blackboard)
    new_goal_start_until_name = new_goal_start_name + "_until"
    new_goal_start_until = Until(name=new_goal_start_until_name, child=new_goal_start)
    overall_intro_sequence.add_child(new_goal_start_until)
    blackboard.add_remapping(new_goal._id, 'new_goal', new_goal_start._id, 'goal')
    blackboard.add_remapping(prev_goal_node, 'exercise', new_goal_start._id, 'exercise')

    #
    #
    # Display behaviours until pre-instruction or questioning
    #
    #
    new_goal_intro_sequence_name = name + "_intro_behav_sequence"
    new_goal_intro_sequence = Progressor(name=new_goal_intro_sequence_name)

    # Get behaviour from policy
    new_goal_intro_behav_name = name + "behaviour"
    new_goal_intro_behav = GetBehaviour(name=new_goal_intro_behav_name, blackboard=blackboard)
    new_goal_intro_sequence.add_child(new_goal_intro_behav)

    # Share data between initialise, new_goal_start, and new_goal_intro_behav.
    blackboard.add_remapping(initialise_node, 'belief', new_goal_intro_behav._id, 'belief')
    blackboard.add_remapping(initialise_node, 'state', new_goal_intro_behav._id, 'state')
    blackboard.add_remapping(new_goal_start._id, 'performance', new_goal_intro_behav._id, 'performance')
    blackboard.add_remapping(new_goal_start._id, 'phase', new_goal_intro_behav._id, 'phase')
    blackboard.add_remapping(new_goal._id, 'new_goal', new_goal_intro_behav._id, 'goal')

    # Check if pre-instruction
    new_goal_intro_pre_instr_sequence_name = name + "_pre_instruction_sequence"
    new_goal_intro_pre_instr_sequence = Progressor(name=new_goal_intro_pre_instr_sequence_name)
    new_goal_intro_check_for_pre_name = name + "_chec_for_pre"
    new_goal_intro_check_for_pre = CheckForBehaviour(name=new_goal_intro_check_for_pre_name, blackboard=blackboard)
    blackboard.save('check_behaviour', Policy.A_PREINSTRUCTION, new_goal_intro_check_for_pre._id)
    # Share behaviour between new_goal_intro_behav and new_goal_intro_check_for_pre.
    blackboard.add_remapping(new_goal_intro_behav._id, 'behaviour', new_goal_intro_check_for_pre._id, 'behaviour')
    new_goal_intro_pre_instr_sequence.add_child(new_goal_intro_check_for_pre)
    # Format and display pre-instruction action.
    new_goal_intro_pre_instr_action_name = name + "_pre_instr_action"
    new_goal_intro_pre_instr_action = FormatAction(name=new_goal_intro_pre_instr_action_name, blackboard=blackboard)
    new_goal_intro_pre_instr_sequence.add_child(new_goal_intro_pre_instr_action)
    # Share data between initialise, session_goal_start, session_goal, new_goal_intro_behav and session_goal_intro_action.
    blackboard.add_remapping(initialise_node, 'bl', new_goal_intro_pre_instr_action._id, 'bl')
    blackboard.add_remapping(new_goal_start._id, 'performance', new_goal_intro_pre_instr_action._id, 'performance')
    blackboard.add_remapping(new_goal_start._id, 'phase', new_goal_intro_pre_instr_action._id, 'phase')
    blackboard.add_remapping(new_goal_start._id, 'score', new_goal_intro_pre_instr_action._id, 'score')
    blackboard.add_remapping(new_goal_start._id, 'target', new_goal_intro_pre_instr_action._id, 'target')
    blackboard.add_remapping(new_goal._id, 'new_goal', new_goal_intro_pre_instr_action._id, 'goal')
    blackboard.add_remapping(new_goal_intro_behav._id, 'behaviour', new_goal_intro_pre_instr_action._id, 'behaviour')
    blackboard.add_remapping(person_node, 'name', new_goal_intro_pre_instr_action._id, 'name')
    blackboard.add_remapping(prev_goal_node, 'exercise', new_goal_intro_pre_instr_action._id, 'exercise')
    new_goal_intro_pre_instr_output_name = name + "_pre_instr_output"
    new_goal_intro_pre_instr_output = DisplayBehaviour(name=new_goal_intro_pre_instr_output_name, blackboard=blackboard)
    new_goal_intro_pre_instr_sequence.add_child(new_goal_intro_pre_instr_output)
    # Share action between session_goal_intro_action and session_goal_intro_output.
    blackboard.add_remapping(new_goal_intro_pre_instr_action._id, 'action', new_goal_intro_pre_instr_output._id,
                    'action')
    new_goal_intro_pre_instr_negate_name = name + "_pre_instr_negate"
    new_goal_intro_pre_instr_negate = Negate(name=new_goal_intro_pre_instr_negate_name,
                                             child=new_goal_intro_pre_instr_sequence)
    new_goal_intro_sequence.add_child(new_goal_intro_pre_instr_negate)

    # Check if questioning
    new_goal_intro_questioning_sequence_name = name + "_questioning_sequence"
    new_goal_intro_questioning_sequence = Progressor(name=new_goal_intro_questioning_sequence_name)
    new_goal_intro_check_for_questioning_name = name + "_check_for_questioning"
    new_goal_intro_check_for_questioning = CheckForBehaviour(name=new_goal_intro_check_for_questioning_name,
                                                             blackboard=blackboard)
    blackboard.save('check_behaviour', Policy.A_QUESTIONING, new_goal_intro_check_for_questioning._id)
    # Share behaviour between new_goal_intro_behav and new_goal_intro_check_for_questioning.
    blackboard.add_remapping(new_goal_intro_behav._id, 'behaviour', new_goal_intro_check_for_questioning._id,
                    'behaviour')
    new_goal_intro_questioning_sequence.add_child(new_goal_intro_check_for_questioning)
    new_goal_user_choice_name = name + "_user_choice"
    new_goal_user_choice = GetUserChoice(name=new_goal_user_choice_name, blackboard=blackboard)
    blackboard.save('choice_type', SHOT_CHOICE, new_goal_user_choice._id)  # TODO: Doesn't matter at the moment because we make all the choices but will need to be updated for long term study.
    new_goal_intro_questioning_sequence.add_child(new_goal_user_choice)
    new_goal_intro_questioning_negate_name = name + "_questioning_sequence_negate"
    new_goal_intro_questioning_negate = Negate(name=new_goal_intro_questioning_negate_name,
                                               child=new_goal_intro_questioning_sequence)
    new_goal_intro_sequence.add_child(new_goal_intro_questioning_negate)

    # Format selected behaviour if not pre-instruction or questioning (i.e. create the output action)
    new_goal_intro_action_name = name + "_action"
    new_goal_intro_action = FormatAction(name=new_goal_intro_action_name, blackboard=blackboard)
    new_goal_intro_sequence.add_child(new_goal_intro_action)

    # Share data between initialise, new_goal_start, new_goal, new_goal_intro_behav and new_goal_intro_action.
    blackboard.add_remapping(initialise_node, 'bl', new_goal_intro_action._id, 'bl')
    blackboard.add_remapping(new_goal_start._id, 'performance', new_goal_intro_action._id, 'performance')
    blackboard.add_remapping(new_goal_start._id, 'phase', new_goal_intro_action._id, 'phase')
    blackboard.add_remapping(new_goal_start._id, 'score', new_goal_intro_action._id, 'score')
    blackboard.add_remapping(new_goal_start._id, 'target', new_goal_intro_action._id, 'target')
    blackboard.add_remapping(new_goal._id, 'new_goal', new_goal_intro_action._id, 'goal')
    blackboard.add_remapping(new_goal_intro_behav._id, 'behaviour', new_goal_intro_action._id, 'behaviour')
    blackboard.add_remapping(person_node, 'name', new_goal_intro_action._id, 'name')
    blackboard.add_remapping(prev_goal_node, 'exercise', new_goal_intro_action._id, 'exercise')

    # Display selected behaviour if not pre-instruction or questioning
    new_goal_intro_output_name = name + "_output"
    new_goal_intro_output = DisplayBehaviour(name=new_goal_intro_output_name, blackboard=blackboard)
    new_goal_intro_sequence.add_child(new_goal_intro_output)
    # Share action between new_goal_intro_action and new_goal_intro_output.
    blackboard.add_remapping(new_goal_intro_action._id, 'action', new_goal_intro_output._id, 'action')

    new_goal_intro_while_name = name + "_while"
    new_goal_intro_while = While(name=new_goal_intro_while_name, child=new_goal_intro_sequence)
    new_goal_intro_while_negate_name = new_goal_intro_while_name + "_negate"
    new_goal_intro_while_negate = Negate(name=new_goal_intro_while_negate_name, child=new_goal_intro_while)
    overall_intro_sequence.add_child(new_goal_intro_while_negate)

    return overall_intro_sequence, new_goal, new_goal_start, new_goal_user_choice, new_goal_intro_behav


def get_feedback_loop(name, behav, blackboard, goal_node, initialise_node, previous_behav_node, timestep_cue_node, person_node):
    """
    Creates a subtree which gives feedback at a given goal level.
    :param name :type str: the name to be used when creating nodes of the tree.
    :param behav :type int: the behaviour (either A_END or A_PREINSTRUCTION) to check for which will end the feedback
        loop.
    :param blackboard :type Blackboard: the Blackboard associated with this behaviour tree.
    :param goal_node :type CreateSubgoal: the goal node from which to share data about the current goal state.
    :return:type: Negate: the root While Node of the created feedback loop tree, negated to allow the tree to continue
        running.
    """
    # Create overall feedback Selector
    overall_name = name + "_overall_sequence"
    overall_feedback_sequence = Selector(name=overall_name)  # Selector so that when pre-instruction is called, end_goal is called. While needs to return FAIL to move on to End Goal.

    # Create feedback loop Progressor
    sequence_name = name + "_sequence"
    feedback_loop_sequence = Progressor(name=sequence_name)

    # Get behaviour from policy
    feedback_behaviour_name = name + "_behav"
    feedback_behaviour = GetBehaviour(name=feedback_behaviour_name, blackboard=blackboard)
    feedback_loop_sequence.add_child(feedback_behaviour)
    # Share data between initialise_node, intro_behav_node, timestep_cue_node and feedback_behaviour.
    blackboard.add_remapping(initialise_node, 'belief', feedback_behaviour._id, 'belief')
    blackboard.add_remapping(previous_behav_node, 'observation', feedback_behaviour._id, 'state')
    blackboard.add_remapping(goal_node, 'new_goal', feedback_behaviour._id, 'goal')
    blackboard.add_remapping(timestep_cue_node, 'performance', feedback_behaviour._id, 'performance')
    blackboard.add_remapping(timestep_cue_node, 'phase', feedback_behaviour._id, 'phase')

    # Check if given behaviour
    check_behav_name = name + "_check_for_" + behav.__str__()
    feedback_loop_check_for_behav = CheckForBehaviour(name=check_behav_name, blackboard=blackboard)
    blackboard.save('check_behaviour', behav, feedback_loop_check_for_behav._id)
    # Share behaviour between feedback_behaviour and feedback_loop_check_for_behav.
    blackboard.add_remapping(feedback_behaviour._id, 'behaviour', feedback_loop_check_for_behav._id, 'behaviour')
    negate_name = name + "_" + behav.__str__() + "_check_negate"

    # If pre-instruction, just negate behaviour check
    if behav == Policy.A_PREINSTRUCTION:
        feedback_loop_sequence.add_child(Negate(name=negate_name, child=feedback_loop_check_for_behav))
    else:  # If end, do the check and then display the behaviour
        feedback_loop_end_sequence = Progressor(name="feedback_loop_end_sequence")
        feedback_loop_end_sequence.add_child(feedback_loop_check_for_behav)

        feedback_loop_end_action = FormatAction(name="feedback_loop_end_action", blackboard=blackboard)
        feedback_loop_end_sequence.add_child(feedback_loop_end_action)
        # Share data between initialise_node, timestep_cue_node, goal_node, feedback_behaviour and feedback_loop_end_action.
        blackboard.add_remapping(initialise_node, 'bl', feedback_loop_end_action._id, 'bl')
        blackboard.add_remapping(timestep_cue_node, 'performance', feedback_loop_end_action._id, 'performance')
        blackboard.save('phase', PolicyWrapper.PHASE_END, feedback_loop_end_action._id)
        blackboard.add_remapping(timestep_cue_node, 'score', feedback_loop_end_action._id, 'score')
        blackboard.add_remapping(timestep_cue_node, 'target', feedback_loop_end_action._id, 'target')
        blackboard.add_remapping(goal_node, 'new_goal', feedback_loop_end_action._id, 'goal')
        blackboard.add_remapping(feedback_behaviour._id, 'behaviour', feedback_loop_end_action._id, 'behaviour')
        blackboard.add_remapping(person_node, 'name', feedback_loop_end_action._id, 'name')
        blackboard.add_remapping(goal_node, 'exercise', feedback_loop_end_action._id, 'exercise')

        feedback_loop_display_end_output = DisplayBehaviour(name="feedback_loop_display_end_output", blackboard=blackboard)
        feedback_loop_end_sequence.add_child(feedback_loop_display_end_output)
        # Share action between feedback_loop_end_action and feedback_loop_display_end_output.
        blackboard.add_remapping(feedback_loop_end_action._id, 'action', feedback_loop_display_end_output._id, 'action')

        feedback_loop_sequence.add_child(Negate(name=negate_name, child=feedback_loop_end_sequence))

    # Format selected behaviour if not given behaviour (i.e. create the output action)
    action_name = name + "_action"
    feedback_loop_action = FormatAction(name=action_name, blackboard=blackboard)
    feedback_loop_sequence.add_child(feedback_loop_action)
    # Share data between initialise_node, timestep_cue_node, goal_node, feedback_behaviour and feedback_loop_end_action.
    blackboard.add_remapping(initialise_node, 'bl', feedback_loop_action._id, 'bl')
    blackboard.add_remapping(timestep_cue_node, 'performance', feedback_loop_action._id, 'performance')
    blackboard.save('phase', PolicyWrapper.PHASE_END, feedback_loop_action._id)
    blackboard.add_remapping(timestep_cue_node, 'score', feedback_loop_action._id, 'score')
    blackboard.add_remapping(timestep_cue_node, 'target', feedback_loop_action._id, 'target')
    blackboard.add_remapping(goal_node, 'new_goal', feedback_loop_action._id, 'goal')
    blackboard.add_remapping(feedback_behaviour._id, 'behaviour', feedback_loop_action._id, 'behaviour')
    blackboard.add_remapping(person_node, 'name', feedback_loop_action._id, 'name')
    blackboard.add_remapping(goal_node, 'exercise', feedback_loop_action._id, 'exercise')

    # Display behaviour if not given behaviour
    output_name = name + "_output"
    feedback_loop_output = DisplayBehaviour(name=output_name, blackboard=blackboard)
    feedback_loop_sequence.add_child(feedback_loop_output)
    # Share action between feedback_loop_end_action and feedback_loop_display_end_output.
    blackboard.add_remapping(feedback_loop_action._id, 'action', feedback_loop_output._id, 'action')
    # overall_feedback_sequence.add_child(feedback_loop_sequence)

    while_name = name + "_while"
    feedback_loop_while = While(name=while_name, child=feedback_loop_sequence)
    overall_feedback_sequence.add_child(feedback_loop_while)

    # End the goal
    end_goal_name = name + "_end_goal"
    end_goal = EndSubgoal(name=end_goal_name, blackboard=blackboard)
    # overall_feedback_sequence.add_child(end_goal)
    # Share goal between goal and end_goal
    blackboard.add_remapping(goal_node, 'new_goal', end_goal._id, 'goal')
    overall_feedback_sequence.add_child(end_goal)
    # negate_name = while_name + "_negate"
    # return Negate(name=negate_name, child=feedback_loop_while), feedback_behaviour, end_goal
    return overall_feedback_sequence, feedback_behaviour, end_goal


def main():
    loggingFilename = "" + participantNo + ".log"
    logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO, filename=loggingFilename)
    logging.info("Logging started")
    coaching_tree = create_coaching_tree()
    result = NodeStatus(NodeStatus.ACTIVE)

    while result == NodeStatus.ACTIVE:
        result = coaching_tree.tick()
        logging.debug(result)
        time.sleep(1)

def api_start():
    api_classes.app.run(host='0.0.0.0', port=5000)


if __name__ == '__main__':
    """
    Creates the behaviour tree and ticks through it until it completes.
    """
    # Start API
    x = threading.Thread(target=api_start)
    x.start()
    main()
    logging.debug("Continuing")
    x.join()



