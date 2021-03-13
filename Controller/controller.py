from datetime import time

from task_behavior_engine.branch import Sequencer, Selector
from task_behavior_engine.decorator import Until, While, Negate, Repeat
from task_behavior_engine.tree import NodeStatus, Blackboard

from Controller.behavior_tree import CoachingTree
from Policy.policy import Policy
from Policy.policy_wrapper import PolicyWrapper

SHOT_CHOICE = 0
STAT_CHOICE = 1

def create_coaching_tree():
    b = Blackboard()
    root = Sequencer("coaching root", blackboard=b)

    # Player stats
    player_stats = GetStats(name="player_stats")
    player_stats_until = Until(name="player_stats_until", child=player_stats)
    root.add_child(player_stats_until)

    # Session duration
    duration = GetDuration(name="duration")
    root.add_child(duration)

    #
    #
    #
    # Conduct session
    #
    #
    #
    gen_session_goal = Sequencer(name="gen_session_goal")

    #
    #
    # Create session goal in guide
    #
    #
    session_goal = CreateSubgoal(name="create_session_goal")
    gen_session_goal.add_child(session_goal)

    #
    #
    # Wait for timestep cue (i.e. session goal has been created by guide and we are ready for intro.
    #
    #
    session_goal_start = TimestepCue(name="session_goal_started_timestep")
    session_goal_start_until = Until(name="session_goal_start_until", child=session_goal_start)
    gen_session_goal.add_child(session_goal_start_until)

    #
    #
    # Display behaviours until pre-instruction or questioning
    #
    #
    session_goal_intro_sequence = Sequencer(name="session_goal_intro_sequence")

    # Get behaviour from policy
    session_goal_intro_behav = GetBehaviour(name="session_goal_intro_behaviour")
    session_goal_intro_sequence.add_child(session_goal_intro_behav)

    # Check if pre-instruction
    session_goal_intro_check_for_pre = CheckForBehaviour(name="session_goal_intro_check_for_pre", behaviour=Policy.A_PREINSTRUCTION)
    session_goal_intro_pre_instr_negate = Negate(name="session_goal_intro_pre_instr_negate", child=session_goal_intro_check_for_pre)
    session_goal_intro_sequence.add_child(session_goal_intro_pre_instr_negate)

    # Check if questioning
    session_goal_intro_questioning_sequence = Sequencer(name="session_goal_intro_questioning_sequence")
    session_goal_intro_check_for_questioning = CheckForBehaviour(name="session_goal_intro_check_for_questioning", beavhiour=Policy.A_QUESTIONING)
    session_goal_intro_questioning_sequence.add_child(session_goal_intro_check_for_questioning)
    session_goal_shot_choice = GetUserChoice(name="session_goal_shot_choice", choice_type=SHOT_CHOICE)
    session_goal_intro_questioning_sequence.add_child(session_goal_shot_choice)
    session_goal_intro_questioning_negate = Negate(name="session_goal_intro_questioning_negate", child=session_goal_intro_questioning_sequence)
    session_goal_intro_sequence.add_child(session_goal_intro_questioning_negate)

    # Display selected behaviour if not pre-instruction or questioning
    session_goal_intro_output = DisplayBehaviour(name="session_goal_intro_output")
    session_goal_intro_sequence.add_child(session_goal_intro_output)

    session_goal_intro_while = While(name="session_goal_intro_while", child=session_goal_intro_sequence)
    gen_session_goal.add_child(session_goal_intro_while)

    #
    #
    # Session loop until chosen session duration is reached
    #
    #
    session_goal_selector = Selector(name="session_goal_selector")

    # Check if session duration has been reached
    session_time_reached = DurationCheck(name="session_time_reached")
    session_goal_selector.add_child(session_time_reached)

    #
    # Conduct coaching for a shot
    #
    gen_shot_goal = Sequencer(name="gen_shot_goal")

    # Create shot goal in guide
    shot_goal = CreateSubgoal(name="create_shot_goal")
    gen_shot_goal.add_child(shot_goal)

    # Wait for timestep cue (i.e. shot goal has been created by guide and we are ready for intro.
    shot_goal_start = TimestepCue(name="shot_goal_started_timestep")
    shot_goal_start_until = Until(name="shot_goal_start_until", child=shot_goal_start)
    gen_session_goal.add_child(shot_goal_start_until)

    #
    # Display intro shot behaviours until pre-instruction or questioning
    #
    shot_goal_intro_sequence = Sequencer(name="shot_goal_intro_sequence")

    # Get behaviour from policy
    shot_goal_intro_behav = GetBehaviour(name="shot_goal_intro_behaviour")
    shot_goal_intro_sequence.add_child(shot_goal_intro_behav)

    # Check if pre-instruction
    shot_goal_intro_pre_instr_sequence = Sequencer(name="shot_goal_intro_pre_instr_sequence")
    shot_goal_intro_check_for_pre = CheckForBehaviour(name="shot_goal_intro_check_for_pre", behaviour=Policy.A_PREINSTRUCTION)
    shot_goal_intro_pre_instr_sequence.add_child(shot_goal_intro_check_for_pre)
    # If pre-instruction is selected run baseline set to make decision of stat choice
    gen_baseline_goal = Sequencer(name="gen_baseline_goal")
    # Create baseline goal
    baseline_goal = CreateSubgoal(name="create_baseline_goal")
    gen_baseline_goal.add_child(baseline_goal)
    # Wait for timestep cue (i.e. baseline goal has been created by guide and we are ready for intro.
    baseline_goal_start = TimestepCue(name="baseline_goal_started_timestep")
    baseline_goal_start_until = Until(name="baseline_goal_start_until", child=baseline_goal_start)
    gen_baseline_goal.add_child(baseline_goal_start_until)
    # Display baseline pre-instruction behaviour
    baseline_goal_intro = DisplayBehaviour(name="baseline_goal_intro")
    gen_baseline_goal.add_child(baseline_goal_intro)
    # Wait for user to finish set
    baseline_goal_end_set_event = EndSetEvent(name="baseline_goal_end_set_event")
    baseline_goal_end_set_until = Until(name="baseline_goal_end_set_until", child=baseline_goal_end_set_event)
    gen_baseline_goal.add_child(baseline_goal_end_set_until)
    shot_goal_intro_pre_instr_negate = Negate(name="shot_goal_intro_pre_instr_negate", child=shot_goal_intro_pre_instr_sequence)
    shot_goal_intro_sequence.add_child(shot_goal_intro_pre_instr_negate)

    # Check if questioning
    shot_goal_intro_questioning_sequence = Sequencer(name="shot_goal_intro_questioning_sequence")
    shot_goal_intro_check_for_questioning = CheckForBehaviour(name="shot_goal_intro_check_for_questioning", beavhiour=Policy.A_QUESTIONING)
    shot_goal_intro_questioning_sequence.add_child(shot_goal_intro_check_for_questioning)
    shot_goal_stat_choice = GetUserChoice(name="shot_goal_stat_choice", choice_type=STAT_CHOICE)
    shot_goal_intro_questioning_sequence.add_child(shot_goal_stat_choice)
    shot_goal_intro_questioning_negate = Negate(name="shot_goal_intro_questioning_negate", child=shot_goal_intro_questioning_sequence)
    shot_goal_intro_sequence.add_child(shot_goal_intro_questioning_negate)

    # Display selected behaviour if not pre-instruction or questioning
    shot_goal_intro_output = DisplayBehaviour(name="shot_goal_intro_output")
    shot_goal_intro_sequence.add_child(shot_goal_intro_output)

    #
    # Conduct coaching for stat
    #
    gen_stat_goal = Sequencer(name="gen_stat_goal")

    # Create stat goal in guide
    stat_goal = CreateSubgoal(name="create_stat_goal")
    gen_stat_goal.add_child(stat_goal)

    # Wait for timestep cue (i.e. stat goal has been created by guide and we are ready for intro.
    stat_goal_start = TimestepCue(name="stat_goal_started_timestep")
    stat_goal_start_until = Until(name="stat_goal_start_until", child=stat_goal_start)
    gen_stat_goal.add_child(stat_goal_start_until)

    # Display pre-instruction behaviour
    stat_goal_intro_output = DisplayBehaviour(name="stat_goal_intro_output")
    gen_stat_goal.add_child(stat_goal_intro_output)

    # Loop through 4 sets of shot
    stat_goal_coaching = Sequencer(name="stat_goal_coaching")

    #
    # Conduct coaching for set
    #
    gen_set_goal = Sequencer(name="gen_set_goal")

    # Create set goal in guide
    set_goal = CreateSubgoal(name="create_set_goal")
    gen_set_goal.add_child(set_goal)

    # Wait for timestep cue (i.e. set goal has been created by guide and we are ready for intro.
    set_goal_start = TimestepCue(name="set_goal_started_timestep")
    set_goal_start_until = Until(name="set_goal_start_until", child=set_goal_start)
    gen_set_goal.add_child(set_goal_start_until)

    # Display intro set behaviours until pre-instruction
    set_goal_intro_sequence = Sequencer(name="set_goal_intro_sequence")

    # Get behaviour from policy
    set_goal_intro_behav = GetBehaviour(name="set_goal_intro_behaviour")
    set_goal_intro_sequence.add_child(set_goal_intro_behav)

    # Check if pre-instruction
    set_goal_intro_check_for_pre_instr = CheckForBehaviour(name="set_goal_intro_check_for_pre_instr", behaviour=Policy.A_PREINSTRUCTION)
    set_goal_intro_pre_instr_negate = Negate(name="set_goal_intro_pre_instr_negate", child=set_goal_intro_check_for_pre_instr)
    set_goal_intro_sequence.add_child(set_goal_intro_pre_instr_negate)

    # Display selected behaviour if not pre-instruction or questioning
    set_goal_intro_output = DisplayBehaviour(name="set_goal_intro_output")
    set_goal_intro_sequence.add_child(set_goal_intro_output)

    set_goal_intro_while = While(name="set_goal_intro_while", child=set_goal_intro_sequence)
    gen_set_goal.add_chil(set_goal_intro_while)

    # Display pre-instruction behaviour for set
    set_goal_pre_instr_intro_output = DisplayBehaviour(name="set_goal_pre_instr_intro_output")
    gen_set_goal.add_child(set_goal_pre_instr_intro_output)

    # Coaching loop fpr set until user initiates end of set event
    set_goal_coaching_selector = Selector(name="set_goal_coaching_selector")

    # Check for user ending set event
    set_goal_end_set_event = EndSetEvent(name="set_goal_end_set_event")
    set_goal_coaching_selector.add_child(set_goal_end_set_event)

    # Individual action coaching loop
    set_goal_individual_action_sequence = Sequencer(name="set_goal_individual_action_sequencer")
    # Wait for timestep cue (i.e. user performs action/hits shot)
    set_goal_individual_action_cue = TimestepCue(name="set_goal_individual_action_cue")
    set_goal_individual_action_until = Until(name="set_goal_individual_action_until", child=set_goal_individual_action_cue)
    set_goal_individual_action_sequence.add_child(set_goal_individual_action_until)
    # Get coaching behaviour from policy for individual action/shot
    set_goal_individual_action_behav = GetBehaviour(name="set_goal_individual_action_behaviour")
    set_goal_individual_action_sequence.add_child(set_goal_individual_action_behav)
    # Display individual action caoching behaviour
    set_goal_individual_action_output = DisplayBehaviour(name="set_goal_individual_action_output")
    set_goal_individual_action_sequence.add_child(set_goal_individual_action_output)

    set_goal_individual_action_repeat = Repeat(name="set_goal_individual_action_repeat", child=set_goal_individual_action_sequencer)
    set_goal_coaching_selector.add_child(set_goal_individual_action_repeat)

    set_goal_coaching_until = Until(name="set_goal_coaching_until", child=set_goal_coaching_selector)
    gen_set_goal.add_child(set_goal_coaching_until)

    stat_goal_coaching.add_child(gen_set_goal)

    # Set feedback loop until pre-instruction
    set_goal_feedback_loop = get_feedback_loop(name="set_goal_feedback_loop", behav=Policy.A_PREINSTRUCTION)
    stat_goal_coaching.add_child(set_goal_feedback_loop)

    stat_goal_coaching_until_count = UntilCount(name="stat_goal_coaching_until_count", max_count=4, child=stat_goal_coaching)
    gen_stat_goal.add_child(stat_goal_coaching_until_count)

    # Stat feedback loop until pre-instruction
    stat_goal_feedback_loop = get_feedback_loop(name="stat_goal_feedback_loop", behav=Policy.A_PREINSTRUCTION)
    gen_stat_goal.add_child(stat_goal_feedback_loop)

    stat_goal_until_count = UntilCount(name="state_goal_until_count", max_count=2, child=gen_stat_goal)
    gen_shot_goal.add_child(stat_goal_until_count)

    # Shot feedback loop until pre-instruction
    shot_goal_feedback_loop = get_feedback_loop(name="shot_goal_feedback_loop", behav=Policy.A_PREINSTRUCTION)
    gen_shot_goal.add_child(shot_goal_feedback_loop)

    shot_goal_repeat = Repeat(name="shot_goal_repeat", child=gen_shot_goal)
    session_goal_selector.add_child(shot_goal_repeat)

    session_goal_until = Until(name="session_goal_until", child=session_goal_selector)
    gen_session_goal.add_child(session_goal_until)

    #
    # Session goal feedback loop
    #
    session_goal_feedback_loop = get_feedback_loop(name="session_goal_feedback_loop", behav=Policy.A_END)
    gen_session_goal.add_child(session_goal_feedback_loop)

    root.add_child(gen_session_goal)
    return root

def get_feedback_loop(name, behav):
    # Create feedback loop sequencer
    sequence_name = name + "_sequence"
    feedback_loop_sequence = Sequencer(name=sequence_name)

    # Get behaviour from policy
    feedback_behaviour_name = name + "_behav"
    feedback_behaviour = GetBehaviour(name=feedback_behaviour_name)
    feedback_loop_sequence.add_child(feedback_behaviour)

    # Check if given behaviour
    check_behav_name = name + "_check_for_" + behav
    feedback_loop_check_for_behav = CheckForBehaviour(name=check_behav_name, behaviour=behav)
    negate_name = name + "_" + behav + "_check_negate"
    feedback_loop_behav_check_negate = Negate(name=negate_name)
    # If pre-instruction, just negate behaviour check
    if behav == Policy.A_PREINSTRUCTION:
        feedback_loop_behav_check_negate.add_child(feedback_loop_check_for_behav)
    else:  # If end, do the check and then display the behaviour
        feedback_loop_end_sequence = Sequencer(name="feedback_loop_end_sequence")
        feedback_loop_end_sequence.add_child(feedback_loop_check_for_behav)
        feedback_loop_display_end_output = DisplayBehaviour(name="feedback_loop_display_end_output")
        feedback_loop_end_sequence.add_child(feedback_loop_display_end_output)
        feedback_loop_behav_check_negate.add_child(feedback_loop_end_sequence)

    feedback_loop_sequence.add_child(feedback_loop_behav_check_negate)

    # Display behaviour if not given behaviour
    output_name = name + "_output"
    feedback_loop_output = DisplayBehaviour(name=output_name)
    feedback_loop_sequence.add_child(feedback_loop_output)

    while_name = name + "_while"
    return While(name=while_name, child=feedback_loop_sequence)


if __name__ == '__main__':
    coaching_tree = create_coaching_tree()
    result = NodeStatus(NodeStatus.ACTIVE)

    while result == NodeStatus.ACTIVE:
        result = coaching_tree.tick()
        print(result)
        time.sleep(0.1)
