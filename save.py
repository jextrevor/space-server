import pickle
import threading
from math import atan2,degrees,sin,cos,pow,sqrt,asin,acos
import math
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
            time.sleep(0.001)
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
        self.thrustermodule = ThrusterModule(self,specs['thrusterhealth'],specs['thrusterpower'],specs['thrustermindamage'],specs['thrusterminpower'],specs['thrusterbreakdamage'],specs['thrustermaxhealth'],specs['thrustermaxpower'])
        self.alertmodule = AlertModule(self,specs['alertstatus'],specs['alerthealth'],specs['alertpower'],specs['alertmindamage'],specs['alertminpower'],specs['alertbreakdamage'],specs['alertmaxhealth'],specs['alertmaxpower'])
        self.coursemodule = CourseModule(self,specs['coursehealth'],specs['coursepower'],specs['coursemindamage'],specs['courseminpower'],specs['coursebreakdamage'],specs['coursemaxhealth'],specs['coursemaxpower'])
        self.communicationsmodule = CommunicationsModule(self,specs['communicationshealth'],specs['communicationspower'],specs['communicationsmindamage'],specs['communicationsminpower'],specs['communicationsbreakdamage'],specs['communicationsmaxhealth'],specs['communicationsmaxpower'],specs['communicationsaddress'])
        self.warpmodule = WarpModule(self,specs['warphealth'], specs['warpstability'], specs['warpmaxstability'], specs['warppower'], specs['warpmindamage'], specs['warpminpower'], specs['warpbreakdamage'], specs['warphealth'], specs['warpmaxpower'], specs['warpinstabledamage'], specs['warpinstablewarp'], specs['warpinstableheat'], specs['warpbreakheat'], specs['warpmaxheat'], specs['warpmaxwarp'], specs['warpheatwarp'], specs['warpheathealth'])
        self.impulsemodule = ImpulseModule(self,specs['impulsehealth'],specs['impulsepower'],specs['impulsemindamage'],specs['impulseminpower'],specs['impulsebreakdamage'],specs['impulsemaxhealth'],specs['impulsemaxpower'],specs['impulsebreakheat'],specs['impulsemaxheat'],specs['impulsespeed'],specs['impulseheatspeed'],specs['impulseheathealth'])
        self.antennamodule = AntennaModule(self,specs['antennarange'],specs['antennastrength'],specs['antennahealth'],specs['antennapower'],specs['antennamindamage'],specs['antennaminpower'],specs['antennabreakdamage'],specs['antennamaxhealth'],specs['antennamaxpower'],specs['antennareceivelist'])
        self.radarmodule = RadarModule(self,specs['radarhealth'],specs['radarpower'],specs['radarmindamage'],specs['radarminpower'],specs['radarbreakdamage'],specs['radarmaxhealth'],specs['radarmaxpower'],specs['radarranges'])
        self.mapmodule = MapModule(self,specs['maphealth'],specs['mappower'],specs['mapmindamage'],specs['mapminpower'],specs['mapbreakdamage'],specs['mapmaxhealth'],specs['mapmaxpower'])
        self.stations = {1:{'name':'Commander','taken':False},2:{'name':'Navigator','taken':False},3:{'name':'Tactical','taken':False},4:{'name':'Operations','taken':False},5:{'name':'Engineer','taken':False},6:{'name':'Main View Screen','taken':False}}
    def update(self):
        self.alertmodule.update()
        self.musicmodule.update()
        self.communicationsmodule.update()
        self.antennamodule.update()
        self.objectives.update()
        self.thrustermodule.update()
        self.coursemodule.update()
        self.warpmodule.update()
        self.impulsemodule.update()
        self.radarmodule.update()
        self.mapmodule.update()
    def action(self):
        self.alertmodule.action()
        self.musicmodule.action()
        self.communicationsmodule.action()
        self.warpmodule.action()
        self.thrustermodule.action()
        self.antennamodule.action()
        self.impulsemodule.action()
        self.objectives.action()
        self.mapmodule.action()
        self.coursemodule.action()
        self.radarmodule.action()
    def move(self,parentmission):
        self.warpmodule.move(parentmission)
        self.impulsemodule.move(parentmission)
        magnitude = 0
        if self.warpmodule.health >= self.warpmodule.mindamage and self.warpmodule.power >= self.warpmodule.minpower and self.warpmodule.warpspeed > 0:
            magnitude += 0.002003989 * math.pow(self.warpmodule.warpspeed,10/3)
        if self.impulsemodule.health >= self.impulsemodule.mindamage and self.impulsemodule.power >= self.impulsemodule.minpower and self.impulsemodule.magnitude > 0:
            magnitude += 0.000486437 * self.impulsemodule.magnitude * self.impulsemodule.impulsespeed
        xchange = math.sin(math.radians(self.thrustermodule.pitch)) * math.cos(math.radians(self.thrustermodule.yaw)) * magnitude
        ychange = math.sin(math.radians(self.thrustermodule.pitch)) * math.sin(math.radians(self.thrustermodule.yaw)) * magnitude
        zchange = math.cos(math.radians(self.thrustermodule.pitch)) * magnitude
        self.x += xchange
        self.y += ychange
        self.z += zchange
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
                    if (obj.strength + (self.antennarange*(self.health/self.maxhealth)*(self.power/self.maxpower))) * (obj.strength + (self.antennarange*(self.health/self.maxhealth)*(self.power/self.maxpower)))>= self.distance(obj):
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
                self.currentobjective += 1
                self.parentmission.parentmission.socket.emit("objective", self.currentobjective, namespace="/station1")
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
        for value in inorder:
            self.inorder.append(Objective(self,value[0],value[1]))
        for value in mustnot:
            self.mustnot.append(Objective(self,value[0],value[1]))
        for value in events:
            self.events.append(Objective(self,value[0],value[1]))
        for value in musthave:
            self.musthave.append(Objective(self,value[0],value[1]))
        self.eventlist = eventlist
    def update(self):
        self.parentmission.parentmission.socket.emit("objectives", {"eventlist":self.eventlist}, namespace="/station1")
        self.parentmission.parentmission.socket.emit("objective", self.currentobjective, namespace="/station1")
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
        if self.inbattle() == True:
            if self.theme != 4:
                self.theme = 4
                self.parentmission.parentmission.socket.emit("theme",str(self.theme), namespace="/station6")
        elif self.intense() == True:
            if self.theme != 3:
                self.theme = 3
                self.parentmission.parentmission.socket.emit("theme",str(self.theme), namespace="/station6")
        elif self.tense() == True:
            if self.theme != 2:
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
class WarpModule:
    def __init__(self,parentmission,health, stability, maxstability, power, mindamage, minpower, breakdamage, maxhealth, maxpower, instabledamage, instablewarp, instableheat, breakheat, maxheat, maxwarp, heatwarp, heathealth):
        self.parentmission = parentmission
        self.health = health
        self.stability = stability
        self.maxstability = maxstability
        self.power = power
        self.mindamage = mindamage
        self.minpower = minpower
        self.breakdamage = breakdamage
        self.maxhealth = maxhealth
        self.maxpower = maxpower
        self.instabledamage = instabledamage
        self.instablewarp = instablewarp
        self.instableheat = instableheat
        self.breakheat = breakheat
        self.maxheat = maxheat
        self.maxwarp = maxwarp
        self.heatwarp = heatwarp
        self.heathealth = heathealth
        self.warpspeed = 0
        self.heat = 0
    def setwarpspeed(self,warpspeed):
        if self.health >= self.mindamage and self.power >= self.minpower:
            if self.warpspeed == 0 and warpspeed != 0:
                self.parentmission.parentmission.socket.emit("startwarp","",namespace="/station6")
            if self.warpspeed != 0 and warpspeed == 0:
                self.parentmission.parentmission.socket.emit("endwarp","",namespace="/station6")
            self.warpspeed = warpspeed
            self.parentmission.parentmission.socket.emit("warpspeed",self.warpspeed, namespace="/station2")
            return True
        else:
            return False
    def update(self):
        self.parentmission.parentmission.socket.emit("warpspeed",self.warpspeed, namespace="/station2")
    def action(self):
        pass
    def move(self,parentmission):
        if self.warpspeed >= self.heatwarp:
            self.heat += 0.01
        if self.health <= self.heathealth:
            self.heat += 0.01
        if self.heat >= self.breakheat:
            self.heat = self.breakheat
            self.health -= self.maxhealth
        if self.health <= self.instabledamage and self.warpspeed > 0:
            self.stability -= 0.01
        if self.warpspeed >= self.instablewarp:
            self.stability -= 0.01
        if self.heat >= self.instableheat:
            self.stability -= 0.01
        if self.stability < self.maxstability:
            self.stability += 0.005
        else:
            self.stability = self.maxstability
        if self.stability <= 0:
            self.stability = 0
            self.health -= self.maxhealth
class ThrusterModule:
    def __init__(self,parentmission,health,power,mindamage,minpower,breakdamage,maxhealth,maxpower):
        self.parentmission = parentmission
        self.health = health
        self.power = power
        self.mindamage = mindamage
        self.minpower = minpower
        self.breakdamage = breakdamage
        self.maxhealth = maxhealth
        self.maxpower = maxpower
        self.pitch = 0
        self.yaw = 0
    def changedegrees(self,pitch,yaw):
        if self.health >= self.mindamage and self.power >= self.minpower:
            self.pitch += pitch
            self.yaw += yaw
            self.parentmission.parentmission.socket.emit("degrees",{"pitch":self.pitch,"yaw":self.yaw},namespace="/station2")
            return True
        else:
            return False
    def setdegrees(self,pitch,yaw):
        if self.health >= self.mindamage and self.power >= self.minpower:
            self.pitch = pitch
            self.yaw = yaw
            self.parentmission.parentmission.socket.emit("degrees",{"pitch":self.pitch,"yaw":self.yaw},namespace="/station2")
            return True
        else:
            return False
    def update(self):
        self.parentmission.parentmission.socket.emit("degrees",{"pitch":self.pitch,"yaw":self.yaw},namespace="/station2")
    def action(self):
        pass
class ImpulseModule:
    def __init__(self,parentmission,health,power,mindamage,minpower,breakdamage,maxhealth,maxpower,breakheat,maxheat,impulsespeed,heatspeed,heathealth):
        self.parentmission = parentmission
        self.health = health
        self.power = power
        self.mindamage = mindamage
        self.minpower = minpower
        self.breakdamage = breakdamage
        self.maxhealth = maxhealth
        self.maxpower = maxpower
        self.breakheat = breakheat
        self.maxheat = maxheat
        self.heat = 0
        self.impulsespeed = impulsespeed
        self.heatspeed = heatspeed
        self.heathealth = heathealth
        self.magnitude = 0
    def setspeed(self,speed):
        if self.health >= self.mindamage and self.power >= self.minpower:
            self.magnitude = speed
            self.parentmission.parentmission.socket.emit("impulsespeed",self.magnitude,namespace="/station2")
            return True
        else:
            return False
    def update(self):
        self.parentmission.parentmission.socket.emit("impulsespeed",self.magnitude,namespace="/station2")
    def move(self,parentmission):
        if self.impulsespeed >= self.heatspeed:
            self.heat += 0.01
        if self.health <= self.heathealth:
            self.heat += 0.01
        if self.heat >= self.breakheat:
            self.heat = self.breakheat
            self.health -= self.maxhealth
    def action(self):
        pass
class CourseModule:
    def __init__(self,parentmission,health,power,mindamage,minpower,breakdamage,maxhealth,maxpower):
        self.parentmission = parentmission
        self.health = health
        self.power = power
        self.mindamage = mindamage
        self.minpower = minpower
        self.breakdamage = breakdamage
        self.maxhealth = maxhealth
        self.maxpower = maxpower
        self.coursex = 0
        self.coursey = 0
        self.coursez = 0
    def setcourse(self,coursex,coursey,coursez):
        if self.health >= self.mindamage and self.power >= self.minpower:
            self.coursex = coursex
            self.coursey = coursey
            self.coursez = coursez
            self.parentmission.parentmission.socket.emit("course",{"x":self.coursex,"y":self.coursey,"z":self.coursez},namespace="/station2")
            coursex = coursex-self.parentmission.x
            coursey = coursey-self.parentmission.y
            coursez = coursez-self.parentmission.z
            if math.sqrt(coursex*coursex+coursey*coursey+coursez*coursez) != 0:
                normalizex = coursex / math.sqrt(coursex*coursex+coursey*coursey+coursez*coursez)
                normalizey = coursey / math.sqrt(coursex*coursex+coursey*coursey+coursez*coursez)
                normalizez = coursez / math.sqrt(coursex*coursex+coursey*coursey+coursez*coursez)
            pitch = math.acos(normalizez)
            if math.sin(pitch) != 0:
                yaw = math.acos(normalizex/math.sin(pitch))
            else:
                yaw = math.acos(normalizey/math.cos(pitch))
            return self.parentmission.thrustermodule.setdegrees(math.degrees(pitch),math.degrees(yaw))
        else:
            return False
    def update(self):
        self.parentmission.parentmission.socket.emit("course",{"x":self.coursex,"y":self.coursey,"z":self.coursez},namespace="/station2")
    def action(self):
        pass
class RadarModule:
    def __init__(self,parentmission,health,power,mindamage,minpower,breakdamage,maxhealth,maxpower,ranges):
        self.parentmission = parentmission
        self.health = health
        self.power = power
        self.mindamage = mindamage
        self.minpower = minpower
        self.breakdamage = breakdamage
        self.maxhealth = maxhealth
        self.maxpower = maxpower
        self.ranges = ranges
        self.range = 0
        self.objects = []
    def setrange(self,setrange):
        if self.health >= self.mindamage and self.power >= self.minpower:
            self.range = setrange
            self.parentmission.parentmission.socket.emit("range",self.range,namespace="/station2")
            return True
        else:
            return False
    def action(self):
        if self.health >= self.mindamage and self.power >= self.minpower:
            for obj in self.objects:
                self.parentmission.parentmission.socket.emit("update",{"id":obj,"x":self.parentmission.parentmission.map.dictionary[obj].x,"y":self.parentmission.parentmission.map.dictionary[obj].y,"z":self.parentmission.parentmission.map.dictionary[obj].z},namespace="/station2")
                if self.distance(self.parentmission.parentmission.map.dictionary[obj]) > (self.ranges[self.range]*(self.health/self.maxhealth)*(self.power/self.maxpower)):
                    self.objects.remove(obj)
                    self.parentmission.parentmission.socket.emit("remove",obj,namespace="/station2")
            for key,value in self.parentmission.parentmission.map.dictionary.items():
                if self.distance(value) <= (self.ranges[self.range]*(self.health/self.maxhealth)*(self.power/self.maxpower)):
                    self.objects.append(key)
                    self.parentmission.parentmission.socket.emit("add",key,namespace="/station2")
                    self.parentmission.parentmission.socket.emit("update",{"id":key,"x":value.x,"y":value.y,"z":value.z},namespace="/station2")
    def distance(self,obj):
        xd = obj.x - self.parentmission.x
        yd = obj.y - self.parentmission.y
        zd = obj.z - self.parentmission.z
        return (xd*xd + yd*yd + zd*zd)
    def update(self):
        self.parentmission.parentmission.socket.emit("clearradar",0,namespace="/station2")
        for obj in self.objects:
            self.parentmission.parentmission.socket.emit("add",obj,namespace="/station2")
            self.parentmission.parentmission.socket.emit("update",{"id":obj,"x":self.parentmission.parentmission.map.dictionary[obj].x,"y":self.parentmission.parentmission.map.dictionary[obj].y,"z":self.parentmission.parentmission.map.dictionary[obj].z},namespace="/station2")
class MapModule:
    def __init__(self,parentmission,health,power,mindamage,minpower,breakdamage,maxhealth,maxpower):
        self.parentmission = parentmission
        self.health = health
        self.power = power
        self.mindamage = mindamage
        self.minpower = minpower
        self.breakdamage = breakdamage
        self.maxhealth = maxhealth
        self.maxpower = maxpower
        self.places = [{"placename":"California","placeinfo":"A tranquil yet expensive place"},{"placename":"Utah","placeinfo":"Place of awesomeness"},{"placename":"Idaho","placeinfo":"Bleak landscape where Napoleon Dynamite resides"},{"placename":"Tennis","placeinfo":"Unknown place"}]
    def addlist(self,newlist):
        if self.health >= self.mindamage and self.power >= self.minpower:
            self.places.extend(newlist)
            self.parentmission.parentmission.socket.emit("places",{"places":self.places},namespace="/station2")
            return True
        else:
            return False
    def action(self):
        pass
    def update(self):
        self.parentmission.parentmission.socket.emit("places",{"places":self.places},namespace="/station2")

newmap = Map()
vesselspecs = {'x':0,'y':0,'z':0,'eventlist':['Set the alert status to red.'],'inorder':[["pass","pass"]],'mustnot':[["pass","pass"]],'events':[],'musthave':[],'briefing':"hey",'control':"UFP",'alertstatus':0,'alerthealth':100,'alertpower':100,'alertmindamage':5,'alertminpower':5,'alertbreakdamage':3,'alertmaxhealth':100,'alertmaxpower':100,'antennarange':10,'antennastrength':5,'antennahealth':100,'antennapower':100,'antennamindamage':5,'antennaminpower':5,'antennabreakdamage':3,'antennamaxhealth':100,'antennamaxpower':100,'antennareceivelist':[1,80,3000],'communicationshealth':100,'communicationspower':100,'communicationsmindamage':5,'communicationsminpower':5,'communicationsbreakdamage':3,'communicationsmaxhealth':100,'communicationsmaxpower':100,'communicationsaddress':9820216841,'warphealth':100,'warppower':100,'warpmindamage':5,'warpminpower':5,'warpbreakdamage':3,'warpmaxhealth':100,'warpmaxpower':100,'warpstability':100,'warpmaxstability':100,'warpinstabledamage':50,'warpinstablewarp':9,'warpinstableheat':50,'warpbreakheat':95,'warpmaxheat':100,'warpmaxwarp':9.9,'thrusterhealth':100,'thrusterpower':100,'thrustermindamage':5,'thrusterminpower':5,'thrusterbreakdamage':3,'thrustermaxhealth':100,'thrustermaxpower':100,'impulsehealth':100,'impulsepower':100,'impulsemindamage':5,'impulseminpower':5,'impulsebreakdamage':3,'impulsemaxhealth':100,'impulsemaxpower':100,'impulsespeed':0.1,'impulsebreakheat':80,'impulsemaxheat':100,'warpheathealth':75,'warpheatwarp':7,'impulseheatspeed':2,'impulseheathealth':50,'coursehealth':100,'coursepower':100,'coursemindamage':5,'courseminpower':5,'coursebreakdamage':3,'coursemaxhealth':100,'coursemaxpower':100,'radarhealth':100,'radarpower':100,'radarmindamage':5,'radarminpower':5,'radarbreakdamage':3,'radarmaxhealth':100,'radarmaxpower':100,'radarranges':[1,5,10],'maphealth':100,'mappower':100,'mapmindamage':5,'mapminpower':5,'mapbreakdamage':3,'mapmaxhealth':100,'mapmaxpower':100}
newid = newmap.Add(Vessel(vesselspecs))
dictionary = {'status':0, 'name':'It\'s Mine', 'map':newmap, 'id':newid}
f = open('missions/Trevor.mis','wb')
pickle.dump(dictionary,f)
f.close()
