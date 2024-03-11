A Python application with html dashboard designed to help use your WigleCSV creating service with TAK products.
For use in a non-production environment.
Defaults are set to be run on the same server as your WigleCSV device service, however other network configurations should work.

Tested using Python and Python 3 with a Chrome browser.
# Quick Start
Step 1:
Clone or download Wigle-to-TAK-Python to your computer

Step 2:
Initialize or start your WigleCSV creating service (e.g. {$ sudo kismet -t some_wardrive -c wlp3s0 --override wardrive}). Another option is to use this for post collection processing.

Step 3:
Navigate to the directory and start
```
$ cd Wigle-to-TAK-Python
$ python WigleToTAK.py
```

Step 4:
Open a browser and navigate to http://<YOUR_IP:8000


# Instructions
