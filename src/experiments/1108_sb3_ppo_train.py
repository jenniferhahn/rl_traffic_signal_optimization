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



#env = sumo_rl.grid4x4(use_gui=False, out_csv_name="outputs/grid4x4/ppo_test", virtual_display=RESOLUTION,sumo_warnings=False)


env = custom_env.MA_grid_new(use_gui=False,
                                traffic_lights= ['tls_159','tls_160', 'tls_161'], #['tls_155','tls_156','tls_157','tls_159','tls_160','tls_161'],
                                sumo_warnings=False,
                                out_csv_name='/Users/jenniferhahn/Documents/GitHub/urban_mobility_simulation/src/data/model_outputs/waitingTime_200000',
                                additional_sumo_cmd="--emission-output /Users/jenniferhahn/Documents/GitHub/urban_mobility_simulation/src/data/model_outputs/1408_ppo_waitingTime.xml")
max_time = env.unwrapped.env.sim_max_time
delta_time = env.unwrapped.env.delta_time

#wrap observation space to have one common observation space for all agents
env = ss.pad_observations_v0(env)

#wrap action space to have one common action space for all agents (based on largest action space)
env = ss.pad_action_space_v0(env)

#wrap pettingzoo env 
env = ss.pettingzoo_env_to_vec_env_v1(env)

#concatenate envs
env = ss.concat_vec_envs_v1(env, 1, num_cpus=4, base_class="stable_baselines3")
    
env = VecMonitor(env)

model = PPO(
    policy="MlpPolicy",
    env=env,
    verbose=3,
    gamma=0.95,
    n_steps=512,
    ent_coef=0.01,
    learning_rate=0.00025,
    vf_coef=0.05,
    max_grad_norm=0.9,
    gae_lambda=0.95,
    n_epochs=10,
    clip_range=0.3,
    batch_size=256,
    tensorboard_log="./logs/MA_grid/diff_waiting_time",
    device='auto' # use 'auto' for cpu only
)

print("Starting training")
model.learn(total_timesteps=200000)

model.save('urban_mobility_simulation/src/data/logs/1408_diff_waiting_time_200')

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
