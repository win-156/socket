from socket import *
from _thread import *           
import time                     
from json.decoder import JSONDecodeError
import json


ThreadCount = 0
HOST = "127.0.0.1"
SERVER_PORT = 7500
FORMAT = 'utf-8'  


#Func kiểm tra 2 mốc thời gian, Time>2h ? false:true
def TestTime(PassTime):
    PassTime = PassTime.split(':')
    PassTime = list(map(int, PassTime))

    t = time.localtime()
    TimeNow = time.strftime("%H:%M:%S", t)
    TimeNow = TimeNow.split(':')
    TimeNow = list(map(int, TimeNow))
    
    hours = 0
    minute = 0
    if TimeNow[0] == PassTime[0]:
        return True

    elif TimeNow[0] > PassTime[0]:
        hours = TimeNow[0] - PassTime[0] - 1
        minute = 60 - PassTime[1]
        minute = minute + TimeNow[1]
        while(minute >=60):
            hours+=1
            minute-=60
        if hours >= 2:
            return False
        else:
            return True

    else:
        hours = PassTime[0] - TimeNow[0] - 1
        minute = 60 - PassTime[1]
        minute = minute + TimeNow[1]
        while(minute >=60):
            hours+=1
            minute-=60
        if hours >= 2:
            return False
        else:
            return True

def totalOrder(ObjUsers):
    totalPrice = 0
    for i in ObjUsers['order']:
        totalPrice = totalPrice + (i['price']*i['amount'])
    return totalPrice
def findUser(table):
    with open("Data/Users.json", "r") as file:
        try:
            previous_json = json.load(file)
            for f in previous_json:
                if f['tableNumber'] == table and TestTime(f['time']):
                    global ObjUser
                    boool = True
                    ObjUser = f
                    return boool, ObjUser
        except JSONDecodeError:
            pass
    boool = False       
    return boool, 0    

#tạo ra 1 đơn hàng mẫu, với các thông tin = NULL 
def createUser(tableNumber):
    
    users = {
                "time": 0,
                "tableNumber": "",
                "order":[],
                "pay":0,
                "total": 0
            }
    
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    users['time'] = current_time
    users["tableNumber"] = tableNumber
    return users

# Lưu thông tin và lịch sử đặt bàn
def retrievedata(tableNumber):
    global list_data,ObjUser,payTotal
    list_data = []

    with open("Data/Users.json", "r") as file:
        try:
            previous_json = json.load(file)
            for f in previous_json:
                if f['tableNumber'] == tableNumber and TestTime(f['time']):
                    continue
                else:
                    list_data.append(f)

        except JSONDecodeError:
            pass
        boool, ObjUser = findUser(tableNumber)
    if boool:
        return ObjUser
    else:
        ObjUser = createUser(tableNumber)
        return ObjUser

#Hàm này sẽ được gọi khi dùng chức năng multil client
def multi_thread_client(clientSocket):
    global ObjUser
    while True:
        message = clientSocket.recv(1024).decode(FORMAT)
        ObjUser = retrievedata(message)
        payTotal = totalOrder(ObjUser)

        message = json.dumps(ObjUser)
        clientSocket.sendall(message.encode(FORMAT))

        message = clientSocket.recv(1024).decode(FORMAT)
        ObjUser = json.loads(message)
        
        totalPrice = totalOrder(ObjUser)
        ObjUser['total'] = totalPrice

        payTotal = totalPrice - payTotal
        ObjUser['pay'] += payTotal

        message = json.dumps(ObjUser)

        clientSocket.sendall(message.encode(FORMAT))

        message = clientSocket.recv(1024).decode(FORMAT)

        if message == '1':
            clientSocket.sendall(message.encode(FORMAT))
            while True:
                message = clientSocket.recv(1024).decode(FORMAT)
                if message != "" and message.isdecimal() and len(message) ==10:
                    ObjUser['pay'] = 0
                    boool = "1"
                    clientSocket.sendall(boool.encode(FORMAT))
                    list_data.append(ObjUser)
                    with open('Data/Users.json' , 'w') as file:
                        json.dump(list_data, file, indent=4)
                        break
                else:
                    boool = "0"
                    clientSocket.sendall(boool.encode(FORMAT))
        else:
            clientSocket.sendall(message.encode(FORMAT))
            while True:
                message = clientSocket.recv(1024).decode(FORMAT)
                if message != "" and message.isdecimal():
                    if int(message) >= ObjUser['pay']:
                        boool = int(message) - ObjUser['pay'] 
                        ObjUser['pay'] = 0
                        boool = str(boool)
                        list_data.append(ObjUser)
                        with open('Data/Users.json' , 'w') as file:
                            json.dump(list_data, file, indent=4)
                        clientSocket.sendall(boool.encode(FORMAT))
                        break

                    else:
                        boool = 'lessMoney'
                        clientSocket.sendall(boool.encode(FORMAT))
                else:
                    boool = "false"
                    clientSocket.sendall(boool.encode(FORMAT))
            
    

#Đọc thông tin file data.json
# sử lý dữ liệu để lấy tên của ảnh, gọi hàm sendOneImage để tiến hành gửi ảnh
def sendimages(fileHaveNameImage, connected):

    with open(fileHaveNameImage) as file:
        data_menu = json.load(file)
        for i in data_menu:
            for j in data_menu[i]:
                sendOneImage(j['image'], connected)

#Sau khi có được tên ảnh, func này sẽ đọc dữ liệu từ file ảnh có tên được cung cấp
#Đọc theo từng gói với dung lượng 2048 bits
#Func sẽ đọc file ảnh và gửi dữ liệu vừa đọc cho đến khi đọc đến cuối file ảnh thì dừng lại
def sendOneImage(nameImage, connected):
        file = open('ImagesOfSever/' + nameImage, 'rb')
        image_data = file.read(2048)

        while image_data:
            connected.send(image_data)
            connected.recv(2048)
            image_data = file.read(2048)
            
        msg = b"end"
        connected.send(msg)
        file.close()


#tương tự như gửi ảnh thì gửi menu cũng tương tự
#Chương trình sẽ đọc và gửi từng gói dữ liệu đến khi đọc đến cuối file dữ liệu menu
def sendMenu(fileHaveNameImage, connected):
    with open(fileHaveNameImage, 'rb') as file:
        menu_data = file.read(2048)
        while menu_data:
            connected.send(menu_data)
            connected.recv(2048)
            menu_data = file.read(2048)
                
        msg = b"end"
        connected.send(msg)
#tạo socket và lắng nghe client kết nối tới
hostSocket = socket(AF_INET, SOCK_STREAM)
hostSocket.bind((HOST, SERVER_PORT))
hostSocket.listen(100)
print ("Waiting for connection...")




#Bắt đầu thực hiện sử lý dữ liệu
#Main
while True:
    clientSocket, clientAddress = hostSocket.accept()
    sendMenu('Data/data.json', clientSocket)
    sendimages('Data/data.json', clientSocket)
    print ("Connection established with: ", clientAddress[0] + ":" + str(clientAddress[1]))
    start_new_thread(multi_thread_client, (clientSocket,))
    
    ThreadCount += 1
    print('Thread number: ' + str(ThreadCount))


