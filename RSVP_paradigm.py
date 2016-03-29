from psychopy import visual,core,event # import some libraries from PsychoPy
from serial import*
import io, os, glob 
import matplotlib.pyplot as plt
from pylab import *
import time
import socket
import optparse, sys, os, fnmatch, traceback

STUDYPATH = "studies"
parser = optparse.OptionParser()
parser.add_option("-s","--studypath", dest="studypath", default=STUDYPATH,
                  help="The directory in which to look for .cfg files, media, .prc files etc. for a particular study.")
(opts,args) = parser.parse_args()



global marker_log
marker_log = None

global lsl_backend
lsl_backend = None

global river_backend
river_backend = None

def init_markers(lsl,logfile,datariver):
    """ Initialize the marker protocols to use. """

    if lsl:
        try:
            global lsl_backend
            import pylsl.pylsl as pylsl
            info = pylsl.stream_info("Pystim-Markers","Markers",1,0,pylsl.cf_string,"Pystim-markers-" + socket.gethostname() + time.asctime())
            lsl_backend = pylsl.stream_outlet(info)
            lsl_backend.pylsl = pylsl
            print "The lab streaming layer is ready for sending markers."
        except:
            print "Error initializing the lab streaming layer backend. You will not be able to send and record event markers via LSL."

    if logfile:
        try:
            # find a new slot for the logfiles
            for k in xrange(10000):
                fname = 'logs/markerlog-' + str(k) + '.log'
                if not os.path.exists(fname):
                    global marker_log
                    marker_log = open(fname,'w')
                    break
            print "A marker logfile has been prepared for logging."
        except:
            print "Error initializing the marker logging. Your event markers will not be logged into a file."

    if datariver:
        try:
            global river_backend
            import framework.eventmarkers.datariver_backend
            river_backend = framework.eventmarkers.datariver_backend
            river_backend.send_marker(int(999))
            print "DataRiver has been loaded successfully for sending markers."
        except:
            print "Error initializing the DataRiver backend. You will not be able to send and record event markers via DataRiver."


def send_marker(markercode):
    """Global marker sending / logging function."""

    global lsl_backend
    if lsl_backend is not None:
        lsl_backend.push_sample(lsl_backend.pylsl.vectorstr([str(markercode)]), lsl_backend.pylsl.local_clock(), True)

    global marker_log
    if marker_log is not None:
        marker_log.write(repr(time.time()) + '\t ' + str(markercode) + '\n')

    global river_backend
    if river_backend is not None:
        river_backend.send_marker(int(markercode))

# read data from text file
def ReadData (f):
    data0=[]
    marker=[]
    data=[]
    for columns in (raw.strip().split() for raw in f):
        data0.append(columns[0])
        marker.append(columns[1])
    data=data0
    data.remove(data[0])
    marker.remove(marker[0])
    num=len(data)
    f.close()
    return data,marker,num


# def trigger(marker):
#    port=parallel.ParallelPort(address=0x0378)
#    trigger_port=port.setData( int("00000000",2) ),port.setData( int("00000001",2) )#pin2 low      pin2 high
#    return trigger_port


def win_display():
    win=visual.Window([1000,800])
    return win

def RSVP_paradigm(data,ti,win,marker): 
# data is text file, ti is time interval between each image
    result=[] # define output



    message = visual.TextStim(win, text='Loading images.....')
    message.draw()
    win.update()

    image_list=[] # preload image list
    image_label=[]
    
    # preload images
    for i in range(0,len(data)):
        image_list.append(visual.ImageStim(win,data[i],size=(2,2)))
        if i % 2 == 0:
            image_label.append(visual.ImageStim(win,'black.jpg',size=(0.5,0.5),pos=(-1, -1)))
        else:
            image_label.append(visual.ImageStim(win,'white.png',size=(0.5,0.5),pos=(-1, -1)))


    # -----------------------------------------fixation----------------------------
    message1 = visual.TextStim(win, text='Please press space button if you are ready')
    message1.draw()
    win.update()
    event.waitKeys(['space'])
    fixation = visual.ShapeStim(win,
    vertices=((0, -0.2), (0, 0.2), (0,0), (-0.2,0), (0.2, 0)),
    lineWidth=5,
    closeShape=False,
    lineColor='white')
    fixation.draw()
    win.update()
    core.wait(2.0)
    onsetTime=core.getTime()

    #----------------------------------------define timing------------------------
    image_time=[] # interval between two stimuli
    RT=[]         # subjective reaction time and the choice of stimuli target
    t_remaining=[] # time of code excuating



    # ----------------------------------display stimuli----------------------
    for i in range(0,len(data)):
        t_start=core.getTime()
        image_time.append(core.getTime())
        image=image_list[i],image_label[i]
        send_marker(1)
        image[0].draw()
        image[1].draw()
        win.flip()
        t_elipse=core.getTime()
        t_remaining.append(t_elipse-t_start)
        core.wait(ti-t_remaining[i])

    # store output
    result.append(image_time)
    result.append(t_remaining)
    return result, win

# ----------------------------check the actual time interval------------------------------
def plot_ti(ti):
    plt.hist(ti)
    plt.title('Histogram of actrual time interval')
    plt.xlabel('Time interval (s)')
    plt.ylabel('Number')
    plt.show()

def calculate_ti(image_time):
    ti=[]     # actual time interval
    for i in range(1,len(image_time)):
        ti.append(image_time[i]-image_time[i-1])
    return ti
#------------------------------------------------------------------------------------------

def main():
    init_markers(True,True,False)


    # trial 1
    # os.chdir('/Users/Villa/Dropbox/python/labstreaminglayer-master/mycode/studies/trial1')
    # f=open('/Users/Villa/Dropbox/python/labstreaminglayer-master/mycode/studies/trial1/RSVP.txt','rb')

    os.chdir('C:\\Users\\Villa_000\\Dropbox\\python\\labstreaminglayer-master\\mycode\\studies\\trial1')
    f=open('C:\\Users\\villa_000\\Dropbox\\python\\labstreaminglayer-master\\mycode\\studies\\trial1\\RSVP.txt','rb')
    data,marker,num=ReadData(f)
    win=win_display()

    result,win=RSVP_paradigm(data,0.2,win,marker)
    # ti=calculate_ti(result[0])
    # plot_ti(ti)
    # print data, marker, result[0]  # 1 is target, 0 is non-target
    print num

    # trial 2
    # os.chdir('C:\\Users\\Villa_000\\Dropbox\\python\\labstreaminglayer-master\\mycode\\studies\\trial2')
    # f=open('C:\\Users\\villa_000\\Dropbox\\python\\labstreaminglayer-master\\mycode\\studies\\trial2\\RSVP.txt','rb')
    # data,marker,num=ReadData(f)
    # win=win_display()
    # result,win=RSVP_paradigm(data,0.2,win,marker)


    # trial 3
    # os.chdir('C:\\Users\\Villa_000\\Dropbox\\python\\labstreaminglayer-master\\mycode\\studies\\trial3')
    # f=open('C:\\Users\\villa_000\\Dropbox\\python\\labstreaminglayer-master\\mycode\\studies\\trial3\\RSVP.txt','rb')
    # data,marker,num=ReadData(f)
    # result,win=RSVP_paradigm(data,0.2,win,marker)









    win.close()
    
    
if __name__=='__main__':
    main()



