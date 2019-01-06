#!/usr/bin/python2.7
# coding:utf-8
import socket
import SerialCmd
import time

#IP_PORT = ('0.0.0.0', 6666)
#SOCKET_ROB = socket.socket()
#SOCKET_ROB.bind(IP_PORT)
MAX_SPEED = 2500

def speed_calculate(max_speed,speeds_cw,speeds_ccw):
    if type(max_speed) is int and max_speed >= 0 and type(speeds_cw) is list and len(speeds_cw) == 13 and type(speeds_ccw) is list and len(speeds_ccw) == 13:
        if max_speed > MAX_SPEED:
            max_speed = MAX_SPEED
        max_speed *= 10
        speeds_cw[7] = max_speed >> 8 & 0xff
        speeds_cw[8] = max_speed & 0xff
        max_speed = 0xffff - max_speed + 1
        speeds_ccw[7] = max_speed >> 8 & 0xff
        speeds_ccw[8] = max_speed & 0xff
        crc_calculate(speeds_cw)
        crc_calculate(speeds_ccw)

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
                
    
if __name__ == "__main__":
    while True:
        enables_motor = [0x01,0x10,0x46,0x57,0x00,0x01,0x02,0x00,0x01,0x4d,0xb3]
        disables_motor = [0x01,0x10,0x46,0x57,0x00,0x01,0x02,0x00,0x00,0x8c,0x73]
        speeds_cw =       [0x01,0x10,0x44,0x20,0x00,0x02,0x04,0x27,0x10,0x00,0x00,0xf9,0xc5]
        speeds_ccw =      [0x01,0x10,0x44,0x20,0x00,0x02,0x04,0xd8,0xf0,0xff,0xff,0xc9,0x97]
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
        ser_4G = SerialCmd.SerialCmd(port='/dev/ttyS4')
        ser = SerialCmd.SerialCmd()
        ser_left = SerialCmd.SerialCmd(port='/dev/ttyS2')
        ser_right = SerialCmd.SerialCmd(port='/dev/ttyS3')
        
        print ('listenning:')
        #SOCKET_ROB.listen(5)
        #conn_rob, addr_rob = SOCKET_ROB.accept()
        while True:
            try:
                cur_time = time.strftime("%y-%m-%d",time.localtime(time.time()))
                log_file = open('/home/guardrobot/guardRobot/log_file/'+cur_time+'.txt','a')
                #cmd_data = conn_rob.recv(1024)
                cmd_data = None
                while not cmd_data:
                    if not ser_4G.serial.isOpen():
                        ser_4G.serial.open_port()
                    if ser_4G.serial.isOpen():
                        cmd_data = ser_4G.receive_info_str()
                if log_file:
                    log_file.write(time.strftime("%y-%m-%d-%H:%M:%S",time.localtime(time.time()))+'----'+cmd_data)
                print(cmd_data)
                if cmd_data:
                    head = cmd_data.find("*")
                    end = cmd_data.find("#")
                    if end > head >-1:
                        cmd_data = cmd_data[head:end+1]
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

                    if not ser.serial.isOpen():
                        ser.open_port()
                    if ser.serial.isOpen():
                        ser.send_cmd(cmd_data)
                    if cmd_data == '*STOP#':
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
                    if cmd_data == '*AHEAD#':
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
                    if cmd_data == '*BACK#':
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
                    if cmd_data == '*LEFT#':
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
                    if cmd_data == '*RIGHT#':
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
