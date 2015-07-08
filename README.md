# TCP Tail Loss Probe

A simple network topology with three hosts is created using Mininet. Two of these hosts act as normal host nodes while the third one is configured as a router which connects the other two hosts. The ultimate goal is to measure the Completion Time and Retransmission Time in a TCP file transfer from a host to the other host over this network. This is done in two phases-
i) TLP Enabled
ii) TLP Disabled

Completion Time is the time elapsed between first and last observed packet of the TCP connection. And by Retransmission Time, we refer to the time elapsed between dropping of first packet and beginning of the first packet retransmission.
