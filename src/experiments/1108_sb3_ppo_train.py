import os
import shutil
import subprocess

import numpy as np
import supersuit as ss
import traci
from pyvirtualdisplay.smartdisplay import SmartDisplay
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import EvalCallback
from stable_baselines3.common.evaluation import evaluate_policy
from stable_baselines3.common.vec_env import VecMonitor
from tqdm import trange

import ma_environment.custom_envs as custom_env
#import sumo_rl


if __name__ == "__main__":
    #RESOLUTION = (3200, 1800)

    #env = sumo_rl.grid4x4(use_gui=False, out_csv_name="outputs/grid4x4/ppo_test", virtual_display=RESOLUTION,sumo_warnings=False)

    #env = ss.multiagent_wrappers.pad_observations_v0(env)
    #env = ss.multiagent_wrappers.pad_action_space_v0(env)


    #print("Environment created")

    # env = ss.multiagent_wrappers.pad_observations_v0(env)
    # env = ss.pad_action_space_v0(env)
    # env = ss.concat_vec_envs_v1(env, 2, num_cpus=1, base_class="stable_baselines3")
    # env = VecMonitor(env)
    
    env = custom_env.MA_grid_new(reward_fn='CO2_emission',
                                 use_gui=False,
                                 sumo_warnings=False,
                                 out_csv_name='/Users/jenniferhahn/Documents/GitHub/urban_mobility_simulation/src/data/model_outputs/CO2_emission_200000',
                                 additional_sumo_cmd="--emission-output /Users/jenniferhahn/Documents/GitHub/urban_mobility_simulation/src/data/model_outputs/1308_ppo_test_emission.xml")
    max_time = env.unwrapped.env.sim_max_time
    delta_time = env.unwrapped.env.delta_time
    env = ss.pad_observations_v0(env)
    env = ss.pad_action_space_v0(env)
    env = ss.pettingzoo_env_to_vec_env_v1(env)
    env = ss.concat_vec_envs_v1(env, 1, base_class="stable_baselines3")
        
    # env = ss.pettingzoo_env_to_vec_env_v1(env)
    # env = ss.concat_vec_envs_v1(env, 2, num_cpus=1, base_class="stable_baselines3")
    env = VecMonitor(env)

    model = PPO(
        policy="MlpPolicy",
        env=env,
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
        tensorboard_log="./logs/MA_grid/CO2_emission",
        device='auto'
    )

    print("Starting training")
    model.learn(total_timesteps=200000)
    
    model.save('urban_mobility_simulation/src/data/logs/1208_ppo_test')

    print("Training finished. Starting evaluation")
    mean_reward, std_reward = evaluate_policy(model, env, n_eval_episodes=1)

    print('Mean Reward: ', mean_reward)
    print('Std Reward: ', std_reward)

    # Maximum number of steps before reset, +1 because I'm scared of OBOE
    # print("Starting rendering")
    # num_steps = (max_time // delta_time) + 1

    # obs = env.reset()

    # if os.path.exists("temp"):
    #     shutil.rmtree("temp")

    # os.mkdir("temp")
    # # img = disp.grab()
    # # img.save(f"temp/img0.jpg")

    # img = env.render()
    # for t in trange(num_steps):
    #     actions, _ = model.predict(obs, state=None, deterministic=False)
    #     obs, reward, done, info = env.step(actions)
    #     img = env.render()
    #     img.save(f"temp/img{t}.jpg")

    # subprocess.run(["ffmpeg", "-y", "-framerate", "5", "-i", "temp/img%d.jpg", "output.mp4"])

    # print("All done, cleaning up")
    # shutil.rmtree("temp")
    env.close()
