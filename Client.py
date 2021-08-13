import logging, time, pdb
from math import log, remainder
import Utility, Logger, os, threading
import random, subprocess
from optparse import OptionParser

class TestDriver(object):
    def __init__(self, identifier):
        self.logger_ = Logger.create_logger(None, identifier, logging.DEBUG)
        self.current_status_ = 0

    def execute(self, job):
        self.logger_.info(f"$$$$ executing job: {job} $$$$")
        self.current_status_ = random.randint(0, 1000000)
        return {'number': self.current_status_}

    def get_status(self):
        return {'number': self.current_status_}

    def update_status(self, status):
        self.current_status_ = status['number']


class ClientSide(Utility.CommBase):
    def __init__(self, logger, signature, actor, identifier="Client"):
        super(ClientSide, self).__init__(logger, signature, actor, identifier)


class HandInput(Utility.CommBase):
    def __init__(self, logger, signature, actor, identifier="HandInput"):
        super(HandInput, self).__init__(logger, signature, actor, identifier)

    def take_input(self):
        data = input("Input a number:")
        try:
            data = int(data)
            self.job_queue_['lock'].acquire()
            self.job_queue_['queue'].append({'user_input': data})
            self.job_queue_['lock'].release()
        except:
            quit()

    def start(self):
        self._create_socket()
        thread_pool = list()
        thread_pool.append(threading.Thread(target=self.execute_job))
        thread_pool.append(threading.Thread(target=self.update_status))
        thread_pool.append(threading.Thread(target=self.listen_loop))
        for tt in thread_pool:
            tt.start()
        # for tt in thread_pool:
        #     tt.join()
        # # self.take_input()


class ControlCenter(Utility.CommBase):
    def __init__(self, logger, signature, actor, identifier="ControlCenter"):
        super(ControlCenter, self).__init__(logger, signature, actor, identifier)


def launch_client(master_host, master_port, signature, log_dir, enable_debug):
    actor = TestDriver("ClientActor")
    log_filename = os.path.join(log_dir, "client.log")
    log_level = logging.DEBUG if enable_debug else logging.INFO
    logger = Logger.create_logger(log_filename, "Client", log_level)
    client = ClientSide(logger, signature, actor)
    client.request_connection(master_host, master_port)
    client.start()
    

def launch_frontend(signature, log_dir, enable_debug):
    actor = TestDriver("InputActor")
    log_filename = os.path.join(log_dir, "input.log")
    log_level = logging.DEBUG if enable_debug else logging.INFO
    logger = Logger.create_logger(log_filename, "HandInput", log_level)
    server = HandInput(logger, signature, actor)
    server.start()
    return server
    # server.request_connection(master_host, master_port)

# def launch_control_center(signature, log_dir, enable_debug):
#     actor = TestDriver("DoNothing")
#     log_filename = os.path.join(log_dir, "master.log")
#     log_level = logging.DEBUG if enable_debug else logging.INFO
#     logger = Logger.create_logger(log_filename, "ControlCenter", log_level)
#     cc = ControlCenter(logger, signature, actor)
#     cc.start()
#     return cc

def main():
    parser = OptionParser()
    parser.add_option("--host", dest="hostname", help="provide the master host name")
    parser.add_option("--port", dest="port", help='provide master port for connection')
    parser.add_option("--sig", dest="signature", help="signature for connection")
    parser.add_option("--debug", dest="enable_debug", help="enable debugging", default=False)
    parser.add_option("--work_dir", dest="work_dir", help="output log directory", default="log")
    parser.add_option("--mode", dest="mode", help="start with master or client mode")
    options, remainder = parser.parse_args()

    log_dir = os.path.abspath(os.path.realpath(options.work_dir))
    if not os.path.isdir(log_dir):
        os.makedirs(log_dir)

    if options.mode == 'Client':
        launch_client(options.hostname, int(options.port), options.signature, log_dir, options.enable_debug)
    # elif options.mode == 'Master':
    #     launch_frontend(options.hostname, options.port, options.signature, log_dir, options.enable_debug)
    else:
        sig = Utility.generate_random_signature()
        cc = launch_frontend(sig, log_dir, options.enable_debug)
        master_host = cc.host_info_['host_info']
        cmd = [
            'python3', os.path.abspath(__file__), 
            '--host', master_host['name'], 
            '--port', str(master_host['port']), 
            '--sig', sig, 
            '--debug', str(options.enable_debug),
            '--work_dir', log_dir]
        client_process = subprocess.Popen(cmd + ['--mode', 'Client'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        while True:
            if 'Client' not in cc.clients_host_info_:
                cc.logger_.info('Wait for client connection')
                time.sleep(1)
            else:
                break
        cc.take_input()

if __name__ == "__main__":
    main()

""" 

class ClientSide(Utility.Comm):
    def __init__(self, signature):
        super(ClientSide, self).__init__(signature=signature, debug=True, msg_prefix="CLIENT")
        self.list_ons = list()
        self.action_ = self.action
        self.update_data_ = self.update # LEI: update_ or update_data_ ??
        self.gpios = Utility.GPIODriver([17,18,22,23])
        self.get_weather = Utility.WeatherService()
        self.weather = self.get_weather.get_weather_forecast()

    def action(self, data, outgoing):
        if self.debug_ == None:
            print(" * (SS) action started")
    
    def update(self, data, outgoing):
        self.list_ons = [False, False, False, False]
        if data is None:
            return

        if data.get_mode() == 1:
            # LEI: better to use "ii" or "gid" to indicate gpio index. 
            for i in range(len(data.get_list_on_sch())):
                # LEI: Why not simply:
                # self.list_ons[i] = (data.get_list_on_sch()[i] <= datetime.datetime.now() < data.get_list_off_sch()[i]) ?
                if data.get_list_on_sch()[i] <= datetime.datetime.now() < data.get_list_off_sch()[i]:
                    self.list_ons[i] = True
                else:
                    self.list_ons[i] = False      
        elif data.get_mode() == 2:
            self.list_ons = data.get_list_ons()
        else:
            if self.weather != "rain":
                if Utility.Utility.time_conversion(5, 0) <= datetime.datetime.now() < Utility.Utility.time_conversion(5, 10):
                    self.list_ons = [True, True, True, True]
        
        if datetime.datetime.now() == Utility.Utility.time_conversion(4, 30):
            self.weather = self.get_weather.get_weather_forecast()

        # LEI: More simple way:
        # for gid in range(len(self.gpios.gpio_pins)):
        # self.gpios.on(gid) if self.list_ons[gid] else self.gpios.off[gid]
        for i in range(len(self.gpios.gpio_pins)):
            if self.list_ons[i]:
                self.gpios.on(i)
            else:
                self.gpios.off(i) """