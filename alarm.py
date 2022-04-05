## 알람 만들기

#!/usr/bin/python

from ast import Module
from datetime import datetime
import threading
import subprocess
import pifacecad

def update_pin_text(event):
    cad.lcd.clear()
    global mode
    global alarmsetmode_flag
    if event.pin_num==2:
        mode=2
    if event.pin_num==3:
        mode=3
    if event.pin_num==4 or event.pin_num==0 or event.pin_num==1:
        mode=1
        alarmsetmode_flag=0
        if(event.pin_num==4):
            Check_time()
    

    event.chip.lcd.set_cursor(13,0)
    event.chip.lcd.write(str(event.pin_num))
    set_mode(mode)

#시계모드
def clock_mode():
    cad.lcd.write(subprocess.run(['hostname', '-I'], capture_output=True, text=True).stdout)
    now = datetime.now()
    cad.lcd.set_cursor(0,1)
    cad.lcd.write(now.strftime("%m/%d %a %H:%M "))
    cad.lcd.set_cursor(12,1)

#알람설정모드
def alarm_set_mode(event):
    cad.lcd.set_cursor(0,1)
    global flag_H
    global flag_M
    global alarmsetmode_flag

    if alarmsetmode_flag == 1:
        global set_H;global set_M
        global change_H;global change_M

        #알람 시간 세팅
        if event.pin_num==5:
            if change_M>59:
                change_M=0
            if change_H>23:
                change_H-=24

            set_H = change_H 
            set_M = change_M

        #알람 시간 조절
        if event.pin_num==6:
            change_H +=1
        if event.pin_num==7:
            change_M +=1
        
        write_alarm(change_H,change_M)
    else:
        cad.lcd.clear()
        cad.lcd.write("PUSH BUTTON 2")

#알람 세팅 중 시간 표시
def write_alarm(change_H,change_M):
    cad.lcd.clear()
    cad.lcd.set_cursor(0,0)

    if change_H>23:
        cad.lcd.write(str(change_H-24))
    else:
        cad.lcd.write(str(change_H))

    cad.lcd.set_cursor(0,1)
    if change_M>59:
        cad.lcd.write(str(change_M-60))
    else:
        cad.lcd.write(str(change_M))

#알람 울림
def alarm_on():
    global set_H;global set_M
    set_H=-1;set_M=-1
    cad.lcd.clear()
    cad.lcd.set_cursor(0,0)
    cad.lcd.write("ALARM RING")
    cad.lcd.set_cursor(0,1)
    cad.lcd.write("END:PushButton4")

#알람과 현재 시간 비교
def Check_time():
    timer = threading.Timer(0.5,Check_time)
    timer.start()
    now = datetime.now()

    global current_H;global current_M
    current_H = now.hour;current_M = now.minute
    global set_H;global set_M
    global mode

    if(current_H==set_H and current_M==set_M):
        timer.cancel()
        mode=1
        alarm_on()
    
#알람 시간 체크 모드
def alarm_check_mode():
    global set_H
    global set_M
    cad.lcd.clear()
    cad.lcd.set_cursor(0,0)
    cad.lcd.write("Check alarm time")
    cad.lcd.set_cursor(0,1)
    cad.lcd.write(str(set_H))
    cad.lcd.set_cursor(4,1)
    cad.lcd.write(str(set_M))


def set_mode(mode=1):
    cad.lcd.clear()
    global alarmsetmode_flag
    if mode==2:
        alarmsetmode_flag=1
    elif mode==3:
        alarm_check_mode()
    else: clock_mode()

cad = pifacecad.PiFaceCAD()
cad.lcd.backlight_on()
cad.lcd.cursor_off()
global alarmsetmode_flag
alarmsetmode_flag=0
global flag_H;global flag_M
flag_H=0; flag_M=0
global set_H;global set_M
global change_H;global change_M
change_H = 0;set_H = -1
change_M = 0;set_M = -1

listener = pifacecad.SwitchEventListener(chip=cad)
listener_setalarm = pifacecad.SwitchEventListener(chip=cad)

Check_time()
set_mode()

alarm_list=[0,1,5,6,7]
button_list=[2,3,4]
for i in button_list:
	listener.register(i, pifacecad.IODIR_FALLING_EDGE, update_pin_text)
for i in alarm_list:
    listener_setalarm.register(i, pifacecad.IODIR_FALLING_EDGE, alarm_set_mode)

listener.activate()
listener_setalarm.activate()
