import dpkt
import argparse

completionTime = 0
def filterPackets(pcapReader):
    """Filters the packets of the transmission being observed"""
    pktsToObserve = []
    count = 0;
    for ts, data in pcapReader:
        ether = dpkt.ethernet.Ethernet(data)
	#print ts
        ip = ether.data
        tcp = ip.data
        if type(tcp) == dpkt.tcp.TCP:
            if tcp.sport == 7777 or tcp.dport == 7777:
		pktsToObserve.append((ts, ether))
		#print "--------------------------------------------------------------------"
		#print pktsToObserve[count]
		#print "--------------------------------------------------------------------"
		count = count + 1

    """Calculate Completion Time"""
    global completionTime
    completionTime = pktsToObserve[count-1][0] - pktsToObserve[0][0]
    #print "completionTime : " + str(completionTime)
    #print "Total packets transmitted : " + str(count)
    return pktsToObserve

def retransmissionTime(pktsToObserve):
    """ Calculate Retransmission time """
    pktsArray = []
    retransmissionCount = 0
    for ts, pkt in pktsToObserve:
        if pkt.data.len == 1500 and pkt.data.data.sport == 7777	:
            for ts1, packet in pktsArray:
		retransmissionCount = retransmissionCount + 1
                if pkt.data.data.seq == packet.data.data.seq:
		    #print "Packets retransmitted : " + str(retransmissionCount)
                    return (ts - ts1)
            pktsArray.append((ts, pkt))
    return 0

def parseArguments():
	""" Function for adding and parsing the arguments passed as userinput in CLI """
	parser = argparse.ArgumentParser()
	parser.add_argument("pcapFile",
		help="Enter the name of pcap file to be analyzed : ",
		type=str)
	args = parser.parse_args()
	return args

if __name__ == "__main__":
    arguments = parseArguments()
    f = open(arguments.pcapFile)
    pcapReader = dpkt.pcap.Reader(f)
    pktsToObserve = filterPackets(pcapReader)
    retransmission_time = retransmissionTime(pktsToObserve)
    #print "-----------------------------------------------------------------"
    print(str(completionTime) + "\t" + str(retransmission_time))
    #print "-----------------------------------------------------------------"
