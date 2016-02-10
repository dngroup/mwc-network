"""Custom topology example

Two directly connected switches plus a host for each switch:

   host --- switch --- switch --- host

Adding the 'topos' dict with a key/value pair to generate our newly defined
topology enables one to pass in '--topo=mytopo' from the command line.
"""

from mininet.topo import Topo


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
        server = self.addHost("server0")
        self.addLink(core_slow, server)
        self.addLink(core_slow, core)
        #self.addLink(core_fast, server)
        #self.addLink(core_fast, core)

        for i in range(1, 4):
            hosts["h%d" % i] = self.addHost("h%d" % i)
            switches["s%d" % i] = self.addSwitch("s%d" % i)
            self.addLink(hosts["h%d" % i], switches["s%d" % i])
            self.addLink(core, switches["s%d" % i])


topos = {'mwc': (lambda: MWCTopo())}
