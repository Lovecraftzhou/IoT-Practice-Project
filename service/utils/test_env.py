"""
Classic cart-pole system implemented by Rich Sutton et al.
Copied from http://incompleteideas.net/sutton/book/code/pole.c
permalink: https://perma.cc/C9ZM-652R
"""
import math
from typing import Optional, Union
import os

os.environ['KMP_DUPLICATE_LIB_OK']='True'

import numpy as np
#import pygame
#from pygame import gfxdraw

import gym
from gym import spaces, logger
from gym.utils import seeding
import torch
import random


class testEnv():
    def __init__(self):
        self.state_num = 6
        self.action_num = 4
        self.state = np.array([1])
        self.action_space = spaces.Discrete(self.action_num)
        high = np.array([self.state_num])
        low =  np.array([0])
        self.observation_space = spaces.Box(
            low=low,
            high=high
        )

    def step(self, action):
        err_msg = f"{action!r} ({type(action)}) invalid"
        assert self.action_space.contains(action), err_msg
        assert self.state is not None, "Call reset before using step method."
        done = False
        self.state[0] += 1
        if self.state[0] >= self.state_num - 1:
            done = True
        reward = -1
        if not done:
            # fixed_reward = 1
            # if action == 0:
            #     reward = fixed_reward - 2
            # if action == 1:
            #     reward = fixed_reward - 3
            # if action == 2:
            #     reward = fixed_reward - 4
            # if action == 3:
            #     reward = fixed_reward - 5
            fixed_reward = -1
            if action == 0:
                reward = fixed_reward - random.uniform(-0.2, 0.2) -1-random.uniform(-0.3, 0.3)
            if action == 1:
                reward = fixed_reward - random.uniform(-0.2, 0.2)
            if action == 2:
                reward = -4 - random.uniform(-1, 1)-5-random.uniform(-1, 1)
            if action == 3:
                reward = -random.uniform(-0.2, 0.2)-1-random.uniform(-0.5, 0.5)
            self.state[0] = max(self.state[0] - action, 0)
        if self.state[0] >= self.state_num - 1:
            done = True
        return self.state, reward, done

    def reset(self):
        self.state = np.array([0])
        return self.state