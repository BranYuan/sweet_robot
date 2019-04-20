#!/usr/bin/python2.7
# coding:utf-8
import socket
import SerialCmd
import time
import cv2
import camera_1

#IP_PORT = ('0.0.0.0', 6666)
#SOCKET_ROB = socket.socket()
#SOCKET_ROB.bind(IP_PORT)
MAX_SPEED = 2500

#speed_cw 和 speed_ccw的命令的list合成,用于固定速度控制模式时的正反转速度的计算
def speed_calculate(max_speed,speeds_cw,speeds_ccw):
    if type(max_speed) is int and max_speed >= 0 and type(speeds_cw) is list and len(speeds_cw) == 13 and type(speeds_ccw) is list and len(speeds_ccw) == 13:
        #输入速度大于最大速度则取最大速度
        if max_speed > MAX_SPEED:
            max_speed = MAX_SPEED
        max_speed *= 10     #速度的10倍
        speeds_cw[7] = max_speed >> 8 & 0xff    #速度高八位
        speeds_cw[8] = max_speed & 0xff         #速度低八位
        max_speed = 0xffff - max_speed + 1      #速度的负数的补码计算，用于反向速度设置
        speeds_ccw[7] = max_speed >> 8 & 0xff   
        speeds_ccw[8] = max_speed & 0xff
        crc_calculate(speeds_cw)        #校验位计算
        crc_calculate(speeds_ccw)


#speed_l 和 speed_r的命令的list合成,用于变速度控制模式时的速度的计算
def speed_calculate(speed_l,speed_r,speeds_l,speeds_r):
    if speed_l >= 0 and speed_r >= 0 and len(speeds_l) == 13 and len(speeds_r) == 13:
        #输入速度大于最大速度则取最大速度
        if speed_l > MAX_SPEED:
            speed_l = MAX_SPEED
        if speed_r > MAX_SPEED:
            speed_r = MAX_SPEED
        speed_l *= 10     #左轮电机速度的10倍
        speed_r *= 10     #右轮电机速度的10倍
        speeds_l[7] = speed_l >> 8 & 0xff    #速度高八位
        speeds_l[8] = speed_l & 0xff         #速度低八位
        speeds_r[7] = speed_r >> 8 & 0xff
        speeds_r[8] = speed_r & 0xff
        crc_calculate(speeds_l)        #校验位计算
        crc_calculate(speeds_r)


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
                
def auto_run(uper_percentage,lower_percentage):


if __name__ == "__main__":
    while True:
        enables_motor = [0x01,0x10,0x46,0x57,0x00,0x01,0x02,0x00,0x01,0x4d,0xb3]    #电机使能
        disables_motor = [0x01,0x10,0x46,0x57,0x00,0x01,0x02,0x00,0x00,0x8c,0x73]   #电机取消使能
        speeds_cw =       [0x01,0x10,0x44,0x20,0x00,0x02,0x04,0x27,0x10,0x00,0x00,0xf9,0xc5]    #电机正转速度
        speeds_ccw =      [0x01,0x10,0x44,0x20,0x00,0x02,0x04,0xd8,0xf0,0xff,0xff,0xc9,0x97]    #电机反转速度
        '''
        ser_4G = serial.Serial(port='/dev/ttyS1', baudrate=9600, bytesize=8,
                                    parity='N', stopbits=1, timeout=0.5,
                                    write_timeout=0.5)
        ser = serial.Serial(port='/dev/ttyS4', baudrate=9600, bytesize=8,
                                    parity='N', stopbits=1, timeout=0.5,
                                    write_timeout=0.5)

        ser_left = serial.Serial(port='/dev/ttyS2', baudrate=9600, bytesize=8,
                                    parity='N', stopbits=1, timeout=0.5,
                                    write_timeout=0.5)
        ser_right = serial.Serial(port='/dev/ttyS3', baudrate=9600, bytesize=8,
                                    parity='N', stopbits=1, timeout=0.5,
                                    write_timeout=0.5)
        '''
        ser_4G = SerialCmd.SerialCmd(port='/dev/ttyS4')     #4G信号通信端口
        ser = SerialCmd.SerialCmd()     #下位机通信端口
        ser_left = SerialCmd.SerialCmd(port='/dev/ttyS2')   #左电机通信端口
        ser_right = SerialCmd.SerialCmd(port='/dev/ttyS3')  #右电机通信端口
        
        print ('listenning:')
        #SOCKET_ROB.listen(5)
        #conn_rob, addr_rob = SOCKET_ROB.accept()
        auto_flag = False   #自动运行标志，True为自动运行模式，False为遥控模式
        
        while True:
            try:
                cur_time = time.strftime("%y-%m-%d",time.localtime(time.time()))
                #log_file = open('/home/guardrobot/guardRobot/log_file/'+cur_time+'.txt','a')
                log_file = open('/home/sweet/github_store/sweet_robot/4G_controller/log_file'+cur_time+'.txt','a')


                #cmd_data = conn_rob.recv(1024)
                cmd_data = None     #接收控制命令变量


                #接收4G端口数据输入
                '''
                while not cmd_data:
                    if not ser_4G.serial.isOpen():
                        ser_4G.serial.open_port()
                    if ser_4G.serial.isOpen():
                        cmd_data = ser_4G.receive_info_str()
                '''
                #打开端口
                if not ser_4G.serial.isOpen():
                    ser_4G.open_port()
                #若端口打开，且有数据输入，则接收，并记录与logfile中
                if ser_4G.serial.isOpen():
                    if ser_4G.serial.inWaiting():
                        cmd_data = ser_4G.receive_info_str()
                        if log_file:
                            log_file.write(time.strftime("%y-%m-%d-%H:%M:%S",time.localtime(time.time()))+'----'+cmd_data)
                    else:
                        cmd_data = None
                else:
                    cmd_data = None
                
                
                print(cmd_data)
                if cmd_data:
                    #以*开头，#结尾，提取命令字段
                    head = cmd_data.find("*")
                    end = cmd_data.find("#")
                    if end > head >-1:
                        cmd_data = cmd_data[head:end+1]
                    
                    #下位机控制命令发送
                    if not ser.serial.isOpen():
                        ser.open_port()
                    if ser.serial.isOpen():
                        ser.send_cmd(cmd_data)


                    #改变速度
                    if cmd_data.find("*SPEED") == 0 and len(cmd_data) == 11:
                        cmd_data = cmd_data[6:10]
                        int_flag = True
                        for i in cmd_data:
                            if not "0"<= i <= "9":
                                int_flag = False
                        if int_flag:
                            print("speed\n")
                            max_speed = int(cmd_data)
                            speed_calculate(max_speed, speeds_cw, speeds_ccw)
                            if not ser_4G.serial.isOpen():
                                ser_4G.serial.open_port()
                            if ser_4G.serial.isOpen():
                                ser_4G.send_cmd("*SPEED_OK#")
                                log_file.write('\nset speed to:'+ cmd_data +' ----speeds_cw:')                              
                                for i in speeds_cw:
                                    log_file.write(str(hex(i)) + "  ")
                                log_file.write("----speeds_ccw:")
                                for i in speeds_ccw:
                                    log_file.write(str(hex(i)) + "  ")

                    #停止
                    elif cmd_data == '*STOP#':
                        auto_flag = False
                        if not ser_left.serial.isOpen():
                            ser_left.open_port()
                        if ser_left.serial.isOpen():
                            ser_left.send_cmd(disables_motor)
                            log_file.write('----cmd_left_motor sended')
                        if not ser_right.serial.isOpen():
                            ser_right.open_port()
                        if ser_right.serial.isOpen():
                            ser_right.send_cmd(disables_motor)
                            log_file.write('----cmd_right_motor sended')
                    
                    #前进
                    elif cmd_data == '*AHEAD#':
                        auto_flag = False
                        if not ser_left.serial.isOpen():
                            ser_left.open_port()
                        if ser_left.serial.isOpen():
                            ser_left.send_cmd(enables_motor)
                            time.sleep(0.1)
                            ser_left.send_cmd(speeds_ccw)
                            log_file.write('----cmd_left_motor sended')
                        if not ser_right.serial.isOpen():
                            ser_right.open_port()
                        if ser_right.serial.isOpen():
                            ser_right.send_cmd(enables_motor)
                            time.sleep(0.1)
                            ser_right.send_cmd(speeds_cw)
                            log_file.write('----cmd_right_motor sended')
                    
                    #后退
                    elif cmd_data == '*BACK#':
                        auto_flag = False
                        if not ser_left.serial.isOpen():
                            ser_left.open_port()
                        if ser_left.serial.isOpen():
                            ser_left.send_cmd(enables_motor)
                            time.sleep(0.1)
                            ser_left.send_cmd(speeds_cw)
                            log_file.write('----cmd_left_motor sended')
                        if not ser_right.serial.isOpen():
                            ser_right.open_port()
                        if ser_right.serial.isOpen():
                            ser_right.send_cmd(enables_motor)
                            time.sleep(0.1)
                            ser_right.send_cmd(speeds_ccw)
                            log_file.write('----cmd_right_motor sended')
                    
                    #左转
                    elif cmd_data == '*LEFT#':
                        auto_flag = False
                        if not ser_left.serial.isOpen():
                            ser_left.open_port()
                        if ser_left.serial.isOpen():
                            ser_left.send_cmd(enables_motor)
                            time.sleep(0.1)
                            ser_left.send_cmd(speeds_cw)
                            log_file.write('----cmd_left_motor sended')
                        if not ser_right.serial.isOpen():
                            ser_right.open_port()
                        if ser_right.serial.isOpen():
                            ser_right.send_cmd(enables_motor)
                            time.sleep(0.1)
                            ser_right.send_cmd(speeds_cw)
                            log_file.write('----cmd_right_motor sended')
                    
                    #右转
                    elif cmd_data == '*RIGHT#':
                        auto_flag = False
                        if not ser_left.serial.isOpen():
                            ser_left.open_port()
                        if ser_left.serial.isOpen():
                            ser_left.send_cmd(enables_motor)
                            time.sleep(0.1)
                            ser_left.send_cmd(speeds_ccw)
                            log_file.write('----cmd_left_motor sended')
                        if not ser_right.serial.isOpen():
                            ser_right.open_port()
                        if ser_right.serial.isOpen():
                            ser_right.send_cmd(enables_motor)
                            time.sleep(0.1)
                            ser_right.send_cmd(speeds_ccw)
                            log_file.write('----cmd_right_motor sended')
                    
                    #自动运行
                    elif cmd_data == "AUTO_RUN":
                        auto_flag = True

                    print('end')
                else:
                    break
                
            except:
                print('err')
                break
        #conn_rob.close()
            finally:
                if log_file:
                    log_file.write("\n")
                    log_file.close
