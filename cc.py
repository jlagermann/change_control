from steelscript.common.app import Application
from steelscript.common.service import OAuth
from steelscript.scc.core import SCC
from steelscript.scc.core.report import AppliancesReport
from steelscript.cmdline import exceptions
import steelscript.steelhead.core.steelhead as steelhead
import multiprocessing as mp
import getpass
import re
import signal
import logging
import datetime
import time
import os
import glob
import difflib
import sys
import ConfigParser


def sh_retry_exec_command(logger=None, sh=None, cmd=None):
    output = None
    for i in range(0,10):
        try:
            output = sh.cli.exec_command(cmd)
        except exceptions.ConnectionError:
            logger.info('SteelHead connection error, attempt #' + str(i) + ' , retrying...')
            time.sleep(5)
            continue
        break
    else:
        logger.info('SteelHead connection error, giving up')

    return output


def unwrap_self_process_steelhead(arg, **kwarg):

    return SteelHeadCC.process_steelhead(*arg, **kwarg)


def steelhead_show_run(sh=None, logger=None):
    """
    :param sh: SteelHead object
    :param logger: Logging object
    :return: string with running configuration
    """
    if sh is not None:
        return sh_retry_exec_command(logger=logger, sh=sh, cmd='show running-config all')



def process_init():
    signal.signal(signal.SIGINT, signal.SIG_IGN)


class SteelHeadCC(Application):

    def add_positional_args(self):
        self.add_positional_arg('scc', 'SteelCentral Controller for SteelHead IP Address')

    def add_options(self, parser):
        super(SteelHeadCC, self).add_options(parser)
        parser.add_option('-u', '--username', help="SteelHead username, default=admin", default="admin")
        parser.add_option('-p', '--password', help="Password for all SteelHead's")
        parser.add_option('-a', '--archive', action="store_true",dest="archive", default=True,
                          help="archive configuration file")
        parser.add_option('-d', '--diff', action="store_true", dest="diff", default=False,
                          help="diff against previous version")
        parser.add_option('-b', '--base_diff', dest="base_filename",
                          help="diff all steelheads against a common base configuration file")
        parser.add_option('', '--html', action="store_true", dest="html", default=False, help="output html file")
        parser.add_option('-t', '--threads', help="how many concurrent devices to process at a given time",
                          type=int, default=10)
        parser.add_option('-c', '--config', help="configuration file")

    def validate_args(self):
        if self.options.config:
            if not os.path.exists(self.options.config):
                print('Configuration file not found')
                exit(1)

            config = ConfigParser.ConfigParser()
            config.readfp(open(self.options.config))
            config.read(['Main'])

            try:
                self.options.username = config.get('Main', 'username')
            except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
                pass

            try:
                self.options.password = config.get('Main', 'password')
            except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
                pass

            try:
                self.options.archive = config.get('Main', 'archive')
            except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
                pass

            try:
                self.options.diff = config.get('Main', 'diff')
            except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
                pass

            try:
                self.options.base_filename = config.get('Main', 'base_diff')
            except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
                pass

            try:
                self.options.html = config.get('Main', 'html')
            except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
                pass

            try:
                self.options.threads = config.get('Main', 'threads')
            except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
                pass

            try:
                self.options.access_code = config.get('Main', 'access_code')
            except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
                pass

            super(SteelHeadCC, self).validate_args()

        if not self.options.password:
            self.options.password = getpass.getpass("Password for all SteelHead's:")

        if self.options.html and not (self.options.diff or self.options.base_filename):
            print('Cannot specify html without dif or base_diff options')
            exit(1)

        if self.options.diff and self.options.base_filename:
            print('Cannot specify diff and base_diff at the same time. Choose one or the other')
            exit(1)



    def appliance_report_get_primary_interface(self, device=None):
        for interface in device['interfaces']:
            if interface['name'] == 'primary':
                return interface['ip_address']
        """ If we are still here is because we cannot find a primary address , use the auto_detected_address instead"""
        if device['auto_detected_address']:
            return device['auto_detected_address']

        return None


    def split_type_name(self, model=None):
        """
        :param model: model of the device like VCX1555H
        :return:
            tuple with (VCX1555, H)
        """
        if model is not None:
            match = re.match(r'([A-Z]{2,}\d+)([A-Z]{1})', model)
            if len(match.groups()) == 2:
                return (match.group(1), match.group(2))

        return None



    def get_running_config(self,logger=None, sh=None):

        logger.info('Fetching running configuration all')
        sh_running = steelhead_show_run(sh=sh, logger=logger)
        if sh_running is None:
            logger.info('Cannot retrieve running configuration')
            return


        return sh_running


    def init_mp_logger(self, name=None, ip=None, logger_filename=None):
        '''Check if logging directory exists '''
        if not os.path.isdir('./logs'):
            os.makedirs('./logs')

        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        fh = logging.FileHandler(logger_filename)
        fh.setLevel(logging.INFO)

        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        formatter = logging.Formatter('[%(asctime)s][' + ip + '] %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        logger.addHandler(fh)
        logger.addHandler(ch)

        return logger


    def get_latest_file(self, device_ip=None):
        files = glob.glob('./logs/' + device_ip + '*-latest.log')
        if len(files) == 0:
            return None
        else:
            return files[0]


    def archive_running_config(self, device_ip=None, running_config=None, date_string= None, latest_file=None):
        """
        Rotate latest file and write new configuration in latest filename
        :param device_ip: The device ip address
        :param running_config: The running configuration to save
        :param date_string: The string representing the time now for the filename
        :param latest_file: the latest filename found ( if found ) or None
        :return: tuple (previous_last_filename, latest_filename)
        """
        new_latest = './logs/' + device_ip + '-' + date_string + '-latest.log'
        last_latest = None
        if latest_file:
            temp = latest_file
            last_latest = re.sub(r"-latest", "", latest_file)
            new_latest = './logs/' + device_ip + '-' + date_string + '-latest.log'
            os.rename(temp,last_latest )

        file = open(new_latest, "w")
        file.write(running_config)
        file.close()


        return (last_latest, new_latest)

    def diff(self, logger=None, type=None, previous_filename=None, running=None, device_ip=None):
        '''
        diff_to_previous , diff against previous configurations
        :param logger: to log any errors
        :param type: Type of diff either 'base' or 'running'
        :param previous_filename: file name of a previous file to diff against
        :param running: latest running configuration , String with the configuration ,will be splited in an array
        :param device_ip: the device ip address
        :return: None always ...
        '''
        if previous_filename is None:
            logger.critical('Cannot find a previous config to diff against.')
            return None
        else:
            if type is 'running':
                logger.info('diff ' + previous_filename + ' vs. running')
            elif type is 'base':
                logger.info('diff ' + previous_filename + ' vs. base')
            if os.path.exists(previous_filename):
                previous_text = open(previous_filename, "U").readlines()
                previous_date_match = re.search(r'\d{8}-\d{6}', previous_filename)
                running_text = running.split('\n')
                if self.options.html:
                    if type is 'running':
                        diff = difflib.HtmlDiff().make_file(previous_text,running_text,previous_filename,'running',
                                                            True)
                    elif type is 'base':
                        diff = difflib.HtmlDiff().make_file(previous_text, running_text, previous_filename, 'running',
                                                            True)
                    try:
                        if type is 'running':
                            diff_file = open(
                                './logs/' + device_ip + '-' + previous_date_match.group() + '-running.diff.html', "w+")
                        elif type is 'base':
                            diff_file = open(
                                './logs/' + device_ip + '-' + previous_date_match.group() + '-running.diff.html', "w+")
                        diff_file.write(diff)
                        diff_file.close()
                    except AttributeError as e:
                        logger.info('cannot find date in file string')
                        return None
                else:
                    diff = difflib.context_diff(previous_text, running_text, previous_filename,'running',
                                                previous_date_match.group(), 'running')

                    diff_file = open(
                        './logs/' + device_ip + '-' + previous_date_match.group() + '-running.diff.txt', "w+")
                    try:
                        for line in diff:
                            diff_file.write(line)
                        diff_file.write('\n')
                        diff_file.close()
                    except AttributeError as e:
                        logger.info('cannot find date in file string')
                        return None

            else:
                logger.error('Cannot read files to diff')


        return None


    def process_steelhead(self, prop):
        device_ip = prop[0]

        logger_filename = './logs/' + device_ip + '.log'
        logger = self.init_mp_logger(prop[1], prop[0], logger_filename)


        auth = steelhead.CLIAuth(username=self.options.username, password=self.options.password)

        sh = steelhead.SteelHead(host=device_ip, auth=auth)
        logger.info('logging in.')

        sh_running = self.get_running_config(logger, sh)
        """ Get latest running config """
        date_string = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        latest_filename = self.get_latest_file(device_ip)
        diff_files = None

        latest_filename = self.get_latest_file(device_ip)
        if latest_filename:
            if self.options.diff:
                self.diff(logger, 'running',latest_filename, sh_running, device_ip)
            elif self.options.base_filename:
                if os.path.exists(self.options.base_filename):
                    base_fd = open(self.options.base_filename,"r")
                    base_text = base_fd.read()
                    self.diff(logger, 'base',latest_filename, base_text, device_ip)
                else:
                    logger.critical('Base config file not found exiting')
                    exit(1)
            if self.options.archive:
                 self.archive_running_config(device_ip, sh_running, date_string, latest_filename)


        time.sleep(5)

        return None

    def main(self):
        """ Get a report of all devices in the SCC inventory """
        scc = SCC(host=self.options.scc, auth=OAuth(self.options.access_code))
        report = AppliancesReport(scc)
        report.run()
        devices = []
        for device in report.data:
            if device['product_code'] == 'SH' or device['product_code'] == 'EX':
                ip = self.appliance_report_get_primary_interface(device)
                try:
                    devices.append((ip, device['hostname']))
                    #self.process_steelhead((ip, device['hostname']))
                except KeyError:
                    pass
        print('Starting with ' + str(self.options.threads) + ' at a time.')
        try:
            pool = mp.Pool(processes=self.options.threads, initializer=process_init)
            pool_outputs = pool.map(unwrap_self_process_steelhead, zip([self]*len(devices),devices))
            pool.close()
            pool.join()
        except KeyboardInterrupt:
            pool.terminate()
            pool.join()

if __name__ == '__main__':
    SteelHeadCC().run()

