'''
modbus rtu 通信协议库
通信协议定义
数据帧格式
Address    Function	Data(n byte)	Check(crc16)
8 bits	   8 bits	N x 8 bits	16 abits

变量名定义：
int  Address		#目标设备地址0-255,即0x00-0xff
int  Function		#功能码,寄存器操作方式，取0-255,即0x00-0xff,默认0x03为读取寄存器数据，0x10为写数据进寄存器
int  crc_H		#crc16校验码高八位(高位在后)	
int  crc_L		#crc16校验码第八位(低位在前)
list data[n-1]		#数据list：cfg[] + data[]

读数据时data[n-1]格式如下：
reg_hi	reg_lo	reg_count_hi	reg_count_lo

读数据的响应data[n-1]格式如下
byte_count	data1_hi	data1_lo	data2_hi        data2_lo	........



方式一写数据,写单个或者多个寄存器，数据包含byte_count时，data[n-1]格式如下：
reg_hi	reg_lo	reg_count_hi	reg_count_lo	byte_count	data1_hi        data1_lo        data2_hi        data2_lo        ........

响应data[n-1]格式如下:
reg_hi  reg_lo  reg_count_hi    reg_count_lo



方式二写数据，写单个寄存器，数据不包含byte)count,只有data1_hi data1_lo时，data[n-1]格式如下:
reg_hi  reg_lo  reg_count_hi    reg_count_lo	data1_hi        data1_lo

响应data[n-1]格式如下:
reg_hi  reg_lo	byte_count


'''
