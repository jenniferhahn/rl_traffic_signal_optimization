import traci
import pandas as pd
import pickle
from stable_baselines3 import PPO
from stable_baselines3.common.evaluation import evaluate_policy
from stable_baselines3.common.callbacks import EvalCallback
from stable_baselines3.common.vec_env import VecMonitor
import ma_environment.custom_envs as custom_env
import supersuit as ss
import numpy as np

# make sure tls logic for selected traffic lights is set to 'static' in the sumo config (net) file
# and run in debug mode


# Initialize SUMO environment as same as you trained the model (you need to replace with your own implementation)
env = custom_env.MA_grid_eval(use_gui=False,
                            reward_fn = 'average-speed',
                            traffic_lights= ['tls_159','tls_160', 'tls_161'],
                            out_csv_name='/Users/jenniferhahn/Documents/GitHub/urban_mobility_simulation/src/data/evaluation/speed_200_1800steps',
                            begin_time=25200,
                            num_seconds=9000,
                            time_to_teleport=300)

#wrap observation space to have one common observation space for all agents
env = ss.pad_observations_v0(env)

#wrap action space to have one common action space for all agents (based on largest action space)
env = ss.pad_action_space_v0(env)

#wrap pettingzoo env 
env = ss.pettingzoo_env_to_vec_env_v1(env)

#concatenate envs
env = ss.concat_vec_envs_v1(env, 1, num_cpus=4, base_class="stable_baselines3")
    
env = VecMonitor(env)


lane_ids = ['251161865#1_2', '189068695#4_0', '276412658_1', ':cluster_1743822458_1743822558_1743822643_1743822689_1743822737_8039877991_cluster_1120310798_1634545540_1665161322_1665161338_1665161344_1743822496_1743822510_1743822551_1743822648_1743822650_1743822666_1743822667_1743822676_1743822687_1754245066_1756301705_1949670169_2004844603_297701075_412123597_412123598_412123601_412181181_w2_0', \
            '96747828#0_0', '276412658_4', ':cluster_cluster_1109568391_cluster_1109568409_1109568428_25422076_834022925_834023464_cluster_1364262300_cluster_1109568414_1364262303_1743822792_297701095_4586935111_w3_0', '96747828#0_2', '96747828#0_1', ':cluster_1743822458_1743822558_1743822643_1743822689_1743822737_8039877991_cluster_1120310798_1634545540_1665161322_1665161338_1665161344_1743822496_1743822510_1743822551_1743822648_1743822650_1743822666_1743822667_1743822676_1743822687_1754245066_1756301705_1949670169_2004844603_297701075_412123597_412123598_412123601_412181181_w0_0',\
            ':cluster_cluster_1743822127_4889543898_cluster_1756301698_25113885_271075996_cluster_1743822142_cluster_1743822133_1743822191_1743822205_1756301686_1756301687_1756301692_1756301694_2003762999_248783350_2574373755_2574373756_2574373757_2574373758_266980758_26936934_419622507_4890135930_6838389013_6838389025_6840644265_705047176_w2_0', '251157594_1', \
            ':cluster_1743822458_1743822558_1743822643_1743822689_1743822737_8039877991_cluster_1120310798_1634545540_1665161322_1665161338_1665161344_1743822496_1743822510_1743822551_1743822648_1743822650_1743822666_1743822667_1743822676_1743822687_1754245066_1756301705_1949670169_2004844603_297701075_412123597_412123598_412123601_412181181_w8_0', \
            ':cluster_cluster_1743822127_4889543898_cluster_1756301698_25113885_271075996_cluster_1743822142_cluster_1743822133_1743822191_1743822205_1756301686_1756301687_1756301692_1756301694_2003762999_248783350_2574373755_2574373756_2574373757_2574373758_266980758_26936934_419622507_4890135930_6838389013_6838389025_6840644265_705047176_w1_0', \
            ':cluster_cluster_1743822127_4889543898_cluster_1756301698_25113885_271075996_cluster_1743822142_cluster_1743822133_1743822191_1743822205_1756301686_1756301687_1756301692_1756301694_2003762999_248783350_2574373755_2574373756_2574373757_2574373758_266980758_26936934_419622507_4890135930_6838389013_6838389025_6840644265_705047176_w4_0', \
            '189877634#0_3',':cluster_1743822458_1743822558_1743822643_1743822689_1743822737_8039877991_cluster_1120310798_1634545540_1665161322_1665161338_1665161344_1743822496_1743822510_1743822551_1743822648_1743822650_1743822666_1743822667_1743822676_1743822687_1754245066_1756301705_1949670169_2004844603_297701075_412123597_412123598_412123601_412181181_w6_0', 
            ':cluster_1743822458_1743822558_1743822643_1743822689_1743822737_8039877991_cluster_1120310798_1634545540_1665161322_1665161338_1665161344_1743822496_1743822510_1743822551_1743822648_1743822650_1743822666_1743822667_1743822676_1743822687_1754245066_1756301705_1949670169_2004844603_297701075_412123597_412123598_412123601_412181181_w5_0', \
            ':cluster_cluster_1743822127_4889543898_cluster_1756301698_25113885_271075996_cluster_1743822142_cluster_1743822133_1743822191_1743822205_1756301686_1756301687_1756301692_1756301694_2003762999_248783350_2574373755_2574373756_2574373757_2574373758_266980758_26936934_419622507_4890135930_6838389013_6838389025_6840644265_705047176_w5_0', '189877634#0_0', \
            '189877634#0_2', '548514763#0_3', '251161865#1_1', '778989039#3_0', '96747818#3_0', '276412658_2', '276412658_3', ':cluster_cluster_1109568391_cluster_1109568409_1109568428_25422076_834022925_834023464_cluster_1364262300_cluster_1109568414_1364262303_1743822792_297701095_4586935111_w2_0', '548514763#0_1', ':cluster_1743822458_1743822558_1743822643_1743822689_1743822737_8039877991_cluster_1120310798_1634545540_1665161322_1665161338_1665161344_1743822496_1743822510_1743822551_1743822648_1743822650_1743822666_1743822667_1743822676_1743822687_1754245066_1756301705_1949670169_2004844603_297701075_412123597_412123598_412123601_412181181_w7_0', \
            '548514763#0_2', ':cluster_cluster_1109568391_cluster_1109568409_1109568428_25422076_834022925_834023464_cluster_1364262300_cluster_1109568414_1364262303_1743822792_297701095_4586935111_w1_0', '251161865#1_3', '96851712#0_0', ':cluster_1743822458_1743822558_1743822643_1743822689_1743822737_8039877991_cluster_1120310798_1634545540_1665161322_1665161338_1665161344_1743822496_1743822510_1743822551_1743822648_1743822650_1743822666_1743822667_1743822676_1743822687_1754245066_1756301705_1949670169_2004844603_297701075_412123597_412123598_412123601_412181181_w3_0',\
            '548514763#0_0', '189877848_0', '251157594_2', '251157594_4', '251157594_3', '189877634#0_1', '278441980#3_0', '189877848_1']


# Load the model
model = PPO.load('/Users/jenniferhahn/Documents/GitHub/urban_mobility_simulation/src/data/logs/avg_speed_200.zip')

# Get state of environment
observation = env.reset()

# Initialize SUMO simulation
traci.start(["sumo", "-c", "urban_mobility_simulation/models/20230718_sumo_ma/osm.sumocfg"])

# Initialize the lists to hold data
data = []

# Run the simulation for step from 25200 to 29700
for step in range(1800):
    # Advance simulation step
    traci.simulationStep()

    # Let model decide based on the current environment state
    actions, _ = model.predict(observation, state=None, deterministic=True)

    # Apply the model's action to simulation
    observation, reward, done, information = env.step(actions) # step takes 5 seconds for one simulation step --> 1800 steps = 9000 seconds = 2.5 hours

    # Collect your required data
    local_vehicles = [item for sublist in (traci.lane.getLastStepVehicleIDs(lane_id) for lane_id in lane_ids) for item in sublist]
    
    CO2_emissions = sum([traci.vehicle.getCO2Emission(vehicle_id) for vehicle_id in local_vehicles])
    CO_emissions = sum([traci.vehicle.getCOEmission(vehicle_id) for vehicle_id in local_vehicles])
    HC_emissions = sum([traci.vehicle.getHCEmission(vehicle_id) for vehicle_id in local_vehicles])
    PMx_emissions = sum([traci.vehicle.getPMxEmission(vehicle_id) for vehicle_id in local_vehicles])
    NOx_emissions = sum([traci.vehicle.getNOxEmission(vehicle_id) for vehicle_id in local_vehicles])
    waiting_time = sum([traci.vehicle.getWaitingTime(vehicle_id) for vehicle_id in local_vehicles])
    total_num_stops = sum([traci.vehicle.getStopState(vehicle_id) for vehicle_id in local_vehicles])
    current_reward = np.mean(reward)
        
    # Append to data (or you can append to a file)
    data.append([step, CO2_emissions, CO_emissions, HC_emissions, PMx_emissions, NOx_emissions, waiting_time, total_num_stops, current_reward])

# Close the TraCI connection
traci.close()

columns = ['step', 'CO2_emissions', 'CO_emissions', 'HC_emissions', 'PMx_emissions', 'NOx_emissions', 'waiting_time', 'total_num_stops', 'current_reward']

df = pd.DataFrame(data, columns=columns)
df.to_csv('urban_mobility_simulation/src/data/evaluation/avg_speed_200_1800.csv', index=False)
