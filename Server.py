import Utility

class ServerSide(Utility.CommBase):
    def __init__(self, signature="SERVER", debug=False):
        super(ServerSide, self).__init__(signature, debug)
        self._def_action(self.action)
    
    def action(self, data, outgoing):
        super(ServerSide, self)._def_action(self, data, outgoing)