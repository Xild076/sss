import Utility, datetime
from Utility import debug_print

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
                self.gpios.off(i)