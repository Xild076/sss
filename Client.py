import Utility, datetime

class ClientSide(Utility.CommBase):
    def __init__(self, signature="CLIENT", debug=False):
        super(ClientSide, self).__init__(signature, debug)
        self._def_action(self.action)
        self.list_ons = [False, False, False, False]
    
    def action(self, data, outgoing):
        if data is None:
            return

        self.logging_.log(self.signature_, f"Mode: {data.get_mode()}", Utility.LogType.Type.DEBUG)

        if data.get_mode() == 1:
            for i in range(len(data.get_list_on_sch())):
                self.list_ons[i] = (data.get_list_on_sch()[i] <= datetime.datetime.now() < data.get_list_off_sch()[i])
     
        elif data.get_mode() == 2:
            self.list_ons = data.get_list_ons()
        else:
            if self.weather != "rain":
                if Utility.Utility.time_conversion(5, 0) <= datetime.datetime.now() < Utility.Utility.time_conversion(5, 10):
                    self.list_ons = [True, True, True, True]
        
        if datetime.datetime.now() == Utility.Utility.time_conversion(4, 30):
            self.weather = self.get_weather.get_weather_forecast()

        for gid in range(len(self.gpios.gpio_pins)):
            if self.list_ons[gid]:
                self.gpios.on(gid)
            else:
                self.gpios.off(gid)