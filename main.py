from flask import Flask,render_template,request,redirect,url_for
import threading
import pickle
import time
import sys
from os import listdir
from os.path import isfile, join
from math import atan2,degrees,sin,cos,pow,sqrt,asin,acos
import math
from time import sleep
from flask.ext.socketio import SocketIO, emit, join_room, leave_room
import urllib
app = Flask(__name__)
socketio = SocketIO(app)
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
        self.warpmodule.action()
        self.thrustermodule.action()
        self.antennamodule.action()
        self.objectives.action()
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
        if self.health <= self.instabledamage and self.warp > 0:
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
            pitch = math.degrees(math.acos(normalizez))
            if math.sin(pitch) != 0:
                yaw = math.degrees(math.acos(normalizex/math.sin(pitch)))
            else:
                yaw = math.degrees(math.acos(normalizey/math.cos(pitch)))
            return self.parentmission.thrustermodule.setdegrees(pitch,yaw)
        else:
            return False
    def update(self):
        self.parentmission.parentmission.socket.emit("course",{"x":self.coursex,"y":self.coursey,"z":self.coursez},namespace="/station2")
    def action(self):
        pass
def allstationconnect(key):
    print "Station "+str(key)+" connected"
    mission.join(key)
    emit('lobbystations',mission.GetStations(), namespace="/lobby")
    with open("static/js/station"+str(key)+".js","r") as myfile:
        emit('js',myfile.read())
    with open("static/html/station"+str(key)+".html") as myfile:
        emit('html',myfile.read())
    with open("static/html/training"+str(key)+".html") as myfile:
        emit('briefingmessage',myfile.read() + mission.GetVessel().objectives.briefingmessage)
def allstationdisconnect(key):
    print "Station "+str(key)+" disconnected"
    if mission.status == 1.5:
        mission.StopCountdown()
    mission.GetStations()[key]["taken"] = False
    if mission.status == 2:
        mission.terminate()
    if mission.status >= 2:
        readytodelete = True
        for dict in mission.GetStations().itervalues():
            if dict["taken"] == True:
                readytodelete = False
            if readytodelete == True:
                mission.terminate()
@socketio.on('connect', namespace="/lobby")
def connect():
    status = None
    if 'mission' not in globals():
        status = 0
    if 'mission' in globals():
        status = mission.status
    emit('lobbyconnect',status)
    if status == 0:
        missiondict = {}
        filelist = listdir('missions/')
        for f in filelist:
            missiondict[f] = pickle.load(open('missions/'+f))['name']
        emit('lobbymissionlist',missiondict)
    if status == 1:
        emit('lobbyname',mission.name)
        emit('lobbystations',mission.GetStations())
@socketio.on('lobbychoose', namespace="/lobby")
def choose(json):
    global mission 
    mission = Mission(json)
    mission.status = 1
    mission.socket = socketio
    emit('lobbyconnect',1,broadcast=True)
    emit('lobbyname',mission.name, broadcast=True)
    emit('lobbystations',mission.GetStations(), broadcast=True)
@socketio.on('lobbyjoin', namespace="/lobby")
def join(json):
    for key, value in mission.GetStations().iteritems():
        if str(key) == json:
            taken = value['taken']
            if taken == False:
                emit("lobbyjoin",str(key))
    emit('lobbystations',mission.GetStations(), broadcast=True)
@socketio.on('connect', namespace="/station1")
def stationconnect():
    allstationconnect(1)
@socketio.on('disconnect', namespace="/station1")
def stationdisconnect():
    allstationdisconnect(1)
@socketio.on('setalert', namespace="/station1")
def setalert(json):
    responding = mission.map.dictionary[mission.vessel].alertmodule.changestatus(json)
    if responding == False:
        emit("message", "not responding", namespace="/station1")
@socketio.on('setfreq', namespace="/station1")
def setalert(json):
    responding = mission.map.dictionary[mission.vessel].communicationsmodule.setfreq(json)
    if responding == False:
        emit("message", "not responding", namespace="/station1")
@socketio.on('sendmessage', namespace="/station1")
def sendmessage(json):
    responding = mission.map.dictionary[mission.vessel].communicationsmodule.send(json['message'],json['to'],mission.map.dictionary[mission.vessel].communicationsmodule.frequency)
    if responding == False:
        emit("message", "not responding", namespace="/station1")
@socketio.on('message', namespace="/station1")
def message(json):
    if json == "restart":
        mission.LoadGame()
@socketio.on('connect', namespace="/station2")
def stationconnect():
    allstationconnect(2)
@socketio.on('setwarp', namespace="/station2")
def setwarp(json):
    responding = mission.map.dictionary[mission.vessel].warpmodule.setwarpspeed(json)
    if responding == False:
        emit("message", "not responding", namespace="/station2")
@socketio.on('setimpulse', namespace="/station2")
def setimpulse(json):
    responding = mission.map.dictionary[mission.vessel].impulsemodule.setspeed(json)
    if responding == False:
        emit("message", "not responding", namespace="/station2")
@socketio.on("changepitch", namespace="/station2")
def changepitch(json):
    responding = mission.GetVessel().thrustermodule.changedegrees(json['pitch'],json['yaw'])
    if responding == False:
        emit("message", "not responding", namespace="/station2")
@socketio.on("setcourse", namespace="/station2")
def setcourse(json):
    responding = mission.GetVessel().coursemodule.setcourse(json['x'],json['y'],json['z'])
    if responding == False:
        emit("message", "not responding", namespace="/station2")
@socketio.on('disconnect', namespace="/station2")
def stationdisconnect():
    allstationdisconnect(2)
@socketio.on('connect', namespace="/station3")
def stationconnect():
    allstationconnect(3)
@socketio.on('disconnect', namespace="/station3")
def stationdisconnect():
    allstationdisconnect(3)
@socketio.on('connect', namespace="/station4")
def stationconnect():
    allstationconnect(4)
@socketio.on('disconnect', namespace="/station4")
def stationdisconnect():
    allstationdisconnect(4)
@socketio.on('connect', namespace="/station5")
def stationconnect():
    allstationconnect(5)
@socketio.on('disconnect', namespace="/station5")
def stationdisconnect():
    allstationdisconnect(5)
@socketio.on('connect', namespace="/station6")
def stationconnect():
    allstationconnect(6)
@socketio.on('disconnect', namespace="/station6")
def stationdisconnect():
    allstationdisconnect(6)
@app.route('/')
def home():
    templateData = {
        }
    return render_template('main.html', **templateData)
@app.errorhandler(404)
def page_not_found(error):
    templateData = {
        'error':"Error 404:"+error
        }
    return render_template("error.html",**templateData)
@app.errorhandler(500)
def internalerror(error):
    templateData = {
        'error':"Error 500:"+error
        }
    return render_template("error.html",**templateData)
@app.after_request
def no_cache(response):
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'no-cache, no-store'
    response.headers['Pragma'] = 'no-cache'
    return response
if __name__ == '__main__':
    print "Server running"
    socketio.run(app, "0.0.0.0",80)
