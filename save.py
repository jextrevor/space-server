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
        self.timethread = None
        self.actionthread = None
        self.lock = None
        self.running = True
        self.willsave = False
        self.timethrough = False
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
    def move(self):
        while self.running:
            for key in self.map.dictionary.keys():
                self.map.dictionary[key].move(self)
            self.timethrough = True
            if self.willsave == True:
                while self.willsave == True:
                    pass
            self.timethrough = False
    def action(self):
        while self.running:
            for key in self.map.dictionary.keys():
                self.map.dictionary[key].action()
            if self.willsave == True:
                while self.timethrough == False:
                    pass
                self.SaveGame()
                self.willsave = False
    def terminate(self):
        self.running = False
        self.status = 0
        self.emittoallstations("status", "0")
        self.GetVessel().musicmodule.theme = 0
        self.socket.emit("theme",str(0), namespace="/station6")
    def fail(self):
        self.running = False
        self.status = 4
        self.emittoallstations("status", "4")
        self.GetVessel().musicmodule.theme = 0
        self.socket.emit("theme",str(0), namespace="/station6")
    def win(self):
        self.running = False
        self.status = 3
        self.emittoallstations("status", "3")
        self.GetVessel().musicmodule.theme = 0
        self.socket.emit("theme",str(0), namespace="/station6")
    def emittoallstations(self,key,value):
        for i in range(len(self.GetStations())+1):
            self.socket.emit(key, value,namespace="/station"+str(i))
    def Start(self):
        self.status = 2
        self.emittoallstations("status","2")
        self.running = True
        self.SaveGame()
        self.timethread = threading.Thread(target=self.move)
        self.timethread.dameon = True
        self.timethread.start()
        self.actionthread = threading.Thread(target=self.action)
        self.actionthread.dameon = True
        self.actionthread.start()
        self.GetVessel().update()
    def StopCountdown(self):
        self.timer.cancel()
        self.status = 1
        self.emittoallstations("status","1")
    def SaveGame(self):
        self.map.dictionary[self.vessel].parentmission = None
        dictionary = {'status':self.status, 'name':self.name, 'map':self.map, 'id':self.vessel}
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
        self.type = "vessel"
        self.parentmission = None
        self.x = specs['x']
        self.y = specs['y']
        self.z = specs['z']
        self.control = specs['control']
        self.objectives = Objectives(self,specs['briefing'])
        self.musicmodule = MusicModule(self)
        self.objectives.init(specs['inorder'],specs['mustnot'],specs['events'],specs['musthave'],specs['eventlist'])
        self.alertmodule = AlertModule(self,specs['alertstatus'],specs['alerthealth'],specs['alertpower'],specs['alertmindamage'],specs['alertminpower'],specs['alertbreakdamage'],specs['alertmaxhealth'],specs['alertmaxpower'])
        self.communicationsmodule = CommunicationsModule(self,specs['communicationshealth'],specs['communicationspower'],specs['communicationsmindamage'],specs['communicationsminpower'],specs['communicationsbreakdamage'],specs['communicationsmaxhealth'],specs['communicationsmaxpower'],specs['communicationsaddress'])
        self.antennamodule = AntennaModule(self,specs['antennarange'],specs['antennastrength'],specs['antennahealth'],specs['antennapower'],specs['antennamindamage'],specs['antennaminpower'],specs['antennabreakdamage'],specs['antennamaxhealth'],specs['antennamaxpower'],specs['antennareceivelist'])
        self.stations = {1:{'name':'Commander','taken':False},2:{'name':'Navigations','taken':False},3:{'name':'Tactical','taken':False},4:{'name':'Operations','taken':False},5:{'name':'Engineer','taken':False},6:{'name':'Main View Screen','taken':False}}
    def update(self):
        self.alertmodule.update()
        self.musicmodule.update()
        self.communicationsmodule.update()
        self.antennamodule.update()
        self.objectives.update()
    def action(self):
        self.alertmodule.action()
        self.musicmodule.action()
        self.communicationsmodule.action()
        self.antennamodule.action()
        self.objectives.action()
    def move(self,parentmission):
        pass
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
                self.parentmission.parentmission.willsave = True
            self.parentmission.parentmission.socket.emit('alert',alertstatus,namespace="/station1")
            self.parentmission.parentmission.socket.emit('alert',alertstatus,namespace="/station6")
            return True
        else:
            return False
    def action(self):
        pass
    def update(self):
        self.parentmission.parentmission.socket.emit('alert',self.alertstatus,namespace="/station1")
        self.parentmission.parentmission.socket.emit('alert',self.alertstatus,namespace="/station6")
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
            for obj in self.parentmission.parentmission.map.dictionary.values():
                if obj.type == "signal" and obj.data['frequency'] in self.receivelist:
                    if (obj.strength + (self.antennarange*(self.health/self.maxhealth))) * (obj.strength + (self.antennarange*(self.health/self.maxhealth)))>= self.distance(obj):
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
    def update(self):
        pass
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
        self.frequency = 1
        self.connectedto = []
        self.messages = []
    def check(self):
        if self.power >= self.minpower and self.health >= self.mindamage:
            for obj in self.parentmission.antennamodule.scanlist:
                if obj.data['type'] == "MESSAGE" and obj.data['to'] == self.address:
                    if obj.data not in self.messages:
                        self.messages.append(obj.data)
                        self.parentmission.parentmission.socket.emit("newmessage",obj.data, namespace="/station1")
                if obj.data['type'] == "MESSAGE" and obj.data['to'] == 0:
                    if obj.data not in self.messages:
                        self.messages.append(obj.data)
                        self.parentmission.parentmission.socket.emit("newmessage",obj.data, namespace="/station1")
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
    def send(self, message, toaddress, frequency):
        if self.power >= self.minpower and self.health >= self.mindamage:
            signal = Signal(self.parentmission.x, self.parentmission.y, self.parentmission.z, self.address,{"type":"MESSAGE","to":toaddress,"message":message, "from":self.address, "frequency":frequency})
            return self.parentmission.antennamodule.send(signal)
        else:
            return False
    def connect(self, toaddress):
        if self.power >= self.minpower and self.health >= self.mindamage:
            signal = Signal(self.parentmission.x, self.parentmission.y, self.parentmission.z, self.address,{"type":"CONNECTION","to":toaddress,"from":self.address})
            return self.parentmission.antennamodule.send(signal)
        else:
            return False
    def disconnect(self, toaddress):
        if self.power >= self.minpower and self.health >= self.mindamage:
            self.connectedto.remove(address)
            signal = Signal(self.parentmission.x, self.parentmission.y, self.parentmission.z, self.address,{"type":"DISCONNECTION","to":toaddress,"message":message, "from":self.address})
            return self.parentmission.antennamodule.send(signal)
        else:
            return False
    def action(self):
        self.check()
    def setfreq(self,newfrequency):
        if self.power >= self.minpower and self.health >= self.mindamage:
            self.frequency = newfrequency
            self.parentmission.parentmission.socket.emit("frequency",self.frequency, namespace="/station1")
            return True
        else:
            return False
    def update(self):
        self.parentmission.parentmission.socket.emit("clearmessage","",namespace="/station1")
        self.parentmission.parentmission.socket.emit("frequency",self.frequency, namespace="/station1")
        self.messages.append({'type':"MESSAGE",'to':self.address,'from':19216801,'message':"Anyone there?"})
        for i in self.messages:
            self.parentmission.parentmission.socket.emit("addmessage",i, namespace="/station1")
        for i in self.connectedto:
            self.parentmission.parentmission.socket.emit("connected",i, namespace="/station4")
class Signal:
    def __init__(self,x,y,z,origin,data):
        self.origin = origin
        self.data = data
        self.type="signal"
        self.x = x
        self.y = y
        self.z = z
    def action(self):
        pass
    def move(self,parentmission):
        self.strength -= 0.0000000001
        if self.strength <= 0:
            for name, age in parentmission.map.dictionary.items():
                if age == self:
                    del parentmission.map.dictionary[name]
class Objectives:
    def __init__(self, parentmission, briefingmessage):
        self.inorder = []
        self.currentobjective = 0
        self.mustnot = []
        self.events = []
        self.parentmission = parentmission
        self.musthave = []
        self.eventlist  = []
        self.briefingmessage = briefingmessage
    def action(self):
        if self.currentobjective < len(self.inorder):
            self.inorder[self.currentobjective].check()
            if self.inorder[self.currentobjective].done == True:
                self.parentmission.parentmisison.socket.emit("objective", self.currentobjective, namespace="/station1")
                self.currentobjective += 1
        for i in self.mustnot:
            i.check()
            if i.done == True:
                self.parentmission.parentmission.fail()
        for i in self.events:
            i.check()
        if self.currentobjective >= len(self.inorder):
            readytowin = True
            for i in self.musthave:
                i.check()
                if i.done != True:
                    readytowin = False
            if readytowin == True:
                self.parentmission.parentmission.win()
    def init(self, inorder, mustnot, events, musthave, eventlist):
        for key, value in inorder.iteritems():
            self.inorder.append(Objective(self,key,value))
        for key, value in mustnot.iteritems():
            self.mustnot.append(Objective(self,key,value))
        for key, value in events.iteritems():
            self.events.append(Objective(self,key,value))
        for key, value in musthave.iteritems():
            self.musthave.append(Objective(self,key,value))
        self.eventlist = eventlist
    def update(self):
        self.parentmission.parentmission.socket.emit("objectives", self.eventlist, namespace="/station1")
        self.parentmission.parentmisison.socket.emit("objective", self.currentobjective, namespace="/station1")
class Objective:
    def __init__(self, parent, code, eventcode):
        self.parent = parent
        self.code = code
        self.eventcode = eventcode
        self.done = False
    def check(self):
        exec self.code
        if self.done == True:
            exec self.eventcode
class MusicModule:
    def __init__(self, parentmission):
        self.parentmission = parentmission
        self.theme = 0
    def update(self):
        self.parentmission.parentmission.socket.emit("theme",str(self.theme), namespace="/station6")
    def action(self):
        if self.theme == 0 and self.parentmission.parentmission.status == 2:
            self.theme = 1
            self.parentmission.parentmission.socket.emit("theme",str(self.theme), namespace="/station6")
        if self.theme != 0 and self.parentmission.parentmission.status == 3:
            self.theme = 0
            self.parentmission.parentmission.socket.emit("theme",str(self.theme), namespace="/station6")
        if self.theme != 0 and self.parentmission.parentmission.status == 4:
            self.theme = 0
            self.parentmission.parentmission.socket.emit("theme",str(self.theme), namespace="/station6")
        if self.theme != 0 and self.parentmission.parentmission.status == 0:
            self.theme = 0
            self.parentmission.parentmission.socket.emit("theme",str(self.theme), namespace="/station6")
        if self.inbattle() == True and self.theme != 4:
            self.theme = 4
            self.parentmission.parentmission.socket.emit("theme",str(self.theme), namespace="/station6")
        elif self.intense() == True and self.theme != 3:
            self.theme = 3
            self.parentmission.parentmission.socket.emit("theme",str(self.theme), namespace="/station6")
        elif self.tense() == True and self.theme != 2:
            self.theme = 2
            self.parentmission.parentmission.socket.emit("theme",str(self.theme), namespace="/station6")
        elif self.theme != 1:
            self.theme = 1
            self.parentmission.parentmission.socket.emit("theme",str(self.theme), namespace="/station6")
    def inbattle(self):
        return False
    def intense(self):
        return False
    def tense(self):
        if self.parentmission.alertmodule.alertstatus != 0:
            return True
        else:
            return False
newmap = Map()
vesselspecs = {'x':0,'y':0,'z':0,'eventlist':['Set the alert status to red.','Set the alert status to yellow.','Set the alert status to red.'],'inorder':{"if self.parent.parentmission.alertmodule.alertstatus == 2:\n    self.done = True":"pass","if self.parent.parentmission.alertmodule.alertstatus == 1:\n    self.done = True":"pass","if self.parent.parentmission.alertmodule.alertstatus == 2:\n    self.done = True":"pass"},'mustnot':{},'events':{},'musthave':{},'briefing':"hey",'control':"UFP",'alertstatus':0,'alerthealth':100,'alertpower':100,'alertmindamage':5,'alertminpower':5,'alertbreakdamage':3,'alertmaxhealth':100,'alertmaxpower':100,'antennarange':10,'antennastrength':5,'antennahealth':100,'antennapower':100,'antennamindamage':5,'antennaminpower':5,'antennabreakdamage':3,'antennamaxhealth':100,'antennamaxpower':100,'antennareceivelist':[1,80,3000],'communicationshealth':100,'communicationspower':100,'communicationsmindamage':5,'communicationsminpower':5,'communicationsbreakdamage':3,'communicationsmaxhealth':100,'communicationsmaxpower':100,'communicationsaddress':9820216841}
newid = newmap.Add(Vessel(vesselspecs))
dictionary = {'status':0, 'name':'It\'s Mine', 'map':newmap, 'id':newid}
f = open('missions/Trevor.mis','wb')
pickle.dump(dictionary,f)
f.close()
