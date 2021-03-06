import socket, threading, time, sys, pickle, gpiozero, datetime, json, requests, pickle
from enum import Enum
from datetime import datetime

"""
class CommBase(object):
    def __init__(self, hostname=None, signature=None):
        self.signature_ = signature
        self.threadpool_ = list()
        self.job_queue_ = list()
        self.hostname_ = '127.0.0.1' if hostname is None else hostname
        self.action_ = None
        self.update_ = None
        self.outgoing_queue_ = list()
        self.thread_pool_ = list()
        self.outgoing_hostname = None
        self.outgoing_port = None
        self.incoming_, self.port_ = self._create_socket()
        self.job_queue_lock_ = threading.Lock()
        self.outgoing_queue_lock_ = threading.Lock()
        self.data = WebInfo(0, [], [], [False, False, False, False])

    def _create_socket(self):
        ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            ss.bind((self.hostname_, 0))
        except socket.error as msg:
            print(f'Failed to bind socket for listening. Error code: {msg[0]}, Message: {msg[1]}')
            sys.exit()
        port = ss.getsockname()[1]
        print(f"## {self.signature_} start listening on {self.hostname_}, port: {port}")
        return ss, port

    def _listen_incoming(self):
        while True:
            print("Im still listening")
            self.incoming_.listen(5)
            conn, address = self.incoming_.accept()
            with conn:
                print(f"## {self.signature_} Connected by: {address}")
                while True:
                    data = conn.recv(8192)
                    if not data:
                        break
                    self.job_queue_lock_.acquire()
                    self.job_queue_.append(pickle.loads(data))
                    self.job_queue_lock_.release()
                    self.data = pickle.loads(data)

    def _take_action(self):
        while True:
            data = None
            self.job_queue_lock_.acquire()
            if self.job_queue_:
                data = self.job_queue_.pop(0)
            self.job_queue_lock_.release()
            if data:
                print(f"== {self.signature_} take action for {data}")
                self.action_(data, self.outgoing_queue_)

    def _do_update(self):
        while True:
            if self.update_ != None:
                self.update_(self.data)

    def _send_back(self):
        while True:
            data = None
            self.outgoing_queue_lock_.acquire()
            if self.outgoing_queue_:
                data = self.outgoing_queue_.pop(0)
            self.outgoing_queue_lock_.release()
            if data:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as ss:
                    ss.connect((self.outgoing_hostname, self.outgoing_port))
                    ss.sendall(pickle.dumps(data))

    def get_port_num(self):
        return self.port_

    def set_peer(self, hostname, port_id):
        self.outgoing_hostname = hostname
        self.outgoing_port = port_id

    def define_action(self, action):
        self.action_ = action

    def define_update(self, update):
        self.update_ = update

    def start(self):
        listening_thread = threading.Thread(target=self._listen_incoming)
        listening_thread.start()
        self.thread_pool_.append(listening_thread)

        action_thread = threading.Thread(target=self._take_action)
        action_thread.start()
        self.thread_pool_.append(action_thread)

        update_thread = threading.Thread(target=self._do_update)
        update_thread.start()
        self.thread_pool_.append(update_thread)

        sendback_thread = threading.Thread(target=self._send_back)
        sendback_thread.start()
        self.thread_pool_.append(sendback_thread)
"""

def debug_print(enable_debug, prefix, msg, *args, **kvargs):
    if enable_debug:
        print(f"{prefix} [{datetime.now().strftime('%Y-%m-%d %H-%M-%S.%f')}]: {msg}")


# class Message(object):
#     class Type(Enum):
#         Unknown = 0
#         Handshake = 1
#         StatusUpdate = 2
#     def __init__(msg_type = Message.Type.Unknown, msg_body=None):


class Comm(object):
    def __init__(self, hostname='127.0.0.1', signature=None, debug=False, msg_prefix=''):
        self.debug_ = debug
        self.msg_prefix_ = msg_prefix
        self.signature_ = signature
        self.threadpool_ = list()
        self.job_queue_ = list()
        self.outgoing_queue_ = list()
        self.hostname_ = hostname
        self.out_hostname_ = None
        self.out_port_ = None
        self.action_ = None
        self.update_data_ = None
        self.in_socket_, self.in_port_ = self._create_socket()
        self.job_queue_lock_ = threading.Lock()
        self.outgoing_queue_lock_ = threading.Lock()
        self.data_ = WebInfo(0, [], [], [False, False, False, False])
        self.comm_buffer_size_ = 8192

    def _create_socket(self):
        ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            ss.bind((self.hostname_, 0))
        except socket.error as msg:
            raise RuntimeError(f'!!! Failed to bind socket for listening. Error code: {msg[0]}, Message: {msg[1]} !!!')
            # if self.debug_:
            #     print(f' ^ Failed to bind socket for listening. Error code: {msg[0]}, Message: {msg[1]}')
        port = ss.getsockname()[1]
        debug_print(self.debug_, self.msg_prefix_, f'* started listening on {self.hostname_} on port {port}')
        # if self.debug_:
        #     print(f' * {self.signature_} started listening on {self.hostname_} on port {port}')
        return ss, port

    def _listen_incoming(self):
        debug_print(True, self.msg_prefix_, "-- Start listening --")
        while True:
            # if self.debug_:
            #     print(" * Listening")
            debug_print(self.debug_, self.msg_prefix_, "* Listening")
            self.in_socket_.listen(5)
            conn, address = self.in_socket_.accept()
            with conn:
                debug_print(self.debug_, self.msg_prefix_, f"* connected by {address}")
                data = conn.recv(self.comm_buffer_size_)
                if data:
                    self.job_queue_lock_.acquire()
                    debug_print(self.debug_, self.msg_prefix_, f"* data received: {data}")
                    unpacked = pickle.loads(data)
                    debug_print(self.debug_, self.msg_prefix_, f"* unpacked data: {unpacked}")
                    self.job_queue_.append(unpacked)
                    self.data_ = unpacked
                    self.job_queue_lock_.release()
                    debug_print(self.debug_, self.msg_prefix_, f"* unpacked data: {self.data_}")
                else:
                    self.data_ = None
            debug_print(self.debug_, self.msg_prefix_, "* sleep for next loop")
            time.sleep(0.1)

    def _take_action(self):
        debug_print(True, self.msg_prefix_, "-- Taking Action --")
        while True:
            data = None
            self.job_queue_lock_.acquire()
            if self.job_queue_:
                self.job_queue_.pop(0)
            self.job_queue_lock_.release()
            if data:
                debug_print(self.debug_, self.msg_prefix_, f"* take action for {data}")
                self.action_(data, self.outgoing_queue_)

    def _run_update(self):
        debug_print(True, self.msg_prefix_, "-- Running for Update --")
        while True:
            if self.update_data_ != None:
                self.update_data_(self.data_, self.outgoing_queue_)

    def _send_back(self):
        debug_print(True, self.msg_prefix_, "-- Sending Back --")
        while True:
            data = None
            self.outgoing_queue_lock_.acquire()
            # if len(self.outgoing_queue_) != 0: # For checking if a list is empty, better do:
            if self.outgoing_queue_:
                debug_print(self.debug_, self.msg_prefix_, f"* outgoing queue length: {len(self.outgoing_queue_)}")
                if self.debug_:
                    print("THERE IS SOMETHING HERE!")
                data = self.outgoing_queue_.pop(0)
            self.outgoing_queue_lock_.release()
            if data:
                debug_print(self.debug_, self.msg_prefix_,  f"* Send {data} back to {self.out_hostname_} on port {self.out_port_}")
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as ss:
                        ss.connect((self.out_hostname_, self.out_port_))
                        ss.sendall(pickle.dumps(data))
                    debug_print(self.debug_, self.msg_prefix_, "* Data successfully sent")
                except Exception as ee:
                    debug_print(True, f"Failed to send data to {self.out_hostname_} on port {self.out_port_}, with exception: {ee}")
                    pass


    def _set_peer(self, hostname, port_id):
        debug_print(True, self.msg_prefix_, f"-- Setting Peer to {hostname} on port {port_id}")
        self.out_hostname_ = hostname
        self.out_port_ = port_id

    def _append_out(self, data):
        debug_print(self.debug_, self.msg_prefix_, f"* appending {data}")
        self.outgoing_queue_lock_.acquire()
        self.outgoing_queue_.append(data)
        self.outgoing_queue_lock_.release()
        debug_print(self.debug_, self.msg_prefix_, f"* finish appending")

    def _def_action(self, action):
        self.action_ = action

    def _def_update(self, update):
        self.update_data_ = update

    def _set_data(self, data):
        self.data_ = data

    def _get_inc_host(self):
        return self.hostname_, self.in_port_

    def _get_out_host(self):
        return self.out_hostname_, self.out_port_

    def _start(self):
        print(" * Start")
        thread_1 = threading.Thread(target=self._listen_incoming)
        self.threadpool_.append(thread_1)
        thread_2 = threading.Thread(target=self._take_action)
        self.threadpool_.append(thread_2)
        thread_3 = threading.Thread(target=self._run_update)
        self.threadpool_.append(thread_3)
        thread_4 = threading.Thread(target=self._send_back)
        self.threadpool_.append(thread_4)

        for tt in self.threadpool_:
            tt.start()



class WebInfo(object):
    def __init__(self, mode, list_on_schedule, list_off_schedule, list_ons):
        self.mode = mode
        self.list_on_schedule = list_on_schedule
        self.list_off_schedule = list_off_schedule
        self.list_ons = list_ons

    def __str__(self):
        return str(self.__dict__)

    def get_mode(self):
        return self.mode

    def get_list_on_sch(self):
        return self.list_on_schedule

    def get_list_off_sch(self):
        return self.list_off_schedule

    def get_list_ons(self):
        return self.list_ons


class WeatherService(object):
    def __init__(self, api_key=None, unit="metric"):
        self._api_key = "00edc016f6b3c21c406e595175511cb0" if api_key is None else api_key
        self._base_url = "http://api.openweathermap.org/data/2.5/"
        self._unit = "metric" if unit is None else unit

    def _get_weather_report_core(self, city, state, country, request_type):
        full_url = f"{self._base_url}{request_type}?q={city},{state},{country}&appid={self._api_key}&units={self._unit}"
        result = requests.get(full_url)
        if result.status_code != 200:
            print(f"WARNING: failed to collect weather report for {city}, {state}, {country}")
        return result.json()

    def get_weather(self, city="San Jose", state="CA", country="US"):
        return self._get_weather_report_core(city=city, state=state, country=country, request_type="weather")

    def get_weather_forecast(self, city="San Jose", state="CA", country="US"):
        return self._get_weather_report_core(city=city, state=state, country=country, request_type="forecast")


class GPIODriver(object):
    def __init__(self, gpio_pins):
        self.gpio_pins = gpio_pins
        self.leds = list()
        
        for pins in self.gpio_pins:
            self.leds.append(gpiozero.LED(pins))

    def on(self, zone):
        self.leds[zone].on()

    def off(self, zone):
        self.leds[zone].off()

    def get_status(self, zone):
        return self.leds[zone].is_lit

class Utility():

    def time_conversion(hour, min):
        now = datetime.now()
        now.replace(hour=hour, minute=min, second=0, microsecond=0)
        return now