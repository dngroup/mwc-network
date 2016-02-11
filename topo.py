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

        core = self.addSwitch("core0", dpid=str(3000), protocols='OpenFlow13')
        slow = self.addSwitch("slow0", dpid=str(3001), protocols='OpenFlow13')
        fast = self.addSwitch("fast0", dpid=str(3002), protocols='OpenFlow13')
        access = self.addSwitch("access0", dpid=str(3003), protocols='OpenFlow13')

        server0 = self.addHost("server0", ip='10.0.0.2/24',cls=Server)

        self.addLink(core, slow, bw=1,port1=1,port2=1)
        self.addLink(core, fast, bw=200,port1=2,port2=1)
        self.addLink(slow, access, bw=200,port1=2,port2=1)
        self.addLink(fast, access, bw=200,port1=2,port2=2)
        self.addLink(server0, access, bw=200,port1=1,port2=3)

        for i in range(1, 64):
            hosts["h%d" % i] = self.addHost("h%d" % i, ip='10.0.0.%d/24' % (i + 3),cls=Client)

            self.addLink(core, hosts["h%d" % i], port1=100 + i, port2=1, bw=200)


topos = {'mwc': (lambda: MWCTopo())}
