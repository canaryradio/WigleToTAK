<img width="279" alt="Screenshot 2024-03-11 at 12 13 25 AM" src="https://github.com/SignalMedic/WigleToTAK/assets/127666889/1b59d52b-244d-4371-b383-60b5aee7e913">

<br>Basic demonstration of Wigle To TAK https://www.youtube.com/watch?v=msWT8neQEdY<br>

<br>Cemaxecuter has done a much more comprehensive, but easy to follow, video illustrating setup and use of Wigle To TAK https://www.youtube.com/watch?v=FBVEbkGHQsE&t=29s<br>

If you find issues please make a ticket using the GitHub Issue tracker for the repo.<br>

If you are running this as part of a **post collection** activity with **more than ~250 devices** in the wiglecsv file you may experience some of the packets falling off depending on your network rules. If this is a limitation in your mind please create a ticket in the Issues section of the repo.<br>

A Python application with html dashboard designed to help use your WigleCSV creating service with TAK products.
For use in a non-production environment.
Defaults are set to be run on the same server as your WigleCSV device service, however other network configurations should work. This is built with WiFi in mind, however other things in a wigleCSV format will display.

Tested using Python 3, a Chrome browser, Kismet, ATAK, and iTAK (the points are different, but it works).
# Quick Start
Step 1:
Clone or download WigleToTAK to your computer
`git clone https://github.com/canaryradio/WigleToTAK`

Step 2:
Initialize or start your WigleCSV creating service<br> ``` $ sudo kismet -c {YOUR WIFI INTERFACE} --override wardrive ```<br> Another option is to use Wigle to TAK for post collection processing.

Step 3:
Create python virtualenv OR install dependencies globally:
```
# Optional, install venv
python3 -m virtualenv .venv
# ensure .venv python is being used, not system
which python3
# prints: $ > ../WigleToTAK/.venv/bin/python3

# if virtualenv is active, requirements will be installed there
# if virtualenv is not installed, requirements will be install system wide - not recommended
# install requirements
pip install -r requirements.txt
```


Step 4:
Start server
```
$ python3 WigleToTAK.py
```

Step 4:
Open a browser and navigate to http://<YOUR_IP:8000


# Instructions
The Wigle to TAK application operates independent of your software or service that creates the WigleCSV file. Wigle to TAK depends on creating a file ending with .wiglecsv in the standard format.<br>

Using Kismet as an example the steps to setup Kismet are:<br>
Edit your kismet.conf file<br>
-Setup GPS for Kismet<br>
-(optional) Setup your source (or use -c flag in your start command)<br>
Edit your kismet_logging.conf file<br>
-I would change your log_prefix to somewhere that does not require root/sudo priveleges. I use /home/{my_username}<br>

You could do some other Kismet modifications, but location is mandatory. I highly recommend doing a test and making sure you have a configuration that results in devices populating in the .wiglecsv file. Once you think you are good you could $ cat <your_file.wiglecsv> and make sure it lists out devices.<br>

  
<h2>TAK Server</h2>  
TAK Server IP is the IP address of your TAK Server. The port should be whichever port you have designated for input of these packets. The Broadcast button is a toggle to enable (default) or disable the multicast to 239.2.3.1:6969.<br>

<img width="506" alt="Screenshot 2024-03-10 at 11 53 15 PM" src="https://github.com/SignalMedic/WigleToTAK/assets/127666889/11e3e3eb-0ebd-40e2-9853-b7c571e992bc">


<h2>Wigle CSV Selection</h2>
Wigle CSV logs directory should be your absolute path to wherever your .wiglecsv files are going to. In Kismet you can set this in the config files. I do not recommend sending to a directory owned by root or requiring sudo priveleges for this application. /home/{YOUR USER} for example is a easy choice. When you click "submit" all of the files ending with .wiglecsv will show in the drop down list. Latest will be at the top. When you click "start" the file will be read and all packets in the file will be parsed, converted to CoT XML, and sent to whatever endpoints you have enabled.<br> Analysis Mode is the selection between Real-Time and Post-Collection. The default is Real-time. Post-Collection handles large files (lots of devices) better.<br>
  
<img width="513" alt="Screenshot 2024-05-19 at 2 27 08 PM" src="https://github.com/canaryradio/WigleToTAK/assets/127666889/d53ed71e-808f-4709-a210-0d991093c537">



<h2>MAC Whitelist</h2>
MAC Whitelist is for devices that you don't want to display or don't care to display. Your own for instance. Add devices to the Whitelist by SSID or MAC. To remove one select it from the drop down and click "Remove from Whitelist".<br>

<img width="509" alt="Screenshot 2024-05-19 at 2 25 51 PM" src="https://github.com/canaryradio/WigleToTAK/assets/127666889/689aafe8-3a71-453a-9a5b-718ae261dfd2">



<h2>MAC Blacklist</h2>
MAC Blacklist is for devices that you want to display in a color other than the default color. You need to select a ARGB value other than -65281 (purple) because that is the default. To remove select it from the drop down and click "Remove from Blacklist".<br> Add devices to the Blacklist by SSID and by MAC.<br>

<img width="519" alt="Screenshot 2024-05-19 at 2 23 45 PM" src="https://github.com/canaryradio/WigleToTAK/assets/127666889/5801450e-a06e-49ed-97e7-194ebb49eaa5">

