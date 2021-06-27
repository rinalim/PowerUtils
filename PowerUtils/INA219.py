import smbus
import time, os
from subprocess import *
from PIL import Image, ImageDraw, ImageFont
import board
from adafruit_ina219 import ADCResolution, BusVoltageRange, INA219

i2c_bus = board.I2C()

ina219 = INA219(i2c_bus)

# optional : change configuration to use 32 samples averaging for both bus voltage and shunt voltage
ina219.bus_adc_resolution = ADCResolution.ADCRES_12BIT_32S
ina219.shunt_adc_resolution = ADCResolution.ADCRES_12BIT_32S
# optional : change voltage range to 16V
ina219.bus_voltage_range = BusVoltageRange.RANGE_16V

v_step = [9.4,10.0,10.6,11.1,11.6,12.1]

INTERVAL = 10
PATH_BAT="/opt/retropie/configs/all/PowerUtils/"

def run_cmd(cmd):
    # runs whatever in the cmd variable
    p = Popen(cmd, shell=True, stdout=PIPE)
    output = p.communicate()[0]
    return output.decode()

def get_step(vin):
    percent = int((vin-v_step[0])/(v_step[5]-v_step[0])*100)
    if vin > v_step[5]:
        return 6, 100
    elif vin > v_step[4]:
        return 5, percent
    elif vin > v_step[3]:
        return 4, percent
    elif vin > v_step[2]:
        return 3, percent
    elif vin > v_step[1]:
        return 2, percent
    elif vin > v_step[0]:
        return 1, percent
    else:
        return 0, 0

GAP = 10
fbset = run_cmd("fbset -s | grep mode | grep -v endmode | awk '{print $2}'").replace('"', '')
res_x = fbset.split("x")[0]
res_y = fbset.split("x")[1].replace('\n', '')
if os.path.isfile(PATH_BAT + "0.png") == False:
    print("Cannot find 0.png")
    sys.exit(0)
width, height = Image.open(PATH_BAT + "0.png").size
x1 = int(res_x)-width-GAP
y1 = 0+GAP
x2 = int(res_x)-GAP
y2 = height + GAP
#POS = "1221,11,1270,35"
POS = str(x1) + "," + str(y1) + "," + str(x2) + "," + str(y2)

os.system("pkill -ef omxiv-battery")
os.system("echo " + PATH_BAT + "0.png > /tmp/battery.txt")
os.system(PATH_BAT + "omxiv-battery /tmp/battery.txt -f -T blend --duration 20 -l 30003 --win '" + POS + "' &")
def draw_text(text, infile, outfile):
    font_size = 14
    font = ImageFont.truetype('NanumBarunGothicBold.ttf', font_size)
    #image = Image.new('RGBA', 
    #        (font.getsize(str(text))[0]+width, font.getsize(str(text))[1]+height), 
    #        (0, 0, 0, 0))
    image = Image.open(infile)
    draw = ImageDraw.Draw(image)
    draw.fontmode = "1"
    draw.text((3,6), text, font=font, fill="black")
    image.save(outfile)

step_old = -1
percent_old = -1
vin = 0
while True:
    bus_voltage = ina219.bus_voltage  # voltage on V- (load side)
    shunt_voltage = ina219.shunt_voltage  # voltage between V+ and V- across the shunt
    current = ina219.current  # current in mA
    power = ina219.power  # power in watts
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
    step,percent = get_step(bus_voltage)
    percent = int(percent)
    print(bus_voltage, percent)
    if step != step_old or percent != percent_old:
        png = str(step) + ".png"
        #os.system("echo " + PATH_BAT + png + " > /tmp/battery.txt")
        draw_text(str(percent)+"%", PATH_BAT+png, "/tmp/bat.png")
        png = "/tmp/bat.png"
        os.system("echo " + png + " > /tmp/battery.txt")
        step_old = step
        percent_old = percent
    time.sleep(INTERVAL)
