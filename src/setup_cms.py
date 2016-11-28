import numpy as np
import os

zeros = np.zeros((3,3))
np.savetxt(os.path.join(os.path.dirname(__file__),'data/user_cm.csv'), zeros, delimiter=',')
np.savetxt(os.path.join(os.path.dirname(__file__),'data/model_cm.csv'), zeros, delimiter=',')

# read it in with: np.loadtxt('data/user_cm.csv', delimiter=',')
