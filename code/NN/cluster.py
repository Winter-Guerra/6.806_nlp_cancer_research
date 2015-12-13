from __future__ import absolute_import
from __future__ import print_function
import numpy as np
np.random.seed(1337)  # for reproducibility

from keras.models import Graph, Sequential
from keras.layers.core import Dense, Dropout, Activation
from keras.layers.advanced_activations import PReLU
from keras.layers.normalization import BatchNormalization
import h5py

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

def load_data(datapath):
    with h5py.File(datapath,'r') as f:
        X1 = np.array(f.get('X1'))
        X2 = np.array(f.get('X2'))
        y = np.array(f.get('y'))
        return (X1, X2, y)

if __name__ == '__main__':

    print("Loading training and testing datasets")
    # Since our dataset is HUGE (7.6 GB for the training set, we must use a file-based read system)
    # The training set is 2,525,437 samples long
    (X1_train, X2_train, y_train) = load_data("/mnt/ephemeral0/training.hdf5")
    #
    # print(X2_train[:1])
    # # The test set is 700,876 samples long
    (X1_test, X2_test, y_test) = load_data("/mnt/ephemeral0/testing.hdf5")

    # (X1_train, X2_train, y_train), (X1_test, X2_test, y_test) = wordVectorizer.get_large_datasets()

    # Problem here!
    # print(X1_train[:3])

    # Reshape y_train


    print('training dataset has shape {}'.format(X1_train.shape))
    print('training dataset Y-vector has shape {}'.format(y_train.shape))

    print("Compiling model")


    # # # # graph model with two inputs and one output
    # graph = Graph()
    # # Inputs
    # graph.add_input(name='input1', input_shape=(200,))
    # graph.add_input(name='input2', input_shape=(200,))
    # # Apply some Dropout
    # graph.add_node(Dropout(0.3), name='drop1', input='input1')
    # graph.add_node(Dropout(0.3), name='drop2', input='input2')
    #
    # # Make a siamese shared layer
    # # graph.add_shared_node(Dense(50, activation='sigmoid'), name='shared1', inputs=['drop1', 'drop2'])
    # graph.add_node(Dense(100, activation='tanh'), name='d1', inputs=['drop1','drop2'])
    #
    # graph.add_node(Dropout(0.3), name='drop3', input='d1')
    #
    # graph.add_node(Dense(75, activation='sigmoid'), name='d2', input='drop3')
    #
    # graph.add_node(Dropout(0.3), name='drop4', input='d2')
    # # 1 hidden layers
    # graph.add_node(Dense(50, activation='tanh'), name='merge1', input='drop4')
    # graph.add_node(Dense(1, activation='tanh'), name='merge2', input='merge1')
    #
    # # output
    # graph.add_output(name='output', input='merge2')
    # graph.compile('rmsprop', {'output':'mse'})
    #
    #
    #
    # print("Training model")
    # history = graph.fit({'input1':X1_train, 'input2':X2_train, 'output':y_train}, verbose=2, nb_epoch=75, shuffle=True, batch_size=256, validation_split=0.15)
    # print(history)
    #
    # score = graph.evaluate({'input1':X1_test, 'input2':X2_test, 'output':y_test})
    # print(score)

    # Here's a Deep Dumb MLP (DDMLP)
    model = Sequential()
    model.add(Dense(512, input_shape=(400,)))
    model.add(PReLU())
    model.add(BatchNormalization())
    model.add(Dropout(0.5))

    model.add(Dense(512))
    model.add(PReLU())
    model.add(BatchNormalization())
    model.add(Dropout(0.5))

    model.add(Dense(512))
    model.add(PReLU())
    model.add(BatchNormalization())
    model.add(Dropout(0.5))

    model.add(Dense(1))
    model.add(Activation('sigmoid'))

    # we'll use MSE (mean squared error) for the loss, and RMSprop as the optimizer
    # model.compile(loss='mse', optimizer='rmsprop')
    model.compile(loss='binary_crossentropy', optimizer='adam', class_mode="binary")

    print("Training...")
    X_train = np.hstack([X1_train, X2_train]) # Larger batch sizes help!
    model.fit(X_train, y_train, nb_epoch=100, shuffle=True, batch_size=1024, validation_split=0.1, show_accuracy=True, verbose=2)
    X_test = np.hstack([X1_test, X2_test])
    print(model.evaluate(X_test, y_test, show_accuracy=True))
