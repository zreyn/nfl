import numpy as np

zeros = np.zeros((3,3))
np.savetxt('data/user_cm.csv', zeros, delimiter=',')
np.savetxt('data/model_cm.csv', zeros, delimiter=',')

# read it in with: np.loadtxt('data/user_cm.csv', delimiter=',')
