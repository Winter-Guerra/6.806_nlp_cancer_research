from __future__ import absolute_import
from __future__ import print_function
import numpy as np
np.random.seed(1337)  # for reproducibility

from keras.models import Graph, Sequential
from keras.layers.core import Dense, Dropout, Activation
from keras.utils.io_utils import HDF5Matrix

# Import our dataset
import redis_dataset
import wordVectorizer

'''
    Train and evaluate a simple MLP on (article1, article2) pairings. Output should be a single neuron that states how close each matching is.
    GPU run command:
        THEANO_FLAGS=mode=FAST_RUN,device=gpu,floatX=float32 python examples/reuters_mlp.py
    CPU run command:
        python examples/reuters_mlp.py
'''

def load_data(datapath, n_examples):
    X1 = HDF5Matrix(datapath, 'X1', 0, n_examples)
    X2 = HDF5Matrix(datapath, 'X2', 0, n_examples)
    y = HDF5Matrix(datapath, 'y', 0, n_examples)
    return (X1, X2, y)

if __name__ == '__main__':

    # Since our dataset is HUGE (7.6 GB for the training set, we must use a file-based read system)
    # The training set is 2,525,437 samples long
    # (X1_train, X2_train, y_train) = load_data("/mnt/ephemeral0/training.hdf5", 2525437)
    #
    # print(X2_train[:1])
    # # The test set is 700,876 samples long
    # (X1_test, X2_test, y_test) = load_data("/mnt/ephemeral0/testing.hdf5", 700876)

    (X1_train, X2_train, y_train), (X1_test, X2_test, y_test) = wordVectorizer.get_large_datasets()

    # Reshape y_train


    print('training dataset has shape {}'.format(X1_train.shape))
    print('training dataset Y-vector has shape {}'.format(y_train.shape))
    y_train = y_train.reshape((y_train.shape[0],1))
    print('NOW: training dataset Y-vector has shape {}'.format(y_train.shape))
    # print('testing dataset has shape {}'.format(X1_test.shape))

    print("Compiling model")

    # # Here's a Deep Dumb MLP (DDMLP)
    # model = Sequential()
    # model.add(Dense(20, input_shape=(400,) ))
    # model.add(Activation('relu'))
    # model.add(Dropout(0.25))
    # # model.add(Dense(128, 128, init='lecun_uniform'))
    # # model.add(Activation('relu'))
    # # model.add(Dropout(0.25))
    # model.add(Dense(1))
    # model.add(Activation('sigmoid'))
    #
    # # we'll use MSE (mean squared error) for the loss, and RMSprop as the optimizer
    # model.compile(loss='mse', optimizer='rmsprop', class_mode="binary")
    #
    # # Retrofit the X1,X2 training set together.
    # X_train = np.hstack([X1_train, X2_train])
    # print("Training...")
    # model.fit(X_train, y_train, nb_epoch=10, batch_size=128, validation_split=0.1, show_accuracy=True, verbose=2)


    # # graph model with two inputs and one output
    graph = Graph()
    graph.add_input(name='input1', input_shape=(200,))
    graph.add_input(name='input2', input_shape=(200,))
    graph.add_node(Dense(16), name='dense1', input='input1')
    graph.add_node(Dense(1), name='dense2', input='input2')
    graph.add_node(Dense(1), name='dense3', input='dense1')
    graph.add_output(name='output', inputs=['dense2', 'dense3'], merge_mode='sum')
    graph.compile('rmsprop', {'output':'mse'})

    print("Training model")
    history = graph.fit({'input1':X1_train, 'input2':X2_train, 'output':y_train}, verbose=2, nb_epoch=10) # Cannot shuffle since from file

    score = graph.evaluate({'input1':X1_test, 'input2':X2_test, 'output':y_test})
    print(score)
