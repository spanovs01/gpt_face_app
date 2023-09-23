import serial, time

ser = serial.Serial ('/dev/ttyAMA1', 921600,  timeout = 3) #Open named port
ser.write("CMD:START_FW\r\n".encode('ascii')) #Send back the received data
