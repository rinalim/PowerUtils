import smbus
import time, os
from subprocess import *
import board
from adafruit_ina219 import ADCResolution, BusVoltageRange, INA219

i2c_bus = board.I2C()

ina219 = INA219(i2c_bus)

# optional : change configuration to use 32 samples averaging for both bus voltage and shunt voltage
ina219.bus_adc_resolution = ADCResolution.ADCRES_12BIT_32S
ina219.shunt_adc_resolution = ADCResolution.ADCRES_12BIT_32S
# optional : change voltage range to 16V
ina219.bus_voltage_range = BusVoltageRange.RANGE_16V

v_step = [9.6,10.1,10.6,11.1,11.6,12.1]

INTERVAL = 10
PATH_BAT="/opt/retropie/configs/all/PowerUtils/"

def run_cmd(cmd):
    # runs whatever in the cmd variable
    p = Popen(cmd, shell=True, stdout=PIPE)
    output = p.communicate()[0]
    return output.decode()

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

#POS = "1221,11,1270,35"
fbset = run_cmd("fbset -s | grep mode | grep -v endmode | awk '{print $2}'").replace('"', '')
res_x = fbset.split("x")[0]
res_y = fbset.split("x")[1].replace('\n', '')
width = 60
height = 25
GAP = 10
x1 = int(res_x)-width-GAP
y1 = 0+GAP
x2 = int(res_x)-GAP
y2 = height + GAP
POS = str(x1) + "," + str(y1) + "," + str(x2) + "," + str(y2)

os.system("echo " + PATH_BAT + "0.png > /tmp/battery.txt")
os.system(PATH_BAT + "omxiv-battery /tmp/battery.txt -f -T blend --duration 20 -l 30003 --win '" + POS + "' &")

step_old = -1
vin = 0
while True:
    bus_voltage = ina219.bus_voltage  # voltage on V- (load side)
    shunt_voltage = ina219.shunt_voltage  # voltage between V+ and V- across the shunt
    current = ina219.current  # current in mA
    power = ina219.power  # power in watts
    '''
    # INA219 measure bus voltage on the load side. So PSU voltage = bus_voltage + shunt_voltage
    print("Voltage (VIN+) : {:6.3f}   V".format(bus_voltage + shunt_voltage))
    print("Voltage (VIN-) : {:6.3f}   V".format(bus_voltage))
    print("Shunt Voltage  : {:8.5f} V".format(shunt_voltage))
    print("Shunt Current  : {:7.4f}  A".format(current / 1000))
    print("Power Calc.    : {:8.5f} W".format(bus_voltage * (current / 1000)))
    print("Power Register : {:6.3f}   W".format(power))
    print("")

    # Check internal calculations haven't overflowed (doesn't detect ADC overflows)
    if ina219.overflow:
        print("Internal Math Overflow Detected!")
        print("")
    '''
    step = get_step(bus_voltage)
    if step != step_old:
        step_old = step
        png = str(step_old) + ".png"
        os.system("echo " + PATH_BAT + png + " > /tmp/battery.txt")
    time.sleep(INTERVAL)
