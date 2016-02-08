#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from time import sleep
from mininet.cli import CLI




# class MWC(Topo):
#     def __init__(self):
#         Topo.__init__(self)
#         host = {}
#         switch = {}
#
#         # TODO: add the description of the topology here
#
#         name = 's101'
#         switch[name] = self.addSwitch(name)
#         # while true; do  dd if=/dev/zero  count=$((1024+$RANDOM)) bs=1024 |nc -l 8080 ; done;
#         for i in range(1, 12):
#             name = 'h' + str(i)
#             host[name] = self.addHost(name, mac= '00:00:00:00:00:'+'{0:02x}'.format(i))
#             self.addLink(switch["s101"], host[name], bw=100)
#
#         # for i in range(1, 1):
#         #     name = 's10' + str(i)
#         #     switch[name] = self.addSwitch(name)
#
#         # self.addLink(switch["s101"], host["h6"], bw=100)
#
#
# topos = {'mwc': (lambda: MWC())}


class SingleSwitchTopo(Topo):
    "Single switch connected to n hosts."
    def build(self, n=2):
        host = {}
        switch = self.addSwitch('s1')
        for i in range(1,n+1):
            name = 'h' + str(i)
            host[name] = self.addHost(name, mac= '00:00:00:00:00:'+'{0:02x}'.format(i))
            self.addLink(switch, host[name], bw=10)

        name = 'cdn'
        host[name] = self.addHost(name, mac= '00:00:00:01:00:00')
        self.addLink(switch, host[name], bw=100)
        name = 'vcdn'
        host[name] = self.addHost(name, mac= '00:00:00:02:00:00')
        self.addLink(switch, host[name], bw=1000)

        # for h in range(n):
        #     # Each host gets 50%/n of system CPU
        #     host = self.addHost('h%s' % (h + 1),
        #        cpu=.5/n)
        #     # 10 Mbps, 5ms delay, 10% loss, 1000 packet queue
        #     self.addLink(host, switch,
        #        bw=10, delay='5ms', loss=10, max_queue_size=1000, use_htb=True)

def mwc():
    "Create network and run simple performance test"
    topo = SingleSwitchTopo(n=6)

    net = Mininet(topo=topo,controller=None ,link=TCLink)
    net.start()
    # print "Dumping host connections"
    # dumpNodeConnections(net.hosts)
    # print "Testing network connectivity"
    # net.pingAll()
    # print "Testing bandwidth between h1 and h4"
    # h1, h4 = net.get('h1', 'h4')
    # net.iperf((h1, h4))
    print "start cdn"
    cdn = net.get('cdn')
    whilecdn = cdn.cmd('while true; do  dd if=/dev/zero  count=$((1024+$RANDOM)) bs=1024 |nc -l 8080 ; done &')

    print "start vcdn"
    vcdn = net.get('vcdn')
    whilevcdn =vcdn.cmd('while true; do  dd if=/dev/zero  count=$((1024+$RANDOM)) bs=1024 |nc -l 8080 ; done &')

    hosts = net.hosts

    whileh={}
    for h in hosts:
        if not (h.name in ("vcdn", "cdn")):
            whileh[h] =h.cmd('while true; do curl -http://'+cdn.IP() +':8080/ >/dev/null 2>/dev/null && sleep 1  ; done &')



    sleep(10)
    CLI(net)
    # vcdn.cmd('kill %while')
    # cdn.cmd('kill %while')
    for h in hosts:
        h.cmd('kill %while')


    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    mwc()