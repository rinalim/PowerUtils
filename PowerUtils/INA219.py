import smbus
import time, os, sys
from subprocess import *
from PIL import Image, ImageDraw, ImageFont
from resizeimage import resizeimage
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
PATH_BAT="/home/pi/PowerUtils/PowerUtils/"
GAP = 10
_width, _height = Image.open(PATH_BAT+"0.png").size

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

def get_concat_h(im1, im2):
    #dst = Image.new('RGBA', (im1.width + im2.width, im1.height))
    #dst.paste(im1, (0, 0))
    dst = Image.new('RGBA', (im2.width*3, im2.height))
    dst.paste(im1, (im2.width*2-im1.width, 0))
    dst.paste(im2, (im2.width*2, 0))
    return dst

def get_concat_v(im1, im2):
    dst = Image.new('RGBA', (im1.width, im1.height + im2.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (0, im1.height))
    return dst

def draw_text(text, infile, outfile):
    text = text + " "
    img_bat = Image.open(infile)
    font_size = 50
    font = ImageFont.truetype('FreeSans.ttf', font_size)
    img = Image.new('RGBA', (font.getsize(str(text))[0], font.getsize(str(text))[1]), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.text((0,0-img.height*0.07), text, font=font, fill="white")
    img = resizeimage.resize_height(img, _height)
    img.save("/tmp/text.png")
    get_concat_h(img, img_bat).save(outfile)
    #img.save(outfile)

fbset = run_cmd("fbset -s | grep mode | grep -v endmode | awk '{print $2}'").replace('"', '')
res_x = fbset.split("x")[0]
res_y = fbset.split("x")[1].replace('\n', '')

if os.path.isfile(PATH_BAT + "0.png") == False:
    print("Cannot find 0.png")
    sys.exit(0)
draw_text("---", PATH_BAT+"0.png", "/tmp/bat.png")
os.system("echo /tmp/bat.png > /tmp/battery.txt")

width, height = Image.open("/tmp/bat.png").size
x1 = int(res_x)-width-GAP
y1 = 0+GAP
x2 = int(res_x)-GAP
y2 = height + GAP
#POS = "1221,11,1270,35"
POS = str(x1) + "," + str(y1) + "," + str(x2) + "," + str(y2)

os.system("pkill -ef omxiv-battery")
os.system(PATH_BAT + "omxiv-battery /tmp/battery.txt -f -T blend --duration 20 -l 30003 --win '" + POS + "' &")

time.sleep(10)

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
