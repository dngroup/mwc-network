

echo "LAUNCH RYU"
GUI_TOPO=$(locate gui_topology.py -n 1)
CONTROLLER=./controller/tm.py
#CONTROLLER=./controller/milestone1.py

xterm -fn 10x20 -e bash -c "ryu-manager --observe-links $GUI_TOPO $CONTROLLER" &

xdg-open http://localhost:8080 &
sleep 1

sudo mn -c
sudo mn --custom topo.py --topo mwc --mac --controller remote --switch ovsk,protocols=OpenFlow13 --link tc 
