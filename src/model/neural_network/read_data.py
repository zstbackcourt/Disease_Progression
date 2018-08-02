# coding=utf-8
import numpy as np

import rnn_config as config


class LoadData(object):
    def __init__(self, train_config, model_config):
        """
         encapsulation the load data process
        要求输入BTD, 输出TBD
        """
        self.__batch_size = train_config.actual_batch_size
        self.__train_x_path = train_config.train_x_path
        self.__train_t_path = train_config.train_t_path
        self.__test_t_path = train_config.test_t_path
        self.__test_x_path = train_config.test_x_path
        self.__time_length = model_config.max_time_stamp
        self.__batch_count = None
        self.__global_batch_index = 0
        self.__x_depth = model_config.input_x_depth
        self.__t_depth = model_config.input_t_depth

        self.__origin_train_x, self.__origin_train_t, self.__origin_test_x, self.__origin_test_t = self.__read_data()
        self.__origin_test_x = np.transpose(self.__origin_test_x, [1, 0, 2])
        self.__origin_test_t = np.transpose(self.__origin_test_t, [1, 0, 2])

        self.__batch_train_x, self.__batch_train_t = self.__pre_process(self.__origin_train_x, self.__origin_train_t)

    def get_batch_count(self):
        return self.__batch_count

    def __read_data(self):
        """
        the data structure of origin_data
        :return:
        train_x: [train_sample_size, time_length, x_depth]
        train_t: [train_sample_size, time_length, t_depth]
        test_x: [test_sample_size, time_length, x_depth]
        test_t: [test_sample_size, time_length, t_depth]
        """
        # TODO check
        train_x = np.load(self.__train_x_path)
        train_t = np.load(self.__train_t_path)
        test_x = np.load(self.__test_x_path)
        test_t = np.load(self.__test_t_path)

        return train_x, train_t, test_x, test_t

    def get_train_next_batch(self):
        """
        return next batch.
        :return:
        """
        if self.__global_batch_index == self.__batch_count:
            batch_train_x, batch_train_t = self.__pre_process(self.__origin_train_x, self.__origin_train_t)
            self.__batch_train_x, self.__batch_train_t = batch_train_x, batch_train_t
            self.__global_batch_index = 0

        x, t = self.__batch_train_x[self.__global_batch_index], self.__batch_train_t[self.__global_batch_index]
        self.__global_batch_index += 1
        return x, t

    def get_test_data(self):
        return self.__origin_test_x, self.__origin_test_t

    def __pre_process(self, train_x, train_t):
        """
        shuffle and reshape the data
        :param train_x: [train_sample_size, time_length, x_depth]
        :param train_t: [train_sample_size, time_length, t_depth]
        :return:
        shuffled, and convert data from batch_major to time_major
        train_x: [batch_count, time_length, batch_size, x_depth]
        train_t: [batch_count, time_length, batch_size, t_depth]
        """
        batch_size = self.__batch_size

        # 数据随机化
        train_data = np.concatenate((train_x, train_t), axis=2)
        np.random.shuffle(train_data)

        train_x = train_data[:, :, 0:-1]
        train_t = train_data[:, :, -1]
        train_t = train_t[:, :, np.newaxis]

        data_length = len(train_x)
        self.__batch_count = data_length // batch_size
        discard = data_length % batch_size
        train_x = train_x[0:data_length - discard, :, :]
        train_t = train_t[0:data_length - discard, :, :]

        # reshape
        train_x = np.reshape(train_x, [data_length // batch_size, batch_size, train_x.shape[1], train_x.shape[2]])
        train_t = np.reshape(train_t, [data_length // batch_size, batch_size, train_t.shape[1], train_t.shape[2]])

        # BTD TO TBD
        train_x = np.transpose(train_x, [0, 2, 1, 3])
        train_t = np.transpose(train_t, [0, 2, 1, 3])

        return train_x, train_t


def unit_test():
    train_config, model_config = config.validate_configuration_set()
    load_data = LoadData(train_config=train_config, model_config=model_config)
    for i in range(0, 100):
        load_data.get_train_next_batch()


if __name__ == "__main__":
    unit_test()