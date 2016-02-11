from operator import attrgetter

from ryu.app import simple_switch_13
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib import hub

import time

import milestone1
import threading
import json
from SimpleXMLRPCServer import SimpleXMLRPCServer






JSON_MAX = 30

class SimpleMonitor(simple_switch_13.SimpleSwitch13):

    def __init__(self, *args, **kwargs):
        super(SimpleMonitor, self).__init__(*args, **kwargs)
        self.datapaths = {}
        self.totals = {}
        self.slices = {}
        #self.bwstats = BandwidthStats(self.topo)
        self.monitor_thread = hub.spawn(self._monitor)

        self.rpcStart()

    def rpcStart(self):
        self.server = SimpleXMLRPCServer(("localhost", 8000), logRequests=False)
        self.server.register_instance(self)
        self.server.register_function(self.rpcLoadPolicy, "load")
        # self.server.register_function(self.rpcLoadPolicy, "load")
        # self.server.register_function(self.rpcCurrentPolicy, "current")
        thread = threading.Thread(target=self.server.serve_forever)
        thread.start()
        self.logger.info("starting rpc server")

    def rpcLoadPolicy(self, nbHost, nbSlow):
        str = "rpc request load {0} host with  {1} slow (befort {2} host with  {3} slow ))".format(nbHost, nbSlow, milestone1.nbHost, milestone1.nbSlow)
        self.logger.info(str)
        milestone1.nbHost=nbHost
        milestone1.nbSlow=nbSlow
        return (True, str)





    @set_ev_cls(ofp_event.EventOFPStateChange,
                [MAIN_DISPATCHER, DEAD_DISPATCHER])
    def _state_change_handler(self, ev):
        datapath = ev.datapath
        if ev.state == MAIN_DISPATCHER:
            if not datapath.id in self.datapaths:
                self.logger.debug('register datapath: %016x', datapath.id)
                self.datapaths[datapath.id] = datapath
        elif ev.state == DEAD_DISPATCHER:
            if datapath.id in self.datapaths:
                self.logger.debug('unregister datapath: %016x', datapath.id)
                del self.datapaths[datapath.id]

    def _monitor(self):
        while True:
            for dp in self.datapaths.values():
                self._request_stats(dp)
            hub.sleep(10)

    def _request_stats(self, datapath):
        self.logger.debug('send stats request: %016x', datapath.id)
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        req = parser.OFPFlowStatsRequest(datapath)
        datapath.send_msg(req)

        req = parser.OFPPortStatsRequest(datapath, 0, ofproto.OFPP_ANY)
        datapath.send_msg(req)

    def addHostBwStat(self,serverName, rxbytes, txbytes):
        host_rx = txbytes
        host_tx = rxbytes

        if serverName not in self.totals:
            self.totals[serverName] = []
            self.totals[serverName].append({ 'in' : 0,
                                       'out' : 0
                                   })
            self.slices[serverName] = []

        last = self.totals[serverName][-1]
        rxslice = rxbytes - last['in']
        txslice = txbytes - last['out']

        self.slices[serverName].append({ 'in': rxslice,'out': txslice,'time':time.time() })
        self.totals[serverName].append({ 'in': rxbytes,'out': txbytes,'time':time.time()})


        if len(self.totals[serverName]) > JSON_MAX:
                start = len(self.totals[serverName]) - JSON_MAX
                self.totals[serverName] = self.totals[serverName][start:]
                self.slices[serverName] = self.slices[serverName][start:]

    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def _flow_stats_reply_handler(self, ev):
        body = ev.msg.body

        self.logger.info('datapath         '
                         'in-port  eth-dst           '
                         'out-port packets  bytes')
        self.logger.info('---------------- '
                         '-------- ----------------- '
                         '-------- -------- --------')
        for stat in sorted([flow for flow in body if flow.priority == 1],
                           key=lambda flow: (flow.match['in_port'],
                                             flow.match['eth_dst'])):
            self.logger.info('%016x %8x %17s %8x %8d %8d',
                             ev.msg.datapath.id,
                             stat.match['in_port'], stat.match['eth_dst'],
                             stat.instructions[0].actions[0].port,
                             stat.packet_count, stat.byte_count)

    @set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
    def _port_stats_reply_handler(self, ev):
        body = ev.msg.body

        self.logger.info('datapath         port     '
                         'rx-pkts  rx-bytes rx-error '
                         'tx-pkts  tx-bytes tx-error')
        self.logger.info('---------------- -------- '
                         '-------- -------- -------- '
                         '-------- -------- --------')
        for stat in sorted(body, key=attrgetter('port_no')):

            self.logger.info('%016x %8x %8d %8d %8d %8d %8d %8d', 
                             ev.msg.datapath.id, stat.port_no,
                             stat.rx_packets, stat.rx_bytes, stat.rx_errors,
                             stat.tx_packets, stat.tx_bytes, stat.tx_errors)

            if (ev.msg.datapath.id==4096):
                self.logger.info("equal 1000 (slow)")
                if (stat.port_no==1):
                    self.logger.info("equal 1")
                    self.addHostBwStat("slow",stat.rx_bytes,stat.tx_bytes)
                    b = json.dumps(self.slices["slow"])
                    self.toJsonFile(b,"slow.js")

            if (ev.msg.datapath.id==8192):
                self.logger.info("equal 2000 (fast)")
                if (stat.port_no==1):
                    self.logger.info("equal 1")
                    self.addHostBwStat("fast",stat.rx_bytes,stat.tx_bytes)
                    b = json.dumps(self.slices["fast"])
                    self.toJsonFile(b,"fast.js")
            if (ev.msg.datapath.id==12288):
                self.logger.info("equal 3000 (kk)")
                if (stat.port_no==1):
                    self.logger.info("equal 1")
                    self.addHostBwStat("autre",stat.rx_bytes,stat.tx_bytes)
                    b = json.dumps(self.slices["autre"])
                    self.toJsonFile(b,"autre.js")


    def toJsonFile(self, b,nameFile):
        print b
        with open(nameFile, "w") as text_file:
            text_file.write(str(b))


