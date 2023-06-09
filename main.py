# importing==================================================================================================================================
import gymnasium as gym
import numpy as np
import matplotlib.pyplot as plt
# ==========================================================================================================================================
env = gym.make('CartPole-v1', render_mode="rgb_array")
# if change the render_mode to "human", it will constantly display the proccess of reinforcement training
# But it will largely slow down the proccess of training since it will display every time it run
# rgb_array will only return data instead of showing the proccess

BIN_SIZE = 20 # size you want the q-table to be 
EPISODES = 40000  # number of times to train

LEARNING_RATE = 0.1
DISCOUNT = 0.95

# epsilon decay settings ===============================================================================================================
epsilon = 1 
START_EPSILON_DECAYING = 1
END_EPSILON_DECAYING = EPISODES // 2
epsilon_decay_value = epsilon / (END_EPSILON_DECAYING - START_EPSILON_DECAYING)

# create ============================================================================================================================
observation_space_size = len(env.observation_space.high)
bins = [
    np.linspace(-4.8, 4.8, BIN_SIZE),
    np.linspace(-4, 4, BIN_SIZE),
    np.linspace(-.418, .418, BIN_SIZE),
    np.linspace(-4, 4, BIN_SIZE)
]

q_table = np.random.uniform(low=-2, high=0, size=([BIN_SIZE] * observation_space_size + [env.action_space.n]))

# function========================================================================================================================================

# Given a state of the enviroment, return its descreteState index in qTable
def get_discrete_state(state):
    state_index = []
    for i in range(observation_space_size):
        state_index.append(np.digitize(state[i], bins[i]) - 1)
    return tuple(state_index)
    
# ===============================================================================================================================================    
    
previous_count = []  # array of all scores over runs
metrics = {'ep': [], 'avg': [], 'min': [], 'max': []} 

# training===========================================================================================================================================
for episode in range(EPISODES+1):

    state, _ = env.reset()
    current_state = get_discrete_state(state)
    done = False  
    count = 0
    
    while not done:
        
        count += 1
        
        # if the random generate number is larger than epsilon (epsilon will delay)
        if np.random.random() > epsilon:
            action = np.argmax(q_table[current_state]) # get action according to q-table
        else:
            action = np.random.randint(0, env.action_space.n) # get a random action
            
        # get new discrete state
        new_state, reward, done, _ = env.step(action)[:4]  
        new_state = get_discrete_state(new_state)

        new_q = np.max(q_table[new_state])  # estimate of optiomal future q value
        current_q = q_table[current_state + (action, )]  # old q value

        # pole fell over / went out of bounds, negative reward
        if done and count < 200:
            reward = -375

        # update the q value in the q table
        new_q = (1 - LEARNING_RATE) * current_q + LEARNING_RATE * (reward + DISCOUNT * new_q)
        q_table[current_state + (action, )] = new_q  # Update q table with new q value

        current_state = new_state

    previous_count.append(count)

    # The epsilon will start to decay once reach half of the training episodes
    if END_EPSILON_DECAYING >= episode >= START_EPSILON_DECAYING:
        epsilon -= epsilon_decay_value

    # Add new metrics for graph
    if episode % 5000 == 0:
        latest_episodes = previous_count[-5000:]
        average_score = sum(latest_episodes) / len(latest_episodes)
        metrics['ep'].append(episode)
        metrics['avg'].append(average_score)
        metrics['min'].append(min(latest_episodes))
        metrics['max'].append(max(latest_episodes))
        print("episode:", episode, "average_score:", average_score, ",min_score:", min(latest_episodes), "max_score:", max(latest_episodes))


env.close()




# Show the training result by render in 'human' mode=====================================================================================================

env = gym.make('CartPole-v1', render_mode="human")
state,_ = env.reset()
current_state = get_discrete_state(state)
done = False
count = 0

while not done:

    count += 1

    action = np.argmax(q_table[current_state])

    # get new discrete state
    new_state, reward, done, _ = env.step(action)[:4]
    new_state = get_discrete_state(new_state)

    current_state = new_state

print(f"Final score: {count}")
env.close()



