#!/usr/bin/env python

from utils import get_weights, get_bias

import theano
import theano.tensor as T
from theano.tensor.signal import downsample
import numpy as np


__author__ = "Sandeep Subramanian"
__maintainer__ = "Sandeep Subramanian"
__version__ = "1.0"
__email__ = "sandeep.subramanian@gmail.com"

class FullyConnectedLayer:

	def __init__(self, input_dim, output_dim, activation='sigmoid', name='fully_connected'):

		"""
		Fully Connected Layer
		"""

		# Set input and output dimensions
		self.input_dim = input_dim
		self.output_dim = output_dim

		# Set the activation function for this layer
		if activation == 'sigmoid':
			self.activation = T.nnet.sigmoid
			low = -4 * np.sqrt(6. / (input_dim + output_dim))
			high = 4 * np.sqrt(6. / (input_dim + output_dim))

		elif activation == 'tanh':
			self.activation = T.tanh
			low = -1 * np.sqrt(6. / (input_dim + output_dim))
			high = np.sqrt(6. / (input_dim + output_dim))
		
		elif activation == 'linear':
			self.activation = None
		
		else:
			raise NotImplementedError("Unknown activation")

		# Initialize weights & biases for this layer		
		self.weights = get_weights(low, high, (input_dim, output_dim), name=name + '__weights')
		self.bias = get_bias(output_dim, name=name + '__bias')
		self.params = [self.weights, self.bias]


	def fprop(self, input):

		# Propogate the input through the layer
		linear_activation = T.dot(input, self.weights) + self.bias
		if self.activation == 'linear':
			return linear_activation
		else:
			return self.activation(linear_activation)

class SoftMaxLayer:

	"""
	Softmax Layer
	"""

	def __init__(self, hierarchical=False):

		# __TODO__ Add Hierarchical Softmax

		self.hierarchical = hierarchical

	def fprop(self, input):

		if not self.hierarchical:
			return T.nnet.softmax(input)



class Convolution2DLayer:

	"""
	2D Convolution Layer
	"""

	def __init__(self, input_height, input_width, filter_width, filter_height, num_filters, num_feature_maps, pooling_factor=(2, 2), flatten=False, wide=False, name='conv'):
	    
	    # Set the parameters for this layer
	    self.num_filters = num_filters
	    self.input_width = input_width
	    self.input_height = input_height
	    self.filter_width = filter_width
	    self.filter_height = filter_height
	    self.pooling_factor = pooling_factor
	    self.flatten = flatten
	    self.wide = wide
	    
	    # Compute fan_in and fan_out to initialize filters
	    self.fan_in = num_feature_maps * filter_width * filter_height
	    self.fan_out = num_filters * filter_width * filter_height

	    # Compute the output shape of the network
	    if self.wide:
	    	self.output_height_shape = (self.input_height + self.filter_height - 1) / self.pooling_factor[0]
	    	self.output_width_shape = (self.input_width + self.filter_width - 1) / self.pooling_factor[1]
	    elif not self.wide:
	    	self.output_height_shape = (self.input_height - self.filter_height + 1) / self.pooling_factor[0]
	    	self.output_width_shape = (self.input_width - self.filter_width + 1) / self.pooling_factor[1]

	    if self.flatten:
	    	self.output_flatten_shape = self.output_height_shape * self.output_width_shape * self.num_filters

	    # Range of values for the filters
	    low = -np.sqrt(6./ (self.fan_in + self.fan_out))
	    high = np.sqrt(6./ (self.fan_in + self.fan_out))
	    
	    self.filter_shape = (num_filters, num_feature_maps, filter_height, filter_width)
	    
	    # Get filters and bias
	    self.filters = get_weights(low=low, high=high, shape=self.filter_shape, name=name + '__filters')
	    self.bias = get_bias(self.num_filters, name=name + '__bias')
	    self.params = [self.filters, self.bias]
	    
	def fprop(self, input):
	    
	    # Convolve the input
	    self.convolution = T.nnet.conv.conv2d(
	        input=input,
	        filters=self.filters,
	        filter_shape=self.filter_shape,
	        border_mode='full' if self.wide else 'valid'
	    )
	    
	    self.conv_out = T.tanh(self.convolution + self.bias.dimshuffle('x', 0, 'x', 'x'))
	    
	    # If the layer has pooling, downsample the convolution output
	    if not self.pooling_factor:
	    	return self.conv_out
	    else:	
		    self.pooled_out = downsample.max_pool_2d(
		        input=self.conv_out,
		        ds=self.pooling_factor,
		        ignore_border=True
		    )

	    # If the layer's output needs to be flattened (for input to a fully connected layer) set output dim to 2
	    if self.flatten:
	    	return self.pooled_out.flatten(ndim=2)
	    else:
	    	return self.pooled_out


class EmbeddingLayer:

	"""
	Embedding layer that acts as a lookup table
	"""

	def __init__(self, input_dim, output_dim, pretrained=None, name='embedding'):

		self.input_dim = input_dim
		self.output_dim = output_dim
		self.pretrained = pretrained

		self.embedding = get_weights(low=-1.0, high=1.0, shape=(input_dim, output_dim), name=name + '__embedding')

		if self.pretrained is not None:
			assert input_dim == pretrained.shape[0] and output_dim == pretrained.shape[1]
			self.embedding = theano.shared(pretrained.astype(np.float32), borrow=True, name=name + '__pretrained_embedding')
		
		self.params = [self.embedding]

	def fprop(self, input):

		return self.embedding[input]
