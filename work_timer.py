import enum
import time
from datetime import date
from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QObject, QThread, pyqtSignal
import sys
import Util
from LogWindow import LogWindow
from Util import UI_DIR, resource_path

class TimerWorker(QObject):
    finished = pyqtSignal(str)
    progress = pyqtSignal(int)
    started = pyqtSignal(str)
    isTimerRunning = False

    def __init__(self):
        super().__init__()
        self.elapsedTime = 0

    def setElapsedTime(self, initTime):
        self.elapsedTime = initTime

    def run(self):
        self.isTimerRunning = True
        startTime = time.time()
        self.started.emit(str(startTime))
        while self.isTimerRunning:
            self.elapsedTime = self.elapsedTime + 1
            self.progress.emit(self.elapsedTime)
            time.sleep(1)

    def getElapsedTime(self):
        return self.elapsedTime

    def endTimer(self):
        print('end')
        self.isTimerRunning = False
        self.finished.emit(str(time.time()))

class Status(enum.Enum):
    STOPPED = 1
    WORKING = 2
    BREAKING = 3

class WorkTimer(QMainWindow):
    def __init__(self):
        super(WorkTimer, self).__init__()

        self.isTimerRunning = False
        uic.loadUi(UI_DIR + 'work_timer.ui', self)  # Load the .ui file
        self.show()  # Show the GUI

        self.initWidgets()
        self.connectButtons()

        self.totalWorkTime = 0
        self.totalBreakTime = 0

        self.status = Status.STOPPED

        # define colors
        self.workColor = '#3FAB21'
        self.breakColor = '#D72638'
        self.logColor = '#FB8B24'

    def startWorkTimerThread(self):
        self.timerThread = QThread()
        self.timerWorker = TimerWorker()
        self.timerWorker.moveToThread(self.timerThread)
        self.timerThread.started.connect(self.timerWorker.run)
        self.timerThread.finished.connect(self.timerThread.deleteLater)

        self.timerWorker.progress.connect(self.showProgress)

        self.timerWorker.finished.connect(self.timerThread.quit)
        self.timerWorker.finished.connect(self.timerWorker.deleteLater)
        self.timerWorker.finished.connect(self.resetTimer)

        self.timerThread.start()

    def initWidgets(self):
        self.lblTimer = self.findChild(QLabel, 'lblTimer')
        self.lblTimer.setText('00:00:00')
        self.btnStartStop = self.findChild(QPushButton, 'btnStart')
        self.btnBreak = self.findChild(QPushButton, 'btnBreak')
        self.btnBreak.setVisible(False)
        self.btnLog = self.findChild(QPushButton, 'btnLog')
        self.lblToday = self.findChild(QLabel, 'lblToday')
        self.today = date.today().strftime("%d/%m/%Y")
        self.lblToday.setText(self.today)
        self.lblStartedWorkAt = self.findChild(QLabel, 'lblStartedWorkAt')
        self.lblStartedWorkAt.setVisible(False)
        self.lblWorkedFor = self.findChild(QLabel, 'lblWorkedFor')
        self.lblBreakFor = self.findChild(QLabel, 'lblBreakFor')
        self.rootLayout: QWidget = self.findChild(QWidget, 'rootLayout')
        self.etNotes = self.findChild(QTextEdit, 'etNotes')

    def connectButtons(self):
        self.btnStartStop.clicked.connect(self.toggleStartStop)
        self.btnBreak.clicked.connect(self.toggleBreak)
        self.btnLog.clicked.connect(self.showLog)

    def toggleStartStop(self):
        self.isTimerRunning = self.isTimerRunning != True
        if self.isTimerRunning:
            self.rootLayout.setStyleSheet(f'background-color:{self.workColor};')
            self.btnBreak.setVisible(True)
            self.startedWorkAt = time.strftime("%H:%M")
            self.status = Status.WORKING
            self.btnStartStop.setText("DONE FOR THE DAY")
            self.startWorkTimerThread()
            # Show and set started working at label
            self.lblStartedWorkAt.setVisible(True)
            self.lblStartedWorkAt.setText(f'Started work at: {self.startedWorkAt}')
        else:
            self.btnBreak.setVisible(False)
            self.lblStartedWorkAt.setVisible(False)
            self.endedWorkAt = time.strftime("%H:%M")
            self.status = Status.STOPPED
            self.btnStartStop.setText("START")
            self.timerWorker.endTimer()
            self.lblTimer.setText('00:00:00')
            self.lblBreakFor.setText('00:00:00')
            self.lblWorkedFor.setText('00:00:00')

    def toggleBreak(self):
        if self.status == Status.BREAKING:
            self.rootLayout.setStyleSheet(f'background-color:{self.workColor};')
            self.btnBreak.setText('TAKE A BREAK')
            self.btnStartStop.setVisible(True)
            self.status = Status.WORKING
            self.totalBreakTime = self.timerWorker.getElapsedTime()
            self.timerWorker.setElapsedTime(self.totalWorkTime)
        else:
            self.rootLayout.setStyleSheet(f'background-color:{self.breakColor};')
            self.btnBreak.setText('GET BACK TO WORK')
            self.btnStartStop.setVisible(False)
            self.status = Status.BREAKING
            self.totalWorkTime = self.timerWorker.getElapsedTime()
            self.timerWorker.setElapsedTime(self.totalBreakTime)

    def showProgress(self, elapsedTime):
        self.lblTimer.setText(Util.formatTime(elapsedTime))
        if self.status == Status.BREAKING:
            self.totalBreakTime = self.timerWorker.getElapsedTime()
        else:
            self.totalWorkTime = self.timerWorker.getElapsedTime()

        if self.totalWorkTime > 0:
            self.lblWorkedFor.setText(f'Worked for: {Util.formatTimeHM(self.totalWorkTime)}')
        if self.totalBreakTime > 0:
            self.lblBreakFor.setText(f'Took break for: {Util.formatTimeHM(self.totalBreakTime)}')

    def showLog(self):
        dialog = LogWindow()
        dialog.exec_()

    def resetTimer(self, endTime):
        self.lblTimer.setText('00:00:00')
        self.saveLog(endTime)
        self.etNotes.clear()

    def saveLog(self, endTime):
        print(f"save log...{endTime}")
        f = open(resource_path("work_timer_log.csv"), "a")
        notes = self.etNotes.toPlainText().replace("\n","|")
        f.write(f'{self.today},{self.startedWorkAt},{Util.formatTimeHM(self.totalBreakTime)},{self.endedWorkAt},{Util.formatTimeHM(self.totalWorkTime)},{notes}\n')
        f.close()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ex = WorkTimer()
    ex.setWindowTitle('Work Timer')
    ex.show()
    app.exec_()
