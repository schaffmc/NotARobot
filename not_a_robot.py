'''
github.com/schaffmc/NotARobot. See github wiki for important setup information. 

NOTE: this code was written for a personal project that was partly to
learn very basic Python-writing/electronics skills and partly to soothe a particular
symptom of PTSD for myself -- depersonalization/realization -- by creating something
that connects my internal world with the external world in a tangible way.

I'm not an expert, I was in no way trying to get this perfect and I had no
intention of sharing it with people; I just wanted it to work for me.
I have since commented as much as possible to make the logic more obvious. 

This code will not work for you right out of the box. You need to update the following
based on your individual setup: <bridgeIP>, <verylongstringoflettersfromtheCLIPAPI>,
<HueBulb1>, <HueBulb2>. There are also a few software dependencies described
in the GitHub wiki. Look at this as a starting point. I would love to see
anything that comes of it.

'''

#IMPORTING ALL THE PACKAGES WE NEED
import requests
import time
from ads1015 import ADS1015
import numpy as np
import matplotlib.pyplot as plt
from rgbmatrix5x5 import RGBMatrix5x5

#USER INPUT
#this controls how long the program will run for in terms of iterations
number_of_points = 500

#brightness of the hue light when it is ON
on_brightness = 250

#brightness of the hue light when it is "OFF"
#rather than turning it all the way off,
#i dial down the brightness -- its speedier
#(and looks cooler)
off_brightness = 50

#-----------------------------------------

INITIAL SETUP OF THE LIGHTS
##I want to be able to return the lights to whatever they were set to after I'm done displaying heartbeats
#finding the current state of the first light -- hue, saturation and brightness
message = requests.get("http://<bridgeIP>/api/<verylongstringoflettersfromtheCLIPAPI>/lights/<HueBulb1>").json()
inithue3 = message['state']['hue']
initsat3 = message['state']['sat']
initbri3 = message['state']['bri']
initialstate3 = {"bri":initbri3,"hue":inithue3,"sat":initsat3}

#finding the current state of the second light -- hue, saturation and brightness
message = requests.get("http://<bridgeIP>/api/<verylongstringoflettersfromtheCLIPAPI>/lights/<HueBulb2>").json()
inithue4 = message['state']['hue']
initsat4 = message['state']['sat']
initbri4 = message['state']['bri']
initialstate4 = {"bri":initbri4,"hue":inithue4,"sat":initsat4}

#turning the first light on and setting the color
message={"hue":2501,"sat":254,"bri":on_brightness}
requests.put("http://<bridgeIP>/api/<verylongstringoflettersfromtheCLIPAPI>/lights/<HueBulb1>/state",json=message)

#turning the second light on and setting the color
message={"hue":46346,"sat":235,"bri":on_brightness}
requests.put("http://<bridgeIP>/api/<verylongstringoflettersfromtheCLIPAPI>/lights/<HueBulb2>/state",json=message)

message = {"on":True,"bri":on_brightness}

# from now on, this is what turning a light "ON" or "OFF" means
onmessage = {"bri":on_brightness}
offmessage = {"bri":off_brightness}

#-----------------------------------------

##PREPPING THE ADC
CHANNELS = ['in0/gnd']
ads1015 = ADS1015()
ads1015.set_mode('single')

#This gain was picked by the max/min output of the analog signal
#from the pulsesensor. T
ads1015.set_programmable_gain(2.048)

#The sample rate in samples-per-second - can choose 128, 250, 490, 920, 1600 (default), 2400 or 3300
#per ADC breakout information. I left it at default even thought Python samples it far, far slower
#than this
ads1015.set_sample_rate(1600)
reference = ads1015.get_reference_voltage()
#print("Reference voltage: {:6.3f}v \n".format(reference))

#-----------------------------------------

##SETTING UP FOR LOOP VARIABLES
#creating various empty numpy arrays
volt_out = np.zeros(number_of_points)
t_record = np.zeros(len(volt_out))
moving_average = np.zeros(len(volt_out))
volt_high_band_pass = np.zeros(len(volt_out))
moving_max = np.zeros(len(volt_out))
moving_min = np.ones(len(volt_out))*1000
heartbeat_rec = []
volt_at_heartbeat = []
moving_avg_at_heartbeat = []


#-----------------------------------------


##SETTING UP THE 5X5 LED MATRIX BREAKOUT
rgbmatrix5x5 = RGBMatrix5x5()
rgbmatrix5x5.clear()
rgbmatrix5x5.show()
rgbmatrix5x5.set_brightness(1)


#-----------------------------------------


##WRITING A COUPLE OF FUNCTIONS
##FLASH THE LIGHTS A FEW TIMES
##There is definitely a better way to write this function; I wrote it out because so I could mess with this code manually more easily
def flash_lights():
    time.sleep(0.5)
    
    response = requests.put("http://<bridgeIP>/api/<verylongstringoflettersfromtheCLIPAPI>/lights/<HueBulb1>/state",json=offmessage)
    response = requests.put("http://<bridgeIP>/api/<verylongstringoflettersfromtheCLIPAPI>/lights/<HueBulb2>/state",json=offmessage)

    time.sleep(0.5)    
    
    response = requests.put("http://<bridgeIP>/api/<verylongstringoflettersfromtheCLIPAPI>/lights/<HueBulb1>/state",json=onmessage)
    response = requests.put("http://<bridgeIP>/api/<verylongstringoflettersfromtheCLIPAPI>/lights/<HueBulb2>/state",json=onmessage)

    time.sleep(0.5)

    response = requests.put("http://<bridgeIP>/api/<verylongstringoflettersfromtheCLIPAPI>/lights/<HueBulb1>/state",json=offmessage)
    response = requests.put("http://<bridgeIP>/api/<verylongstringoflettersfromtheCLIPAPI>/lights/<HueBulb2>/state",json=offmessage)

    time.sleep(0.5)
    
    response = requests.put("http://<bridgeIP>/api/<verylongstringoflettersfromtheCLIPAPI>/lights/<HueBulb1>/state",json=onmessage)
    response = requests.put("http://<bridgeIP>/api/<verylongstringoflettersfromtheCLIPAPI>/lights/<HueBulb2>/state",json=onmessage)

    time.sleep(0.5)


##SET THE PIXELS TO DRAW A HEART
#sets the pixels 
def set_heart(r,g,b):
    rgbmatrix5x5.set_pixel(0,1,r,g,b)
    rgbmatrix5x5.set_pixel(0,3,r,g,b)
    rgbmatrix5x5.set_pixel(1,0,r,g,b)
    rgbmatrix5x5.set_pixel(1,1,r,g,b)
    rgbmatrix5x5.set_pixel(1,2,r,g,b)
    rgbmatrix5x5.set_pixel(1,3,r,g,b)
    rgbmatrix5x5.set_pixel(1,4,r,g,b)
    rgbmatrix5x5.set_pixel(2,0,r,g,b)
    rgbmatrix5x5.set_pixel(2,1,r,g,b)
    rgbmatrix5x5.set_pixel(2,2,r,g,b)
    rgbmatrix5x5.set_pixel(2,3,r,g,b)
    rgbmatrix5x5.set_pixel(2,4,r,g,b)
    rgbmatrix5x5.set_pixel(3,1,r,g,b)
    rgbmatrix5x5.set_pixel(3,2,r,g,b)
    rgbmatrix5x5.set_pixel(3,3,r,g,b)
    rgbmatrix5x5.set_pixel(4,2,r,g,b)
    
#-----------------------------------------

##THIS IS WHERE THE MAGIC HAPPENS
#we're going to rip through those arrays we created as quickly as possible
#to read the pulse and flash some lights
    
#NOTE: if this loop gets too complicated, it will affect how quickly measurements can be taken
#off the ADC and you may not be able to see the shape of the heartbeat in the raw data
    
#Set counter to help identify the X range of the moving average
ma_shift = 0

#give a startup light flash
#flash_lights()


#start the main loop
for t in range(len(volt_out)):
    #grab ADC data and record the time
    value = ads1015.get_compensated_voltage(channel='in0/gnd', reference_voltage=reference)
    volt_out[t] = value
    t_record[t] = time.time()
    
    ##MOVING AVERAGE, MIN AND MAX LOOP
    #if there has already been two hearbeats, start moving that moving average
    if len(heartbeat_rec)<2:
        moving_average[t] = sum(volt_out)/(t+1)
        moving_max[t] = np.max(volt_out)
        if t == 0: moving_min[t] = volt_out[t]
        else: moving_min[t] = np.min(volt_out[0:t])
    #otherwise, just keep going
    else:
        moving_average[t]= sum(volt_out[ma_shift:t])/(t-ma_shift)
        moving_max[t] = np.max(volt_out[ma_shift:t])
        moving_min[t] = np.min(volt_out[ma_shift:t])
        ma_shift+=1


    ##DEBIAS THE DATA USING THE MOVING AVERAGE, AND CHECK IF IT'S PAST
    ##HALFWAY TO THE MOVING MAX -- IF SO, YOU'VE GOT YOURSELF A HEARTBEAT
    if volt_out[t] - moving_average[t] >= (moving_max[t] - moving_average[t])*.5:
        
        ##record the fact that we think we're in the midst of a hearbeat
        volt_high_band_pass[t] = 1
        
        ##start displaying a heart on the 5x5 LED breakout
        set_heart(255,0,0)
        rgbmatrix5x5.show()
        

        if t >= 10 and sum(volt_high_band_pass[t-9:t]) == 0:
            #if we recorded a heartbeat and its after the first few datapoints, lets record that as an official heartbeat!
            #(we need to give the moving average a chance to be realistic to avoid false positives)
            #volt_at_heartbeat is the FIRST detection of a rise that indicates a heartbeat
            heartbeat_rec.append(float(t_record[t]))
            volt_at_heartbeat.append(volt_out[t])
            moving_avg_at_heartbeat.append(moving_average[t])
            
            #we're going to flash two different lights in alternation; using whether the count is even or odd to determine
            #which goes on and which goes off
            if len(heartbeat_rec) % 2 == 0:
                ##turn on 3, wait, turn off 4
                response = requests.put("http://<bridgeIP>/api/<verylongstringoflettersfromtheCLIPAPI>/lights/<HueBulb1>/state",json=onmessage)
                time.sleep(.025)
                response = requests.put("http://<bridgeIP>/api/<verylongstringoflettersfromtheCLIPAPI>/lights/<HueBulb2>/state",json=offmessage)
                time.sleep(.025)
            else:
                ##turn on 4, wait, turn off 3
                response = requests.put("http://<bridgeIP>/api/<verylongstringoflettersfromtheCLIPAPI>/lights/<HueBulb2>/state",json=onmessage)
                time.sleep(.025)
                response = requests.put("http://<bridgeIP>/api/<verylongstringoflettersfromtheCLIPAPI>/lights/<HueBulb1>/state",json=offmessage)
                time.sleep(.025)
    
    ##we've come out of the heartbeat -- turn that 5x5 LED matrix off           
    else:
        volt_high_band_pass[t] = 0
        rgbmatrix5x5.clear()
        rgbmatrix5x5.show()
        
##END OF THE MAGIC FOR LOOP


#-----------------------------------------

##LETS CLEAN UP THE LIGHTS

##flash HUE lights to indicate we're done
#flash_lights()
#flash_lights()
        
##clear the RGB
rgbmatrix5x5.clear()
rgbmatrix5x5.show()
        

##reset the light back to initial state
#flash_lights()
#time.sleep(1)
requests.put("http://<bridgeIP>/api/<verylongstringoflettersfromtheCLIPAPI>/lights/<HueBulb1>/state",json=initialstate3)
requests.put("http://<bridgeIP>/api/<verylongstringoflettersfromtheCLIPAPI>/lights/<HueBulb2>/state",json=initialstate4)
time.sleep(1)


##Display a green square on the 5x5 LED breakout
#rgbmatrix5x5.set_all(0,255,0)
#rgbmatrix5x5.show()
#time.sleep(2)
#rgbmatrix5x5.clear()
#rgbmatrix5x5.show()

#-----------------------------------------

##PLOTTING THE RUN DATA
#this can't happen in the FOR loop as it is because it slows it down too much

##doing some initial math....
time_between_beats = np.stack(heartbeat_rec[1:len(heartbeat_rec)]) - np.stack(heartbeat_rec[0:len(heartbeat_rec)-1])
bpm_estimate = 60/time_between_beats
std_bpm = np.std(bpm_estimate)
ave_bpm = np.sum(bpm_estimate)/len(bpm_estimate)

##plotting
f, ((ax1, ax2),(ax4,ax3)) = plt.subplots(2,2)
ax1.plot(t_record - t_record[0],volt_out,label='ADC Output')
ax1.plot(t_record - t_record[0],moving_average,label='Moving Average')
ax1.plot(heartbeat_rec - t_record[0],volt_at_heartbeat,'ro',label='Heartbeat Detected')
ax1.plot(t_record - t_record[0],moving_max,'g--',label='Recent Maximum')
ax1.plot(t_record - t_record[0],moving_min,'y--',label='Recent Minimum')

ax2.plot(t_record - t_record[0],volt_high_band_pass)

ax3.plot(range(len(time_between_beats)),bpm_estimate,label='BPM Estimate')
ax3.plot(range(len(time_between_beats)),np.ones(len(time_between_beats))*ave_bpm,'g-',label='Average BPM')
ax3.plot(range(len(time_between_beats)),np.ones(len(time_between_beats))*(ave_bpm+std_bpm),'y-',label='BPM STD')
ax3.plot(range(len(time_between_beats)),np.ones(len(time_between_beats))*(ave_bpm-std_bpm),'y-')

ax4.plot(t_record - t_record[0], volt_out - moving_average,label='ADC Output')
ax4.plot(t_record - t_record[0],moving_average - moving_average,label='Moving Average')
ax4.plot(heartbeat_rec - t_record[0],volt_at_heartbeat-np.array(moving_avg_at_heartbeat),'ro',label='Heartbeat Detected')

ax1.set(title = 'Raw Voltage from ADC', ylabel = 'Volts', xlabel = 'Runtime (s)')
ax2.set(title='Boolean Heartbeat Filter Output',ylabel='0 or 1',xlabel = 'Runtime (s)')
ax3.set(title='Heart Rate',ylabel = 'Beats per Minute',xlabel = 'Runtime (s)')
ax4.set(title = 'Debiased Voltage from ADC', ylabel = 'Measured Volts - Running Average', xlabel = 'Runtime (s)')

ax1.legend()
ax3.legend()
ax4.legend()

plt.show()

#-----------------------------------------



