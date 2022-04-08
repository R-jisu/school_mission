## 알람 만들기

#!/usr/bin/python

from ast import Module
from datetime import datetime
from itertools import count
from signal import alarm
from pyowm.owm import OWM
import threading
import subprocess
import pifacecad
import pygame
import time
import pygments
import lirc

sockid = lirc.init("myprogram")
pygame.mixer.init()
pygame.mixer.music.load("alarmring.mp3")

def update_pin_text(event):
    cad.lcd.clear()
    global mode;global ring;global alarmsetmode_flag
    global alarm_timer; global timer
    if event.pin_num==2:
        alarm_timer.cancel()
        mode=2
    if event.pin_num==3:
        cad.lcd.clear()
        mode=3
    if event.pin_num==4:
        pygame.mixer.music.stop()
        timer.cancel()
        alarm_timer.cancel()
        mode=1
        alarmsetmode_flag=0
        Check_time()
        alarm_update()
    # event.chip.lcd.set_cursor(13,0)
    # event.chip.lcd.write(str(event.pin_num))
    cad.lcd.clear()
    set_mode(mode)

#시계모드
def clock_mode():
    cad.lcd.write(subprocess.run(['hostname', '-I'], capture_output=True, text=True).stdout)
    now = datetime.now()
    cad.lcd.set_cursor(0,1)
    cad.lcd.write(now.strftime("%m/%d %H:%M:%S"))
    cad.lcd.set_cursor(0,0)

#알람설정모드
def alarm_set_mode(event):
    global i
    cad.lcd.set_cursor(0,1)
    global alarmsetmode_flag
    global set_H;global set_M
    global change_H;global change_M
    global alarm_timer
    alarm_timer.cancel()
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
    elif alarmsetmode_flag == 0 and event.pin_num==5:
        i+=1
        weather(i)
    # elif alarmsetmode_flag ==0 and lirc.nextcode()[0]=='99':
        # draw_pic()

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
    global ring;global mode
    global set_H;global set_M
    set_H=-1 ;set_M=-1
    global alarm_timer; global timer
    alarm_timer.cancel()
    cad.lcd.clear()
    cad.lcd.set_cursor(0,0)
    cad.lcd.write("ALARM RING")
    cad.lcd.set_cursor(0,1)
    cad.lcd.write("END:PushButton4")
    mode=0
    pygame.mixer.music.play()

#알람과 현재 시간 비교
def Check_time():
    global timer
    timer = threading.Timer(0.5,Check_time)
    timer.start()
    now = datetime.now()

    global current_H;global current_M
    current_H = now.hour;current_M = now.minute
    global set_H;global set_M
    global mode

    if(current_H==set_H and current_M==set_M):
        timer.cancel()
        alarm_on()

#알람 업데이트
def alarm_update():
    global alarm_timer
    alarm_timer = threading.Timer(1,alarm_update)
    alarm_timer.start()
    if mode==1:
        clock_mode()

#알람 시간 체크 모드
def alarm_check_mode():
    global set_H
    global set_M
    global mode
    global cnt

    cnt+=1
    timer_3s = threading.Timer(1,alarm_check_mode)
    timer_3s.start()

    if cnt==3:
        cnt=0
        timer_3s.cancel()
        set_mode()
        return
    cad.lcd.set_cursor(0,0)
    cad.lcd.write("Check alarm time")
    cad.lcd.set_cursor(0,1)
    cad.lcd.write(f'at {set_H:02d}:{set_M:02d}')

#날씨
def weather(i):
    cad.lcd.clear()
    owm = OWM('b03b3e37c20ee389a016795db687a7be')
    mgr = owm.weather_manager()

    if i%6==0:
        observation = mgr.weather_at_place('Incheon')
        place='Incheon' 
    elif i%6==1:
        observation = mgr.weather_at_place('London') 
        place='London' 
    elif i%6==2:
        observation = mgr.weather_at_place('Holman') 
        place='Holman' 
    elif i%6==3:
        observation = mgr.weather_at_place('Tokyo') 
        place='Tokyo' 
    elif i%6==4:
        observation = mgr.weather_at_place('Bangkok')
        place='Bangkok' 
    elif i%6==5:
        observation = mgr.weather_at_place('Paris') 
        place='Paris' 


    weather = observation.weather
    cad.lcd.write(f'{place}')
    cad.lcd.set_cursor(0,1)
    cad.lcd.write(f'{weather.detailed_status}')

#시계 모드 설정
def set_mode(mode_=1):
    global change_H;global change_M
    global alarmsetmode_flag
    cad.lcd.clear()
    global mode
    mode = mode_
    if mode==2:
        alarmsetmode_flag=1
        cad.lcd.set_cursor(0,0)
        cad.lcd.write(f'at {change_H:02d}:{change_M:02d}')
        cad.lcd.set_cursor(0,1)
        cad.lcd.write('Not SET')
    elif mode==3:
        alarm_check_mode()
    elif mode==1: clock_mode()

cad = pifacecad.PiFaceCAD();cad.lcd.backlight_on();cad.lcd.cursor_off()
global alarmsetmode_flag;alarmsetmode_flag=0
global mode; mode=1
global i;i=-1; 
global cnt; cnt=0
now_for_change = datetime.now()
global set_H;global set_M
global change_H;global change_M
change_H = now_for_change.hour; set_H = -1
change_M = now_for_change.minute;   set_M = -1

listener = pifacecad.SwitchEventListener(chip=cad)
listener_setalarm = pifacecad.SwitchEventListener(chip=cad)

Check_time()
set_mode()
alarm_update()

alarm_list=[0,1,5,6,7]
button_list=[2,3,4]
for i in button_list:
	listener.register(i, pifacecad.IODIR_FALLING_EDGE, update_pin_text)
for i in alarm_list:
    listener_setalarm.register(i, pifacecad.IODIR_FALLING_EDGE, alarm_set_mode)


listener.activate()
listener_setalarm.activate()




