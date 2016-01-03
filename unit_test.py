from sequential import SequentialNetwork
from layer import FullyConnectedLayer, SoftMaxLayer, Convolution2DLayer
from utils import get_data

import numpy as np
import pickle, gzip

def unit_test_mlp():

	train_x, train_y, dev_x, dev_y, test_x, test_y = get_data(dataset='mnist')

	network = SequentialNetwork(input_type='2d', output_type='multiple_class')
	network.add(FullyConnectedLayer(train_x.shape[1], 500, activation='tanh'))
	network.add(FullyConnectedLayer(500, 10, activation='tanh'))
	network.add(SoftMaxLayer(hierarchical=False))

	network.compile(loss='categorical_crossentropy')

	network.train(train_x, train_y, nb_epochs=10, valid_x=dev_x, valid_y=dev_y, test_x=test_x, test_y=test_y)

def unit_test_conv():

	train_x, train_y, dev_x, dev_y, test_x, test_y = get_data(dataset='mnist')

	train_x = train_x.reshape(train_x.shape[0], 1, int(np.sqrt(train_x.shape[1])), int(np.sqrt(train_x.shape[1])))
	dev_x = dev_x.reshape(dev_x.shape[0], 1, int(np.sqrt(dev_x.shape[1])), int(np.sqrt(dev_x.shape[1])))
	test_x = test_x.reshape(test_x.shape[0], 1, int(np.sqrt(test_x.shape[1])), int(np.sqrt(test_x.shape[1])))

	network = SequentialNetwork(input_type='4d', output_type='multiple_class')

	convolution_layer0 = Convolution2DLayer(
	    input_height=train_x.shape[2], 
	    input_width=train_x.shape[3], 
	    filter_width=5, 
	    filter_height=5, 
	    num_filters=20, 
	    num_feature_maps=1, 
	    flatten=False, 
	    wide=False
	)

	convolution_layer1 = Convolution2DLayer(
	    input_height=convolution_layer0.output_height_shape, 
	    input_width=convolution_layer0.output_width_shape, 
	    filter_width=5, 
	    filter_height=5, 
	    num_filters=50, 
	    num_feature_maps=20, 
	    flatten=True, 
	    wide=False
	)

	network.add(convolution_layer0)
	network.add(convolution_layer1)
	network.add(FullyConnectedLayer(800, 500, activation='tanh'))
	network.add(FullyConnectedLayer(500, 10, activation='tanh'))
	network.add(SoftMaxLayer(hierarchical=False))

	network.compile(loss='categorical_crossentropy', lr=0.1)

	network.train(train_x, train_y, nb_epochs=10, valid_x=dev_x, valid_y=dev_y, test_x=test_x, test_y=test_y)

print 'Testing Multi-layer Perceptron ...'
unit_test_mlp()
print 'Testing Convolutional Neural Network ...'
unit_test_conv()
