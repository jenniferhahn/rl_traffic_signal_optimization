import os
import sys

import platform
if platform.system() != "Linux":
    if 'SUMO_HOME' in os.environ:
        tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
        sys.path.append(tools)  # we need to import python modules from the $SUMO_HOME/tools directory
    else:
        sys.exit("please declare environment variable 'SUMO_HOME'")
    import traci
else:
    import libsumo as traci

import numpy as np
import pandas as pd
import ray
import traci
from ray import tune
#from ray.rllib.algorithms.ppo import PPOConfig
from ray.rllib.algorithms.ppo import (
    PPOConfig,
    PPOTF1Policy,
    PPOTF2Policy,
    PPOTorchPolicy,
)
from ray.rllib.env.wrappers.pettingzoo_env import ParallelPettingZooEnv, PettingZooEnv
from ray.tune.registry import register_env
from ray.tune.logger import pretty_print

from stable_baselines3.common.evaluation import evaluate_policy
from stable_baselines3 import PPO

import ma_environment.custom_envs as custom_env
import supersuit as ss


def env_creator(args):
        env = custom_env.MA_grid_new(
                    net_file = "/Users/jenniferhahn/Documents/GitHub/urban_mobility_simulation/models/20230718_sumo_ma/osm.net.xml, \
                                /Users/jenniferhahn/Documents/GitHub//urban_mobility_simulation/models/20230718_sumo_ma/pt/gtfs_pt_stops.add.xml, \
                                /Users/jenniferhahn/Documents/GitHub/urban_mobility_simulation/models/20230718_sumo_ma/pt/stops.add.xml, \
                                /Users/jenniferhahn/Documents/GitHub/urban_mobility_simulation/models/20230718_sumo_ma/pt/vtypes.xml, \
                                /Users/jenniferhahn/Documents/GitHub/urban_mobility_simulation/models/20230718_sumo_ma/osm.poly.xml",
                    route_file ="/Users/jenniferhahn/Documents/GitHub/urban_mobility_simulation/models/20230718_sumo_ma/veh_routes.xml, \
                                /Users/jenniferhahn/Documents/GitHub/urban_mobility_simulation/models/20230718_sumo_ma/pt/gtfs_pt_vehicles.xml, \
                                /Users/jenniferhahn/Documents/GitHub/urban_mobility_simulation/models/20230718_sumo_ma/truck_routes.xml, \
                                /Users/jenniferhahn/Documents/GitHub/urban_mobility_simulation/models/20230718_sumo_ma/bicycle_routes.xml, \
                                /Users/jenniferhahn/Documents/GitHub/urban_mobility_simulation/models/20230718_sumo_ma/motorcycle_routes.xml",
                    out_csv_name='/Users/jenniferhahn/Documents/GitHub/urban_mobility_simulation/src/data/model_outputs/MA_grid_emissionAllTest',
                    use_gui=False,
                    num_seconds=30000,
                    begin_time=19800,
                    time_to_teleport=300,
                    reward_fn='combined_emission',
                    sumo_warnings=False)
        return env
    
    
def select_policy(framework):
        if framework == "torch":
            return PPOTorchPolicy
        elif framework == "tf":
            return PPOTF1Policy
        else:
            return PPOTF2Policy
        
def policy_mapping_fn(agent_id, episode, worker, **kwargs):
        return "ppo_policy"


if __name__ == "__main__":
    ray.init()
   
    env_name = "MA_grid_new"

    # register env
    register_env(env_name, lambda config: ParallelPettingZooEnv(env_creator(config)))
    # create env
    env = ParallelPettingZooEnv(env_creator({}))
    #get obs and action space
    obs_space = env.observation_space
    act_space = env.action_space
    

    
    config = (
        PPOConfig()
        .environment(env=env_name, disable_env_checking=True)
        .rollouts(num_rollout_workers=3, rollout_fragment_length='auto')
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
        # .multiagent(
        #     policies=env.get_agent_ids(),
        #     policy_mapping_fn=policy_mapping_fn#(lambda agent_id, *args, **kwargs: agent_id)
        # )
        # .multiagent(
        #     policies={id: (PPOTF1Policy, env.observation_spaces[id], env.action_spaces[id], {}) for id in env.agents},
        #     policy_mapping_fn= (lambda id: id) 
        #)
        .debugging(log_level="ERROR")
        .framework(framework="torch")
        .resources(num_gpus=int(os.environ.get("RLLIB_NUM_GPUS", "2")))
        .evaluation(evaluation_num_workers=1)
    )
    
    algo = config.build()  # 2. build the algorithm,

    for _ in range(10):
        print(algo.train())  # 3. train it,

    algo.evaluate()  # 4. and evaluate it.
    
    # tune.Tuner(
    #     "PPO",
    #     #name="PPO",
    #     stop={"timesteps_total": 100000},
    #     checkpoint_freq=10,
    #     local_dir="~/ray_results/" + env_name,
    #     config=config.to_dict(),
    # ).fit()
    
    
    # policies = {'ppo_policy':(
    #             select_policy('torch'),
    #             obs_space,
    #             act_space,
    #             config,
    #         )}
    
    
    # config.multi_agent(
    #         policies=policies,
    #         policy_mapping_fn=policy_mapping_fn,
    #         policies_to_train=["ppo_policy"]
    # )
    
    #ppo = config.build()
    
    # tune.run(
    #     "PPO",
    #     name="PPO",
    #     stop={"timesteps_total": 100000},
    #     checkpoint_freq=10,
    #     local_dir="~/ray_results/" + env_name,
    #     config=config.to_dict(),
    #)#.fit()
    
    # results = tune.Tuner(
    # args.run,
    # run_config=air.RunConfig(
    #     stop=stop,
    # ),
    # param_space=config,
    # ).fit()

    # if not results:
    #     raise ValueError(
    #         "No results returned from tune.run(). Something must have gone wrong."
    #     )
    
    ray.shutdown()

    # print("Starting training")
    # model.learn(total_timesteps=50000)
    
    # print("Training finished. Starting evaluation")
    # mean_reward, std_reward = evaluate_policy(model, env, n_eval_episodes=1)

    # print(mean_reward)
    # print(std_reward)

    
    
    
    # trainer = PPOConfig(env="4x4grid", config={
    #     "multiagent": {
    #         "policies": {
    #             id: (PPO, env.observation_spaces[id], env.action_spaces[id], {}) for id in env.agents
    #         },
    #         "policy_mapping_fn": (lambda id: id)  # Traffic lights are always controlled by this policy
    #     },
    #     "lr": 0.001,
    #     "no_done_at_end": True
    # })
    



