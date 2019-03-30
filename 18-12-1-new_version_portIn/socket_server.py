#!/usr/bin/python2.7
# coding:utf-8
import socket
import SerialCmd
import time

#IP_PORT = ('0.0.0.0', 6666)
#SOCKET_ROB = socket.socket()
#SOCKET_ROB.bind(IP_PORT)


if __name__ == "__main__":
    while True:
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
                    enables_motor = [0x00,0x10,0x46,0x57,0x00,0x01,0x02,0x00,0x01,0x4d,0xb3]
                    disables_motor = [0x00,0x10,0x46,0x57,0x00,0x01,0x02,0x00,0x01,0x4d,0xb3]
                    speeds_cw =       [0x01,0x10,0x44,0x20,0x00,0x02,0x04,0x03,0xe8,0x00,0x00,0x72,0xc4]
                    speeds_ccw =      [0x01,0x10,0x44,0x20,0x00,0x02,0x04,0xfc,0x18,0xff,0xff,0x43,0x53]
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
                            ser_left.send_cmd(speeds_cw)
                            log_file.write('----cmd_left_motor sended')
                        if not ser_right.serial.isOpen():
                            ser_right.open_port()
                        if ser_right.serial.isOpen():
                            ser_right.send_cmd(enables_motor)
                            ser_right.send_cmd(speeds_cw)
                            log_file.write('----cmd_right_motor sended')
                    if cmd_data == '*BACK#':
                        if not ser_left.serial.isOpen():
                            ser_left.open_port()
                        if ser_left.serial.isOpen():
                            ser_left.send_cmd(enables_motor)
                            ser_left.send_cmd(speeds_ccw)
                            log_file.write('----cmd_left_motor sended')
                        if not ser_right.serial.isOpen():
                            ser_right.open_port()
                        if ser_right.serial.isOpen():
                            ser_right.send_cmd(enables_motor)
                            ser_right.send_cmd(speeds_ccw)
                            log_file.write('----cmd_right_motor sended')
                    if cmd_data == '*LEFT#':
                        if not ser_left.serial.isOpen():
                            ser_left.open_port()
                        if ser_left.serial.isOpen():
                            ser_left.send_cmd(enables_motor)
                            ser_left.send_cmd(speeds_ccw)
                            log_file.write('----cmd_left_motor sended')
                        if not ser_right.serial.isOpen():
                            ser_right.open_port()
                        if ser_right.serial.isOpen():
                            ser_right.send_cmd(enables_motor)
                            ser_right.send_cmd(speeds_cw)
                            log_file.write('----cmd_right_motor sended')
                    if cmd_data == '*RIGHT#':
                        if not ser_left.serial.isOpen():
                            ser_left.open_port()
                        if ser_left.serial.isOpen():
                            ser_left.send_cmd(enables_motor)
                            ser_left.send_cmd(speeds_ccw)
                            log_file.write('----cmd_left_motor sended')
                        if not ser_right.serial.isOpen():
                            ser_right.open_port()
                        if ser_right.serial.isOpen():
                            ser_right.send_cmd(enables_motor)
                            ser_right.send_cmd(speeds_cw)
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
