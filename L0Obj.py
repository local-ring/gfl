import numpy as np
from scipy.sparse import spdiags, csr_matrix
from scipy.linalg import inv

def L0Obj(X, m, y, L, pho, mu, d, h, n):
    """
    Compute the objective function value and gradient for the L0 regularized least squares problem.
    Parameters:
    - X: n x d matrix of features
    - y: n x 1 vector of labels
    - pho: regularization parameter for L2 penalty
    - mu: regularization parameter for L0-graph penalty
    - u: d x 1 vector of weights
    Returns:
    - f: objective function value
    - g: gradient
    """
    n, dh = X.shape
    if d*h != dh:
        raise ValueError("The dimensions of X and d*h do not match.")
    
    SpDiag = spdiags(m.flatten(), 0, dh, dh)
    # B_inv = (1/pho) * X @ SpDiag @ X.T + np.sqrt(n) * np.eye(n)
    # if np.linalg.matrix_rank(B_inv) != n:
    #     print(f"rank: {np.linalg.matrix_rank(B_inv)}, shape: {B_inv.shape}")
    #     raise ValueError("The matrix is not full rank.")
    # B = inv(B_inv)
    regularization = 1e-8
    B_inv = (1 / pho) * X @ SpDiag @ X.T + np.eye(n) + regularization * np.eye(n)
    B = np.linalg.solve(B_inv, np.eye(n))
    # y = n * y
    precision_penalty = y.T @ B @ y

    epsilon = 0.1
    r = 1 + epsilon
    eta = 2 * r * mu + 2 * d + 0.4 * (pho ** 2) 
    L = csr_matrix(L + r * np.eye(d)) # this can keep L as np.ndarray instead of np.matrix which will mess up with the flatten() function


    M = m.reshape(d,h) # generate the assignment matrix
    graph_penalty = 0.5 * mu * np.trace(M.T @ L @ M) # generate the graph penalty term

    MTM = np.dot(M.T, M)
    correction_term = 0.5 * eta * (np.sum(MTM) - np.sum(np.diag(MTM)))

    row_sums = np.sum(M, axis=1, keepdims=True)  
    f = precision_penalty + graph_penalty + correction_term # AL: why conjuate transpose? i remove the .conj()

    A_grad = -(1/pho) * ((X.conj().T @ B @ y)**2) # the gradient of the first term

    B_grad =  mu * (L @ M)  # the gradient of the second term

    C_grad = eta * (M - row_sums) # the gradient of the third term

    B_grad = B_grad.flatten()

    C_grad = C_grad.flatten()

    g = A_grad + B_grad + C_grad

    return f, g


def L0Obj_separate(X, m, y, L, pho, mu, d, h, n):
    """
    Compute the objective function value and gradient for the L0 regularized least squares problem.
    Parameters:
    - X: n x d matrix of features
    - y: n x 1 vector of labels
    - pho: regularization parameter for L2 penalty
    - mu: regularization parameter for L0-graph penalty
    - u: d x 1 vector of weights
    Returns:
    - f: objective function value
    - g: gradient
    """
    n, dh = X.shape
    if d*h != dh:
        raise ValueError("The dimensions of X and d*h do not match.")
    
    SpDiag = spdiags(m.flatten(), 0, dh, dh)
    B_inv = (1/pho) * X @ SpDiag @ X.T + n * np.eye(n)
    if np.linalg.matrix_rank(B_inv) != n:
        print(f"rank: {np.linalg.matrix_rank(B_inv)}, shape: {B_inv.shape}")
        raise ValueError("The matrix is not full rank.")
    B = inv(B_inv)

    precision_penalty = y.T @ B @ y

    epsilon = 0.1
    r = 1 + epsilon
    eta = 2 * r * mu + 2 * d + 0.4 * (pho ** 2) 

    # L = L + C * np.eye(d) # add identity matrix to L
    L = csr_matrix(L + r * np.eye(d)) # this can keep L as np.ndarray instead of np.matrix which will mess up with the flatten() function


    M = m.reshape(d,h) # generate the assignment matrix
    graph_penalty = 0.5 * mu * np.trace(M.T @ L @ M) # generate the graph penalty term

    MTM = np.dot(M.T, M)
    correction_term = 0.5 * eta * (np.sum(MTM) - np.sum(np.diag(MTM)))

    row_sums = np.sum(M, axis=1, keepdims=True)  
    f = precision_penalty + graph_penalty + correction_term # AL: why conjuate transpose? i remove the .conj()

    A_grad = -(1/pho) * ((X.conj().T @ B @ y)**2) # the gradient of the first term
    # print("L type:", type(L))
    # print("M type:", type(M))
    B_grad =  mu * (L @ M)  # the gradient of the second term

    C_grad = eta * (M - row_sums) # the gradient of the third term

    # print("A_grad shape:", A_grad.shape)
    # print("B_grad shape:", B_grad.shape)
    B_grad = B_grad.flatten()
    # print("B_grad shape:", B_grad.shape)
    # print("C_grad shape:", C_grad.shape)
    C_grad = C_grad.flatten()
    # print("C_grad shape:", C_grad.shape)

    g = A_grad + B_grad + C_grad

    return f, g, graph_penalty, precision_penalty, correction_term, A_grad, B_grad, C_grad