#!/bin/bash
for i in {1..5}
do
   sudo ovs-ofctl add-flow sh$i "in_port=1,actions=push_vlan:0x8100,set_field:1->vlan_vid,output:2" -O openflow13
   sudo ovs-ofctl add-flow sh$i in_port=2,actions=output:1
done
#for s1

sudo ovs-ofctl add-flow s1 "dl_vlan=1,actions=output:1" -O openflow13
sudo ovs-ofctl add-flow s1 "dl_vlan=2,actions=output:2" -O openflow13

for i in {1..5}
do
   sudo ovs-ofctl add-flow sh1 "dl_dst=00:00:00:00:00:05,actions=output:2" -O openflow13
done
#for s1