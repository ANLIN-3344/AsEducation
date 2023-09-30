import os
import sys

__file__ = sys.argv[0]
os.chdir(os.path.split(__file__)[0])


if os.path.exists("startUp"):
    for i in os.listdir("startUp"):
        os.startfile(f"{os.path.split(__file__)[0]}/startUp/{i}")


from ANewPy.pyqtpro import pyqtpro
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap, QIcon
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QApplication, QWidget
import datetime
import string
import psutil
import ANewPy
import ANewPy.control_volume


def Nonlinear(t):
    y = - ((t ** 2) * 1.2 / (CP["EffectTotalTime"] ** 2)) + (t * (4 * CP["EffectK"] - 1) / (CP["EffectTotalTime"]))
    if y > 1:
        y = 1
    return y


def SetAlpha(widget, alpha):
    op = QGraphicsOpacityEffect(None)
    op.setOpacity(alpha)
    widget.setGraphicsEffect(op)
    widget.setAutoFillBackground(True)


def beautifulTime(timeUnit):
    timeUnit = str(timeUnit)
    if len(timeUnit) == 1:
        timeUnit = "0" + timeUnit
    return timeUnit


def CheckIfItIsRunning():
    try:
        pidNotHandle = list(psutil.process_iter())
        get_pid = os.getpid()
        TheName = os.path.split(__file__)[-1]
        for each in pidNotHandle:
            pid = each.pid
            name = each.name()
            if name == TheName and pid != get_pid:
                return True
        return False
    except:
        return False


def get_disklist():
    disk_list_ = []
    for c in string.ascii_uppercase:
        disk = c + ':'
        if os.path.isdir(disk):
            disk_list_.append(disk)
    return disk_list_


class Tray(QWidget):
    def __init__(self):
        super().__init__(None)
        self.SystemTray = QSystemTrayIcon(self)
        self.SystemTray.setToolTip("AsEducationDesktop 正在运行\n双击以退出")
        self.SystemTray.setIcon(QIcon("files\\AsEducation.png"))
        pyqtpro.connect(self.SystemTray.activated, self.act)
        self.SystemTray.show()

    def act(self, _):
        if _ == 2:
            self.SystemTray.hide()
            ANewPy.quit(1)


class DesktopWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.size = CP["WindowSize"]
        self.effect_do_timer_time = int((CP["EffectTotalTime"] / CP["EffectTotalFrame"] * 1000))
        self.used_time = self.effect_do_timer_time
        self.outFlag = False

        self.setStyleSheet("background:transparent")
        if CP["BgAlpha"] == 0:
            self.setAttribute(Qt.WA_TranslucentBackground)
            self.setWindowFlags(Qt.WindowTransparentForInput | Qt.WindowStaysOnBottomHint | Qt.FramelessWindowHint | Qt.Tool)
        else:
            ANewPy.pyqtpro.windowEffect.AcrylicEffectPreposition(self, (255, 255, 255, 200))
            self.setWindowFlags(Qt.WindowStaysOnBottomHint | Qt.FramelessWindowHint | Qt.Tool)
        self.move(CP["ScreenSize"][0], 0)
        self.resize(self.size[0], self.size[1])

        self.count_subtext = 0
        self.mode_subtext = 0
        self.flag_subtext = 1
        self.alpha_subtext = 1
        self.subtextList = []
        L_Notice = CP['L_Notice']["text"]
        if L_Notice != "":
            self.subtextList.append("[通知] " + L_Notice)
        import requests
        from bs4 import BeautifulSoup
        import datetime
        # 获取天气
        url = "https://tianqi.2345.com/today-71955.htm"
        header = {
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; Media Center '
                          'PC 6.0; InfoPath.2; MS-RTC LM 8'
        }
        response = requests.get(url=url, headers=header)
        response.encoding = "utf-8"
        bs = BeautifulSoup(response.text, 'html.parser')
        today_weather = bs.find_all('a', href="/today-71955.htm", title="今天天气")
        today_weather = ' '.join(today_weather[0].text.split())
        tomorrow_weather = bs.find_all('a', href="/tomorrow-71955.htm", title="明天天气")
        tomorrow_weather = ' '.join(tomorrow_weather[0].text.split())
        self.subtextList.append(f"[天气预报] {today_weather}  |  {tomorrow_weather}")
        # 获取每日一句
        url = "http://open.iciba.com/dsapi/"
        r = requests.get(url)
        content = r.json()['content']
        note = r.json()['note']
        self.subtextList.append(f"[每日一句] {content}")
        self.subtextList.append(f"[每日一句] {note}")
        # 倒计时
        if CP["countDown"]["text"] != "":
            date = CP["countDown"]["date"]
            countdown = (datetime.date(date[0], date[1], date[2]) - datetime.date.today()).days
            self.subtextList.append("[倒计时] " + CP["countDown"]["text"] % countdown)

        now = datetime.datetime.now()

        tmp_file = "ini/Flag.tmp"
        if now.weekday() == 0:
            if not os.path.exists(tmp_file):
                flag = ANewPy.open_("ini/Flag.ini")
                _flag = flag.r() + 1
                if _flag >= len(ANewPy.open_("ini/HygieneFormStudent.ini").r()):
                    _flag = 0
                open(tmp_file, 'w').close()
                flag.w(_flag)
        elif os.path.exists(tmp_file):
            os.remove(tmp_file)

        self.setUp()

        self.show()

        self.time_count = 0
        pyqtpro.CTimer(self, 100, self.second_do)
        self.effect_do_time_flag = False
        self.effect_do_timer = pyqtpro.CTimer(self, self.effect_do_timer_time, self.effect_do)
        self.LessonProgressbar = lessonProgress()
        self.HideTipWindow = HideTipWindow()

        self.start_effect()

    def setUp(self, mode=1):
        now = datetime.datetime.now()
        if mode == 1:
            self.size = CP["WindowSize"]
        elif mode == 2:
            self.size = CP["WindowSizeUnfold"]
        self.resize(self.size[0], self.size[1])

        self.L_Logo = QLabel(self)
        self.L_Logo.move(CP['L_Logo']['x'], CP['L_Logo']['y'])
        self.L_Logo.resize(CP['L_Logo']['size'], CP['L_Logo']['size'])
        self.L_Logo.setScaledContents(True)
        self.L_Logo.setPixmap(QPixmap(CP['L_Logo']['path']))

        self.L_Time = QLabel(self)
        self.L_Time.move(CP['L_Time']['x'], CP['L_Time']['y'])
        self.L_Time.resize(self.size[0] - CP['L_Time']['x'] - 10, self.size[1] - CP['L_Time']['y'] - 10)
        self.L_Time.setFont(QFont(CP["Font"], CP['L_Time']['size']))
        self.L_Time.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.L_Time.setText(CP['L_Time']['text']
                            % (beautifulTime(now.hour), beautifulTime(now.minute), beautifulTime(now.second)))

        self.L_Data = QLabel(self)
        self.L_Data.move(CP['L_Data']['x'], CP['L_Data']['y'])
        self.L_Data.resize(self.size[0] - CP['L_Data']['x'] - 10, self.size[1] - CP['L_Data']['y'] - 10)
        self.L_Data.setFont(QFont(CP["Font"], CP['L_Data']['size']))
        self.L_Data.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.L_Data.setText(CP['L_Data']['text'] % (now.year, now.month, now.day,
                                                    ["一", "二", "三", "四", "五", "六", "日"][now.weekday()]))

        self.L_Notice = QLabel(self)
        self.L_Notice.move(CP['L_Notice']['x'], CP['L_Notice']['y'])
        self.L_Notice.resize(self.size[0] - CP['L_Notice']['x'] - 10, self.size[1] - CP['L_Notice']['y'] - 10 + CP['L_Notice']['subLabelHAdd'])
        self.L_Notice.setFont(QFont(CP["Font"], CP['L_Notice']['size']))
        self.L_Notice.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.L_Notice.setText(CP['L_Notice']["text"])

        self.L_SchoolTimetable = QLabel(self)
        self.L_SchoolTimetable.move(CP['L_SchoolTimetable']['x'], CP['L_SchoolTimetable']['y'])
        self.L_SchoolTimetable.resize(self.size[0] - CP['L_SchoolTimetable']['x'] - 10,
                                      self.size[1] - CP['L_SchoolTimetable']['y'] - 10)
        self.L_SchoolTimetable.setFont(QFont(CP["Font"], CP['L_SchoolTimetable']['size']))
        self.L_SchoolTimetable.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.L_SchoolTimetable.setText(CP['L_SchoolTimetable']["text"])

        I_ST = ANewPy.open_(f"{CP['IniDirPath']}SchoolTimetable.ini").r()
        I_LN = ANewPy.open_(f"{CP['IniDirPath']}LessonName.ini").r()
        today_lessons = I_ST[now.weekday()]
        x = 0
        self.L_ST_Dict = {}
        for index in I_LN:
            self.L_ST_ = QLabel(self)
            self.L_ST_.move(CP['L_SchoolTimetable']['x'] + x, CP['L_SchoolTimetable']['subTextY'])
            self.L_ST_.resize(int(CP['L_SchoolTimetable']['subTextSize'] * len(I_LN[index]) * 1.5),
                              CP['L_SchoolTimetable']['subTextSize'] + CP['L_SchoolTimetable']['subLabelHAdd'])
            self.L_ST_.setFont(QFont(CP["Font"], CP['L_SchoolTimetable']['subTextSize'], QFont.Bold))
            self.L_ST_.setAlignment(Qt.AlignLeft | Qt.AlignTop)
            self.L_ST_.setText(I_LN[index])
            self.L_ST_2 = QLabel(self)
            self.L_ST_2.move(CP['L_SchoolTimetable']['x'] + x, CP['L_SchoolTimetable']['subTextY_2'])
            self.L_ST_2.resize(int(CP['L_SchoolTimetable']['subTextSize'] * len(I_LN[index]) * 1.5),
                               CP['L_SchoolTimetable']['subTextSize'] + CP['L_SchoolTimetable']['subLabelHAdd'])
            self.L_ST_2.setFont(QFont(CP["Font"], CP['L_SchoolTimetable']['subTextSize']))
            self.L_ST_2.setAlignment(Qt.AlignLeft | Qt.AlignTop)
            self.L_ST_2.setText(today_lessons[index])
            self.L_ST_Dict[I_LN[index]] = (self.L_ST_, self.L_ST_2)
            x += int(CP['L_SchoolTimetable']['subTextSize'] * len(I_LN[index]) * 1.5) + CP['L_SchoolTimetable'][
                'eachAdd']

        self.L_HygieneForm = QLabel(self)
        self.L_HygieneForm.move(CP['L_HygieneForm']['x'], CP['L_HygieneForm']['y'])
        self.L_HygieneForm.resize(self.size[0] - CP['L_HygieneForm']['x'] - 10,
                                  self.size[1] - CP['L_HygieneForm']['y'] - 10)
        self.L_HygieneForm.setFont(QFont(CP["Font"], CP['L_HygieneForm']['size']))
        self.L_HygieneForm.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.L_HygieneForm.setText(CP['L_HygieneForm']["text"])

        I_DSL = ANewPy.open_(f"{CP['IniDirPath']}DutyStudentList.ini").r().split("\n")
        fn = f"{CP['IniDirPath']}DutyStudentFlag.tmp"
        today_text = [now.month, now.day]
        if os.path.exists(fn):
            c = ANewPy.open_(fn).r()
            if isinstance(c[1], str):
                if c[1] in I_DSL:
                    c[1] = I_DSL.index(c[1])
                else:
                    c[1] = 0
            else:
                if c[0] == today_text:
                    pass
                else:
                    c[0] = today_text
                    c[1] += 1
                    if c[1] >= len(I_DSL):
                        c[1] = 0
        else:
            c = [today_text, 0]
        ANewPy.open_(fn).w(f"[{c[0]}, {c[1]}]")
        i = c[1]
        DutyStudentName = I_DSL[i]
        i += 1
        if i >= len(I_DSL):
            i = 0
        DutyStudentName_2 = I_DSL[i]
        I_HFS = ANewPy.open_(f"{CP['IniDirPath']}HygieneFormStudent.ini").r()
        I_HF = ANewPy.open_(f"{CP['IniDirPath']}HygieneForm.ini").r()
        I_HF[0] = CP['DutyStudentText']['today']
        I_HF[1] = CP['DutyStudentText']['tomorow']
        toWeek_HFS = [DutyStudentName, DutyStudentName_2]
        toWeek_HFS.extend(I_HFS[ANewPy.open_(f"{CP['IniDirPath']}Flag.ini").r()])
        x = 0
        I_HFNL = list(I_HF.keys())
        I_HFNL.sort()
        for index in I_HFNL:
            self.L_HF_ = QLabel(self)
            self.L_HF_.move(CP['L_HygieneForm']['x'] + x, CP['L_HygieneForm']['subTextY'])
            self.L_HF_.resize(self.size[0], CP['L_HygieneForm']['subTextSize'] + CP['L_HygieneForm']['subLabelHAdd'])
            self.L_HF_.setFont(QFont(CP["Font"], CP['L_HygieneForm']['subTextSize'], QFont.Bold))
            self.L_HF_.setAlignment(Qt.AlignLeft | Qt.AlignTop)
            self.L_HF_.setText(I_HF[index])
            self.L_HF_2 = QLabel(self)
            if len(I_HF[index]) >= len(toWeek_HFS[index]):
                maxLen = len(I_HF[index])
            else:
                maxLen = len(toWeek_HFS[index])
            self.L_HF_2.move(CP['L_HygieneForm']['x'] + x, CP['L_HygieneForm']['subTextY_2'])
            self.L_HF_2.resize(int(CP['L_HygieneForm']['subTextSize'] * maxLen * 1.5),
                               CP['L_HygieneForm']['subTextSize'] + CP['L_HygieneForm']['subLabelHAdd'])
            self.L_HF_2.setFont(QFont(CP["Font"], CP['L_HygieneForm']['subTextSize']))
            self.L_HF_2.setAlignment(Qt.AlignLeft | Qt.AlignTop)
            self.L_HF_2.setText(toWeek_HFS[index])
            x += int(CP['L_HygieneForm']['subTextSize'] * maxLen * 1.5) + CP['L_HygieneForm']["eachAdd"]

        for SplitLine in CP['SplitLines']:
            L_SplitLine = QLabel(self)
            L_SplitLine.move(SplitLine[0], SplitLine[1])
            L_SplitLine.resize(SplitLine[2], SplitLine[3])
            L_SplitLine.setStyleSheet(f"background-color:black;")

    def second_do(self):
        global disk_list, CP, _DesktopWindow
        self.time_count += 1
        # ↓ subtext 时间更新
        self.count_subtext += 0.1
        if self.count_subtext >= CP["subtext_countMax"]:
            self.mode_subtext += 1
            if self.mode_subtext >= len(self.subtextList):
                self.mode_subtext = 0
            self.flag_subtext = 1
            self.count_subtext = 0
        # ↓ 更新时间
        now = datetime.datetime.now()
        now += datetime.timedelta(seconds=CP["SchoolTimeDelay"])
        self.L_Time.setText(CP['L_Time']['text']
                            % (beautifulTime(now.hour), beautifulTime(now.minute), beautifulTime(now.second)))
        # ↓ 检测移动存储器
        try:
            usb_disk = get_disklist()[-1]
            if usb_disk not in disk_list:
                os.startfile(usb_disk)
        except:
            pass
        disk_list = get_disklist()
        # ↓ 检测当前时间课堂信息
        if self.time_count >= 10:
            ifLesson = False
            now_lesson_ordinal = 0
            I_T = ANewPy.open_(r"ini/Timetable.ini").r()
            for el in I_T:
                sTS = el[0][0] * 3600 + el[0][1] * 60
                eTS = el[1][0] * 3600 + el[1][1] * 60
                nTS = now.hour * 3600 + now.minute * 60 + now.second
                if nTS < sTS:
                    ifLesson = False
                elif sTS <= nTS < eTS:
                    ifLesson = True
                else:
                    now_lesson_ordinal += 1
                    continue
                break
            I_LN = ANewPy.open_(f"{CP['IniDirPath']}LessonName.ini").r()
            if now_lesson_ordinal < len(I_LN):
                now_lesson = I_LN[now_lesson_ordinal]
                for i in self.L_ST_Dict:
                    if i == now_lesson:
                        if not ifLesson and self.L_ST_Dict[i][0].styleSheet() != "":
                            self.L_ST_Dict[i][0].setStyleSheet("")
                            self.L_ST_Dict[i][1].setFont(QFont(CP["Font"], CP['L_SchoolTimetable']['subTextSize']))
                            self.L_ST_Dict[i][1].setStyleSheet("")
                        else:
                            self.L_ST_Dict[i][0].setStyleSheet(
                                f"color: {CP['HighlightTextColor']}; background-color:{CP['HighlightBackgroundColor']};")
                            self.L_ST_Dict[i][1].setFont(
                                QFont(CP["Font"], CP['L_SchoolTimetable']['subTextSize'], QFont.Bold))
                            self.L_ST_Dict[i][1].setStyleSheet(
                                f"color: {CP['HighlightTextColor']}; background-color:{CP['HighlightBackgroundColor']};")
                    else:
                        self.L_ST_Dict[i][0].setStyleSheet("")
                        self.L_ST_Dict[i][1].setFont(QFont(CP["Font"], CP['L_SchoolTimetable']['subTextSize']))
                        self.L_ST_Dict[i][1].setStyleSheet("")
        if self.time_count >= 10:
            CP_ = ANewPy.open_('ConfigurationParameter.ini').r()
            if CP_ != CP:
                CP = CP_
                _DesktopWindow = DesktopWindow()
            self.time_count = 1

    def effect_do(self):
        if self.flag_subtext != 0:
            if self.flag_subtext == 1:
                self.alpha_subtext -= CP["subtext_alphaChange"]
                if self.alpha_subtext < 0:
                    self.alpha_subtext = 0
            elif self.flag_subtext == 2:
                self.alpha_subtext += CP["subtext_alphaChange"]
                if self.alpha_subtext > 1:
                    self.alpha_subtext = 1
            SetAlpha(self.L_Notice, self.alpha_subtext)
            if self.alpha_subtext == 0:
                self.flag_subtext = 2
                self.L_Notice.setText(self.subtextList[self.mode_subtext])
            elif self.alpha_subtext == 1:
                self.flag_subtext = 0
        if self.used_time <= CP["EffectTotalTime"] and self.effect_do_time_flag:
            func = Nonlinear(self.used_time)
            if self.outFlag:
                y = func
                self.move(0, int(-self.size[1] * y))
                self.setWindowOpacity(1 - y)
                self.HideTipWindow.start()
            else:
                y = 1 - func
                self.move(0, int(-self.size[1] * y))
                self.setWindowOpacity(1 - y)
            self.used_time += self.effect_do_timer_time / 1000
            if func == 1:
                self.setWindowOpacity(1)
                if self.outFlag:
                    self.move(0, -self.size[1])

                    self.outFlag = False
                else:
                    self.move(0, 0)
                    self.outFlag = True
                self.effect_do_time_flag = False
                self.used_time = self.effect_do_timer_time

    def start_effect(self):
        self.used_time = self.effect_do_timer_time / 1000
        self.effect_do_time_flag = True

    def exit(self):
        self.close()
        ANewPy.quit(1)

    def expand(self):
        self.outFlag = False
        self.start_effect()

    def mousePressEvent(self, _):
        if not self.effect_do_time_flag:
            self.outFlag = True
            self.start_effect()


class HideTipWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.size = CP["W_HideTipWindow"]["size"]

        self.setStyleSheet("background:transparent")
        self.setWindowFlags(Qt.WindowStaysOnBottomHint | Qt.FramelessWindowHint | Qt.Tool)
        ANewPy.pyqtpro.windowEffect.AeroEffectPreposition(self)
        self.move(CP["W_HideTipWindow"]["x"], CP["W_HideTipWindow"]["y"])
        self.resize(self.size[0], self.size[1])

        self.L_Logo = QLabel(self)
        self.L_Logo.move(10, 10)
        self.L_Logo.resize(self.size[0] - 20, self.size[1] - 20)
        self.L_Logo.setScaledContents(True)
        self.L_Logo.setPixmap(QPixmap(CP['L_Logo']['path']))

    def start(self):
        self.show()

    def mousePressEvent(self, _):
        _DesktopWindow.expand()
        self.hide()


class lessonProgress(QMainWindow):
    def __init__(self):
        super().__init__(None)
        self.setWindowTitle("AsEducationDesktop - LessonProgress")
        self.win_weight = ANewPy.screensize()[0]
        self.win_height = 10
        self.resize(self.win_weight - 1, self.win_height)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowTransparentForInput | Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)

        self.w = 0
        self.r = 255
        self.g = 255
        self.b = 255

        self.BG = QLabel(self)
        self.BG.move(-3, 0)
        self.BG.setAutoFillBackground(True)

        self.D_L_splitLine_list = []
        self.aTM_flag = 0

        self.lL = ANewPy.open_(r"ini/Timetable.ini").r()

        ANewPy.pyqtpro.pyqtpro.CTimer(self, 100, self.timer_do)

        self.show()

    def D_L_splitLine(self, k):
        L_splitLine = QLabel(self)
        L_splitLine.move(int(self.win_weight * k), 0)
        L_splitLine.resize(5, self.win_height)
        L_splitLine.setStyleSheet("QWidget{background-color: rgba(0, 0, 0, 180);}")
        L_splitLine.setAutoFillBackground(True)
        self.D_L_splitLine_list.append(L_splitLine)

    def cL(self):
        eTS_ = 0
        for el in self.lL:
            sTS = el[0][0] * 3600 + el[0][1] * 60
            eTS = el[1][0] * 3600 + el[1][1] * 60
            now = datetime.datetime.now()
            SchoolTimeDelay = ANewPy.open_("ConfigurationParameter.ini").r()["SchoolTimeDelay"]
            nTS = now.hour * 3600 + now.minute * 60 + now.second + SchoolTimeDelay
            if nTS < sTS:
                nTS -= eTS_
                ifLesson = False
                aTS = sTS - eTS_
            elif sTS <= nTS < eTS:
                nTS -= sTS
                ifLesson = True
                aTS = eTS - sTS
            else:
                eTS_ = eTS
                continue
            break
        else:
            return False, -1
        return ifLesson, nTS / aTS, int(aTS / 60)

    def timer_do(self):
        self.BG.setStyleSheet(f"QWidget{{background:rgba({self.r}, {self.g}, {self.b},180); border-radius: 5px;}}")
        self.BG.resize(self.w, self.win_height)
        k = self.cL()
        if k[1] == -1:
            for i in self.D_L_splitLine_list:
                i.hide()
            self.r = 255
            self.g = 255
            self.b = 255
            self.w = self.win_weight
        else:
            if k[0]:
                if self.aTM_flag != k[2]:
                    for i in self.D_L_splitLine_list:
                        i.close()
                    self.D_L_splitLine_list.clear()
                    self.D_L_splitLine(2 / k[2])
                    self.D_L_splitLine(7 / k[2])
                    self.D_L_splitLine((k[2] - 5) / k[2])
                    self.aTM_flag = k[2]
                    for i in self.D_L_splitLine_list:
                        i.show()
                self.r = CP["lessonProgress"]["isLesson_color"][0]
                self.g = CP["lessonProgress"]["isLesson_color"][1]
                self.b = CP["lessonProgress"]["isLesson_color"][2]
            else:
                for i in self.D_L_splitLine_list:
                    i.hide()
                self.r = CP["lessonProgress"]["notLesson_color"][0]
                self.g = CP["lessonProgress"]["notLesson_color"][1]
                self.b = CP["lessonProgress"]["notLesson_color"][2]
                self.aTM_flag = 0
            self.w = int(self.win_weight * k[1])


CP = ANewPy.open_('ConfigurationParameter.ini').r()
disk_list = get_disklist()
if __name__ == "__main__":
    app = QApplication(sys.argv)
    QApplication.setQuitOnLastWindowClosed(False)
    if CheckIfItIsRunning():
        ANewPy.quit(1)
    else:
        _Tray = Tray()
        _DesktopWindow = DesktopWindow()
    sys.exit(app.exec_())
