import os
import sys

import gym
import numpy as np

import platform
# on the server (platform = Linux) we use libsumo and also don't need the tools in the path
# if platform.system() != "Linux":
#     if 'SUMO_HOME' in os.environ:
#         tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
#         sys.path.append(tools)  # we need to import python modules from the $SUMO_HOME/tools directory
#     else:
#         sys.exit("please declare environment variable 'SUMO_HOME'")
#     import traci
# else:
import libsumo as traci

from sumolib import checkBinary

from stable_baselines3.ppo.ppo import PPO

#from sumo_rl import SumoEnvironment
from environment.env import SumoEnvironment


env = SumoEnvironment(
    net_file="urban_mobility_simulation/models/20230502_SUMO_MA/osm.net.xml, \
            urban_mobility_simulation/models/20230502_SUMO_MA/pt/stops.add.xml, \
            urban_mobility_simulation/models/20230502_SUMO_MA/osm.poly.xml",
    single_agent=True,
    route_file="urban_mobility_simulation/models/20230502_SUMO_MA/routes.xml, \
               urban_mobility_simulation/models/20230502_SUMO_MA/osm.bicycle.trips.xml,\
            urban_mobility_simulation/models/20230502_SUMO_MA/osm.motorcycle.trips.xml,\
                urban_mobility_simulation/models/20230502_SUMO_MA/osm.truck.trips.xml, \
               urban_mobility_simulation/models/20230502_SUMO_MA/pt/ptflows.rou.xml, \
                urban_mobility_simulation/models/20230502_SUMO_MA/osm.passenger.trips.xml", 
    out_csv_name="urban_mobility_simulation/src/data/model_outputs/ppo_orig_1",
    use_gui=False,
    num_seconds=43200,
    yellow_time=4,
    min_green=5,
    max_green=60,
    time_to_teleport=300,
    fixed_ts=False,
#    additional_sumo_cmd="--scale 0.75",
#    begin_time=10000,
)

model = PPO(
    env=env,
    policy="MultiInputPolicy",
    verbose=3,
    gamma=0.95,
    n_steps=256,
    ent_coef=0.0905168,
    learning_rate=0.00062211,
    vf_coef=0.042202,
    max_grad_norm=0.9,
    gae_lambda=0.99,
    n_epochs=5,
    clip_range=0.3,
    batch_size=256,
)

# Paths:
save_path = 'PPO_20000_orig_1'
log_path = 'Logs_1'

print(env.observation_space)
print(env.action_space)
print(env.action_space.sample())

model.learn(total_timesteps=43200)

model.save(save_path)


