"""

	http://stackoverflow.com/questions/207234/list-of-ip-addresses-hostnames-from-local-network-in-python

"""

import scapy, sys, socket, math

def long2ip(arg):
    ip = [0,0,0,0]
    for i in xrange(0, 4):
        ip[i] = arg%256
        arg /= 256
    return ".".join(map(str, ip))

def long2net(arg):
    return int(round(math.log(arg,2)))

def to_CIDR_notation(bytes_network, bytes_netmask):
    network = long2ip(bytes_network)
    netmask = long2net(bytes_netmask)
    net = "%s/%s"%(network,netmask)
    return net

def scan_and_print_neighbors(net):
    ans,unans = scapy.arping(net, timeout=1, verbose=False)
    for s,r in ans.res:
        hostname = socket.gethostbyaddr(r.psrc)
        print r.sprintf("%Ether.src%  %ARP.psrc%"),
        print " ", hostname[0]

def main():

	print "Scanning neighbourhood"

	for r in scapy.conf.route.routes:
	    # skip 127.0.0.0/8 and 0.0.0.0/0
	    if r[0]==127 or r[0]==0:
	        continue
	
	    scan_and_print_neighbors(to_CIDR_notation(r[0], r[1]))
	

if __name__ == "__main__":
	main()