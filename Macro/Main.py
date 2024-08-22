#########################모듈호출
import sys, time, datetime
import pyautogui
import win32api
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QMessageBox, QComboBox, QLabel
from PyQt5.QtCore import QObject, QThread

#########################전역함수
def up_num(t):
    while True:
        if t[-1] == ".":
            t = t[:-1]
            return t
        t = t[:-1]
def list_to_line(arr):
    text = ""
    for i in arr:
        text = text+"-"+i
    return text[1:]
def Get_Data_Name():
    file = open("DATA_Name.txt","r")
    save_list = []
    for i in file:
        save_list.append(i.strip())
    file.close()
    return save_list
def Get_Data_List():
    file = open("DATA_List.txt","r")
    save_list = []
    for i in file:
        save_list.append(i.strip())
    file.close()
    return save_list

#########################스레드
class record_class(QThread):
    def run(self):
        auto_l = []
        bx,by = 0,0
        x,y = 0,0
        l = 0
        while True:
            l += 1
            if win32api.GetKeyState(0x23) < 0:
                break
            elif win32api.GetKeyState(0x01) < 0:
                if auto_l[-1] != "click_left":
                    auto_l.append("click_left")
            elif win32api.GetKeyState(0x02) < 0:
                if auto_l[-1] != "click_right":
                    auto_l.append("click_right")
            else:
                scan = pyautogui.position()
                x = scan.x
                y = scan.y
                if x != bx or y != by:
                    auto_l.append(f"{x} / {y}")
                    bx = x
                    by = y
        #zip
        auto = []
        idx = 0
        for i in range(len(auto_l)):
            idx += 1
            if i%5 == 0:
                auto.append(auto_l[i])
            elif auto_l[i] == "click_right" or auto_l[i] == "click_left":
                auto.append(auto_l[i-3])
                auto.append(auto_l[i-2])
                auto.append(auto_l[i-1])
                auto.append(auto_l[i])
        #읽기
        file = open("DATA_Name.txt","r")
        arr = []
        for line in file:
            arr.append(line.strip())
        file.close()
        file = open("DATA_List.txt","r")
        rarr = []
        for line in file:
            rarr.append(line.strip())
        file.close()
        #저장
        if arr == ['None']:#데이터가 없는 경우
            #write name
            file = open("DATA_Name.txt","w")
            file.write(up_num(str(datetime.datetime.now())))
            file.close()
            #write list
            file = open("DATA_List.txt","w")
            file.write(str(list_to_line(auto)))
            file.close()
            
            # return
        else:#데이터가 있는 경우
            file = open("DATA_Name.txt","w")
            file.write(up_num(str(datetime.datetime.now()))+"\n")
            for idx,t in enumerate(arr):
                if idx == len(arr)-1:
                    file.write(t)
                    break
                file.write(t)
                file.write("\n")
            file.close()
            file = open("DATA_List.txt","w")
            file.write(str(list_to_line(auto))+"\n")
            for idx,t in enumerate(rarr):
                if idx == len(rarr)-1:
                    file.write(t)
                    break
                file.write(t)
                file.write("\n")
            file.close()

class move_class(QThread):
    def __init__(self,idx):
        super().__init__()
        self.idx = idx
    def run(self):
        arr = Get_Data_List()
        auto = arr[self.idx].strip().split("-")
        while True:
            if win32api.GetKeyState(0x23) < 0:
                break
            for m in auto:
                if win32api.GetKeyState(0x23) < 0:
                    break
                elif m == "click_left":
                    pyautogui.leftClick()
                elif m == "click_right":
                    pyautogui.rightClick()
                else:
                    x,y = map(int,m.split(" / "))
                    pyautogui.moveTo(x,y)

#########################디자인 클래스
class Site(QMainWindow):
    global QComboBox_Macro
    ################# 초기화
    def __init__(self):
        super().__init__()
        #set num
        mover_data = 0
    ################# UI구성
    def initUI(self):
        #Set button
        self.record = QPushButton("마우스 움직임 녹음하기",self)
        self.record.resize(200,50)
        self.record.move(5,5)
        
        self.repeat = QPushButton("마우스 움직임 반복하기",self)
        self.repeat.resize(200,50)
        self.repeat.move(5,60)
        
        self.reset = QPushButton("마우스 움직임 기록 지우기",self)
        self.reset.resize(200,50)
        self.reset.move(5,115)
        
        self.time = QLabel("현재 메크로 준비 중...",self)
        self.time.resize(190,30)
        self.time.move(8,193)
        
        #set Button Conect
        self.record.clicked.connect(self.recordf)
        self.repeat.clicked.connect(self.repeatf)
        self.reset.clicked.connect(self.resetf)
        
        #Choose Labe
        self.data = QComboBox(self)
        self.data.resize(190,25)
        self.data.move(8,170)
        self.Load()
        
        #Show Screen
        self.setWindowTitle('Auto Move')
        self.resize(210,220)
        self.show()
    
    ################# 녹음 호출
    def recordf(self):
        self.record.setEnabled(False)
        self.repeat.setEnabled(False)
        self.reset.setEnabled(False)
        self.threader = record_class()
        self.threader.finished.connect(self.finish_record)
        #time
        self.time.setText("마우스 녹음까지 3초")
        self.time.repaint()
        time.sleep(1)
        self.time.setText("마우스 녹음까지 2초")
        self.time.repaint()
        time.sleep(1)
        self.time.setText("마우스 녹음까지 1초")
        self.time.repaint()
        time.sleep(1)
        self.time.setText("마우스 녹음중...")
        self.threader.start()
    
    ################# 실행호출
    def repeatf(self):
        self.record.setEnabled(False)
        self.repeat.setEnabled(False)
        self.reset.setEnabled(False)
        self.threader = move_class(self.data.currentIndex())
        self.threader.finished.connect(self.finish_repeat)
        #time
        self.time.setText("마우스 재생까지 3초")
        self.time.repaint()
        time.sleep(1)
        self.time.setText("마우스 재생까지 2초")
        self.time.repaint()
        time.sleep(1)
        self.time.setText("마우스 재생까지 1초")
        self.time.repaint()
        time.sleep(1)
        self.time.setText("마우스 재생중 (end 키로 종료)...")
        self.threader.start()
    
    ################# 저장소 초기화
    def resetf(self):
        file = open("DATA_Name.txt",'w')
        file.write("None")
        file.close()
        file = open("DATA_List.txt",'w')
        file.write("None")
        file.close()
        self.data.clear()
        self.data.addItem("None")
    ################# 리스트 업데이트
    def Load(self):
        self.data.clear()
        l = Get_Data_Name()
        for i in l:
            self.data.addItem(i)
    

    ################# 스레드 종료알림
    def finish_record(self):
        self.time.setText("-녹음 종료-")
        self.time.repaint()
        time.sleep(1)
        self.time.setText("현재 메크로 준비 중...")
        self.time.repaint()
        self.record.setEnabled(True)
        self.repeat.setEnabled(True)
        self.reset.setEnabled(True)
        self.Load()
    def finish_repeat(self):
        self.time.setText("-반복 종료-")
        self.time.repaint()
        time.sleep(1)
        self.time.setText("현재 메크로 준비 중...")
        self.time.repaint()
        self.record.setEnabled(True)
        self.repeat.setEnabled(True)
        self.reset.setEnabled(True)
    
        
        

#need code(don't touch)
app = QApplication(sys.argv)
site = Site()
site.initUI()
sys.exit(app.exec_())