## 알람 만들기

#!/usr/bin/python

from datetime import datetime
import subprocess
import pifacecad

mode=1

def update_pin_text(event):
    cad.lcd.clear()
    if mode==1:
        clock_mode()
    if event.pin_num==2:
        mode=2
    if event.pin_num==3:
        mode=3
    if event.pin_num==4:
        mode=1
	event.chip.lcd.set_cursor(13,0)
	event.chip.lcd.write(str(event.pin_num))

cad = pifacecad.PiFaceCAD()
cad.lcd.backlight_on()
cad.lcd.cursor_off()
listener = pifacecad.SwitchEventListener(chip=cad)
for i in range(8):
	listener.register(i, pifacecad.IODIR_FALLING_EDGE, update_pin_text)
listener.activate()

def clock_mode():
    cad.lcd.write(subprocess.run(['hostname', '-I'], capture_output=True, text=True).stdout)
    now = datetime.now()
    cad.lcd.set_cursor(0,1)
    cad.lcd.write(now.strftime("%m/%d %a %H:%M "))
    cad.lcd.set_cursor(12,1)
