
import socket
from tkinter import*
from tkinter.messagebox import * 
import json
from PIL import Image, ImageTk                 
from json.decoder import JSONDecodeError        



HOST = '127.0.0.1'  
PORT = 7500
FORMAT = 'utf-8'       

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (HOST, PORT)
clientSocket.connect(server_address)

print('connecting to %s port ' + str(server_address))

#tạo màn hình tkinter với các thông số bên dưới
root = Tk()
root.config(background="red")
root.geometry('1100x1000')

#func sử lý xoá 1 món trong danh sách order
def delete_selected():
    global ObjUser
    try:
        abs = listbox.curselection()
        indexPosition = (abs[0] - 1)
        sizeUser = len(ObjUser['order']) - 1
        sizelistBox = listbox.size() - 2
        
        indexPosition = sizelistBox - indexPosition
        indexPosition = sizeUser - indexPosition

        ObjUser['order'].pop(indexPosition)
        
        listbox.delete(listbox.curselection())
    except:
        pass
 
#Khuôn mẫu json gồm những thông tin món ăn
def createDish(object):
    order_obj = {
                    "id":0,
                    "name": "",
                    "amount": 0,
                    "price": 0
                }
    order_obj["id"] = object['id']
    order_obj["name"] = object['name']
    order_obj["price"] = object['price']
    order_obj["amount"] = int(amount.get())

    return order_obj

#Tìm món ăn trong data 
def searchId(id):
    data_search = []
    with open('Data/data.json', 'r') as file:
        try:
            data_search = json.load(file)
            for i in data_search:
                for j in data_search[i]:
                    if j['id'] == id:
                        return j
        except JSONDecodeError:
            pass
    return 0

#thông báo ra màn hình lỗi nhập ID
def answerId():
    showerror("Answer", "Xin lỗi bạn đã nhập ID hoặc số lượng sản Phẩm bị sai")    

#Func thêm 1 món vào trong danh sách
def add_item():
    if content.get() != "" and content.get().isdecimal() and amount.get()!= "" and amount.get().isdecimal() and int(amount.get()) > 0:
        if int(content.get()) < 16 and  int(content.get()) >= 0:
            result_search = searchId(int(content.get()))
            
            listbox.insert(END, str(result_search['id']) + '\t' + result_search['name'] + '\t\t\t' + amount.get() + '\t\t' + str(result_search['price']) + '$')
            ObjUser["order"].append(createDish(result_search))

            content.set("")
            amount.set("")
        else:
            answerId()
    else:
        answerId()

# Hàm sử lý khi nhấn nút thanh toán
def StartPay():
    global ObjUser
    pages.destroy()
    msg = json.dumps(ObjUser)
    clientSocket.sendall(msg.encode(FORMAT))
    

    message = clientSocket.recv(1024)
    message = json.loads(message.decode(FORMAT))
    ObjUser = message
    Show_invoice()
#Tổng tiền của các món order
def totalOrder(ObjUser):
    totalPrice = 0
    for i in ObjUser['order']:
        totalPrice = totalPrice + (i['price']*i['amount'])
    return totalPrice

#Hiển thị hoá đơn
def Show_invoice():
    global frame_invoice, payTotal
    frame_invoice = Frame(root)
    frame_invoice.place(relx=0.5, rely=0.5, anchor=CENTER)
    Label(frame_invoice, text='HOÁ ĐƠN', font=('Arian Bold', 30)).grid(row=0, column=0, pady=20)
    global listbox_invoice
    listbox_invoice = Listbox(frame_invoice, width=30)
    listbox_invoice.grid(row=1, column=0,pady=20, padx=100)
    
    for i in ObjUser['order']:
        listbox_invoice.insert(END, str(i['id']) + '\t' + i['name'] + '\t\t\t' + str(i['amount']) + '\t\t' + str(i['price']) + '$')
    listbox_invoice.insert(END," ")

    totalPrice = ObjUser["total"]
    listbox_invoice.insert(END,"Tổng Tiền:\t\t\t\t\t\t" + str(totalPrice) + "$")

    payTotal = ObjUser["pay"]
    listbox_invoice.insert(END,"Tổng tiền thanh toán:\t\t\t\t" + str(ObjUser['pay']) + "$")

    global frame_invoice_button
    frame_invoice_button = Frame(frame_invoice)
    frame_invoice_button.grid(row=2, column=0)

    Label(frame_invoice_button, text="Chọn phương thức thanh toán.", font=("Arial Italic", 12)).grid(row=0,column=0,columnspan=2)
    Button(frame_invoice_button, text="Chuyển khoản", command=lambda:payCard(frame_invoice)).grid(row=1, column=0)
    global button_cash
    button_cash = Button(frame_invoice_button, text="Tiền mặt", command=lambda:payCash(frame_invoice)).grid(row=1, column=1)
def answerCard():
    inp_STK = Input_STK.get()
    clientSocket.sendall(inp_STK.encode(FORMAT))
    msg = clientSocket.recv(1024).decode(FORMAT)
    if msg == '1':
        showerror("Answer", "Thanh toán thành công!")
        frame_invoice.destroy()
        screenStartOrder()
        
    else:
        showerror("Answer", "Số tài khoản không đúng!")
        Input_STK.set('')

def payCard(frame_invoice):
    boool = "1"
    clientSocket.sendall(boool.encode(FORMAT))
    clientSocket.recv(1024)
    frame_invoice_button.destroy()
    frame_invoice_card = Frame(frame_invoice)
    frame_invoice_card.grid(row=2, column=0)
    Label(frame_invoice_card, text="Nhập số tài khoản:").grid(row=0, column=0)
    global Input_STK
    Input_STK = StringVar()
    entry_STK = Entry(frame_invoice_card, textvariable=Input_STK)
    entry_STK.grid(row=0, column=1)
    
    Button(frame_invoice_card, text="OK", command=answerCard).grid(row=0, column=3)

#Sử lý các trường hợp khi server gửi thông báo đến client 
# Về việc thanh toán bằng tiền mặt 
def answerCash():
    inp_money = Input_money.get()
    clientSocket.sendall(inp_money.encode(FORMAT))
    msg = clientSocket.recv(1024).decode(FORMAT)
    if msg == 'lessMoney':
        showerror("Answer", "số tiền không đủ để thanh toán!")
        Input_money.set('')
        
    elif msg == 'false':
        showerror("Answer", "Số tiền nhập vào bị sai cú pháp!")
        Input_money.set('')

    else:
        showerror("Answer", "Thanh toán thành công!\n số tiền thối lại là: " + msg)
        frame_invoice.destroy()
        screenStartOrder()

#UI của nút thanh toán bằng tiền mặt
def payCash(frame_invoice):
    boool = "0"
    clientSocket.sendall(boool.encode(FORMAT))
    clientSocket.recv(1024)

    frame_invoice_button.destroy()
    frame_invoice_cash = Frame(frame_invoice)
    frame_invoice_cash.grid(row=2, column=0)
    Label(frame_invoice_cash, text="Số tiền mặt: ").grid(row=0, column=0)
    global Input_money
    Input_money = StringVar()
    entry_money = Entry(frame_invoice_cash, textvariable=Input_money)
    entry_money.grid(row=0, column=1)
    
    Button(frame_invoice_cash, text="OK", command=answerCash).grid(row=0, column=3)
    
#UI của việc đặt món ăn
def order():

    frame_input = Frame(page_frame1_child1)
    frame_input.pack()

    global content, amount
    content = StringVar()
    amount = StringVar()

    Label(frame_input, text='Nhập ID:').grid(row=0, column=0, sticky=W)
    entry = Entry(frame_input, textvariable=content)
    entry.grid(row=0, column=1, sticky=W)

    Label(frame_input, text='Nhập số lượng: ').grid(row=1, column=0, sticky=W)
    entry2 = Entry(frame_input, textvariable=amount, width=5)
    entry2.grid(row=1, column=1, sticky=W)


    frame_button = Frame(page_frame1_child1)
    frame_button.pack()

    button = Button(frame_button, text="Add Item", command=add_item)
    button.grid(row=0, column=0)

    button_delete_selected = Button(frame_button, text="Delete Selected", command=delete_selected)
    button_delete_selected.grid(row=0, column=1)

    #Danh sách
    global listbox
    listbox = Listbox(page_frame1_child2, width=30, height=10)
    listbox.pack()
    listbox.insert(END, 'ID\tName\t\t\tAmount\t\tPrice')

    bquit = Button(page_frame1_child2, text="Thanh Toán", command=StartPay)
    bquit.pack()

    #Lich su order 
    Label(page_frame1_child2, text="History Order!", font=('Arian Bold', 20)).pack(pady=20)
    global listbox_HOrder
    listbox_HOrder = Listbox(page_frame1_child2, width=30, height=10)
    listbox_HOrder.pack()
    listbox_HOrder.insert(END, 'ID\tName\t\t\tAmount\t\tPrice')


    for passOrder in ObjUser['order']:
        listbox_HOrder.insert(END, str(passOrder['id']) + '\t' + passOrder['name'] + '\t\t\t' +str(passOrder['amount']) + '\t\t' + str(passOrder['price']) + '$')

#xoa menu cu thay menu moi
def nextPage(typeOfDish):
    frame.destroy()
    showMenu(typeOfDish)

#Nut thay doi menu
def pagess():
    Label(root)
    Button(page_frame2_child1, text="khai vị", width=12, command=lambda:nextPage('appetizers')).grid(row=1, column=0)
    Button(page_frame2_child1, text="Món chính", width=12, command=lambda:nextPage('main_dishes')).grid(row=1, column=1)
    Button(page_frame2_child1, text="Tráng miệng", width=12, command=lambda:nextPage('desserts')).grid(row=1, column=2)

# Hien thi menu
def showMenu(typeOfDish):
    row_ = 0
    col_ = 0

    global frame
    frame = Frame(page_frame2_child2)
    with open('Data/data.json', 'r') as f:
        data = json.load(f)
        data = data[typeOfDish]
        
        frame.place(relx=0.5, rely=0.5, anchor=CENTER)

        for i in data:
            img = Image.open('ImagesOfClient/' + i['image'])
            img = img.resize((100, 100))
            img = ImageTk.PhotoImage(img)
            e1 = Label(frame)
            e1.grid(row=row_, column=col_, padx=30, pady=10)
            e1.image = img 

            frame2 = Frame(frame)
            frame2.grid(row=row_+ 1, column=col_)
            Label(frame2, text=i['name'] + '(ID: ' + str(i['id']) + ')', font=("Arial Bold", 15)).grid(row=0, column=0)
            Label(frame2, text=i['describe'], font=("Arial Italic", 10)).grid(row=1, column=0)
            Label(frame2, text= str(i['price']) + "$").grid(row=2, column=0)
            e1['image']=img
            if col_ == 2:
                col_ = 0
                row_ +=2
            else:
                col_+=1

#hien thi màn hình đặt món
def screenMenu():

    global pages
    pages = Frame(root, width=800, height=600)
    pages.place(relx=0.5, rely=0.5, anchor=CENTER)

    global page_frame1
    page_frame1 = Frame(pages, width=300, height=400, padx=50, pady=20)
    page_frame1.grid(row=1, column=0)

    global page_frame1_child1
    page_frame1_child1 = Frame(page_frame1, width=300, height=150)
    page_frame1_child1.grid(row=0, column=0)

    global page_frame1_child2
    page_frame1_child2 = Frame(page_frame1, width=300, height=350)
    page_frame1_child2.grid(row=1, column=0)
    
    global page_frame2
    page_frame2 = Frame(pages,width=400, height=500)
    page_frame2.grid(row=1, column=1)

    global page_frame2_child1
    page_frame2_child1 = Frame(page_frame2,width=400, height=100)
    page_frame2_child1.grid(row=0, column=0)
    Label(page_frame2_child1, text="MENU ORDER.", font=("Arial Bold", 40)).grid(row=0, column=0, columnspan=3, pady=20)

    global page_frame2_child2
    page_frame2_child2 = Frame(page_frame2,width=600, height=400)
    page_frame2_child2.grid(row=1, column=0)


def answer():
    showerror("Answer", "Xin lỗi, bạn nhập sai cú pháp số điện thoại!")

def get_data():
    tableNumber = tableNumber_input.get()
    if tableNumber.isdecimal() and len(tableNumber) < 100:
        pase_start.destroy()
        clientSocket.sendall(tableNumber.encode(FORMAT))
    
        message = clientSocket.recv(1024)
        message = json.loads(message.decode(FORMAT))
        global ObjUser
        ObjUser = message

        screenMenu()
        order()
        showMenu('appetizers')
        pagess()
    else:
        answer()



#Màn hình đầu tiên để nhập số bàn
def screenStartOrder():
    global pase_start, tableNumber
    tableNumber = StringVar()
    pase_start = Frame(root, width=200, height=200)
    
    pase_start.place(relx=0.5, rely=0.5, anchor=CENTER)
    Label(pase_start, text = "Hello Client!", font= ('Helvetica 25 bold')).grid(row = 0, column = 0, columnspan=2)
    Label(pase_start, text = "Table Number:").grid(row = 1, column = 0)
    global tableNumber_input
    tableNumber_input = Entry(pase_start, textvariable=tableNumber)
    tableNumber_input.grid(row = 1, column = 1, padx=10, pady=10)
    button = Button(pase_start, text ="Start Order", bg='red', command= get_data).grid(row=2, column=0, columnspan=2)

#Sau khi bên server gửi ảnh.
#func này sẽ nhận tín hiệu đọc file menu vừa gửi
#Lấy tên của ảnh để tạo ra file ảnh 
#rồi gọn hàm receiveOneImage()
def receiveMoreImages(nameFile, connected):
    with open(nameFile) as file:
        data_menu = json.load(file)
        for i in data_menu:
            for j in data_menu[i]:
                receiveOneImage(j['image'], connected)
# Func này sẽ đưa dữ liệu vừa nhận từ server để đưa vào file ảnh vừa tạo của func receiveMoreImages()
def receiveOneImage (nameImage, connected):
    file = open('ImagesOfClient/' + nameImage, "wb")
    image_chunk = connected.recv(2048)  
    while image_chunk != b'end':
        file.write(image_chunk)
        connected.send(image_chunk)
        image_chunk = connected.recv(2048)
    file.close()
    
#Nhận dữ liệu menu gửi từ server
def receiveMenu(nameFile, connected):
    with open(nameFile, "wb") as file:
        menu_chunk = connected.recv(2048) 
        while menu_chunk != b'end':
            file.write(menu_chunk)
            connected.send(menu_chunk)
            menu_chunk = connected.recv(2048)                 



#Main
receiveMenu('Data/data.json', clientSocket)
receiveMoreImages('Data/data.json', clientSocket)
screenStartOrder()
root.mainloop()




