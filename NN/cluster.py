from __future__ import absolute_import
from __future__ import print_function
import numpy as np
np.random.seed(1337)  # for reproducibility

from keras.datasets import reuters
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation
from keras.layers.normalization import BatchNormalization
from keras.utils import np_utils
from keras.preprocessing.text import Tokenizer, text_to_word_sequence

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

if __name__ == '__main__':

    max_words = 1000
    batch_size = 32
    nb_epoch = 1

    # Get a list of combinations from redis
    ((X_train, y_train), (X_test, y_test)) = redis_dataset.get_dataset(test_split=0.2)
    # Convert these lists to vector matrices using word2vec

    print("Getting embeddings")

    X1_train, X2_train = wordVectorizer.convertData(X_train)
    X1_test, X2_test = wordVectorizer.convertData(X_test)

    print(len(X_train), 'train pairings')
    print(len(X_test), 'test pairings')

    print('X_train shape:', X1_train.shape)
    print('X_test shape:', X1_test.shape)

    print("Compiling model")

# WE PROBABLY WANT TO USE THE GRAPH EXAMPLE
#
# model = Sequential()
#
# model.add(Dense(512, input_shape=(max_words,)))
# model.add(Activation('relu'))
# model.add(Dropout(0.5))
#
# model.add(Dense(nb_classes))
# model.add(Activation('softmax'))
#
# model.compile(loss='categorical_crossentropy', optimizer='adam')
#
# print "Fitting model"
#
# history = model.fit(X_train, Y_train, nb_epoch=nb_epoch, batch_size=batch_size, verbose=2, show_accuracy=True, validation_split=0.1)
# score = model.evaluate(X_test, Y_test, batch_size=batch_size, verbose=1, show_accuracy=True)
#
#
#
# print('Test score:', score[0])
# print('Test accuracy:', score[1])
