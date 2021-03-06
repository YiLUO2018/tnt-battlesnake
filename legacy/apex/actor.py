from typing import List
import atexit
import logging
import pickle
import random
import zlib
import zmq

import numpy as np

from .models import Experience, Observation
from .utils import get_ip_address
from .configuration import Configuration
from .actor_statistics import ActorStatistics

LOGGER = logging.getLogger("Actor")


class AbstractActor:
    def __init__(
        self,
        config: Configuration,
        actor_idx: int,
        starting_port: int,
        tensorboard_logger,
    ):
        self.stats = ActorStatistics(config, actor_idx, tensorboard_logger)
        self.buffer: List[Observation] = list()
        self.episode_buffer: List[Observation] = list()
        self.config = config
        self.idx = actor_idx
        self.starting_port = starting_port
        self.epsilon = np.power(
            self.config.epsilon_base, (self.idx / self.config.get_num_actors()) * 7
        )
        LOGGER.info(f"Epsilon: {self.epsilon}")
        learner_address = config.learner_ip_address + ":" + config.starting_port
        self._connect_sockets(learner_address)

    def act(self, state, deterministic=False):
        if not deterministic and random.random() < self.epsilon:
            return np.random.choice(3), False
        else:
            return self._act(state)

    def _act(self, state):
        pass

    def observe(self, observation: Observation):
        self.episode_buffer.append(observation)
        self.stats.on_observe(observation)

        if observation.next_state is None:
            self.buffer += self._compute_multistep_bootstrap(self.episode_buffer)
            self.episode_buffer.clear()
            if len(self.buffer) >= self.config.actor_buffer_size:
                self.send_experiences()
                self.buffer.clear()

    def _update_parameters(self, message):
        pass

    def update_parameters(self):
        try:
            message = self.parameter_socket.recv_multipart(flags=zmq.NOBLOCK)
            return self._update_parameters(message)
        except zmq.Again:
            return False

    def _compute_errors(self):
        pass

    def send_experiences(self):
        errors = self._compute_errors()
        experiences = [
            Experience(observation, errors[idx])
            for idx, observation in enumerate(self.buffer)
        ]
        experiences_pickled = pickle.dumps(experiences, -1)
        experiences_compressed = zlib.compress(experiences_pickled)
        self.experience_socket.send_multipart([b"experiences", experiences_compressed])

    def _compute_multistep_bootstrap(self, episode_observations: List[Observation]):
        episode_length = len(episode_observations)
        for idx, obs in enumerate(episode_observations):
            multi_step_reward = obs.reward
            nth_observation = obs
            n = 0
            for i in range(1, self.config.multi_step_n):
                if idx + i < episode_length and nth_observation.greedy:
                    multi_step_reward += (
                        np.power(self.config.discount_factor, i)
                        * episode_observations[idx + i].reward
                    )
                    nth_observation = episode_observations[idx + i]
                    n = i
                else:
                    break
            obs.reward = multi_step_reward
            obs.discount_factor = np.power(
                self.config.discount_factor, np.amin([self.config.multi_step_n, n + 1])
            )
            obs.next_state = nth_observation.next_state
        return episode_observations

    def _connect_sockets(self, learner_address: str):
        self.context = zmq.Context()
        self.parameter_socket = self.context.socket(zmq.SUB)
        self.parameter_socket.setsockopt(zmq.LINGER, 0)
        self.parameter_socket.connect(f"tcp://{learner_address}")
        self.parameter_socket.setsockopt(zmq.SUBSCRIBE, b"parameters")
        LOGGER.info(f"Connected socket to learner at {learner_address}")

        self.experience_socket = self.context.socket(zmq.PUB)
        self.experience_socket.setsockopt(zmq.LINGER, 0)
        ip_address = get_ip_address()
        port = self.starting_port + self.idx
        self.experience_socket.bind(f"tcp://{ip_address}:{port}")
        LOGGER.info(f"Created socket at {ip_address}:{port}")
        atexit.register(self._disconnect_sockets)

    def _disconnect_sockets(self):
        self.experience_socket.close()
        self.parameter_socket.close()
        self.context.term()
