# cc.py
#####Requirements
This script requires steelscript to be installed. You can install all dependencies with:
pip install requirements.txt

Change Control is a SteelScript that will query the SteelCentral controller for SteelHead to fetch all Steelheads.
With that information it will ssh into all the devices and will query its running configuration.
The configuration can be saved for archiving purposes or it can be 'diff' with either a base configuration or with
the last saved configuration for that specific device.

To ease the use of this script a config file is being use to allow secure access to the devices.

the following are the contents of the configuration file:

######[Main]
username = admin  
password = password  
archive = True  
diff = True  
html = True  
threads = 5  
access_code = eyJhdWQiOiAiaHR0cHM8Ly9yaXZlcmJlZGNtYy5jaGxsbmdZLmhvbWUvYXBpL2NvbW1vbi8xLjAvdG9rZW4iLCAiaXNzIjogImh0dHBzOi8vcml2ZXJiZWRjbWMuY2hsbG5nci5ob21lIiwgInBybiI6ICJhZG1pbiIsICJqdGkiOiAiOTUwNTNkMzAtYjMyMy00OWQ5LTk2NzEtOTk4YmQ0Y2ZhOTc0IiwgImV4cCI6ICIwIiwgImlhdCI6ICIxNDYxNjE5ODQwIn0=  
base_diff = ./logs/base_text.txt  


######Config file parameters:
**username:** The username to use to access the SteelHeads via ssh.

**password:** The password associated with the username to access the SteelHeads via ssh.

**archive:** Flag specifying if we should archive the running configuration in a file. By default all configurations will
be archived in the log directory, created the first time that the script is run. The latest configuration will be
be appended with the "_latest.log" suffix.

**diff:** Will instruct the script to generate a diff file between the latest configuration archived and the running
configuration fetched. By default the script will generate a diff text file.

* Note: The archive and diff options can be used together.

**base_diff:**: This flag will instruct the script to diff the running config against a "golden" configuration, instead
of the latest archived configuration. This flag is mutually exclusive of the diff option. This option requires a filename
as an argument.

**html:** For the diff and base_diff options, generate an html report instead of the text file format.

**threads:** The script is meant to process multiple SteelHeads at the same time, the thread option will instruct the
script how many  devices should be query at the same time, by default 10 devices will que query at the same time.

**access_code:** The access code from the rest_api to access the SteelCentral Controller for SteelHead.

### *Running the script*.
#### Help
```
$ ~/steelscript/bin/python2.7 cc.py --help
Usage: cc.py <SCC> [options] ...

Required Arguments:
  SCC         SteelCentral Controller for SteelHead IP Address

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -u USERNAME, --username=USERNAME
                        SteelHead username, default=admin
  -p PASSWORD, --password=PASSWORD
                        Password for all SteelHead's
  -a, --archive         archive configuration file
  -d, --diff            diff against previous version
  -b BASE_FILENAME, --base_diff=BASE_FILENAME
                        diff all steelheads against a common base
                        configuration file
  --html                output html file
  -t THREADS, --threads=THREADS
                        how many concurrent devices to process at a given time
  -c CONFIG, --config=CONFIG
                        configuration file

  Logging Parameters:
    --loglevel=LOGLEVEL
                        log level: debug, warn, info, critical, error
    --logfile=LOGFILE   log file, use '-' for stdout
```
### Running with a config file
```
~/steelscript/bin/python2.7 cc.py -c cc.ini riverbedcmc
/Users/marcelo/steelscript/lib/python2.7/site-packages/requests/packages/urllib3/connectionpool.py:730: InsecureRequestWarning: Unverified HTTPS request is being made. Adding certificate verification is strongly advised. See: https://urllib3.readthedocs.org/en/latest/security.html (This warning will only appear once by default.)
  InsecureRequestWarning)
Starting with 5 at a time.
...
```

### Running from the cli , archiving and diff with html enable
```
~/steelscript/bin/python2.7 cc.py -c cc.ini riverbedcmc -u admin -a --diff --html
Password for all SteelHead's:
/Users/marcelo/steelscript/lib/python2.7/site-packages/requests/packages/urllib3/connectionpool.py:730: InsecureRequestWarning: Unverified HTTPS request is being made. Adding certificate verification is strongly advised. See: https://urllib3.readthedocs.org/en/latest/security.html (This warning will only appear once by default.)
  InsecureRequestWarning)
Starting with 10 at a time.
[2016-05-12 10:51:55,790][10.0.10.211] logging in.
[2016-05-12 10:51:55,791][10.0.10.211] Fetching running configuration all
[2016-05-12 10:51:55,791][10.0.10.209] logging in.
[2016-05-12 10:51:55,792][10.0.10.209] Fetching running configuration all
[2016-05-12 10:51:55,792][10.0.10.240] logging in.
[2016-05-12 10:51:55,793][10.0.10.240] Fetching running configuration all
[2016-05-12 10:51:55,793][10.0.10.212] logging in.
[2016-05-12 10:51:55,794][10.0.10.212] Fetching running configuration all
[2016-05-12 10:51:55,797][10.0.10.210] logging in.
[2016-05-12 10:51:55,797][10.0.10.210] Fetching running configuration all
[2016-05-12 10:51:55,798][10.0.10.179] logging in.
[2016-05-12 10:51:55,799][10.0.10.179] Fetching running configuration all
[2016-05-12 10:52:05,941][10.0.10.240] diff ./logs/10.0.10.240-20160430-134932-latest.log vs. running
[2016-05-12 10:52:06,239][10.0.10.210] diff ./logs/10.0.10.210-20160430-134932-latest.log vs. running
[2016-05-12 10:52:06,285][10.0.10.212] diff ./logs/10.0.10.212-20160430-134932-latest.log vs. running
[2016-05-12 10:52:06,309][10.0.10.211] diff ./logs/10.0.10.211-20160430-134931-latest.log vs. running
[2016-05-12 10:52:06,381][10.0.10.209] diff ./logs/10.0.10.209-20160430-134932-latest.log vs. running
[2016-05-12 10:52:21,947][10.0.10.179] SteelHead connection error, attempt #0 , retrying...
[2016-05-12 10:52:26,948][10.0.10.179] SteelHead connection error, attempt #1 , retrying...
[2016-05-12 10:52:31,950][10.0.10.179] SteelHead connection error, attempt #2 , retrying...
[2016-05-12 10:52:36,951][10.0.10.179] SteelHead connection error, attempt #3 , retrying...
[2016-05-12 10:52:41,953][10.0.10.179] SteelHead connection error, attempt #4 , retrying...
[2016-05-12 10:52:46,954][10.0.10.179] SteelHead connection error, attempt #5 , retrying...
[2016-05-12 10:52:51,956][10.0.10.179] SteelHead connection error, attempt #6 , retrying...
[2016-05-12 10:52:56,958][10.0.10.179] SteelHead connection error, attempt #7 , retrying...
[2016-05-12 10:53:01,960][10.0.10.179] SteelHead connection error, attempt #8 , retrying...
[2016-05-12 10:53:06,962][10.0.10.179] SteelHead connection error, attempt #9 , retrying...
[2016-05-12 10:53:11,962][10.0.10.179] SteelHead connection error, giving up
[2016-05-12 10:53:11,963][10.0.10.179] Cannot retrieve running configuration
```
* Note 1: The script will prompt for the username password if is not specified in the config file or via a parameter when running the script.
* Note 2: In case a device cannot be reach, the script will try again up to ten times to access the device.

### Sample text diff report
```
** ./logs/10.0.10.240-20160512-121735-latest.log	20160512-121735
--- running	running
***************
*** 15,18 ****
! interface inpath0_0 dhcp! interface inpath0_0 dhcp dynamic-dns! interface inpath0_0 force-mdi-x enable! no interface inpath0_0 ip address 10.0.10.235 /24--- 15,18 ----
! no interface inpath0_0 dhcp! no interface inpath0_0 dhcp dynamic-dns! no interface inpath0_0 force-mdi-x enable! interface inpath0_0 ip address 10.0.10.235 /24***************
*** 68 ****
! ip default-gateway "10.0.10.54"--- 68 ----
! ip default-gateway "10.0.10.254"***************
*** 79 ****
! hostname "VCX-changed"--- 79 ----
! hostname "VCX"
```

#### Caveats

```
/steelscript/lib/python2.7/site-packages/requests/packages/urllib3/connectionpool.py:730: InsecureRequestWarning: Unverified HTTPS request is being made. Adding certificate verification is strongly advised. See: https://urllib3.readthedocs.org/en/latest/security.html (This warning will only appear once by default.)
  InsecureRequestWarning)
```
This warning is about using self signed certificates and  the root CA not found for the SteelCentral Controller for SteelHead SSL certificate, if this is the case, is perfectly normal to ignore.
