# Let's convert the training data into a shape that caffe likes

# files
# /mnt/testing.hdf5
# /mnt/training.hdf5

import h5py
import numpy as np

def load_data(datapath):
    with h5py.File(datapath,'r') as f:
        X1 = np.array(f.get('X1'))
        X2 = np.array(f.get('X2'))
        y = np.array(f.get('y'))
        return (X1, X2, y)

# Output the dataset
def save_dataset(datapath, x1,x2,y):

    x = np.hstack([x1, x2])
    # x = x # Transpose it so that it is Nxd
    # y = y.T

    # make the y's binary
    y = (y != 0).astype(int)
    print ("Y shape:",y.shape)

    print ("X shape:",x.shape)

    # We should print the statistics of what the accuracy is
    y_sum = np.sum(y)
    y_size = float(y.size)
    ratio = y_sum/y_size
    print "Data ratio is: {}".format(ratio)

    # Let's do a random test on the dataset choosing true false and see how they compare
    results = []
    for i in range(10):
        guess = np.random.randint(2, size=y.size).reshape(y.shape)

        correct_guesses = (guess == y)
        # print correct_guesses[:100]
        acc = np.sum(correct_guesses)/float(guess.size)
        # print acc
        results.append(acc)

    # Let's return the results
    print "Random test accuracy: {}".format(sum(results)/float(10.0))


    with h5py.File(datapath, "w") as f:
        dset_1 = f.create_dataset("data", data=x, dtype='float32')
        dset_2 = f.create_dataset("label", data=y, dtype='float32')

    return (y_sum, y_size)

if __name__ == '__main__':


    print "loading training"
    (X1_train, X2_train, y_train) = load_data("/mnt/training.hdf5")
    (y_train_sum, y_train_size) = save_dataset("/mnt/caffe_training.hdf5", X1_train, X2_train, y_train)

    print '---------------------------'
    print "loading testing"
    (X1_test, X2_test, y_test) = load_data("/mnt/testing.hdf5")
    (y_test_sum, y_test_size) = save_dataset("/mnt/caffe_test.hdf5", X1_test, X2_test, y_test)

    print "Total ratio is: {}".format((y_train_sum+y_test_sum)/(y_train_size+y_test_size))

    print "Done!"
