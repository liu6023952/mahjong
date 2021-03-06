# -*- coding: utf-8 -*-
# @Time    : 18-3-1 下午5:53
# @Author  : Yan
# @Site    : 
# @File    : CNNmodel_sysnthesis_kings.py
# @Software: PyCharm Community Edition
# @Function: 
# @update:

"""
利用keras对tensorflow的代码进行重构的简单版
一般的epoch=10
根据层数不同命名,规则如下
e10--epoch=10,c1--cov=1,l2r--regularizers=l2,d2--dense=2,u1200--units=1200
"""
from __future__ import division
from __future__ import print_function

import keras
import numpy as np
import matplotlib.pyplot as plt
import datetime
# import txt2pic

np.random.seed(1337)  # for reproducibility
from keras.utils import np_utils
from keras.models import Sequential
from keras.layers import Dense, Activation, Convolution2D, MaxPooling2D, Flatten, Dropout
from keras.optimizers import Adam
from keras import regularizers
from keras.utils.vis_utils import plot_model


# 写一个LossHistory类，保存loss和acc
class LossHistory(keras.callbacks.Callback):
    def on_train_begin(self, logs={}):
        self.losses = {'batch': [], 'epoch': []}
        self.accuracy = {'batch': [], 'epoch': []}
        self.val_loss = {'batch': [], 'epoch': []}
        self.val_acc = {'batch': [], 'epoch': []}

    def on_batch_end(self, batch, logs={}):
        self.losses['batch'].append(logs.get('loss'))
        self.accuracy['batch'].append(logs.get('acc'))
        self.val_loss['batch'].append(logs.get('val_loss'))
        self.val_acc['batch'].append(logs.get('val_acc'))

    def on_epoch_end(self, batch, logs={}):
        self.losses['epoch'].append(logs.get('loss'))
        self.accuracy['epoch'].append(logs.get('acc'))
        self.val_loss['epoch'].append(logs.get('val_loss'))
        self.val_acc['epoch'].append(logs.get('val_acc'))

    def loss_plot(self, loss_type):
        iters = range(len(self.losses[loss_type]))
        plt.figure()
        # acc
        plt.plot(iters, self.accuracy[loss_type], 'r', label='train acc')
        # loss
        plt.plot(iters, self.losses[loss_type], 'g', label='train loss')
        if loss_type == 'epoch':
            # val_acc
            plt.plot(iters, self.val_acc[loss_type], 'b', label='val acc')
            # val_loss
            plt.plot(iters, self.val_loss[loss_type], 'k', label='val loss')
        plt.grid(True)
        plt.xlabel(loss_type)
        plt.ylabel('acc-loss')
        plt.legend(loc="upper right")
        plt.savefig('loss/loss_sys_e10c2d3l2r.png')
        plt.show()


# time record
starttime = datetime.datetime.now()

batch = 50
input_features = 296
output_features = 34
units = 1200
num_epoch = 10
model_save_path = 'model/sys_e10c2d3l2r.h5'
model_pic = 'model/sys_e10c2d3l2r.png'

# data path
trainData_tmp = np.loadtxt('small_train_18.txt', delimiter=' ', dtype=np.float16)
testData_tmp = np.loadtxt('small_test_18.txt', delimiter=' ', dtype=np.float16)

x_train = np.array(trainData_tmp[:, 0:-1])
y_train = np.array(trainData_tmp[:, -1]).astype(np.int32)
y_train = np_utils.to_categorical(y_train, num_classes=34)

x_test = np.array(testData_tmp[:, 0:-1])
y_test = np.array(testData_tmp[:, -1]).astype(np.int32)
y_test = np_utils.to_categorical(y_test, num_classes=34)

# reshape
x_train = x_train.reshape(-1, 1, 18, 18)
x_test = x_test.reshape(-1, 1, 18, 18)


# model define
model = Sequential()
model.add(Convolution2D(
    batch_input_shape=(None, 1, 18, 18),
    filters=64,
    kernel_size=3,
    strides=1,
    padding='same',     # Padding method
    data_format='channels_first',
))
model.add(Activation('relu'))

model.add(Convolution2D(64, 3, strides=1, padding='same', data_format='channels_first'))
model.add(Activation('relu'))

# Pooling layer 2 (max pooling) output shape (64, 7, 7)
model.add(MaxPooling2D(2, 2, 'same', data_format='channels_first'))

# Fully connected layer 1 input shape (64 * 7 * 7) = (3136), output shape (1024)
model.add(Flatten())
model.add(Dense(1024))
model.add(Dense(1024))
model.add(Activation('relu'))

# Fully connected layer 2 to shape (10) for 10 classes
model.add(Dense(34))
model.add(Activation('softmax'))


adam = Adam(lr=1e-4)
# We add metrics to get more results you want to see
model.compile(optimizer=adam,
              loss='categorical_crossentropy',
              metrics=['accuracy'])
model.summary()
print(model)

# 创建一个实例history
history = LossHistory()
plot_model(model, to_file=model_pic)

# 开始训练和测试
print('Training ------------')
model.fit(x_train, y_train, batch_size=batch,epochs=num_epoch, validation_data=(x_test, y_test), callbacks=[history])
print('\nTesting ------------')
loss, accuracy = model.evaluate(x_test, y_test)
print('\ntest loss: ', loss)
print('\ntest accuracy: ', accuracy)
model.save(model_save_path)
# 绘制acc-loss曲线
history.loss_plot('epoch')

endtime = datetime.datetime.now()
print('usetime | ',endtime - starttime)

