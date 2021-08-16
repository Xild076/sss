import enum, threading, datetime, socket, sys, pickle, gpiozero, requests
from flask import Flask, render_template

class Logger(object):
    def __init__(self, file="/home/pi/projects/riss/logs.txt", print=False):
        self.file = file
        self.print = print
    
    def log(self, signature, msg, log_type):
        file = open(self.file, "a")
        text = ""
        if log_type == LogType.Type.CLEAR:
            text += "  ------  "
        else:
            if log_type == LogType.Type.DEBUG:
                text += "DEBUG -- "
            elif log_type == LogType.Type.ERROR:
                text += "ERROR -- "
            elif log_type == LogType.Type.STARTUP:
                text += "STARTUP -- "
            text += signature
            text += " ["
            text += datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S.%f')
            text += "]: "
            text += msg

        if self.print:
            print(text)
        
        text += "\n"
        file.write(text)
        file.close()


class LogType(object):
    class Type(enum.Enum):
        DEBUG = 0
        ERROR = 1
        STARTUP = 2
        CLEAR = 3


class CommBase(object):
    def __init__(self, signature=None, debug=False):
        self.signature_ = signature
        self.hostname_ = '127.0.0.1'
        self.job_queue_ = {'lock': threading.Lock(), 'queue': list()}
        self.out_queue_ = {'lock': threading.Lock(), 'queue': list()}
        self.buffer_ = 8912
        self.incoming_socket_ = None
        self.incoming_port_ = None
        self.outgoing_socket_ = None
        self.outgoing_port_ = None
        self.logging_ = Logger(print=True)
        self.data_ = None
        self.threadpool_ = list()
        self.action_ = None
        self.update_data_ = None
    
    def _create_socket(self):
        ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            ss.bind((self.hostname_, 0))
        except socket.error as msg:
            self.logging_.log(self.signature_, f'!!! Failed to bind socket for listening. Error code: {msg[0]}, Message: {msg[1]} !!!', LogType.Type.ERROR)
        port = ss.getsockname()[1]
        self.logging_.log(self.signature_, f'Started listening on {self.hostname_} on port {port}', LogType.Type.DEBUG)
        return ss, port

    def _create_sending_socket(self):
        self.incoming_socket_, self.incoming_port_ = self._create_socket()

    def _create_recv_socket(self):
        self.outgoing_socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def _listen_inc(self):
        self.logging_.log(self.signature_, f"{self._listen_inc.__name__} started", LogType.Type.STARTUP)
        while True:
            self.incoming_socket_.listen(5)
            conn, address = self.incoming_socket_.accept()
            self.logging_.log(self.signature_, f"Connected by {address}", LogType.Type.DEBUG)
            with conn:
                data = conn.recv(self.buffer_)
                if data:
                    self.job_queue_['lock'].acquire()
                    unpacked = pickle.loads(data)
                    self.job_queue_['queue'].append(unpacked)
                    self.data_ = unpacked
                    self.logging_.log(self.signature_, f"Data [{unpacked}] received and saved", LogType.Type.DEBUG)
                    self.job_queue_['lock'].release()
                else:
                    self.data_ = None
                    self.logging_.log(self.signature_, "Data is none, receiving nothing", LogType.Type.ERROR)
            self.logging_.log(self.signature_, f"Waiting for new connection", LogType.Type.DEBUG)

    def _send_through(self):
        while True:
            data = None
            self.out_queue_['lock'].acquire()
            if self.out_queue_['queue']:
                self.logging_.log(self.signature_, "There is something in outgoing queue", LogType.Type.DEBUG)
                data = pickle.dumps(self.out_queue_['queue'].pop(0))
                self.logging_.log(self.signature_, f"Data is: {data}", LogType.Type.DEBUG)
            self.out_queue_['lock'].release()
            if data:
                try:
                    self.outgoing_socket_.connect((self.hostname_, self.outgoing_port_))
                    self.outgoing_socket_.sendall(data)
                    self.logging_.log(self.signature_, "Data send", LogType.Type.DEBUG)
                except Exception as ee:
                    self.logging_.log(self.signature_, f"Failed to send data to {self.hostname_} on port {self.outgoing_port_}, with exception {ee}", LogType.Type.ERROR)
                    self.exit()

    def _run_job(self):
        self.logging_.log(self.signature_, f"{self._run_job.__name__} started", LogType.Type.STARTUP)
        while True:
            if self.action_ != None:
                data = None
                self.job_queue_['lock'].acquire()
                if self.job_queue_['queue']:
                    self.job_queue_['queue'].pop(0)
                self.job_queue_['lock'].release()
                if data:
                    self.logging_.log(self.signature_, f"Taking action for {data}")
                    self.action_(data, self.out_queue_['queue'])

    def _run_update(self):
        self.logging_.log(self.signature_, f"{self._run_update.__name__} started", LogType.Type.STARTUP)
        while True:
            if self.update_data_ != None:
                self.update_data_(self.data_, self.out_queue_['queue'])

    def _set_peer(self, hostname, port_id):
        self.outgoing_port_ = port_id
        self.logging_.log(self.signature_, f"Set peer: -hostname <{self.outgoing_socket_.__str__()}> -port <{self.outgoing_port_}", LogType.Type.DEBUG)

    def _append_out(self, data):
        self.logging_.log(self.signature_, f"Appending data", LogType.Type.DEBUG)
        self.out_queue_['lock'].acquire()
        self.out_queue_['queue'].append(data)
        self.out_queue_['lock'].release()

    def _def_action(self, action):
        self.action_ = action

    def _def_update(self, update):
        self.update_data_ = update

    def _set_data(self, data):
        self.data_ = data

    def _get_inc_host(self):
        return self.hostname_, self.incoming_port_

    def _get_out_host(self):
        return self.outgoing_port_

    def _start(self):
        self._create_sending_socket()
        self._create_recv_socket()
        self.logging_.log(self.signature_, f"Running on {self.hostname_} with outgoing port {self.outgoing_port_} and in port {self.incoming_port_}", LogType.Type.STARTUP)
        thread_1 = threading.Thread(target=self._listen_inc)
        self.threadpool_.append(thread_1)
        thread_2 = threading.Thread(target=self._run_job)
        self.threadpool_.append(thread_2)
        thread_3 = threading.Thread(target=self._send_through)
        self.threadpool_.append(thread_3)
        thread_4 = threading.Thread(target=self._run_update)
        self.threadpool_.append(thread_4)

        for tt in self.threadpool_:
            tt.start()

    def exit(self):
        self.outgoing_socket_.close()
        self.incoming_socket_.close()
        sys.exit()


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
        now = datetime.datetime.now()
        now.replace(hour=hour, minute=min, second=0, microsecond=0)
        return now
