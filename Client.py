import Utility, datetime

class ClientSide(Utility.Comm):
    def __init__(self, signature):
        super(ClientSide, self).__init__(signature=signature, debug=False)
        self.list_ons = list()
        self.action_ = self.action
        self.update_ = self.update
        self.gpios = Utility.GPIODriver([17,18,22,23])
        self.get_weather = Utility.WeatherService()
        self.weather = self.get_weather.get_weather_forecast()

    def action(self, data, outgoing):
        if self.debug_:
            print(" * (SS) action started")
    
    def update(self, data, outgoing):
        self.list_ons = [False, False, False, False]

        if data.get_mode() == 1:
            for i in range(len(data.get_list_on_sch())):
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
        
        for i in range(len(self.gpios.gpio_pins)):
            if self.list_ons[i]:
                self.gpios.on(i)
            else:
                self.gpios.off(i)