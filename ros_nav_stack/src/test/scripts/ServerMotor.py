#!/usr/bin/env python3
# coding:utf-8

import SerialCmd
import time

class ServerMotor:

    def __init__(self):
        print('__init__')
        self.ID = 0x01
        self.address = 0x00
        self.ERR = 0x00             # 默认清除报警
        self.data = 0x00
        self.__mode = 0x00
        self.CMD = 0x00
        self.__addressH = 0x00
        self.__addressL = 0x00
        self.__data3 = 0x00
        self.__data2 = 0x00
        self.__data1 = 0x00
        self.__data0 = 0x00
        self.__check = 0x00
        self.__cmd_list = [self.ID, self.CMD, self.__addressH, self.__addressL, self.ERR,
                           self.__data3, self.__data2, self.__data1, self.__data0,
                           self.__check]
        self.ser = SerialCmd.SerialCmd()
        self.ser.timeout = 0.1
        self.ser.write_timeout = 0.1
        self.ser.set_port()

    # 分离目标地址高地八位
    def __address_split(self):
        print('address_split')
        if self.address <= 0xffff:
            self.__addressH = (self.address & 0xff00) >> 8
            self.__addressL = self.address & 0xff
        else:
            self.__addressH = 0x00
            self.__addressL = 0x00

    # 合成校验和
    def __check_sum(self, check_list=None):
        print('Check,len of check_list')
        if check_list is not None:
            if len(check_list) == 10:
                self.__check = 0
                for i in check_list[:9]:
                    self.__check += i
                self.__check &= 0xff
                return 1             # 用于自定义命令输入时检验是否合法
        else:
            sum_check = self.ID + self.CMD + self.__addressH + self.__addressL + self.ERR + self.data
            self.__check = sum_check & 0xff
            return 0

    # 将data分割成几个BYTE，用于数据发送
    def __data_split(self):
        print('data_split')
        if self.data < 0:
            self.__data0 = self.__data1 = self.__data2 = self.__data3 = 0x00
        elif self.data <= 0xff:
            self.__data0 = self.data
            self.__data1 = self.__data2 = self.__data3 = 0x00
        elif self.data <= 0xffff:
            self.__data0 = self.data & 0xff
            self.__data1 = (self.data & 0xff00) >> 8
            self.__data2 = self.__data3 = 0x00
        elif self.data <= 0xffffff:
            self.__data0 = self.data & 0xff
            self.__data1 = (self.data & 0xff00) >> 8
            self.__data2 = (self.data & 0xff0000) >> 16
            self.__data3 = 0x00
        elif self.data <= 0xffffffff:
            self.__data0 = self.data & 0xff
            self.__data1 = (self.data & 0xff00) >> 8
            self.__data2 = (self.data & 0xff0000) >> 16
            self.__data3 = (self.data & 0xff000000) >> 24
        else:
            self.__data0 = self.__data1 = self.__data2 = self.__data3 = 0xff

    # 合成一个符合电机协议规则到命令列表
    def __combine_cmd(self):
        print('combine_cmd')
        self.__cmd_list = [self.ID, self.CMD, self.__addressH, self.__addressL, self.ERR,
                           self.__data3, self.__data2, self.__data1, self.__data0,
                           self.__check]

    # 校验电机的写入类命令是否写入成功,最后到校验和丢弃，不进行判断
    def __write_check(self, cmd):
        print('server_write_check')
        time_waite = 0
        i = 0
        err_record = 0x00
        # 命令不正确，返回False
        if len(cmd) != 10:
            return False
        while time_waite <= 2:
            if not self.ser.serial.in_waiting:
                time.sleep(0.2)
                time_waite += 0.2
            temp_read = self.ser.serial.read()
            if i < 9 and temp_read != b'':
                temp_read = temp_read.hex()
                temp_read = int(temp_read, 16)
                i += 1
                print('i is :', i-1, 'temp_read is:', temp_read, 'cmd[i] is :', cmd[i-1])
                if i == 2:
                    if temp_read != cmd[i-1] + 0x10:
                        i = 0
                elif i == 5:
                    # 判断到ERR位时跳过，并记录ERR信息
                    err_record = temp_read
                else:
                    if temp_read != cmd[i-1]:
                        i = 0
            # 收到电机报错信息则记录返回错误
            if i == 9:
                self.ERR = err_record
                return True
        # 若结束循环，则规定时间内未接收到数据，返回False
        return False

    # 校验电机的读取类命令是否发送成功,若成功，返回收到的数据，若失败，返回False
    def __read_check(self, cmd):
        print('server_read_check')
        time_waite = 0
        i = 0
        err_record = 0x00
        data_list = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        data = 0x00
        # 命令不正确，返回False
        if len(cmd) != 10:
            return False
        while time_waite <= 2:
            if not self.ser.serial.in_waiting:
                time.sleep(0.2)
                time_waite += 0.2
            temp_read = self.ser.serial.read()
            if i < 10 and temp_read != b'':
                print('type of temp_read', type(temp_read))
                temp_read = temp_read.encode('hex')
                temp_read = int(temp_read, 16)
                data_list[i] = temp_read
                i += 1
                print('i is :', i-1, 'temp_read is:', temp_read, 'cmd[i] is :', cmd[i-1])
                # 校验数据头
                if i == 1:
                    print('i==1')
                    if temp_read != cmd[i-1]:
                        i = 0
                # 校验地址高位
                elif i == 3:
                    print('i==3')
                    if temp_read != cmd[i-1]:
                        i = 0
                # 校验地址低位
                elif i == 4:
                    print('i==4')
                    if temp_read != cmd[i-1]:
                        i = 0
                # 记录ERR信息
                elif i == 5:
                    print('i==5')
                    err_record = temp_read
            # 收到电机报错信息则记录返回错误
            if i == 10:
                if self.__check_sum(data_list) == 1:
                    if self.__check == data_list[9] and data_list[1] != 0x5F:
                        self.ERR = err_record
                        for j in data_list[5:9]:
                            data = (data << 8) + j
                        return data
                break
        # 若结束循环，则规定时间内未接收到数据，返回False
        return False

    # 支持直接输入发送命令和通过实例属性来合成命令两种放送命令方式，直接发送到命令须满足len(list)==10.
    def send_cmd_write(self, server_cmd=None):
        print('send_cmd_write')
        if server_cmd is None:
            self.__address_split()
            self.__data_split()
            self.__check_sum()
            self.__combine_cmd()
            server_cmd = self.__cmd_list
        print('len of server_cmd is :', len(server_cmd), '\nserver_cmd is :', server_cmd)
        if len(server_cmd) != 10:
            return False
        if self.ser.serial.isOpen():
            self.ser.serial.flushInput()
            self.ser.send_cmd(server_cmd)
            send_flag = self.__write_check(server_cmd)
            if not send_flag:
                print('send_flag is :', send_flag)
                return False
        else:
            return False
        return True

    # 支持直接输入发送命令和通过实例属性来合成命令两种放送命令方式，直接发送到命令须满足len(list)==10.
    def send_cmd_read(self, server_cmd=None):
        print('send_cmd_read')
        if self.ser.serial.isOpen():
            self.ser.serial.flushInput()
            self.ser.send_cmd(server_cmd)
            return self.__read_check(server_cmd)
        return False

    # 读取目标地址信息命令
    def read_status(self, address=None):
        data = False
        if not isinstance(address, int) or address is None:
            return data
        cmd = [self.ID, 0xA0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0f, 0x00]
        cmd[2] = (address & 0xff00) >> 8
        cmd[3] = address & 0xff
        if self.__check_sum(cmd) == 1:
            cmd[9] = self.__check
            data = self.send_cmd_read(cmd)
        return data

    # 读取电机当前速度
    def read_speed(self):
        print('speed read')
        data = self.read_status(0x7075)
        return data

    def read_position(self):
        print('position read')
        data = self.read_status(0x7071)
        return data

    # read if err exist is server
    def read_err_info(self):
        print('position read')
        data = self.read_status(0x7001)
        if self.ERR != 0x00 or data == 0x08:
            data = self.read_status(0x7011)
        return data

    # 电机上电
    def enable(self):
        print('server_enable')
        if not self.ser.serial.isOpen():
            return False
        cmd_enable = [self.ID, 0x52, 0x70, 0x19, 0x00, 0x00, 0x00, 0x00, 0x0f, 0xEB]
        if self.__check_sum(cmd_enable) != 1:
            return False
        cmd_enable[9] = self.__check
        return self.send_cmd_write(cmd_enable)

    def clear_err(self):
        print('clear_err')
        if not self.ser.serial.isOpen():
            return False
        cmd = [self.ID, 0x52, 0x70, 0x19, 0x00, 0x00, 0x00, 0x00, 0x86, 0x4d]
        if self.__check_sum(cmd) != 1:
            return False
        cmd[9] = self.__check
        return self.send_cmd_write(cmd)

    # 电机加减速度设置，默认值为0，即不，不可设置为0
    def set_acc(self, acc=0, de_acc=0):
        print('server_acc_set')
        set_flag = False
        if acc > 0:
            self.address = 0x7096
            self.ERR = 0x00
            self.data = acc
            self.CMD = 0x52
            set_flag = self.send_cmd_write()
            if not set_flag:
                return set_flag

        if de_acc > 0:
            self.address = 0x7097
            self.ERR = 0x00
            self.data = de_acc
            self.CMD = 0x52
            set_flag = self.send_cmd_write()
            if not set_flag:
                return set_flag

        return set_flag

    # 工作模式设置,mode == 3,带加减速的速度模式; mode == 1 位置模式， mode == 6 原点模式。
    def set_mode(self, mode=3):
        print('server_mode_set')
        if not self.ser.serial.isOpen():
            return False
        if mode == 3 or mode == 1 or mode == 6:
            cmd_mode_set = [self.ID, 0x51, 0x70, 0x17, 0x00, 0x00, 0x00, 0x00, mode, 0x00]
            check_flag = self.__check_sum(cmd_mode_set)
            if check_flag == 1:
                cmd_mode_set[9] = self.__check
                print('cmd_mode_set:', cmd_mode_set)
                if self.send_cmd_write(cmd_mode_set):
                    self.__mode = mode
                    return True
        return False

    # 设置电机速度
    def set_speed(self, speed):
        print('speed set')
        set_flag = False
        if self.__mode != 3:
            return set_flag
        self.address = 0x70B1
        self.ERR = 0x00
        self.data = speed
        self.CMD = 0x54
        return self.send_cmd_write()


if __name__ == '__main__':
    print('start:')
    left_sever = ServerMotor()
    left_sever.ID = 0x01
    left_sever.CMD = 0x51
    left_sever.address = 0x7017
    left_sever.ERR = 0xff
    left_sever.data = 0xf1f201F4
    left_sever.ser = SerialCmd.SerialCmd()
    left_sever.ser.write_timeout = 2
    if left_sever.ser.set_port():
        while(1):
            time.sleep(3)
            print('start to set speed:')
            '''
            left_sever.server_acc_set(80, 80)
            left_sever.server_mode_set(3)
            left_sever.sever_enable()
            left_sever.server_speed_set(500)
            '''
            print('mode set status', left_sever.read_speed())
            time.sleep(10)
    else:
        print('串口设置失败')

