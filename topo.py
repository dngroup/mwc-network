"""Custom topology example

Two directly connected switches plus a host for each switch:

   host --- switch --- switch --- host

Adding the 'topos' dict with a key/value pair to generate our newly defined
topology enables one to pass in '--topo=mytopo' from the command line.
"""

from mininet.topo import Topo
from mininet.node import Host
from mininet.link import TCLink


class Server( Host ):
    def config( self, **params ):
        super( Host, self).config( **params )
        print (params)
        self.cmd( 'while true; do  dd if=/dev/zero  count=$((1024+$RANDOM)) bs=1024 |nc -l 8080 ; done &' )
class Client( Host ):
    def config( self , **params):
        super( Host, self).config( **params )
        print (params)
        self.cmd( 'while true; do curl http://10.0.0.1:8080/ >/dev/null 2>/dev/null && sleep 1  ; done &' )

class MWCTopo(Topo):
    "Simple topology example."

    def __init__(self):
        "Create custom topo."

        # Initialize topology
        Topo.__init__(self)
        hosts = {}
        switches = {}
        core_slow = self.addSwitch("fast0",dpid='1000')
        core_fast = self.addSwitch("slow0",dpid='2000')
        core = self.addSwitch("core0",dpid='3000')
        server = self.addHost("cdn0",cls=Server)
        self.addLink(core_slow, server,port1=1,port2=1, bw=100, cls=TCLink)
        self.addLink(core_slow, core, bw=10, cls=TCLink )
        #self.addLink(core_fast, server,port1=1,port2=2)
        #self.addLink(core_fast, core)

        for i in range(1, 4):
            hosts["h%d" % i] = self.addHost("h%d" % i,cls=Client)
            switches["s%d" % i] = self.addSwitch("s%d" % i)
            self.addLink(switches["s%d" % i],hosts["h%d" % i], bw=1, cls=TCLink )
            self.addLink(switches["s%d" % i],core, cls=TCLink, bw=1)


topos = {'mwc': (lambda: MWCTopo())}


