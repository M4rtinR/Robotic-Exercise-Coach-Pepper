from policy import Policy
import random
import numpy as np

def constrainedSumSamplePos(n, total, rangeGap):
    """Return a randomly chosen list of n positive integers summing to total.
    Each such list is equally likely to occur."""
    numpyRange = np.arange(0.0, total, rangeGap)
    range = np.ndarray.tolist(numpyRange)
    dividers = sorted(random.sample(range, n - 1))
    return [a - b for a, b in zip(dividers + [total], [0.0] + dividers)]

def constrainedSumSampleNonneg(n, total, rangeGap):
    """Return a randomly chosen list of n nonnegative integers summing to total.
    Each such list is equally likely to occur."""

    return [x - rangeGap for x in constrainedSumSamplePos(n, total + (n * rangeGap), rangeGap)]


if __name__ == '__main__':
    style_distribution = [x / 100 for x in constrainedSumSamplePos(12, 100, 0.001)]
    print('style_distribution =', style_distribution)
    p = Policy(style_distribution)

    # change to start in max of style_distribution
    observation = 0

    for i in range(15):
        action = p.sample_action(observation)
        print('i =', 0)
        print('action =', action)
        observation = p.sample_observation(observation, action)
        print('observation =', observation)
        print('/n/n')
