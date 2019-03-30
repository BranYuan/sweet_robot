#!/usr/bin/python
# coding:utf-8
import socket
import SerialCmd
import time

if __name__ == "__main__":
    while True:
        print ('start:')
        ser = SerialCmd.SerialCmd()
        ser.port = '/dev/ttyUSB0'
        ser.set_port()
        ser.open_port()
        ser.receive_info_str()
        print ('received data : %s', ser.receive_info_str())
        time.sleep(2)
        # cmd = recv_data()
