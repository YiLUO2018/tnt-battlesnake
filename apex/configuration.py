import json


class Configuration:

    def __init__(self, path):
        with open(path) as f:
            config = json.load(f)

            self.report_interval = config['report_interval']
            self.output_directory = config['output_directory']

            self.width = config['width']
            self.height = config['height']
            self.snakes = config['snakes']
            self.fruits = config['fruits']

            self.random_initial_steps = config['random_initial_steps']
            self.batch_size = config['batch_size']
            self.learning_rate = config['learning_rate']
            self.discount_factor = config['discount_factor']
            self.target_update_interval = config['target_update_interval']
            self.parameter_update_interval = config['parameter_update_interval']

            self.replay_capacity = config['replay_capacity']
            self.replay_min_priority = config['replay_min_priority']
            self.replay_max_priority = config['replay_max_priority']
            self.replay_prioritization_factor = config['replay_prioritization_factor']
            self.replay_importance_weight = config['replay_importance_weight']
            self.replay_importance_weight_annealing_step_size = config['replay_importance_weight_annealing_step_size']

            self.learner_ip_address = config['learner_ip_address']
            self.starting_port = config['starting_port']
            self.actors = config['actors']
            self.actor_buffer_size = config['actor_buffer_size']

    def get_num_actors(self):
        num_actors = 0
        actor_ip_addresses = self.actors.keys()
        for ip_address in actor_ip_addresses:
            num_actors += self.actors[ip_address]
        return num_actors
