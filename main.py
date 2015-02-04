from flask import Flask,render_template,request,redirect,url_for
import threading
import pickle
import time
import sys
from os import listdir
from os.path import isfile, join
from math import atan2,degrees,sin,cos,pow,sqrt
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
        self.lock = threading.Lock()
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
        while True:
            for key, value in self.map.dictionary.iteritems():
                value.move()
    def action(self):
        while True:
            for key, value in self.map.dictionary.iteritems():
                value.action()
    def terminate(self):
        self.status = 0
        self.emittoallstations("status", "0")
    def fail(self):
        self.status = 4
        self.emittoallstations("status", "4")
    def win(self):
        self.status = 3
        self.emittoallstations("status", "3")
    def emittoallstations(self,key,value):
        for i in range(len(self.GetStations())+1):
            self.socket.emit(key, value,namespace="/station"+str(i))
    def Start(self):
        self.status = 2
        self.emittoallstations("status","2")
        self.timethread = threading.Thread(self.move)
        self.timethread.dameon = True
        self.SaveGame()
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
        self.parentmission = None
        self.x = specs['x']
        self.y = specs['y']
        self.z = specs['z']
        self.control = specs['control']
        self.objectives = Objectives(self,specs['briefing'])
        self.objectives.init(specs['inorder'],specs['mustnot'],specs['events'],specs['musthave'])
        self.alertmodule = AlertModule(self,specs['alertstatus'],specs['alerthealth'],specs['alertpower'],specs['alertmindamage'],specs['alertminpower'],specs['alertbreakdamage'],specs['alertmaxhealth'],specs['alertmaxpower'])
        self.communicationsmodule = CommunicationsModule(self,specs['communicationshealth'],specs['communicationspower'],specs['communicationsmindamage'],specs['communicationsminpower'],specs['communicationsbreakdamage'],specs['communicationsmaxhealth'],specs['communicationsmaxpower'],specs['communicationsaddress'])
        self.antennamodule = AntennaModule(self,specs['antennarange'],specs['antennastrength'],specs['antennahealth'],specs['antennapower'],specs['antennamindamage'],specs['antennaminpower'],specs['antennabreakdamage'],specs['antennamaxhealth'],specs['antennamaxpower'],specs['antennareceivelist'])
        self.stations = {1:{'name':'Commander','taken':False},2:{'name':'Navigations','taken':False},3:{'name':'Tactical','taken':False},4:{'name':'Operations','taken':False},5:{'name':'Engineer','taken':False},6:{'name':'Main View Screen','taken':False}}
    def update(self):
        self.alertmodule.update()
        self.communicationsmodule.update()
        self.antennamodule.update()
        self.objectives.update()
    def action(self):
        self.alertmodule.action()
        self.communicationsmodule.action()
        self.antennamodule.action()
        self.objectives.action()
    def move(self):
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
                self.parentmission.parentmission.SaveGame()
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
            signal = Signal(self.address,{"type":"MESSAGE","to":toaddress,"message":message, "from":self.address, "frequency":frequency})
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
    def setfreq(self,newfrequency):
        if self.power >= self.minpower and self.health >= self.mindamage:
            self.frequency = newfrequency
            self.parentmission.parentmission.socket.emit("frequency",self.frequency, namespace="/station1")
            return True
        else:
            return False
    def update(self):
        self.parentmission.parentmission.socket.emit("frequency",self.frequency, namespace="/station1")
        self.messages.append({'type':"MESSAGE",'to':self.address,'from':19216801,'message':"Anyone there?"})
        for i in self.messages:
            self.parentmission.parentmission.socket.emit("addmessage",i, namespace="/station1")
        for i in self.connectedto:
            self.parentmission.parentmission.socket.emit("connected",i, namespace="/station4")
class Signal:
    def __init__(self,origin,data):
        self.origin = origin
        self.data = data
class Objectives:
    def __init__(self, parentmission, briefingmessage):
        self.inorder = []
        self.currentobjective = 0
        self.mustnot = []
        self.events = []
        self.parentmission = parentmission
        self.musthave = []
        self.briefingmessage = briefingmessage
    def run(self):
        if self.currentobjective < len(self.inorder):
            self.inorder[self.currentobjective].check()
            if self.inorder[self.currentobjective].done == True:
                self.parentmission.parentmisison.socket.emit("objective", self.currentobjective, namespace="/station1")
                self.currentobjective += 1
        for i in mustnot:
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
    def init(self, inorder, mustnot, events, musthave):
        for key, value in inorder.iteritems():
            inorder.append(Objective(self,key,value))
        for key, value in mustnot.iteritems():
            mustnot.append(Objective(self,key,value))
        for key, value in events.iteritems():
            events.append(Objective(self,key,value))
        for key, value in musthave.iteritems():
            musthave.append(Objective(self,key,value))
    def update(self):
        pass
class Objective:
    def __init__(self, parent, code, eventcode):
        self.parent = parent
        self.code = code
        self.eventcode = eventcode
        self.done = False
    def check(self):
        eval(self.code)
        if self.done == True:
            eval(eventcode)
def allstationconnect(key):
    print "Station "+str(key)+" connected"
    mission.join(key)
    emit('lobbystations',mission.GetStations(), namespace="/lobby")
    with open("static/js/station"+str(key)+".js","r") as myfile:
        emit('js',myfile.read())
    with open("static/html/station"+str(key)+".html") as myfile:
        emit('html',myfile.read())
    emit('briefingmessage',mission.GetVessel().objectives.briefingmessage)
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
@socketio.on('message', namespace="/station1")
def message(json):
    if message == "restart":
        mission.LoadGame()
@socketio.on('connect', namespace="/station2")
def stationconnect():
    allstationconnect(2)
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
