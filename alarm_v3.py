## 알람 만들기

#!/usr/bin/python

from ast import Module
from datetime import datetime
import threading
import subprocess
import pifacecad
import pygame
import time
import pygments

pygame.mixer.init()
pygame.mixer.music.load("alarmring.mp3")

def update_pin_text(event):
    cad.lcd.clear()
    global mode
    global ring
    global alarmsetmode_flag
    if event.pin_num==2:
        mode=2
    if event.pin_num==3:
        mode=3
    if event.pin_num==4:
        pygame.mixer.music.stop()
        mode=1
        alarmsetmode_flag=0
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
    global alarmsetmode_flag
    global set_H;global set_M
    global change_H;global change_M

    if alarmsetmode_flag == 1:

        #알람 시간 세팅
        if event.pin_num==5:

            set_H = change_H 
            set_M = change_M
            cad.lcd.set_cursor(0,1)
            cad.lcd.write('SET Alarm')
        #알람 시간 조절
        
        if event.pin_num==6:
            change_H +=1
        
        if event.pin_num==0:
            change_H +=8

        if event.pin_num==7:
            change_M +=1
        
        if event.pin_num==1:
            change_M +=10

        write_alarm()
    else:
        cad.lcd.clear()
        cad.lcd.write("PUSH BUTTON 2")

#알람 세팅 중 시간 표시
def write_alarm():
    global change_M; global change_H
    cad.lcd.set_cursor(0,0)

    if change_H>23:
        change_H-=24
    if change_M>59:
        change_M-=60
    
    cad.lcd.write(f'at {change_H:02d}:{change_M:02d}')

#알람 울림
def alarm_on():
    global ring
    global set_H;global set_M
    set_H=-1;set_M=-1
    cad.lcd.clear()
    cad.lcd.set_cursor(0,0)
    cad.lcd.write("ALARM RING")
    
    pygame.mixer.music.play()
    
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
    cad.lcd.write(f'at {set_H:02d}:{set_M:02d}')


def set_mode(mode=1):
    global change_H;global change_M
    global alarmsetmode_flag
    cad.lcd.clear()

    if mode==2:
        alarmsetmode_flag=1
        cad.lcd.set_cursor(0,0)
        cad.lcd.write(f'at {change_H:02d}:{change_M:02d}')
        cad.lcd.set_cursor(0,1)
        cad.lcd.write('Not SET')
    elif mode==3:
        alarm_check_mode()
    else: clock_mode()

cad = pifacecad.PiFaceCAD();cad.lcd.backlight_on();cad.lcd.cursor_off()
global alarmsetmode_flag
alarmsetmode_flag=0
global set_H;global set_M
global change_H;global change_M
now_for_change = datetime.now()
change_H = now_for_change.hour; set_H = -1
change_M = now_for_change.minute;   set_M = -1

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




