# Truck-Jetson
***********************

Change Truck token in post_office.py for new trucks

***********************




**Jetson Xavier setup** :

For this task you would need a Host computer with Ubuntu 20 installed.

Setup the xavier on SSD directly using the SDKManager :

First remove the jetson xavier from its box and place the SSD on the bottom side of the board

This tutorial contains most of the infos for insallation (with some modifications): 

https://www.stereolabs.com/blog/getting-started-with-jetson-xavier-nx/

**Modifications to perform**

**Run NVIDIA SDK Manager** :

Change the target operating system on step 1 of instalation to Jetpack 4.6.1

A pop up window will appear to enter a username / password, set the mode to Devkit on manual setup,

change the initalization type from oem to runtime, change the storage from SDCard to nvme for the SSD.

After insallation another popup window will appear to install the OS softwares which requires either USB or SSH,

You could try with USB but if that doesn't work :

- Plug the board on a screen with a keyboard complete the installation

- After the board desktop setup is completed, open a terminal on the jetson, connect the board through wifi or ethernet on the same network as your computer, use ifconfig to grab the @ip : 

```
ifconfig eth0 (for ethernet) or ifconfig wlan0 (for wifi)
```

Now back to the SDK manager, insert the ip@ to ssh so it could install what's needed



#Now the installation is completed remove the PINs #9 and #10 that were connected to force the recovery mode for installation (on the first step) and start the board

#Using the Ip address from your computer connect the jetson

```
ssh ficha@IP
```

#Or just run the commands on the jetson terminal

#in terminal

```
sudo apt update

sudo apt upgrade

sudo apt install python3-pip

python3 -m pip install --upgrade pip

sudo apt install nano
```

**GPS / 4G**

Setup the Jetson Hat for 4G :

https://github.com/phillipdavidstearns/simcom_wwan-setup



Finally :) install remote.it :

```
sudo wget https://downloads.remote.it/remoteit/v4.14.1/remoteit-4.14.1.arm64.deb

sudo apt install remoteit-4.14.1.arm64.deb
```


*********************************************

To run the code on the jetsons

Git clone this repo, copy its content to the default directory of ficha :

git clone ...

```
cd Truck-Jetson folder

cp -r ./* /home/ficha/
```

To run the script as a service :

```
cd /home/ficha 
```

Copy 

```
sudo cp run_service.service /lib/systemd/system/ 

sudo chmod 777 ./run.sh

sudo chmod +x start_service.sh
```

**Change the truck ID in post_office.py**

```
nano post_office.py
```

and do the changes.

Start it using 

```
sudo ./start_service.sh
```

To check the status of the service run :

```
sudo systemctl status run_service.service
```


*********************************************

##################################################### 


Run the code : 

Main code in arg.py

flags are as follow :

-v for the videos folder path

-o for output directory

-f the video format the default value is .h264

-qr 1 if you want use the qr code 0 if you want use the standard one.

-c 1 to use camera, default value is 0

**************************

Must have : 

directory as /home/ficha/data 


FAQ :


When inserting new sim connect to a screen to be able to enter the PIN code.




**********************************************************************************

***Jetson nano setup and extraction***

Jetson nano setup :

#First :

#Download the image of the OS that support the jetson nano hardware :

https://developer.nvidia.com/jetson-nano-sd-card-image


#boot it on an SD Card using (on windows, you can look for alternatives on other platforms) :

https://win32-disk-imager.en.uptodown.com/windows


#after the installation of the operating system and connecting to the internet via an ethernet cable:

#in terminal
```

sudo apt update

sudo apt upgrade

sudo apt install python3-pip

python3 -m pip install --upgrade pip

sudo apt install nano

```

Incremente swap size : 

https://www.jetsonhacks.com/2019/11/28/jetson-nano-even-more-swap/


OpenCV installation instructions can be found in the [installation file](Opencv_jetson.setup.txt)

```

python3 -m pip install progress



nano ~/.bashrc
```

add at the bottom of the file the following line :

export OPENBLAS_CORETYPE=ARMV8

Setup the PI HQ 2018 v1 camera on the jeton nano (IMX 477)

Follow the commands on this website with : sudo /opt/nvidia/jetson-io/jetson-io.py

  https://www.arducam.com/docs/camera-for-jetson-nano/jetson-nano-xavier-nx-configuring-the-csi-connector-w-jetson-io/
  set the mode to dual IMX477 (the driver for the camera, the camera should be connected)

Install the gps modules [this way](GPS)

Final step is to make the script runnable after the os starts using the [following commands](linux_tricks.setup.txt)

****************************************************

Setup the Jetson Hat for 4G :

https://github.com/phillipdavidstearns/simcom_wwan-setup

Finally :) install remote.it :

```
sudo wget https://downloads.remote.it/remoteit/v4.14.1/remoteit-4.14.1.arm64.deb

sudo apt install remoteit-4.14.1.arm64.deb
```

**********************************************************************************

TIPS :

# Jetson_doc

If you want run the computer vision algorithm only locally on videos check qr_extraction.py for instructions

*********************************

#install nano, text editor

```
sudo apt get install nano
```

*********************************

#Install python3.8 and pip

*********************************

```
sudo apt install python3.8-dev

sudo apt install python3-pip
```

*********************************

#Make python3.8 the default

```
sudo rm /usr/bin/python3

sudo ln -s /usr/bin/python3.8 /usr/bin/python3
```

*********************************

#Upgrade pip

```
sudo python3 -m pip install --upgrade pip
```

*********************************

#Uninstall old numpy

```
sudo apt purge numpy

sudo python3 -m pip install numpy
```

*********************************

#Installing opencv with python 3.8


Make python3.8 as your default python3 and then install opencv as mentionned earlier

*********************************

#Download our custom pytorch 

https://drive.google.com/file/d/1pJYv2rzuf8qe33ZsodwCRf4SuORZTknT/view?usp=sharing

you'll get a file named torch-1.7.0a0-cp38-cp38-linux_aarch64

#Install pytorch 1.7 with cuda support ]

```
python3 -m pip install torch-1.7.0a0-cp38-cp38-linux_aarch64
```

#torchvision on the other hand is TO DO, in the YOLOv5 code I had to recode some torchvision functions to avoid calling them

```
sudo apt-get install libopenblas-base libopenmpi-dev 
```

*********************************

#Possibly needed command with torch & cuda :

```
sudo ln -s /usr/lib/aarch64-linux-gnu/libcublas.so /usr/local/cuda/lib64/libcublas.so

export LD_PRELOAD=/usr/lib/aarch64-linux-gnu/libgomp.so.1
```

*********************************************

#to install pycuda : 

```
export PATH=/usr/local/cuda/bin:${PATH}
export LD_LIBRARY_PATH=/usr/local/cuda/lib64:${LD_LIBRARY_PATH}

python3 -m pip install pycuda --user
```

*********************************************

To install libomp5

```
apt-get install libomp5
```

*********************************************

#After installing the OS, the SD card might not be detected on the host computer, you could reset it using diskpart on windows by removing the partition of the SD & recreating it :

https://www.techtarget.com/searchwindowsserver/tip/Using-Diskpart-to-create-extend-or-delete-a-disk-partition


*********************************************

Useful commands to run the SIM7600 (the HAT) modem using minicom:

https://m2msupport.net/m2msupport/atcfun-set-phone-functionality/


## Useful commands to debug

* Remember to connect as "root" user with `sudo su`

* If you need to use the camera, you need to disable the service running at each reboot:
```
systemctl stop run_service.service
systemctl disable run_service.service
sudo reboot
```
Don't forget to reenable it with `./start_service.sh` 

* If you need to test sending a new collection to the server, and a collection has already been created today, you just have to delete the file `data/connection_token.txt`, as only one collection is created per day.










