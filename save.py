import pickle
import threading
from flask.ext.socketio import emit
class Mission:
    def __init__(self, missiondata):
        f = open('missions/'+missiondata,'rb')
        dictionary = pickle.load(f)
        f.close()
        self.status = dictionary['status']
        self.name = dictionary['name']
        self.map = dictionary['map']
        self.vessel = dictionary['id']
        self.map.dictionary[self.vessel].parentmission = self
        self.objective = dictionary['obj']
        self.socket = None
        self.timer = None
    def GetStations(self):
        return self.map.dictionary[self.vessel].stations
    def Countdown(self):
        self.status = 1.5
        self.emittoallstations("status","1.5")
        self.timer = threading.Timer(10, self.Start)
        self.timer.daemon = True
        self.timer.start()
    def GetVessel(self):
        return self.map.dictionary[self.vessel]
    def join(self,key):
        self.GetStations()[key]['taken'] = True
        self.socket.emit("lobbystations", self.GetStations(), namespace="/lobby")
        readytostart = True
        for dict in self.GetStations().itervalues():
            if dict['taken'] == False:
                readytostart = False
        if readytostart == True:
            self.Countdown()
    def terminate(self):
        self.status = 0
        self.emittoallstations("status", "0")
    def emittoallstations(self,key,value):
        for i in range(len(self.GetStations())+1):
            self.socket.emit(key, value,namespace="/station"+str(i))
    def Start(self):
        self.status = 2
        self.emittoallstations("status","2")
        self.SaveGame()
    def StopCountdown(self):
        self.timer.cancel()
        self.status = 1
        self.emittoallstations("status","1")
    def SaveGame(self):
        self.map.dictionary[self.vessel].parentmission = None
        dictionary = {'status':self.status, 'name':self.name, 'map':self.map, 'id':self.vessel, 'obj':self.objective}
        f = open('save.mis','wb')
        pickle.dump(dictionary,f)
        f.close()
        self.map.dictionary[self.vessel].parentmission = self
    def LoadGame(self):
        f = open('save.mis','rb')
        dictionary = pickle.load(f)
        f.close()
        self.status = dictionary['status']
        self.name = dictionary['name']
        self.map = dictionary['map']
        self.vessel = dictionary['id']
        self.map.dictionary[self.vessel].parentmission = self
        self.objective = dictionary['obj']
        self.emittoallstations("status","1.5")
        self.Start()
class Map:
    def __init__(self):
        self.dictionary = {}
        self.counter = -1
    def Add(self, obj):
        self.counter += 1
        self.dictionary[str(self.counter)] = obj
        return str(self.counter)
class Vessel:
    def __init__(self, specs):
        self.parentmission = None
        self.x = specs['x']
        self.y = specs['y']
        self.z = specs['z']
        self.alertmodule = AlertModule(self,specs['alertstatus'],specs['alerthealth'],specs['alertpower'],specs['alertmindamage'],specs['alertminpower'],specs['alertbreakdamage'],specs['alertmaxhealth'],specs['alertmaxpower'])
        self.communicationsmodule = CommunicationsModule(self,specs['communicationshealth'],specs['communicationspower'],specs['communicationsmindamage'],specs['communicationsminpower'],specs['communicationsbreakdamage'],specs['communicationsmaxhealth'],specs['communicationsmaxpower'],specs['communicationsaddress'])
        self.antennamodule = AntennaModule(self,specs['antennarange'],specs['antennastrength'],specs['antennahealth'],specs['antennapower'],specs['antennamindamage'],specs['antennaminpower'],specs['antennabreakdamage'],specs['antennamaxhealth'],specs['antennamaxpower'],specs['antennareceivelist'])
        self.stations = {1:{'name':'Commander','taken':False},2:{'name':'Navigations','taken':False},3:{'name':'Tactical','taken':False},4:{'name':'Operations','taken':False},5:{'name':'Engineer','taken':False},6:{'name':'Main View Screen','taken':False}}
class AlertModule:
    def __init__(self, parentmission, alertstatus, health, power, mindamage, minpower, breakdamage, maxhealth, maxpower):
        self.parentmission = parentmission
        self.alertstatus = alertstatus
        self.health = health
        self.power = power
        self.mindamage = mindamage
        self.minpower = minpower
        self.breakdamage = breakdamage
        self.maxhealth = maxhealth
        self.maxpower = maxpower
    def changestatus(self,alertstatus):
        if self.health > self.mindamage and self.power > self.minpower:
            self.alertstatus = alertstatus
            if self.alertstatus == 0:
                self.parentmission.parentmission.SaveGame()
            self.parentmission.parentmission.socket.emit('alert',alertstatus,namespace="/station1")
            self.parentmission.parentmission.socket.emit('alert',alertstatus,namespace="/station6")
            return True
        else:
            return False
    def action(self):
        pass
class AntennaModule:
    def __init__(self, parentmission, antennarange, antennastrength, health, power, mindamage, minpower, breakdamage, maxhealth, maxpower, receivelist):
        self.parentmission = parentmission
        self.antennarange = antennarange
        self.antennastrength = antennastrength
        self.health = health
        self.power = power
        self.mindamage = mindamage
        self.minpower = minpower
        self.breakdamage = breakdamage
        self.maxhealth = maxhealth
        self.maxpower = maxpower
        self.receivelist = receivelist
        self.scanlist = []
    def scan(self):
        if self.power >= self.minpower and self.health >= self.mindamage:
            del self.scanlist[:]
            for obj in self.parentmission.parentmission.map.dictionary:
                if obj.type == "signal" and obj.data['frequency'] in self.receivelist:
                    if (obj.strength + (self.antennarange*(self.health/self.maxhealth))) * (obj.strength + (self.antennarange*(self.health/self.maxhealth)))<= self.distance(obj):
                        self.scanlist.append(obj)
    def distance(self,obj):
        xd = obj.x - self.parentmission.x
        yd = obj.y - self.parentmission.y
        zd = obj.z - self.parentmission.z
        return (xd*xd + yd*yd + zd*zd)
    def send(self,signal):
        if self.power >= self.minpower and self.health >= self.mindamage:
            signal.strength = self.antennastrength*(self.power/self.maxpower)
            signal.origin = self.parentmission.communicationsmodule.address
            self.parentmission.parentmission.map.Add(signal)
            return True
        else:
            return False
    def action(self):
        self.scan()
class CommunicationsModule:
    def __init__(self, parentmission, health, power, mindamage, minpower, breakdamage, maxhealth, maxpower, address):
        self.parentmission = parentmission
        self.health = health
        self.power = power
        self.mindamage = mindamage
        self.minpower = minpower
        self.breakdamage = breakdamage
        self.maxhealth = maxhealth
        self.maxpower = maxpower
        self.address = address
        self.connectedto = []
    def check(self):
        if self.power >= self.minpower and self.health >= self.mindamage:
            for obj in self.parentmission.antennamodule.scanlist:
                if obj.data['type'] == "MESSAGE" and obj.data['to'] == self.address:
                    self.parentmission.parentmission.socket.emit("message",obj.data, namespace="/station1")
                if obj.data['type'] == "MESSAGE" and obj.data['to'] != self.address:
                    if obj.origin in self.connectedto:
                        self.parentmission.antennamodule.send(obj)
                if obj.data['type'] == "DISCONNECTION" and obj.data['to'] == self.address:
                    if obj.data['from'] in self.connectedto:
                        self.connectedto.remove(obj.data['from'])
                        self.parentmission.antennamodule.send(Signal(self.address,{"type":"DISCONNECTION","to":obj.data["from"]}))
                        self.parentmission.parentmission.socket.emit('disconnected',obj.data["from"],namespace="/station4")
                if obj.data['type'] == "CONNECTION" and obj.data['to'] == self.address:
                    if obj.data['from'] in self.connectedto:
                        self.connectedto.append(obj.data['from'])
                        self.parentmission.parentmission.socket.emit('connected',obj.data['from'],namespace="/station4")
                    else:
                        self.parentmission.parentmission.socket.emit('connectrequest',obj.data['from'],namespace="/station4")
    def send(self, message, toaddress):
        if self.power >= self.minpower and self.health >= self.mindamage:
            signal = Signal(self.address,{"type":"MESSAGE","to":toaddress,"message":message, "from":self.address})
            return self.parentmission.antennamodule.send(signal)
        else:
            return False
    def connect(self, toaddress):
        if self.power >= self.minpower and self.health >= self.mindamage:
            signal = Signal(self.address,{"type":"CONNECTION","to":toaddress,"from":self.address})
            return self.parentmission.antennamodule.send(signal)
        else:
            return False
    def disconnect(self, toaddress):
        if self.power >= self.minpower and self.health >= self.mindamage:
            self.connectedto.remove(address)
            signal = Signal(self.address,{"type":"DISCONNECTION","to":toaddress,"message":message, "from":self.address})
            return self.parentmission.antennamodule.send(signal)
        else:
            return False
    def action(self):
        self.check()
class Signal:
    def __init__(self,origin,data):
        self.origin = origin
        self.data = data
newmap = Map()
vesselspecs = {'x':0,'y':0,'z':0,'alertstatus':0,'alerthealth':100,'alertpower':100,'alertmindamage':5,'alertminpower':5,'alertbreakdamage':3,'alertmaxhealth':100,'alertmaxpower':100,'antennarange':10,'antennastrength':5,'antennahealth':100,'antennapower':100,'antennamindamage':5,'antennaminpower':5,'antennabreakdamage':3,'antennamaxhealth':100,'antennamaxpower':100,'antennareceivelist':[1,80,3000],'communicationshealth':100,'communicationspower':100,'communicationsmindamage':5,'communicationsminpower':5,'communicationsbreakdamage':3,'communicationsmaxhealth':100,'communicationsmaxpower':100,'communicationsaddress':9820216841}
newid = newmap.Add(Vessel(vesselspecs))
dictionary = {'status':0, 'name':'It\'s Mine', 'map':newmap, 'id':newid, 'obj':None}
f = open('missions/Trevor.mis','wb')
pickle.dump(dictionary,f)
f.close()
