import os
import sys


#if "SUMO_HOME" in os.environ:
#    tools = os.path.join(os.environ["SUMO_HOME"], "tools")
#    sys.path.append(tools)
#else:
#    sys.exit("Please declare the environment variable 'SUMO_HOME'")
import numpy as np
import pandas as pd
import ray
import libsumo as traci
from ray import tune
from ray.rllib.algorithms.ppo import PPOConfig
from ray.rllib.env.wrappers.pettingzoo_env import ParallelPettingZooEnv
from ray.tune.registry import register_env
import supersuit as ss

#import sumo_rl
import ma_environment.env as custom_env

if __name__ == "__main__":
    ray.init()

    env_name = "MA_grid"

    register_env(
        env_name,
        lambda _: ParallelPettingZooEnv(
            custom_env.parallel_env(
                net_file='urban_mobility_simulation/models/20230718_sumo_ma/osm.net_1.xml, \
                        urban_mobility_simulation/models/20230718_sumo_ma/pt/gtfs_pt_stops.add.xml, \
                        urban_mobility_simulation/models/20230718_sumo_ma/pt/stops.add.xml, \
                        urban_mobility_simulation/models/20230718_sumo_ma/pt/vtypes.xml, \
                        urban_mobility_simulation/models/20230718_sumo_ma/osm.poly.xml',
                route_file='urban_mobility_simulation/models/20230718_sumo_ma/routes_nm.xml, \
                            urban_mobility_simulation/models/20230718_sumo_ma/bicycle_routes.xml, \
                            urban_mobility_simulation/models/20230718_sumo_ma/trucks_routes.xml, \
                            urban_mobility_simulation/models/20230718_sumo_ma/motorcycle_routes.xml, \
                            urban_mobility_simulation/models/20230718_sumo_ma/pt/gtfs_pt_vehicles.add.xml',
                out_csv_name='urban_mobility_simulation/src/data/model_outputs/0801_MA_test',
                use_gui=False,
                num_seconds=80000,
                begin_time=19800,
                time_to_teleport=300,
                additional_sumo_cmd="--scale 0.5"
            )
        ),
    )

    config = (
        PPOConfig()
        .environment(env=env_name, disable_env_checking=True)
        .rollouts(num_rollout_workers=4, rollout_fragment_length=128)
        .training(
            train_batch_size=512,
            lr=2e-5,
            gamma=0.95,
            lambda_=0.9,
            use_gae=True,
            clip_param=0.4,
            grad_clip=None,
            entropy_coeff=0.1,
            vf_loss_coeff=0.25,
            sgd_minibatch_size=64,
            num_sgd_iter=10,
        )
        .debugging(log_level="ERROR")
        .framework(framework="torch")
        .resources(num_gpus=int(os.environ.get("RLLIB_NUM_GPUS", "0")))
    )

    tune.run(
        "PPO",
        name="PPO",
        stop={"timesteps_total": 100000},
        checkpoint_freq=10,
        local_dir="~/ray_results/" + env_name,
        config=config.to_dict(),
    )
