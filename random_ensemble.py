import numpy as np
import scipy.io as sio
from scipy.linalg import toeplitz
from scipy.stats import multivariate_normal
import time

from L0Obj import L0Obj
from data_generator import generate_synthetic_data_with_graph, read_synthetic_data_from_file, save_synthetic_data_to_file
from ProjectOperator import ProjOperator_Gurobi
from minConf.minConf_PQN import minConF_PQN
import random


tStart = time.process_time()
# Generate synthetic data
# Parametersx
n = 500  # Number of samples
d = 200   # Number of features
k = 20   # Number of non-zero features
h = 4    # Number of clusters
nVars = d*h # Number of Boolean variables in m
theta = 1  # Probability of connection within clusters
gamma = 2.5  # Noise standard deviation
pho = 0.1
mu = 0.8
SNR = 1

fixed_seed = False
# read a fixed synthetic data from a file if fixed_seed is True because we want to compare the results with the original results
if fixed_seed:
    file_path = "synthetic_data.npz"
    X, w_true, y, adj_matrix, L, clusters_true, selected_features_true = read_synthetic_data_from_file(file_path)
else:
    # Generate synthetic data
    X, w_true, y, adj_matrix, L, clusters_true, selected_features_true = generate_synthetic_data_with_graph(n, d, k, h, theta, gamma, visualize=True)
    # Save the synthetic data to a file
    file_path = "synthetic_data.npz"
    save_synthetic_data_to_file(file_path, X, w_true, y, adj_matrix, L, clusters_true, selected_features_true)
    print("selected_features_true", selected_features_true)
    print("clusters_true", clusters_true)

# we need to modify the matrix X to define the objective function
X_hat = np.repeat(X, h, axis=1)


print("Check!!!")
tEnd = time.process_time() - tStart
print("Execution time (generating the data):", tEnd)

# Initial guess of parameters
m_initial = np.ones((nVars, 1)) * (1 / nVars)


# Set up Objective Function L0Obj(X, m, y, pho, mu):
funObj = lambda m: L0Obj(X_hat, m, y, L, pho, mu, d, h)

# Set up Simplex Projection Function ProjOperator_Gurobi(m, k, d, h):
funProj = lambda m: ProjOperator_Gurobi(m, k, d, h)

tEnd = time.process_time() - tStart
print("Execution time(Before):", tEnd)
print("start!!!")
# Solve with PQN
options = {'maxIter': 50}
tStart = time.process_time()
mout, obj, _ = minConF_PQN(funObj, m_initial, funProj, options)
print(f"uout: {mout}")
tEnd = time.process_time() - tStart

# round the result randomly according to its value for a few times and select the best one in terms of the objective function
T = 500
min_obj = np.inf
min_round = np.zeros((nVars, ))  # initialize the best result
for _ in range(T):
    m_round = (np.random.rand(nVars, ) < mout).astype(int)
    obj_round, _ = funObj(m_round)
    if obj_round < min_obj:
        min_obj = obj_round
        min_round = m_round

print("min_obj", min_obj)
print("min_round", min_round)

selected_features_predict = []
clusters_predict = {}
# parse the result m_round to the selected features and clusters
m = min_round.reshape(d, h)
for i in range(d):
    if np.sum(m[i]) > 0:
        selected_features_predict.append(i)
        cluster = np.where(m[i] > 0)[0][0]
        if cluster in clusters_predict:
            clusters_predict[cluster].append(i)
        else:
            clusters_predict[cluster] = [i]

# find the intersection of the selected features and clusters
C = np.intersect1d(selected_features_true, selected_features_predict)

# Find the intersection
AccPQN = len(C) / k


print("Execution time:", tEnd)
print("Accuracy PQN:", AccPQN)
print("clusters_predict", clusters_predict)
print("clusters_true", clusters_true)  
print("selected_features_predict", selected_features_predict)
print("selected_features_true", selected_features_true)
