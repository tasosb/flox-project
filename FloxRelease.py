##############################################################################
##        ~Flox Team Project~                                               ##
##     VERSION 1.1 | PUBLIC RELEASE                                         ##
##     Website: [Will be updated-WIP]                                       ##
##     1st Lyceum of Kifissia,Greece                                        ##
##            2017-2018                                                     ##
##        Flox project (c) by                                               ##
##      A.Bithas & X. Xanthopoulos                                          ##
##    Flox Project is licensed under a                                      ##
## Creative Commons Attribution-NonCommercial 4.0 International License.    ##
## You should have received a copy of the license along with this           ##
## work. If not, see <http://creativecommons.org/licenses/by-nc/4.0/>.      ##
##############################################################################

##---------IMPORTS----------##
import ephem
import time
import datetime as dt
import csv
import picamera
import os
from PIL import Image
from sense_hat import SenseHat
import numpy as numpy

##--------Set necessary values--------##
total_time = 695 #(in loops) 1 loop approximately 4-5 seconds plus sleep time
loop_sleep = 6 #Enter time in seconds before the code re-starts. Consider that it takes 2-3 seconds to run the actual code.

##--------MESSASGES--------##
sense = SenseHat()
sense.set_rotation(270)
L = (255, 0, 0)
O = (255, 255, 255)
W = (0, 0, 0)
p= (0, 0, 255)
k=(128,128,128)
z=(139,69,19)
g=(0, 0, 0)
red=(255,0,0)
green=(0, 255, 0)
sense.show_message('1st Lyceum Kifisia, Greece', text_colour=[255,255,0], back_colour=[0,0,255])
greek_flag = [
    p, O, p, p, p, p, p, p,
    O, O, O, O, O, O, O, O,
    p, O, p, p, p, p, p, p,
    O, O, O, O, O, O, O, O,
    p, p, p, p, p, p, p, p,
    O, O, O, O, O, O, O, O,
    p, p, p, p, p, p, p, p,
    W, W, W, W, W, W, W, W
]
sense.set_pixels(greek_flag)
time.sleep(2)
sense.show_message('Flox Team', text_colour=[255,0,0], back_colour=[0,0,0])

##--------ISS EPHEM INITIALISATION--------##
## UPDATE VIA https://www.celestrak.com/NORAD/elements/stations.txt
## Last updated: 06/02/2018
names = "ISS (ZARYA)"
line1 = "1 25544U 98067A   18036.91906692  .00002035  00000-0  38067-4 0  9998"
line2 = "2 25544  51.6418 313.1103 0003188  79.0634  44.8685 15.54059236 98101"
iss = ephem.readtle(names, line1, line2)

##--------Initialise camera and values--------##
cam = picamera.PiCamera()
cam.annotate_text_size = 20
j = 0
blackRGB = 50
nblack=0
n=0
pixel=0
pixels=0
numpy.seterr(divide='ignore', invalid='ignore')
#Show an hourglass
in_progress = [
    k, k, k, k, k, k, k, k,
    k, z, z, z, z, z, z, k,
    g, k, z, z, z, z, k, g,
    g, g, k, z, z, k, g, g,
    g, g, k, z, z, k, g, g,
    g, k, g, z, g, g, k, g,
    k, g, g, g, g, g, g, k,
    k, k, k, k, k, k, k, k,
]

##--------CORE, OPEN .CSV--------##
with open('flox.csv', 'w') as ofile:
    writer=csv.writer(ofile, delimiter='\t',lineterminator='\n',)
    time_format = "%d/%m/%Y %H:%M:%S"
#WRITE INITIAL ROW
    writer.writerow(['Filename','delete?', 'P3', 'ISS Sublat', 'ISS Sublong'])
#BEGIN LOOP
    for j in range(0,total_time):
#GET ISS LOCATION-SHOW PROGRESS#
        progress=int((64*j)/total_time)
        sense.show_message('Progress:', text_colour=[0,255,0])
        pixels = [green if i < progress else red for i in range(64)]
        sense.set_pixels(pixels)
        time.sleep(.75)
        sense.set_pixels(in_progress)
        iss.compute()
#GET PICTURE
        filename1 = dt.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        cam.capture((filename1 + '.jpg'))
#Image processing(Black/Discard)
        img = Image.open((filename1 + '.jpg'))
        pixels = Image.open((filename1 + '.jpg')).getdata()
        DEL = 0
        nblack=0
        for pixel in pixels:
            if sum(pixel) < blackRGB:
                nblack +=1
        n = len(pixels)
        #FORdebug/print(nblack)
        #FORdebug/print(sum(pixel))
        if (nblack / float(n)) > 0.5:
            DEL = 1
            P3 = 0
            os.remove((filename1 + '.jpg'))       
        #BEGIN NDVI CALCULATION
        if DEL == 0:
            imgR, imgB, imgG = img.split() #get channels
            arrR = numpy.asarray(imgR).astype('float64')
            arrB = numpy.asarray(imgB).astype('float64')
            num   = (arrR - arrB)
            denom = (arrR + arrB)
            if denom.any() == 0.0:    #preventing division by zero.
                denom = 0.000001
            arr_ndvi = num/denom
            numpy.vstack(arr_ndvi)
            outputlist = []
            for i in arr_ndvi:
                outputlist.append(i[0])
            P1=len(outputlist)
            if P1==0:  #preventing division by zero
                P1=0.0001
            P5=0
            l = [x5 for x5 in outputlist if x5 > 0.25] #vegetation threshold
            P5 = len(l)
            P3=100*P5/P1
## WRITE AT CSV
        writer.writerow([filename1, DEL, P3, iss.sublat, iss.sublong])
#LOOP
        j = j+1
        if loop_sleep > 0:
            time.sleep(loop_sleep)
#LOOP END
##------CODE END------##
