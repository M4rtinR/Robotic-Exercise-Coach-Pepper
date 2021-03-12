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

    # Wait for timestep cue (i.e. session goal has been created by guide and we are ready for intro.
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
    basline_goal = CreateSubgoal(name="create_baseline_goal")
    gen_baseline_goal.add_child(basline_goal)
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

    shot_goal_repeat = Repeat(name="shot_goal_repeat", child=gen_shot_goal)
    gen_session_goal.add_child(shot_goal_repeat)

    session_goal_until = Until(name="session_goal_until", child=session_goal+session_goal_selector)
    gen_session_goal.add_child(session_goal_until)

    #
    # Session goal feedback loop
    #

    root.add_child(gen_session_goal)
    return root


if __name__ == '__main__':
    coaching_tree = create_coaching_tree()
    result = NodeStatus(NodeStatus.ACTIVE)

    while result == NodeStatus.ACTIVE:
        result = coaching_tree.tick()
        print(result)
        time.sleep(0.1)
