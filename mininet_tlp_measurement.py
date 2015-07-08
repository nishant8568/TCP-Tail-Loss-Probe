"""

Two hosts connected through another host which is configured as router:

   host A --- host B (router) --- host C

Adding the 'topos' dict with a key/value pair to generate our newly defined
topology enables one to pass in '--topo=mytopo' from the command line.
"""

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.log import setLogLevel
from mininet.link import TCLink
from time import sleep
import argparse


# Topology
class Router_Topo(Topo):
    """ Main class which sets up the topology and helps in communication with the hosts """
    def __init__(self):
		Topo.__init__(self)
        	# Add hosts
        	hostA = self.addHost( 'hostA' )
        	hostB = self.addHost( 'hostB' )
	        hostC = self.addHost( 'hostC' )

        	# Add links
	        self.addLink( hostA, hostB, bw=bw1, delay=delay1, use_tbf=True )
        	self.addLink( hostB, hostC, bw=bw2, delay=delay2, use_tbf=True )

# Function for Starting and Testing Topology
def simpleTest():
	topo = Router_Topo()
	net = Mininet(topo, link=TCLink)
	
	hostA = net.get('hostA')
	hostB = net.get('hostB')
	hostC = net.get('hostC')

	# Setting IP Address to various interfaces of hosts
	hostA.cmd('ifconfig hostA-eth0 10.0.1.1 netmask 255.255.255.0')
	hostC.cmd('ifconfig hostC-eth0 10.0.2.1 netmask 255.255.255.0')
	hostB.cmd('ifconfig hostB-eth0 10.0.1.2 netmask 255.255.255.0')
	hostB.cmd('ifconfig hostB-eth1 10.0.2.2 netmask 255.255.255.0')

	# Setting Default Gateway
	hostA.cmd('route add default gw 10.0.1.2')
	hostC.cmd('route add default gw 10.0.2.2')
	hostB.setHostRoute(ip="10.0.1.1/24", intf="hostB-eth0")
	hostB.setHostRoute(ip="10.0.2.1/24", intf="hostB-eth1")
	
	# Enabling IP Forwarding
	hostB.cmd('sysctl net.ipv4.ip_forward=1')

	# Sending packets to netfilter queue
	hostB.cmd('iptables -A FORWARD -i hostB-eth0 -o hostB-eth1 -p tcp -j NFQUEUE --queue-num 0')
	
	#Start Network
	net.start()

	# wait for the network
	sleep(1)

	# Capturing network activities
	tcpDump(hostB)

	# wait for tcpdump to start up
	sleep(1)

	#command = 'python drop_tail.py '+payloadSize+' '+packetsToDrop+' >successLogs_1 2>errorLogs &'
	command = 'python drop_tail.py '+payloadSize+' '+packetsToDrop+'  &'
	print "command : " + command
	hostB.cmd(command)

	#hostA.cmd('ping -c2 hostC')
	# TCP Transfer
	tcpTransfer(hostA, hostC)	

	# stop capturing
	hostB.sendInt()
	tcpDumpStop(hostB)

	# kill drop_tail.py
	hostB.cmd("pkill -9 -f drop_tail.py")

	# give the network some time
	sleep(1)
	
	#Run CLI
	#CLI(net)
	#Stop Network
	net.stop()

# Function for adding and parsing the arguments passed as userinput in CLI
def parseArguments():
	""" Function for adding and parsing the arguments passed as userinput in CLI """
	parser = argparse.ArgumentParser()
	parser.add_argument("linkConfig1",
		help="Choose the configuration for  link 1 to set the desired Bandwidth & Delay : " +
		"1) fast 2) moderate 3) slow",
		type=str)
	parser.add_argument("linkConfig2",
		help="Choose the configuration for  link 2 to set the desired Bandwidth & Delay : " +
		"1) fast 2) moderate 3) slow",
		type=str)
	parser.add_argument("segmentSize", help="TCP Segment Size : 1) short 2) medium 3) long", type=str)
	parser.add_argument("logFile", help="Set Log File's Name generated from tcpdump", type=str)
	parser.add_argument("packetsToDrop",
		help="Enter the number of packets to be dropped",
		type=str)
	args = parser.parse_args()
	return args

# Function for setting the bandwidth and delay of links according to the link configuration
def setConfiguration():
	global bw1, delay1, bw2, delay2
	if "fast" == linkConfig1:
		print "### FAST connection at link 1 ###"
		bw1 = 1
		delay1 = "5ms"
	elif "moderate" == linkConfig1:
		print "### MODERATE connection at link 1 ###"
		bw1 = 0.5
		delay1 = "10ms"
	elif "slow" == linkConfig1:
		print "### SLOW connection at link 1 ###"
		bw1 = 0.1
		delay1 = "20ms"
	else:
		print "ERROR! Wrong Input! Please try again. For help please type"
		print "python mininet_tlp_measurement.py --help"
		exit(0)

	if "fast" == linkConfig2:
		print "### FAST connection at link 2 ###"
		bw2 = 1
		delay2 = "5ms"
	elif "moderate" == linkConfig2:
		print "### MODERATE connection at link 2 ###"
		bw2 = 0.5
		delay2 = "10ms"
	elif "slow" == linkConfig2:
		print "### SLOW connection at link 2 ###"
		bw2 = 0.1
		delay2 = "20ms"
	else:
		print "ERROR! Wrong Input! Please try again. For help please type"
		print "python mininet_tlp_measurement.py --help"
		exit(0)
	
# Function for setting transfer size of TCP Segments
def setSegmentSize():
	tcpSegments=(1500-18)*256
	if "short" == segment:
		print "### Short segments ###"
		tcpSegments = 64
	elif "medium" == segment:
		print "### Medium segments ###"
		tcpSegments = 128
	elif "long" == segment:
		print "### Long segments ###"
		tcpSegments = 256
	else:
		print "ERROR! Wrong Input! Please try again. For help please type"
		print "python mininet_tlp_measurement.py --help"
		exit(0)
	return tcpSegments

# Function for creating dump file (.pcap) which can be analysed in Wireshark
def tcpDump(hostB):
	LogFile = logFile + '.pcap'
	hostB.cmd('tcpdump -p -s 68 -w ' + LogFile + ' -i hostB-eth0 &')
	print "### TCP Dump generated with name " + LogFile + " ###"

def tcpDumpStop(hostB):
	hostB.cmd("killall tcpdump 2> errorDUMP.txt")

def tcpTransfer(hostA, hostC):	
	""" Function for transferring segments from Host A to Host C """
	print "### tcp transfer begins ###"
	hostA.cmd('dd if=/dev/zero count=' + str(segmentsSize) + ' bs=1448 | nc6 -X -l -p 7777 &')
	hostC.cmd('nc6 -X 10.0.1.1 7777 > /dev/null')
	#hostC.cmd('nc6 -X 10.0.1.1 7777 > target ')
	print "### Total Bytes transferred : " + str(segmentsSize) + " bytes ###"

if __name__ == '__main__':
	setLogLevel('info')
	arguments = parseArguments()

	linkConfig1 = arguments.linkConfig1
	linkConfig2 = arguments.linkConfig2
	segment = arguments.segmentSize
	logFile = arguments.logFile
	packetsToDrop = arguments.packetsToDrop

	setConfiguration()
	segmentsSize = setSegmentSize()
	payloadSize = str(segmentsSize * 1448)

	simpleTest()

