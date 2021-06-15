import sys
import os
import numpy as np
from PyQt5 import QtGui,QtCore, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QApplication,QMainWindow,QHeaderView,QTextBrowser,QMessageBox
import pymysql
from main_ui import Ui_MainWindow as Main_ui
from search_ui import Ui_Dialog as Search_ui
from DisFac_ui import Ui_Dialog as DisFac_ui
from DisSym_ui import Ui_Dialog as DisSym_ui

class MainWindow(QtWidgets.QMainWindow, Main_ui):
    switch_window1=QtCore.pyqtSignal()#职业病查询
    switch_window2=QtCore.pyqtSignal()#职业病-有害因素
    switch_window3=QtCore.pyqtSignal()#职业病-症状
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.goSearch)
        self.pushButton_2.clicked.connect(self.goDisFac)
        self.pushButton_3.clicked.connect(self.goDisSym)
    def goSearch(self):
        self.switch_window1.emit()
    def goDisFac(self):
        self.switch_window2.emit()
    def goDisSym(self):
        self.switch_window3.emit()

class SearchWindow(QtWidgets.QMainWindow, Search_ui):
    switch_window1=QtCore.pyqtSignal()#返回主菜单
    diseaseresult=[]#存放同种疾病所有轻中重度的判断结果
    diseaselist=[]#轻度中度还是重度的病
    currenti=0
    currentj=2
    finalresult=""
    process=""
    def __init__(self):
        super(SearchWindow, self).__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.Clicked)#查询可能职业病按钮
        self.pushButton_2.clicked.connect(self.ClickedClear)#清空按钮
        self.pushButton_3.clicked.connect(self.ClickedJudge)#判断按钮
        self.pushButton_4.clicked.connect(self.ClickedYes)#是按钮
        self.pushButton_5.clicked.connect(self.ClickedNo)#否按钮
        self.pushButton_6.clicked.connect(self.goMain)#回到主菜单
    def Clicked(self):
        conn=pymysql.connect(host='localhost',port=3306,user='root',password="123456",db="disease")
        cur = conn.cursor()
        job=self.plainTextEdit.toPlainText()
        #print(job)
        # 查询的sql语句
        sql = "SELECT tag FROM occupational_hazards WHERE examples LIKE '%"+ job +"%' OR occupations LIKE '%"+job+"%';"
        #print(sql)
        cur.execute(sql)
        # 获取查询到的数据，是以字典的形式存储的，所以读取需要使用data[i][j]下标定位
        data = cur.fetchall()
        data=list(set(data))
        #print(len(data))
        if len(data)==0:
            QMessageBox.about(self, '提示','暂时查不到对应行业工种，建议换一种表述方式,点击“清空”重新输入！'+SearchWindow.finalresult)
        mayresults=""
        for i in range(len(data)):
            mayresults+=(str(i+1)+str(data[i])+'\n')
        #print(mayresults)
        self.textEdit.setText(mayresults)
        return data
    def ClickedClear(self):
        self.plainTextEdit.clear()
        SearchWindow.diseaseresult=[]#存放同种疾病所有轻中重度的判断结果
        SearchWindow.diseaselist=[]#轻度中度还是重度的病
        SearchWindow.currenti=0
        SearchWindow.currentj=2
        SearchWindow.finalresult=""
        SearchWindow.process=""
    def ClickedJudge(self):
        num=int(self.lineEdit.text())
        searchdisease=str(SearchWindow.Clicked(self)[num-1])[2:-3]#去掉括号和逗号,提取出当前用户要查的疾病
        f = open("规则.txt",encoding='utf-8')
        
        for line in f.readlines():#遍历规则文本
            symptom=line.split(' ')#以空格分隔，得出列表
            if symptom[0] == searchdisease:
                SearchWindow.diseaselist.append(symptom)
        #print(diseaselist)   现在diseaselist里面存放了所有诊断为这个病的所有可能结果
        f.close()
        self.textEdit_2.setText(SearchWindow.diseaselist[0][2])
        
    def ClickedYes(self):
        if SearchWindow.currenti==len(SearchWindow.diseaselist):
            if len(SearchWindow.finalresult)==0:
                QMessageBox.about(self, '诊断结束','您没有患这种职业病')
            else:
                QMessageBox.about(self, '诊断结束','当前您的诊断结果：'+SearchWindow.finalresult+'\n'+"推理过程：\n"+SearchWindow.process+'\n')
            return
        SearchWindow.process+=(SearchWindow.diseaselist[SearchWindow.currenti][SearchWindow.currentj]+"  ")
        SearchWindow.currentj+=1
        if SearchWindow.currentj==len(SearchWindow.diseaselist[SearchWindow.currenti]):#该种疾病的症状因子已经判断完成
            SearchWindow.diseaseresult.append(1)
            SearchWindow.currenti+=1
            SearchWindow.currentj=2
            SearchWindow.finalresult=SearchWindow.diseaselist[SearchWindow.currenti-1][1]
            SearchWindow.process+=("-->("+SearchWindow.finalresult+")-->\n")
            print(len(SearchWindow.finalresult))
            self.textEdit_3.setText(SearchWindow.finalresult)
            if SearchWindow.currenti==len(SearchWindow.diseaselist):#所有的轻中重度都判断完成
                return
        self.textEdit_2.setText(SearchWindow.diseaselist[SearchWindow.currenti][SearchWindow.currentj])

    def ClickedNo(self):
        if SearchWindow.currenti==len(SearchWindow.diseaselist):
            if len(SearchWindow.finalresult)==0:
                QMessageBox.about(self, '诊断结束','您没有患这种职业病')
            else:
                QMessageBox.about(self, '诊断结束','当前您的诊断结果：'+SearchWindow.finalresult+'\n'+"推理过程："+SearchWindow.process+'\n')
            return
        SearchWindow.currentj+=1
        #flag=0#AND条件不能继续与下去
        SearchWindow.diseaseresult.append(0)
        SearchWindow.currenti+=1
        SearchWindow.currentj=2
        if SearchWindow.currenti==len(SearchWindow.diseaselist):#所有的轻中重度都判断完成
            return
        self.textEdit_2.setText(SearchWindow.diseaselist[SearchWindow.currenti][SearchWindow.currentj])
        

    def goMain(self):#返回主菜单
        self.switch_window1.emit()

class DisFacWindow(QtWidgets.QMainWindow, DisFac_ui):
    switch_window1=QtCore.pyqtSignal()#返回主菜单
    def __init__(self):
        super(DisFacWindow, self).__init__()
        self.setupUi(self)
        self.goback.clicked.connect(self.goMain)#回到主菜单
        self.addrule.clicked.connect(self.ClickedAdd)#查询可能职业病按钮
        self.removerule.clicked.connect(self.ClickedRemove)#清空按钮
        self.clearrule.clicked.connect(self.ClickedClear)#判断按钮
    def ClickedAdd(self):
        conn=pymysql.connect(host='localhost',port=3306,user='root',password="123456",db="disease",autocommit=True)
        cur = conn.cursor()
        Big_hazards=self.big_hazards.toPlainText()
        Small_hazards=self.small_hazards.toPlainText()
        Diseases=self.diseases.toPlainText()
        Occupations=self.occupations.toPlainText()
        Examples=self.examples.toPlainText()
        Tag=self.tag.toPlainText()
        sql = "INSERT INTO occupational_hazards (big_hazards,small_hazards,diseases,occupations,examples,tag) VALUES('"+Big_hazards+"','"+Small_hazards+"','"+Diseases+"','"+Occupations+"','"+Examples+"','"+Tag+"');"
        print(sql)
        cur.execute(sql)
        QMessageBox.about(self, '提示','规则增加完成！')
    def ClickedRemove(self):
        conn=pymysql.connect(host='localhost',port=3306,user='root',password="123456",db="disease",autocommit=True)
        cur = conn.cursor()
        Big_hazards=self.big_hazards.toPlainText()
        Small_hazards=self.small_hazards.toPlainText()
        Diseases=self.diseases.toPlainText()
        Occupations=self.occupations.toPlainText()
        Examples=self.examples.toPlainText()
        Tag=self.tag.toPlainText()
        sql = "DELETE FROM occupational_hazards WHERE diseases='"+Diseases+"' AND examples LIKE '%"+ Examples +"%';"
        cur.execute(sql)
        QMessageBox.about(self, '提示','规则去除完成！')
    def ClickedClear(self):
        self.big_hazards.clear()
        self.small_hazards.clear()
        self.diseases.clear()
        self.occupations.clear()
        self.examples.clear()
        self.tag.clear()
    def goMain(self):#返回主菜单
        self.switch_window1.emit()
    
class DisSymWindow(QtWidgets.QMainWindow, DisSym_ui):
    switch_window1=QtCore.pyqtSignal()#返回主菜单
    def __init__(self):
        super(DisSymWindow, self).__init__()
        self.setupUi(self)
        self.goback.clicked.connect(self.goMain)#回到主菜单
        self.addrules.clicked.connect(self.ClickedAdd)#查询可能职业病按钮
        self.removerules.clicked.connect(self.ClickedRemove)#清空按钮
        self.clearrules.clicked.connect(self.ClickedClear)#判断按钮
    def ClickedAdd(self):
        Name=self.name.toPlainText()
        Level=self.level.toPlainText()
        Symptoms=self.symptoms.toPlainText()
        f=open("规则.txt","a",encoding='utf-8')
        f.write(str(Name)+' '+str(Level)+' '+str(Symptoms)+'\n')
        QMessageBox.about(self, '提示','规则增加完成！')
    def ClickedRemove(self):
        Name=self.name.toPlainText()
        Level=self.level.toPlainText()
        Symptoms=self.symptoms.toPlainText()
        lines = (i for i in open('规则.txt', 'r',encoding='utf-8') if str(Name)+' '+str(Level) not in i )
        f = open('规则_new.txt', 'w', encoding="utf-8")
        f.writelines(lines)
        f.close()
        os.rename('规则.txt', '规则.bak')
        os.rename('规则_new.txt', '规则.txt')
        os.remove('规则.bak')
        QMessageBox.about(self, '提示','规则删除完成！')
    def ClickedClear(self):
        self.name.clear()
        self.level.clear()
        self.symptoms.clear()
    def goMain(self):#返回主菜单
        self.switch_window1.emit()
# 利用一个控制器来控制页面的跳转
class Controller:
    def __init__(self):
        pass
    # 跳转到 main 窗口
    def show_main(self):
        self.main = MainWindow()
        self.main.switch_window1.connect(self.show_search)
        self.main.switch_window2.connect(self.show_DisFac)
        self.main.switch_window3.connect(self.show_DisSym)
        self.main.show()
    # 跳转到search窗口, 注意关闭原页面
    def show_search(self):
        self.search = SearchWindow()
        self.search.switch_window1.connect(self.show_main)
        self.main.close()
        self.search.show()
        
     #跳转到 DisFac 窗口, 注意关闭原页面
    def show_DisFac(self):
        self.DisFac = DisFacWindow()
        self.DisFac.switch_window1.connect(self.show_main)
        self.main.close()
        self.DisFac.show()

    def show_DisSym(self):
        self.DisSym = DisSymWindow()
        self.DisSym.switch_window1.connect(self.show_main)
        self.main.close()
        self.DisSym.show()

def main():
    app = QtWidgets.QApplication(sys.argv)
    controller = Controller() # 控制器实例
    controller.show_main() # 默认展示的是 main 页面
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
