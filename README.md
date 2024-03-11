A Python application with html dashboard designed to help use your WigleCSV creating service with TAK products.
For use in a non-production environment.
Defaults are set to be run on the same server as your WigleCSV device service, however other network configurations should work. This is built with WiFi in mind, however other things in a wigleCSV format will display.

Tested using Python and Python 3 with a Chrome browser.
# Quick Start
Step 1:
Clone or download WigleToTAK to your computer

Step 2:
Initialize or start your WigleCSV creating service (e.g. {$ sudo kismet -t some_wardrive -c {YOUR WIFI INTERFACE} --override wardrive}). Another option is to use this for post collection processing.

Step 3:
Navigate to the directory and start
```
$ cd WigleToTAK
$ python WigleToTAK.py
```

Step 4:
Open a browser and navigate to http://<YOUR_IP:8000


# Instructions
  TAK Server IP is the IP address of your TAK Server. The port should be whichever port you have designated for input of these packets. The Broadcast button is a toggle to enable (default) or disable the multicast to 239.2.3.1:6969.
<img width="506" alt="Screenshot 2024-03-10 at 11 53 15 PM" src="https://github.com/SignalMedic/WigleToTAK/assets/127666889/11e3e3eb-0ebd-40e2-9853-b7c571e992bc">


  Wigle CSV logs directory should be your absolute path to wherever your .wiglecsv files are going to. In Kismet you can set this in the config files. I do not recommend sending to a directory owned by root or requiring sudo priveleges for this application. /home/{YOUR USER} for example is a easy choice. When you click "submit" all of the files ending with .wiglecsv will show in the drop down list. Latest will be at the top. When you click "start" the file will be read and all packets in the file will be parsed, converted to CoT XML, and sent to whatever endpoints you have enabled.
<img width="510" alt="Screenshot 2024-03-10 at 11 53 34 PM" src="https://github.com/SignalMedic/WigleToTAK/assets/127666889/e5bacf15-d163-4395-b63d-b34a7f420c68">


  MAC Whitelist is for devices that you don't want to display or don't care to display. Your own for instance. To remove one select it from the drop down and click "Remove from Whitelist".
<img width="511" alt="Screenshot 2024-03-10 at 11 53 53 PM" src="https://github.com/SignalMedic/WigleToTAK/assets/127666889/643fbc22-9be6-43cb-947b-2dbd65a6b204">


  MAC Blacklist is for devices that you want to display in a color other than the default color. You need to select a ARGB value other than -65281 (purple) because that is the default. To remove select it from the drop down and click "Remove from Blacklist".
<img width="516" alt="Screenshot 2024-03-10 at 11 54 06 PM" src="https://github.com/SignalMedic/WigleToTAK/assets/127666889/c8e60d06-5ba6-48ff-a97c-ed7ac05dfd96">
