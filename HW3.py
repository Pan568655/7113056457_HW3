import numpy as np
import matplotlib.pyplot as plt

# Simulation parameters
np.random.seed(42)
k = 10                      # number of arms
true_means = np.random.rand(k)      # hidden Bernoulli means for each arm
T = 1000                    # time horizon
n_runs = 200                # number of independent repetitions for averaging

def simulate_algo(algo_name, **kwargs):
    """
    Simulate a single algorithm over n_runs, return mean cumulative reward curve.
    """
    rewards = np.zeros(T)
    for _ in range(n_runs):
        Q = np.zeros(k)
        N = np.zeros(k)
        # For Thompson Sampling keep Beta priors
        a_beta = np.ones(k)
        b_beta = np.ones(k)

        for t in range(T):
            if algo_name == 'epsilon-greedy':
                epsilon = kwargs['epsilon']
                if np.random.rand() < epsilon:
                    arm = np.random.randint(k)
                else:
                    arm = np.argmax(Q)

            elif algo_name == 'ucb':
                # play each arm once to initialize
                if t < k:
                    arm = t
                else:
                    ucb_values = Q + np.sqrt(2 * np.log(t + 1) / (N + 1e-9))
                    arm = np.argmax(ucb_values)

            elif algo_name == 'softmax':
                tau = kwargs['tau']
                # avoid overflow by shifting
                logits = Q / tau
                logits -= np.max(logits)
                probs = np.exp(logits)
                probs /= probs.sum()
                arm = np.random.choice(k, p=probs)

            elif algo_name == 'thompson':
                samples = np.random.beta(a_beta, b_beta)
                arm = np.argmax(samples)

            else:
                raise ValueError("Unknown algorithm name")

            # obtain reward
            reward = np.random.rand() < true_means[arm]
            rewards[t] += reward

            # update statistics
            N[arm] += 1
            if algo_name == 'thompson':
                a_beta[arm] += reward
                b_beta[arm] += 1 - reward
                Q[arm] = a_beta[arm] / (a_beta[arm] + b_beta[arm])
            else:
                Q[arm] += (reward - Q[arm]) / N[arm]

    mean_rewards = rewards / n_runs
    cumulative_rewards = np.cumsum(mean_rewards)
    return cumulative_rewards

# Run simulations
results = {
    'Epsilon-Greedy (ε=0.1)': simulate_algo('epsilon-greedy', epsilon=0.1),
    'UCB1': simulate_algo('ucb'),
    'Softmax (τ=0.1)': simulate_algo('softmax', tau=0.1),
    'Thompson Sampling': simulate_algo('thompson')
}

# Plot each algorithm separately
for name, curve in results.items():
    plt.figure()
    plt.plot(curve)
    plt.title(f'{name} – Average Cumulative Reward')
    plt.xlabel('Time step')
    plt.ylabel('Average cumulative reward')
    plt.tight_layout()
    plt.show()
