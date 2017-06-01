from transitions.extensions import GraphMachine
import time
import requests
from bs4 import BeautifulSoup
import re
import telegram

class TocMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.machine = GraphMachine(
            model = self,
            **machine_configs
        )
          
        
        
    def find_route_pic(self, update):
        text = update.message.text
   #     print(update.message.message_id)
        
    #    print(re.match(r'路線圖', text))
        return re.match(r'.*路線圖.*', text)!= None

    def find_time_table(self, update):
        text = update.message.text
        return re.match(r'.*時刻表.*', text)!= None

    def find_stop_name(self, update):
        text = update.message.text
        return re.match(r'.*站牌.*', text)!= None
    


    def on_enter_route_pic(self, update):
        update.message.reply_text("請輸入欲查詢的路線")

  #  def on_exit_route_pic(self, update):
  #      update.message.reply_text("查詢路線："+update.message.text)


    def on_enter_time_table(self, update):
        update.message.reply_text("請輸入欲查詢的路線")

  #  def on_exit_time_table(self, update):
  #      update.message.reply_text("查詢路線："+update.message.text)

    def on_enter_stop_name(self, update):
        update.message.reply_text("請輸入欲查詢的路線")

  #  def on_exit_stop_name(self, update):
  #      update.message.reply_text("查詢路線："+update.message.text)

    def which_route_pic_do_you_need(self, update):
        t = update.message.text
        res = requests.get('http://busmap.tainan.gov.tw/ebus/routeList_New.jsp')
        soup = BeautifulSoup(res.text, "lxml")
 
        line = repr(soup.find_all(class_ =["district1TD","tourTD","shuttleTD","cityTD"],text = t))
        print(len(line))
        if len(line)>5 :
            self.line = line
            return 1
        else:
            update.message.reply_text("查無此路線！請重新輸入：")
            return 0
        

    def on_enter_which_route_pic(self, update):
        match = re.findall(r'\d\d\d\d\d?',self.line)
        print(self.line)
        if match :
            print("match")
            num = match[1]
            print(num)            
        else :
            print("not match")
            
            return 0
        pic = "http://www.2384.com.tw/ebus/resources/PathPic/zh_TW/"+str(num)+".jpg"
        print(pic) 
        update.message.reply_photo(pic)
        self.go_back(update)

    def on_exit_which_route_pic(self, update):
        print('Leaving state1')

    def which_time_table_do_you_need(self, update):
        t = update.message.text 
        print("Transition : which_time_table_do_you_need")
        res = requests.get('http://busmap.tainan.gov.tw/ebus/routeList_New.jsp')
        soup = BeautifulSoup(res.text, "lxml")
 
        line = repr(soup.find_all(class_ =["district1TD","tourTD","shuttleTD","cityTD"],text = t))
        
        print(len(line))
        if len(line)>5:
            self.line = line
            return 1
        else:
            update.message.reply_text("查無此路線！請重新輸入：")
            return 0

        
        
    def on_enter_which_time_table(self, update):
        print("ENTER which_time_table")
        match = re.findall(r'\d\d\d\d\d?', self.line)
        
        if match :
            print("match")
            num = match[1]
            if num == "1803" :
                update.message.reply_text("本路線營運時間及班距：每逢國定例假日之 10 時至 19 時，每 20 分鐘 1 班！")
                self.go_back(update)
                return 1
            table_web = "http://busmap.tainan.gov.tw/ebus/pathInfo.jsp?pathId=" + str(num);            
        else :
            print("not match")
            
            return 0
        self.table_website = str(table_web)
        print(self.table_website) 
        update.message.reply_text("請輸入去程或返程")
        return 1

    def which_stop_name_do_you_need(self, update):
        t = update.message.text
        res = requests.get('http://busmap.tainan.gov.tw/ebus/routeList_New.jsp')
        soup = BeautifulSoup(res.text, "lxml")
 
        line = repr(soup.find_all(class_ =["district1TD","tourTD","shuttleTD","cityTD"],text = t))
        print(len(line))
        if len(line)>5 :
            self.line = line
            return 1
        else:
            update.message.reply_text("查無此路線！請重新輸入：")
            return 0
        

    def on_enter_which_bus_line(self, update):
        print("ENTER which_time_table")
        match = re.findall(r'\d\d\d\d\d?', self.line)
        
        if match :
            print("match")
            num = match[1]
            print(num)
            table_web = "http://busmap.tainan.gov.tw/ebus/pathInfo.jsp?pathId=" + str(num);            
        else :
            print("not match")
            
            return 0
 #       self.table_website = str(table_web)
 #       print(self.table_website) 
        res = requests.get(table_web)
        soup = BeautifulSoup(res.text, "lxml")
        bus_stop = ""
        line = repr(soup.find_all(style='text-align : left;'))
        for test in re.findall(r'<td style="text-align : left;">[^td0-9─]+</td>', line) :
            bus_stop = bus_stop + test[31:-5] + "\n"
        update.message.reply_text(bus_stop)
        self.go_back(update)
    
    def go_forward(self,update):
        print("Transition : go_forward")
        text = update.message.text        
        return text == '去程'

    def on_enter_forward(self,update):
        text = update.message.text
        print(text)
        res = requests.get(self.table_website)
        soup = BeautifulSoup(res.text, "lxml")
        print(self.table_website)
        title = "" 
        stopnum = -1
        count = 0
        time_table = ""
        line = repr(soup.find_all(id ="timeTable0"))
    

        hour = int(time.strftime("%H"))
        print(hour)

        for title_test in re.findall(r'<td>[^td0-9─]+</td>', line) :            
            fomart = 'td<br/>'   
            for c in title_test:   
               if c in fomart:   
                   title_test = title_test.replace(c,'');
            title = title + '{0:<10.10s}'.format(title_test)
            stopnum+=1
        title = title+"\n"
    #    update.message.reply_text(title)
    #    title = ""
        buf = ""
        i=-1
        for match in re.findall(r'(\d\d:\d\d)|─', line) :
            
            if len(match)==5 :
                buf = buf + '{0:<15.15s}'.format(match)
                i = int(match[0:2])-hour
            else:
                buf = buf + '{0:<15.15s}'.format("  ──  ")
            count+=1
            if count == stopnum :
                buf = buf +"\n\n"
                if (i>0)&(i<5) :
       #             update.message.reply_text(title)
                    time_table = time_table + buf
                    print(i)
                    i = -1
                    buf = ""
                    count =0
                else:
                    i = -1
                    buf = ""
                    count =0
                    continue
        print(title)       
        if len(time_table)!=0 :
            update.message.reply_text(title[0:-12]+"\n"+time_table)
        else :
            update.message.reply_text("末班駛離")
        self.go_back(update)

    def go_backward(self,update):
        print("Transition : go_backward")
        text = update.message.text        
        return text== '返程'

    def on_enter_backward(self,update):
        text = update.message.text
        res = requests.get(self.table_website)
        soup = BeautifulSoup(res.text, "lxml")
        print(self.table_website)
        title = "" 
        stopnum = -1
        count = 0
        hour = int(time.strftime("%H"))
        line = repr(soup.find_all(id ="timeTable1"))
        for title_test in re.findall(r'<td>[^td0-9─]+</td>', line) :            
            fomart = 'td<br/>'   
            for c in title_test:   
               if c in fomart:   
                   title_test = title_test.replace(c,'');
            title = title + '{0:<10.10s}'.format(title_test)
            stopnum+=1
        title = title+"\n"
    #    update.message.reply_text(title)
    #    title = ""
        time_table = ""
        buf = ""
        i=-1
        for match in re.findall(r'(\d\d:\d\d)|─', line) :
            
            if len(match)==5 :
                buf = buf + '{0:<15.15s}'.format(match)
                i = int(match[0:2])-hour
            else:
                buf = buf + '{0:<15.15s}'.format("  ──  ")
            count+=1
            if count == stopnum :
                buf = buf +"\n"
                if (i>0)&(i<5) :
   #                 update.message.reply_text(title)
                    time_table = time_table + buf
                    print(i)
                    i = -1
                    buf = ""
                    count =0
                else:
                    i = -1
                    buf = ""
                    count =0
                    continue
        print(title)       
        if len(time_table)!=0 :
            update.message.reply_text(title[0:-12]+"\n"+time_table)
        else :
            update.message.reply_text("末班駛離")
        self.go_back(update)
