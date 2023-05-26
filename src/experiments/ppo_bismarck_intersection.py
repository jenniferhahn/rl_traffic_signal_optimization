import os
import sys

import gym


if "SUMO_HOME" in os.environ:
    tools = os.path.join(os.environ["SUMO_HOME"], "tools")
    sys.path.append(tools)
else:
    sys.exit("Please declare the environment variable 'SUMO_HOME'")
import numpy as np
import traci
from stable_baselines3.ppo.ppo import PPO

from sumo_rl import SumoEnvironment


env = SumoEnvironment(
    net_file="urban_mobility_simulation/models/20230502_SUMO_MA/osm.net.xml",
    single_agent=True,
    route_file="urban_mobility_simulation/models/20230502_SUMO_MA/routes.xml, \
                urban_mobility_simulation/models/20230502_SUMO_MA/osm.bicycle.trips.xml,\
                urban_mobility_simulation/models/20230502_SUMO_MA/osm.motorcycle.trips.xml,\
                urban_mobility_simulation/models/20230502_SUMO_MA/osm.truck.trips.xml", \
                #urban_mobility_simulation/models/20230502_SUMO_MA/pt/test_flow.rou.xml",
    out_csv_name="urban_mobility_simulation/src/data/model_outputs/ppo_woPT",
    use_gui=True,
    num_seconds=5000,
    yellow_time=4,
    min_green=5,
    max_green=60,
)
model = PPO(
    env=env,
    policy="MlpPolicy",
    learning_rate=3e-4,
    verbose=1,
    

)

model.learn(total_timesteps=5000)
