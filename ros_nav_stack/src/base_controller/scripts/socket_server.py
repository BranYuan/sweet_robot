#!/usr/bin/env python3
# coding:utf-8
import socket
import SerialCmd
import time
import commands

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
                cmd_data = conn_rob.recv(1024)
                if cmd_data:
                    if not ser.serial.isOpen():
                        ser.open_port('/dev/ttyUSB0')
                    if ser.serial.isOpen():
                        ser.send_cmd(cmd_data)
                else:
                    break
            except:
                print('err')
                break
        conn_rob.close()