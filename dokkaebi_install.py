import paramiko
import time
import tkinter.ttk as ttk
from tkinter import *
from tkinter import filedialog
import tkinter.messagebox as msgbox
import webbrowser

def waitStrems(chan): 
    time.sleep(1) 
    outdata=errdata = "" 
    while chan.recv_ready(): 
        outdata += str(chan.recv(1000)) +"\n"     
    while chan.recv_stderr_ready(): 
        errdata += str(chan.recv_stderr(1000)) 
    return outdata, errdata

def docker_install():
    channel.send("sudo apt update\n")
    outdata, errdata = waitStrems(channel)
    # print(outdata)
    # print(errdata)

    channel.send('sudo apt-get install ca-certificates curl gnupg lsb-release\n')
    outdata, errdata = waitStrems(channel)
    # print(outdata)

    channel.send('sudo mkdir -p /etc/apt/keyrings\n')
    outdata, errdata = waitStrems(channel)
    # print(outdata)

    channel.send('curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg\n')
    outdata, errdata = waitStrems(channel)
    # print(outdata)

    channel.send('y\n')
    outdata, errdata = waitStrems(channel)
    # print(outdata)

    channel.send('''echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
    $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null\n''')
    outdata, errdata = waitStrems(channel)
    # print(outdata)

    channel.send('sudo apt update\n')
    outdata, errdata = waitStrems(channel)
    # print(outdata)

    channel.send('sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin\n')
    outdata, errdata = waitStrems(channel)
    # print(outdata)

    channel.send('y\n')
    outdata, errdata = waitStrems(channel)
#    print(outdata)

def dokkaebi_install():
    channel.send('sudo systemctl start docker\n')
    outdata, errdata = waitStrems(channel)

    channel.send('sudo systemctl enable docker\n')
    outdata, errdata = waitStrems(channel)

    channel.send('sudo chmod 666 /var/run/docker.sock\n')
    outdata, errdata = waitStrems(channel)
    
    channel.send('sudo docker run -d -p 8482:80 -v /var/run/docker.sock:/var/run/docker.sock -v /usr/bin/docker:/usr/bin/docker -v /var/dockerby:/var/dockerby --name dockerby edh1021/dockerby:latest\n')
    outdata, errdata = waitStrems(channel)
    # print(outdata)

def getAuthkey():
    global authkey

    channel.send('docker cp dockerby:/AuthKey /home/ubuntu/\n')
    outdata, errdata = waitStrems(channel)
    # print(outdata)
    channel.send('cat AuthKey\n')
    outdata, errdata = waitStrems(channel)
    authkey = outdata.split("\\r\\n")[1]
    # print(outdata)
    channel.send('rm AuthKey\n')
    outdata, errdata = waitStrems(channel)
    # print(outdata)

    #text창에 출력
    authkeyTxt.delete(0,END)
    authkeyTxt.insert(0, authkey)

def swap(): #추후 개발
    channel.send(' sudo dd if=/dev/zero of=/swapfile bs=128M count=16\n')
    outdata, errdata = waitStrems(channel)
    # print(outdata)
    channel.send('sudo chmod 600 /swapfile\n')
    outdata, errdata = waitStrems(channel)
    # print(outdata)
    channel.send('sudo mkswap /swapfile\n')
    outdata, errdata = waitStrems(channel)
    # print(outdata)
    channel.send('sudo swapon /swapfile\n')
    outdata, errdata = waitStrems(channel)
    # print(outdata)
    channel.send('sudo swapon -s\n')
    outdata, errdata = waitStrems(channel)
    # print(outdata)

def client_connect():
    global client,channel,connect_status
    
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #54.180.101.94
        client.connect(host.get(), username='ubuntu', password=None, key_filename=files)
        channel = client.invoke_shell()
        channel.settimeout(9999)
        connect_status = True
        connectlabel.config(text=" 연결상태 : "+str(connect_status))
        msgbox.showinfo("알림", "연결 되었습니다")
    except Exception as err: # 예외처리
        msgbox.showerror("에러", err)

def client_disconnect():
    global connect_status
    if connect_status:
        client.close()
        connect_status = False
        connectlabel.config(text=" 연결상태 : "+str(connect_status))
        msgbox.showinfo("알림", "연결이 해제되었습니다")
    else:
        msgbox.showwarning("경고", "연결 되어있지 않습니다.")


def add_pem():
    global files
    files = filedialog.askopenfilenames(title="이미지 파일을 선택하세요", \
        filetypes=(("pem 파일", "*.pem"), ("모든 파일", "*.*")), )
    pem.insert(0,files)

def run_dokkaebi():
    if connect_status:
        dokkaebt_url = "http://" + host.get()+":8482"
        webbrowser.open(dokkaebt_url)
    else:
        msgbox.showwarning("경고", "연결 되어있지 않습니다.")




root = Tk()
root.title("Dokkaebi Installer")
root.geometry("640x480") 
authkey = ""
connect_status = False

#프레임
setting_frame = LabelFrame(root,text="Setting")
setting_frame.pack(padx=5, pady=5) # 간격 띄우기
host_frame = Frame(setting_frame)
host_frame.pack(padx=5, pady=5) # 간격 띄우기
pem_frame = Frame(setting_frame)
pem_frame.pack(padx=5, pady=5) # 간격 띄우기
connect_frame = Frame(root)
connect_frame.pack( padx=5, pady=5) # 간격 띄우기

install_frame = LabelFrame(root,text="Install")
install_frame.pack(padx=5, pady=5) # 간격 띄우기

program_frame = LabelFrame(root,text="Authkey")
program_frame.pack( padx=5, pady=5) # 간격 띄우기
authkey_frame = Frame(program_frame)
authkey_frame.pack(padx=5, pady=5) # 간격 띄우기

run_frame = Frame(root)
run_frame.pack(padx=5, pady=5) # 간격 띄우기

#입력 창
#authkey 텍스트
host_label = Label(host_frame, text="host", width=8)
host_label.pack(side="left", padx=5, pady=5)
host = Entry(host_frame, width=60)
host.pack(side="left")
pem_label = Label(pem_frame, text="pem", width=8)
pem_label.pack(side="left", padx=5, pady=5)
pem = Entry(pem_frame, width=60)
pem.pack(side="left")
btn_add_pem = Button(setting_frame, padx=5, pady=5, width=12, text="pem 파일 추가", command=add_pem)
btn_add_pem.pack(side="right")

#버튼
connectBtn = Button(setting_frame, text="연결",command=client_connect)
connectBtn.pack(side="left")
disConnectBtn = Button(setting_frame, text="연결 해제",command=client_disconnect)
disConnectBtn.pack(side="left")
connectlabel = Label(setting_frame, text=" 연결상태 : "+str(connect_status))
connectlabel.pack(side="left")

dockerBtn = Button(install_frame, text="Docker 설치",command=docker_install ,width=70)
dockerBtn.grid(row=0, column=0,  rowspan=3,columnspan=3, sticky=N+E+W+S, padx=3, pady=3)
dokkaebiBtn = Button(install_frame, text="Dokkabi 설치",command=dokkaebi_install,width=70)
dokkaebiBtn.grid(row=5, column=0,  rowspan=3,columnspan=3, sticky=N+E+W+S, padx=3, pady=3)

#authkey 텍스트
authkey_label = Label(authkey_frame, text="Authkey", width=8)
authkey_label.pack(side="left", padx=5, pady=5)
authkeyTxt = Entry(authkey_frame, width=60)
authkeyTxt.pack(side="left")
authkeyBtn = Button(program_frame, text="Authkey 가져오기",command=getAuthkey)
authkeyBtn.pack(side="right")
runDokkaebiBtn = Button(run_frame, text="Dokkaebi 실행",command=run_dokkaebi,width=70,height=5)
runDokkaebiBtn.pack()
root.mainloop()