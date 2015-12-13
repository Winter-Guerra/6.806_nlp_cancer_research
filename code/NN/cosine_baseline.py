from __future__ import absolute_import
from __future__ import print_function
import numpy as np
np.random.seed(1337)  # for reproducibility

import h5py
from scipy.spatial.distance import cosine
import itertools


'''
    Train and evaluate a simple MLP on (article1, article2) pairings. Output should be a single neuron that states how close each matching is.
    GPU run command:
        THEANO_FLAGS=mode=FAST_RUN,device=gpu,floatX=float32 python examples/reuters_mlp.py
    CPU run command:
        python examples/reuters_mlp.py
'''

# def load_data(datapath, n_examples):
#     X1 = HDF5Matrix(datapath, 'X1', 0, n_examples)
#     X2 = HDF5Matrix(datapath, 'X2', 0, n_examples)
#     y = HDF5Matrix(datapath, 'y', 0, n_examples)
#     return (X1, X2, y)

def load_data(datapath):
    with h5py.File(datapath,'r') as f:
        X1 = np.array(f.get('X1'))
        X2 = np.array(f.get('X2'))
        y = np.array(f.get('y'))
        return (X1, X2, y)

def rmse(predictions, targets):
    return np.sqrt(np.mean((predictions-targets)**2))

if __name__ == '__main__':

    print("Loading training and testing datasets")
    # Since our dataset is HUGE (7.6 GB for the training set, we must use a file-based read system)
    # The training set is 2,525,437 samples long
    # (X1_train, X2_train, y_train) = load_data("/mnt/ephemeral0/training.hdf5")
    #
    # print(X2_train[:1])
    # # The test set is 700,876 samples long
    (X1_test, X2_test, y_test) = load_data("/mnt/ephemeral0/testing.hdf5")

    # (X1_train, X2_train, y_train), (X1_test, X2_test, y_test) = wordVectorizer.get_large_datasets()

    # Problem here!
    # print(X1_train[:3])

    # Reshape y_train


    # print('training dataset has shape {}'.format(X1_train.shape))
    # print('training dataset Y-vector has shape {}'.format(y_train.shape))

    print("Compiling model")

    # Let's get the rmse between rows in both matrices in the test set

    output = []
    for row1, row2 in itertools.izip(X1_test, X2_test):
        # The positive cosine similarity ()
        output.append( abs(cosine(row1, row2)) )

    # Convert to array
    output = np.array(output)
    output = output.reshape(output.shape[0], 1)

    # Calculate the rmse
    print("Shapes: {} {}".format(output.shape, y_test.shape))


    score = rmse(output, y_test)

    print("RMSE: {}".format(score))
