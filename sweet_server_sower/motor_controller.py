#!/usr/bin/env python
# _*_ coding: utf-8 _*_

"""
Created on 2019-3-7
马达等硬件控制器，上位机

@author:Bran
"""

import SerialCmd
import time

MAX_SPEED = 3000    # 电机最大速度
enables_motor = [0x01,0x06,0x00,0x46,0x7f,0xb2,0xc8,0x5a]    #电机使能
disables_motor = [0x01,0x06,0x00,0xa9,0x00,0x00,0x59,0xea]   #电机停止，速度为0
speeds_cw =   [0x01,0x06,0x00,0xa9,0x03,0x20,0x58,0xc2]    #电机正转速度,默认800
speeds_ccw =  [0x01,0x06,0x00,0xa9,0xfc,0xe0,0x19,0x62]    #电机反转速度，默认-800


ser_4G = SerialCmd.SerialCmd(port='/dev/ttyS4')     #4G信号通信端口
ser = SerialCmd.SerialCmd()     #下位机通信端口

ser_left = SerialCmd.SerialCmd(port='/dev/ttyS2')   #左电机通信端口
ser_left.bauterate = 115200
ser_left.stopbits = 2
ser_left.set_port()

ser_right = SerialCmd.SerialCmd(port='/dev/ttyS3')  #右电机通信端口
ser_right.bauterate = 115200
ser_right.stopbits = 2
ser_right.set_port()


# 遥控运行时，左右轮速度的计算函数
def manul_speed_calculate(max_speed,speeds_cw,speeds_ccw):
    if type(max_speed) is int and max_speed >= 0 and type(speeds_cw) is list and len(speeds_cw) == 8 and type(speeds_ccw) is list and len(speeds_ccw) == 8:
        if max_speed > MAX_SPEED:
            max_speed = MAX_SPEED
        speeds_cw[4] = max_speed >> 8 & 0xff
        speeds_cw[5] = max_speed & 0xff
        max_speed = 0xffff - max_speed + 1
        speeds_ccw[4] = max_speed >> 8 & 0xff
        speeds_ccw[5] = max_speed & 0xff
        crc_calculate(speeds_cw)
        crc_calculate(speeds_ccw)

#校验位计算函数
def crc_calculate(data_list):
    crc = 0xffff
    if type(data_list) is list and len(data_list)>2:
        for i  in data_list[:-2]:
            crc ^= i
            for j in range(8):
                if (crc & 1):
                    crc >>= 1
                    crc ^= 0xA001
                else:
                    crc >>= 1
        data_list[-2] =  crc & 0xff
        data_list[-1] =  crc >>8 & 0xff


# 自动运行
def auto_run():
    cur_time = time.strftime("%y-%m-%d",time.localtime(time.time()))
    #log_file = open('/home/guardrobot/guardRobot/log_file/'+cur_time+'.txt','a')
    log_file =None  #open('/home/sweet/github_store/sweet_robot/4G_controller/log_file'+cur_time+'.txt','a')
    cmd_data = None     #接收控制命令变量
    #打开端口
    if not ser_4G.serial.isOpen():
        ser_4G.open_port()
    #若端口打开，且有数据输入，则接收，并记录与logfile中
    if ser_4G.serial.isOpen():
        while not ser_4G.serial.inWaiting():
            cmd_data = None
        else: # ser_4G.serial.inWaiting():
            cmd_data = ser_4G.receive_info_str()
            ser_4G.send_cmd(cmd_data)
            if log_file:
                log_file.write(time.strftime("%y-%m-%d-%H:%M:%S",time.localtime(time.time()))+'----'+cmd_data)
    else:
        cmd_data = None
    #print(cmd_data)
    if cmd_data:
        print(cmd_data)
        #以*开头，#结尾，提取命令字段
        head = cmd_data.find("*")
        end = cmd_data.find("#")
        if end > head >-1:
            cmd_data = cmd_data[head:end+1]
        
        print("speed\n")
        # 通过遥控改变最大运行速度
        #解析命令：SPEEDXXXX,XXXX为最大速度值
        if cmd_data.find("SPEED") == 1 and len(cmd_data) == 11:
            cmd_data = cmd_data[6:10]
            int_flag = True
            for i in cmd_data:
                if not "0" <= i <= "9":
                    int_flag =False
            if int_flag:
                max_speed = int(cmd_data)
                # 计算速度指令
                manul_speed_calculate(max_speed, speeds_cw, speeds_ccw)
                # 开4G串口
                if not ser_4G.serial.isOpen():
                    ser_4G.serial.open_port()
                if ser_4G.serial.isOpen:
                    ser_4G.send_cmd("*SPEED_OK#")
                    if log_file:
                        log_file.write('\nset speed to:'+ cmd_data +' ----speeds_cw:')
                        for i in speeds_cw:
                            log_file.write(str(hex(i)) + "  ")
                        log_file.write("----speeds_ccw:")
                        for i in speeds_ccw:
                            log_file.write(str(hex(i)) + "  ")
        
        print("sleep")
        print(cmd_data)
        time.sleep(60)
        print("wake_up")


        #下位机控制命令发送
        if not ser.serial.isOpen():
            ser.open_port()
        if ser.serial.isOpen():
            ser.send_cmd(cmd_data)
        #停止
        if cmd_data == '*STOP#':
            if not ser_left.serial.isOpen():
                ser_left.open_port()
            if ser_left.serial.isOpen():
                ser_left.send_cmd(disables_motor)
                if log_file:
                    log_file.write('----cmd_left_motor sended')
            if not ser_right.serial.isOpen():
                ser_right.open_port()
            if ser_right.serial.isOpen():
                ser_right.send_cmd(disables_motor)
                if log_file:
                    log_file.write('----cmd_right_motor sended')
        
        #前进
        elif cmd_data == '*AHEAD#':
            print("forward")
            if not ser_left.serial.isOpen():
                ser_left.open_port()
            if ser_left.serial.isOpen():
                ser_left.send_cmd(enables_motor)
                time.sleep(0.1)
                ser_left.send_cmd(speeds_ccw)
                if log_file:
                    log_file.write('----cmd_left_motor sended')
            if not ser_right.serial.isOpen():
                ser_right.open_port()
            if ser_right.serial.isOpen():
                ser_right.send_cmd(enables_motor)
                time.sleep(0.1)
                ser_right.send_cmd(speeds_cw)
                if log_file:
                    log_file.write('----cmd_right_motor sended')
        
        #后退
        elif cmd_data == '*BACK#':
            if not ser_left.serial.isOpen():
                ser_left.open_port()
            if ser_left.serial.isOpen():
                ser_left.send_cmd(enables_motor)
                time.sleep(0.1)
                ser_left.send_cmd(speeds_cw)
                if log_file:
                    log_file.write('----cmd_left_motor sended')
            if not ser_right.serial.isOpen():
                ser_right.open_port()
            if ser_right.serial.isOpen():
                ser_right.send_cmd(enables_motor)
                time.sleep(0.1)
                ser_right.send_cmd(speeds_ccw)
                if log_file:
                    log_file.write('----cmd_right_motor sended')
        
        #左转
        elif cmd_data == '*LEFT#':
            if not ser_left.serial.isOpen():
                ser_left.open_port()
            if ser_left.serial.isOpen():
                ser_left.send_cmd(enables_motor)
                time.sleep(0.1)
                ser_left.send_cmd(speeds_cw)
                if log_file:
                    log_file.write('----cmd_left_motor sended')
            if not ser_right.serial.isOpen():
                ser_right.open_port()
            if ser_right.serial.isOpen():
                ser_right.send_cmd(enables_motor)
                time.sleep(0.1)
                ser_right.send_cmd(speeds_cw)
                if log_file:
                    log_file.write('----cmd_right_motor sended')
        
        #右转
        elif cmd_data == '*RIGHT#':
            if not ser_left.serial.isOpen():
                ser_left.open_port()
            if ser_left.serial.isOpen():
                ser_left.send_cmd(enables_motor)
                time.sleep(0.1)
                ser_left.send_cmd(speeds_ccw)
                if log_file:
                    log_file.write('----cmd_left_motor sended')
            if not ser_right.serial.isOpen():
                ser_right.open_port()
            if ser_right.serial.isOpen():
                ser_right.send_cmd(enables_motor)
                time.sleep(0.1)
                ser_right.send_cmd(speeds_ccw)
                if log_file:
                    log_file.write('----cmd_right_motor sended')
    
    if log_file:
        if cmd_data:
            log_file.write("\n")
        log_file.close
    

def motor_controller():
    auto_run()
    if ser_4G.serial.isOpen():
        ser_4G.serial.close()
    if ser.serial.isOpen():
        ser.serial.close()
    if ser_left.serial.isOpen():
        ser_left.serial.close()
    if ser_right.serial.isOpen():
        ser_right.serial.close()



if __name__ == '__main__':
    while True:
        #try:
            motor_controller()
            print("ending")
        # except:
        #    print("err")
