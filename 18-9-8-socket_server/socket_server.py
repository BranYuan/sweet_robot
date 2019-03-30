#!/usr/bin/python2.7
# coding:utf-8
import socket
import SerialCmd
import os
import subprocess

IP_PORT = ('0.0.0.0', 6666)
SOCKET_ROB = socket.socket()
SOCKET_ROB.bind(IP_PORT)

if __name__ == "__main__":
    while True:
        ser = SerialCmd.SerialCmd()
        print ('listenning:')
        SOCKET_ROB.listen(5)
        conn_rob, addr_rob = SOCKET_ROB.accept()
        while True:
            try:
                fnull = open(os.devnull,'w')
                flag_break = subprocess.call('ping 61.135.169.125',shell = True, stdout = fnull, stderr = fnull)
                print('ping over')
                if flag_break:
                    print('disconnected the net')
                    if not ser.serial.isOpen():
                        ser.open_port
                    if ser.serial.isOpen():
                        ser.send_cmd('*STOP#')
                cmd_data = conn_rob.recv(1024)
                if cmd_data:
                    if not ser.serial.isOpen():
                        ser.open_port()
                    if ser.serial.isOpen():
                        ser.send_cmd(cmd_data)
                else:
                    break
            except:
                print('err')
                break
        conn_rob.close()
