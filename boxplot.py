from pylab import *
import os

def calculateData():
    """ Function to parse data for plotting box and whisker plots """
    
    fig = figure()
    ax = axes()
    hold(True)


    a = 0
    
    for linkConfig in ["fast", "moderate", "slow"]:
        for transferSize in ["short", "medium", "long"]:
            completionTime_Array = []
            retransTime_Array = []
            for packets_to_drop in [1,2,4,8]:
                plot_completionTime = [[],[]]
                plot_retransTime = [[],[]]
                for status in ["tlpDisabled", "tlpEnabled"]:
                    fileName = status + "_" + linkConfig + "_" + transferSize + "_" + str(packets_to_drop)
                    #imageFile = "OutputFiles/" + linkConfig + "_" + transferSize
                    imageFile = linkConfig + "_" + transferSize
                    f = open("OutputFiles/" + fileName)
                    readValue = f.read()
                    f.close()
                    """
                    print "----------------BEGIN-----------------------------"
                    print readValue
                    print "---------------------------------------------"
                    """
                    readValue = readValue.split("\n")
                    readValue.pop()
                    """
                    print "---------------------------------------------"
                    print readValue
                    print "---------------------------------------------"
                    print "-----------------END----------------------------"
                    """
                    for i in range(len(readValue)):
                        readValue[i] = readValue[i].split("\t")
                        if status == "tlpDisabled":
                            plot_completionTime[0].append(float(readValue[i][0]))
                            plot_retransTime[0].append(float(readValue[i][1]))
                        elif status == "tlpEnabled":
                            plot_completionTime[1].append(float(readValue[i][0]))
                            plot_retransTime[1].append(float(readValue[i][1]))
                            
                completionTime_Array.append(plot_completionTime)
                retransTime_Array.append(plot_retransTime)

                if a == 0:
                    """
                    print "=============================================================================="
                    print completionTime_Array
                    print "=============================================================================="
                    """
                    a = 1

            generateBoxPlot(completionTime_Array, "completionTime", imageFile, fig, ax)
            generateBoxPlot(retransTime_Array, "retransTime", imageFile, fig, ax)

def generateBoxPlot(timeArray, timeType, imageFile, fig, ax):
    """ Function to plot box and whisker plots """
    ax = axes()
    ymin = 9999
    ymax = 0

    ax.set_xlabel('Tail Loss Length')
    ax.set_ylabel('Elapsed Time')
    
    for time in timeArray:
        tempMin = min(time)
        tempMax = max(time)
        """
        print "------------------------------------"
        print tempMin
        print "------------------------------------"
        print tempMax
        print "------------------------------------"
        """
        tempMin = min(tempMin)
        tempMax = max(tempMax)
        """
        print "------------------------------------"
        print tempMin
        print "------------------------------------"
        print tempMax
        print "------------------------------------"
        """
        ymin = min(tempMin, ymin)
        ymax = max(tempMax, ymax)
        
    ymin = ymin - 0.15*ymin
    ymax = ymax + 0.15*ymin

    #print "ymin : " + str(ymin)

    boxPosition = 1
    length = len(timeArray)
    for i in range(0,length):
        bp = boxplot(timeArray[i], notch = False, vert = True, whis = 2, positions = [boxPosition, boxPosition+2], widths = 0.8)
        setBoxColors(bp)
        boxPosition = boxPosition + 5
    ylim(ymin, ymax)
    xlim(0, 20)
    ax.set_xticklabels(['1', '2', '4', '8'])
    #ax.set_xticks([1, 4.5, 7.5, 10.5])
    ax.set_xticks([2, 7, 12, 17])
    
    #Legend
    l1, = plot ([1,1], 'b-', label='TLP Disabled')
    l2, = plot ([1,1], 'r-', label='TLP Enabled')
    legend(framealpha=0.5)

    #print imageFile
    if not os.path.exists("OutputFiles/plots"):
        os.makedirs("OutputFiles/plots") # for Windows
        #os.mkdir("OutputFiles/plots") # for linux
    imageFile = "OutputFiles/plots/" + imageFile + "_" + timeType + ".png"
    print imageFile
    savefig(imageFile)
    fig.clear()

# function for setting the colors of the box plots pairs
def setBoxColors(bp):
    setp(bp['boxes'][0], color='blue')
    setp(bp['caps'][0], color='blue')
    setp(bp['caps'][1], color='blue')
    setp(bp['whiskers'][0], color='blue')
    setp(bp['whiskers'][1], color='blue')
    setp(bp['fliers'][0], color='blue')
    setp(bp['fliers'][1], color='blue')
    setp(bp['medians'][0], color='blue')

    setp(bp['boxes'][1], color='red')
    setp(bp['caps'][2], color='red')
    setp(bp['caps'][3], color='red')
    setp(bp['whiskers'][2], color='red')
    setp(bp['whiskers'][3], color='red')
    setp(bp['fliers'][2], color='red')
    setp(bp['fliers'][3], color='red')
    setp(bp['medians'][1], color='red')

if __name__ == "__main__":
    calculateData()
