import logging
import os
from abc import ABC
from datetime import time

import gym
from gym import spaces
import numpy as np
from typing import Optional
# from gym.utils.renderer import Renderer
from CoachingBehaviourTree import controller, nodes, config
from Policy.policy import Policy
from task_behavior_engine.tree import NodeStatus

from Policy.policy_wrapper import PolicyWrapper


class CoachingEnvironment(gym.Env, ABC):
    """
    A class which acts as an interface between the raw policy and the behaviour tree. It can give the tree a behaviour
    or observation generated by the policy which is within a set of defined valid behaviours for a given state.
    ...
    Attributes
    ----------
    Goal Levels :type int
        6 different goal levels which correspond to stages in the interaction and the goal hierarchy of the racketware
        guide.
    Phases :type int
        2 different phases (start and end) which correspond respectively to either an intro or feedback sequence.
    Performance Levels :type int
        8 different performance levels which represent how the user did in their previous action.
    policy
        The policy we will query to obtain behaviours and observations.

    Methods
    -------
    get_behaviour(state, goal_level, performance, phase)
        Obtain a behaviour from the underlying policy and check it is valid in the current state of interaction.
    _get_valid_list(goal_level, performance, phase)
        Local method which creates the list of valid for each state of interaction.
    get_observation(state, behaviour)
        Obtain an observation from the underlying policy.
    """
    def __init__(self, render_mode: Optional[str] = None):
        self.coaching_tree = controller.create_coaching_tree()
        self.observation_space = spaces.Discrete(69)
        self.action_space = spaces.Discrete(68)  # All the possible states but without A_START
        self.policy = None

    def reset(self, seed=None, return_info=False, options=None):
        # Will be called at the start of a new session, so load the policy from file, or choose policy if first session.
        super().reset(seed=seed)

        filename = "/home/martin/PycharmProjects/coachingPolicies/AdaptedPolicies/" + config.participant_filename
        if os.path.exists(filename):
            f = open(filename, "r")
            matrix = f.readlines()
            f.close()
            observation = 0
            self.policy = PolicyWrapper(policy=matrix)
        else:
            # TODO: check this is the correct measure for choosing the initial policy.
            belief_distribution = [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0] if config.ability < 4 else [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]
            observation = 0
            self.policy = PolicyWrapper(belief=belief_distribution)

        return observation, self.policy

    def _get_start(self, style):
        if style == 0:
            return 0
        elif style == 1:
            return 45
        elif style == 2:
            return 90
        elif style == 3:
            return 135
        elif style == 4:
            return 180
        elif style == 5:
            return 225
        elif style == 6:
            return 270
        elif style == 7:
            return 323
        elif style == 8:
            return 376
        elif style == 9:
            return 429
        elif style == 10:
            return 482
        else:
            return 535

    def step(self, action, state):

        done = False

        config.behaviour_displayed = False
        # config.behaviour = 1

        print("config.behaviour = " + str(config.behaviour))
        while not config.behaviour_displayed:  # Keep ticking the tree until a behaviour is given by the robot. This is the point the controller can select a new action and learn.
            result = self.coaching_tree.tick()
            if config.behaviour_displayed:
                print("Tree ticked, not returning: " + str(result))
            else:
                print("Tree ticked, returning: " + str(result))
            logging.debug(result)

        observation = self.policy.get_observation(state, action)
        reward = self._calculate_reward(action, observation, config.score, config.target)

        if action == config.A_END and config.goal_level == config.PERSON_GOAL:
            done = True

        return observation, reward, done, result

    def _calculate_reward(self, action, observation, score, target, performance):
        if score is None:
            return 0
        else:
            # Calculate reward based on how close score is to target
            if score == target:
                return 1
            elif score == 0:
                return -1
            elif score > target:
                return 0.5
            else:
                return -0.5

        # Option 1
        '''
        if score is None:
            if action == config.A_QUESTIONING and config.question_type = config.FEEDBACK_QUESTION:
                if config.question_feedback = 1:
                    return 0.2
                else:
                    return -0.2
            elif action == config.A_QUESTIONING or action == config.A_PRE-INSTRUCTION:
                if config.overriden:
                    return -1  # If policy's decision to select shots for user or have user select shots, is overriden, receive a large negative reward.
            else:
                return None  # No actions from user so reward is None and policy does not change.
        else:
            if score == target:
                return 1
            # Each shot and stat has a different target score so reward will have to be calculated individually.
            # This is just an example for racket face angle.
            else:
                if stat == "impactCutAngle":
                    difference = abs(target - score)
                    # For every degree away from target, reward decreases by 0.1 down to a maximum of -1.
                    reward = 1 - (difference * 0.1)
                    return -1 if reward < -1 else reward
                elif stat == "followThroughTime":
                    etc
        '''

        # Option 2
        '''
        if score is None:
            if action == config.A_QUESTIONING and config.question_type = config.FEEDBACK_QUESTION:
                if config.question_feedback = 1:
                    return 0.2
                else:
                    return -0.2
            elif action == config.A_QUESTIONING or action == config.A_PRE-INSTRUCTION:
                if config.overriden:
                    return -1  # If policy's decision to select shots for user or have user select shots, is overriden, receive a large negative reward.
            else:
                return None  # No actions from user so reward is None and policy does not change.
        else:
            # Reward becomes the absolute value of score as a percentage of target. More generalisable and consistent across stats.
            decimal = score/target
            if decimal > 1:
                decimal = 1 - (decimal - 1)  # Deal with case where the score is higher than the target.
            if decimal < 0:
                reward = -1  # If score is more than double the target, reward will be -1.
            else:
                reward = -1 + (decimal*2)  # return a reward between -1 and 1.
            return reward
        '''

        # Option 3
        '''
        if score is None:
            if action == config.A_QUESTIONING and config.question_type = config.FEEDBACK_QUESTION:
                if config.question_feedback = 1:
                    return 0.2
                else:
                    return -0.2
            elif action == config.A_QUESTIONING or action == config.A_PRE-INSTRUCTION:
                if config.overriden:
                    return -1  # If policy's decision to select shots for user or have user select shots, is overriden, receive a large negative reward.
            else:
                return None  # No actions from user so reward is None and policy does not change.
        else:
            # Reward is based on improvement since last time or since baseline set if this is the first time.
            if performance == config.MET:
                reward = 1
            elif performance == config.MUCH_IMPROVED:
                reward = 0.6
            elif performance == config.IMPROVED or performance == config.IMPROVED_SWAP:
                reward = 0.3
            elif performance == config.STEADY:
                reward = 0
            elif performance == config.REGRESSED or performance == config.REGRESSED_SWAP:
                reward = -0.3
            elif performance == config.MUCH_REGRESSED:
                reward = -0.6
                
            # Levels of performance:
            MET = 0             # Met the target
            MUCH_IMPROVED = 1   # Moved a lot closer to the target
            IMPROVED = 2        # Moved closer to the target
            IMPROVED_SWAP = 3   # Moved closer to the target but passed it
            STEADY = 4          # Stayed the same
            REGRESSED = 5       # Moved further away from the target
            REGRESSED_SWAP = 6  # Moved past the target and further from it
            MUCH_REGRESSED = 7  # Moved a lot further away from the target
        '''
