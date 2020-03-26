from tkinter import *
from threading import Thread
import serial
import time
import pymysql
from pymysql.cursors import DictCursor

def findports():
    ports = []
    portsvariants = ['COM%s' % (i + 1) for i in range(256)]
    for port in portsvariants:
        try:
            s = serial.Serial(port)
            s.close()
            ports.append(port)
        except (OSError, serial.SerialException):
            pass
    return ports

class Table(Frame):
    def __init__(self, parent, rows=10, columns=2):
        Frame.__init__(self, parent, background="black")
        self._widgets = []
        for row in range(rows):
            current_row = []
            for column in range(columns):
                label = Label(self, text="%s/%s" % (row, column),
                                 borderwidth=0, width=30)
                label.grid(row=row, column=column, sticky="nsew", padx=1, pady=1)
                current_row.append(label)
            self._widgets.append(current_row)

        for column in range(columns):
            self.grid_columnconfigure(column, weight=1)

    def set(self, row, column, value):
        widget = self._widgets[row][column]
        widget.configure(text=value)

class AutoElectricMeter():
    root = Tk()
    usingDB=True
    try:
        connection = pymysql.connect(
            host='localhost',
            user='bazauser',
            password='123456789q',
            db='elmeterdb',
            charset='utf8',
            cursorclass=DictCursor
        )
    except pymysql.Error:
        usingDB=False

    selectedPort = 0
    toWrite = False
    data = [0, 0, 0, 0]
    graphdata = []

    def makegraph(self):
        width = 500
        height = 200
        canv = Canvas(self.root, width=width, height=height, bg="#002")
        for x in range(61):
            k = width / 60 * x
            canv.create_line(10 + k, height - 10, 10 + k, 10, width=0.3, fill='#191938')
            canv.create_line(10, 10 + k, width, 10 + k, width=0.3, fill='#191938')
        canv.create_line(10, height - 10, 10, 0, width=1, arrow=LAST, fill='white')
        canv.create_line(10, height - 10, width, height - 10, width=1, arrow=LAST, fill='white')
        canv.place(x=45, y=200)
        canv.after_idle(self.graphupdate, canv, 1, 10, height - 10)

    def graphupdate(self,canv, writed, lastx, lasty):
        if (len(self.graphdata) != writed - 1):
            for dataset in self.graphdata[writed - 1:]:
                canv.create_line(lastx, lasty, lastx + 0.13, 200 - dataset[0] / 2, width=1, fill='red')
                lastx = lastx + 0.13
                lasty = 200 - dataset[0] / 2
                writed = writed + 1
        canv.after(500, self.graphupdate, canv, writed, lastx, lasty)

    def readport(self):
        while True:
            if (self.selectedPort == 0):
                time.sleep(1)

            else:
                line = self.selectedPort.readline().decode("utf-8")
                if line != '':
                    datapack = line.rstrip().split(' ')
                    millis = int(datapack[0])
                    watts = float(datapack[1])
                    hours = millis // 3600000
                    minuts = millis // 60000 - hours * 60
                    seconds = round(millis / 1000) - minuts * 60 - hours * 3600
                    self.data[0] = "{0} Часов, {1} Минут, {2} Секунд".format(hours, minuts, seconds)
                    self.data[1] = watts
                    self.data[2] = round(watts / (millis / 1000), 2)
                    self.data[3] = millis

                    if(self.usingDB):
                        if hours // 24 == hours / 24 and minuts == 0 and seconds == 0:
                            with self.connection.cursor() as cursor:
                                cursor.execute(
                                    'INSERT INTO `records` '
                                    '(`daterecord`, `consumption`) '
                                    'VALUES (now(), \'{0}\')'
                                        .format(watts / 1000))
                                self.connection.commit()
                                cursor.close()

    def onselect(self,evt):
        wiget = evt.widget
        index = int(wiget.curselection()[0])
        self.selectedPort = serial.Serial(wiget.get(index), 9600, timeout=3)
        self.toWrite = True
        time.sleep(2.5)

    def startthread(self):
        Thread(target=self.readport).start()
        self.root.update()

    def datalabeltick(self,datalabel):
        if self.toWrite and self.data == [0, 0, 0, 0]:
            datalabel['text'] = "Возможно выбран \n " \
                                "неверный порт"
        else:
            if self.toWrite and self.data != [0, 0, 0, 0]:
                datalabel['text'] = 'Время работы счетчика: {0}\n' \
                                    'Потрачено энергии: {1} ватт\n' \
                                    'Расход ватт в секунду: {2}'\
                    .format(self.data[0],self.data[1], self.data[2])
                self.graphdata.append([self.data[2], self.data[3]])
        datalabel.after(1000, self.datalabeltick, datalabel)

    def maketable(self):
        with self.connection.cursor() as cursor:
            query = """
            SELECT
                daterecord,consumption
            FROM
                records
            ORDER BY 
                id DESC
            LIMIT 5
            """
            cursor.execute(query)

            recordDates = []
            consumptions = []

            for row in cursor:
                recordDates.append(row['daterecord'])
                consumptions.append(row['consumption'])

            table = Table(self.root, len(recordDates)+1, 2)
            table.place(x=80, y=450)
            table.set(0, 0, "Дата и время замера")
            table.set(0, 1, "Расход энергии за день")

            cursor.close()

            row = 1
            for record in recordDates:
                table.set(row,0,record)
                row=row+1

            row = 1
            for consumption in consumptions:
                table.set(row,1,str(consumption)+" Киловатт")
                row=row+1




    def start(self):
        self.root.title('Просмотр данных счётчика')
        self.root.geometry('600x600+300+200' if self.usingDB else '600x450+300+200')

        Label(self.root, text="Выберите порт счётчика: ").place(x=5, y=10)
        Label(self.root, text="Расход\n(Ватт)\n\n 400\n\n\n\n\n 200\n\n\n\n\n\n  0").place(x=8, y=168)
        Label(self.root, text="0                       " +
                         "10                       20" +
                         "                       30" +
                         "                       40" +
                         "                       50" +
                         "                     60").place(x=50, y=405)
        Label(self.root, text="Время\n(Минут) ").place(x=545, y=385)
        Label(self.root, text="График расхода электроэнергии за последний час", font='Arial 14').place(x=76, y=165)

        datalabel = Label(self.root, text="", font='Arial 16')
        datalabel.place(x=40, y=70)
        datalabel.after_idle(self.datalabeltick, datalabel)

        ports = findports()
        portbox = Listbox(self.root, height=len(ports), width=15, selectmode=EXTENDED)
        for port in ports:
            portbox.insert(END, port)
        portbox.place(x=160, y=10)
        portbox.bind('<<ListboxSelect>>', self.onselect)

        if(self.usingDB):
            self.maketable()
        self.makegraph()
        self.root.after(100, func=self.startthread)

        self.root.mainloop()


