sleep 3
sudo -S chmod 777 /dev/ttyUSB1 | sudo -S chmod 777 /dev/ttyUSB2
sleep 3
sudo minicom -D /dev/ttyUSB2 -b 115200 -S /home/ficha/gps_cmds.txt < /home/ficha/escape.txt  
sleep 3
sudo python3 /home/ficha/arg.py -c 1 > launch_logs.txt
