import smbus
import time, os
address = 0x48
A0 = 0x40
A1 = 0x41
A2 = 0x42
A3 = 0x43
bus = smbus.SMBus(1)
v_step = [9.6,10.1,10.6,11.1,11.6,12.1]
v_shutdown = 9.0

INTERVAL = 1
RESET_COUNT = 3
PATH_BAT="/opt/retropie/configs/all/PowerUtils/"
POS = "1221,11,1270,35"

def get_step(vin):
    if vin > v_step[5]:
        return 6
    elif vin > v_step[4]:
        return 5
    elif vin > v_step[3]:
        return 4
    elif vin > v_step[2]:
        return 3
    elif vin > v_step[1]:
        return 2
    elif vin > v_step[0]:
        return 1
    else:
        return 0

os.system("echo " + PATH_BAT + "0.png > /tmp/battery.txt")
os.system(PATH_BAT + "omxiv-battery /tmp/battery.txt -f -T blend --duration 20 -l 30003 --win '" + POS + "' &")

step_old = -1
countdown = RESET_COUNT
btn_pushed = False
vin = 0
while True:
    bus.write_byte(address,A0)
    value = bus.read_byte(address)
    vout = value*5.0/256
    if vin == 0:
        vin = vout*5
    elif vout == 0:
        vin = 0
    else:
        vin = vin*0.9 + vout*5*0.1
    if vin < v_shutdown:
        btn_pushed = True
    if btn_pushed == True:
        if vin < v_shutdown:
            countdown = countdown-1
            if countdown < 0:
                os.system("shutdown -h now")
        else:
            os.system("shutdown -r now")
    
    step = get_step(vin)
    if step != step_old:
        step_old = step
        png = str(step_old) + ".png"
        os.system("echo " + PATH_BAT + png + " > /tmp/battery.txt")
    time.sleep(INTERVAL)
