# cc.py
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
script how many  devices should be query at the same time, by default 5 devices will que query at the same time.

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
...
```
* Note: The script will prompt for the username password if is not specified in the config file or via a parameter when running the script.

