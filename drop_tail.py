#!/usr/bin/python

""" Implementing tail loss """


import sys
import nfqueue

from socket import AF_INET

sys.path.append('python')
sys.path.append('build/python')
sys.path.append('dpkt-1.6')

import argparse
count = 0
lastPacketFlag = False


def cb(payload):
	""" Function for creating tail loss """
	global remainingDropCount
    	global lastPacketFlag
	global count
	print " "	
	count = count + 1
	print "count : " + str(count)
	if count > 1 and count <= int(segmentSize) + int(packetsToDrop) + 1:
		print "payload.get_length() : " + str(payload.get_length())
        	if remainingDropCount > 0:
            		if count > int(segmentSize) -int(packetsToDrop) + 1:
                		remainingDropCount = remainingDropCount - 1
			#	if remainingDropCount == 0:
			#		lastPacketFlag = True
				print "DROPPED..!!"
				print "Drop packets remaining : " + str(remainingDropCount)
                		payload.set_verdict(nfqueue.NF_DROP)
            		else:
				print "Drop packets remaining : " + str(remainingDropCount) + " .. ACCEPT....!!!!"
                		payload.set_verdict(nfqueue.NF_ACCEPT)
        	else:
			print "All drops packets dropped >> Retransmission"
            		payload.set_verdict(nfqueue.NF_ACCEPT)
    	elif lastPacketFlag is True:
		print "payload.get_length() : " + str(payload.get_length())
        	lastPacketFlag = False
		print "Tail Drop"
        	payload.set_verdict(nfqueue.NF_DROP)
    	else:
		print "payload.get_length() : " + str(payload.get_length())
		print "ELSE....!!!!"
        	payload.set_verdict(nfqueue.NF_ACCEPT)
	sys.stdout.flush()
	return 1


def parseArguments():
	""" Function for adding and parsing the arguments passed as userinput in CLI """
	print "!!!!!!!!!!!!!!!!!!!!! drop_tail.py !!!!!!!!!!!!!!!!!!!!!!!!"
	parser = argparse.ArgumentParser()
	parser.add_argument("payloadSize",
		help="Enter payload size : " +
		"1) short 2) medium 3) long",
		type=str)
	parser.add_argument("packetsToDrop",
		help="Enter the number of packets to be dropped",
		type=str)
	args = parser.parse_args()
	return args

def tailDrop(segmentSize, packetsToDrop):
		q = nfqueue.queue()

		print "setting callback"
		q.set_callback(cb)

		print "open"
		q.fast_open(0, AF_INET)

		q.set_queue_maxlen(50000)

		print "trying to run"
		try:
			q.try_run()
		except KeyboardInterrupt, e:
			print "interrupted"+str(e)

		print "%d packets handled" % count

		print "unbind"
		q.unbind(AF_INET)

		print "close"
		q.close()

if __name__ == '__main__':
	arguments = parseArguments()
	payloadSize = arguments.payloadSize
	segmentSize = int(payloadSize)/1448
	packetsToDrop = arguments.packetsToDrop
	remainingDropCount = int(packetsToDrop)
	tailDrop(segmentSize, packetsToDrop)
