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
        self.objective = dictionary['obj']
        self.socket = None
        self.timer = None
    def GetStations(self):
        return self.map.dictionary[self.vessel].stations
    def Countdown(self):
        self.status = 1.5
        self.emittoallstations("status","1.5")
        self.timer = threading.Timer(600, self.Start)
        self.timer.start()
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
        dictionary = {'status':self.status, 'name':self.name, 'map':self.map, 'id':self.vessel, 'obj':self.objective}
        f = open('save.mis','wb')
        pickle.dump(dictionary,f)
        f.close()
    def LoadGame(self):
        f = open('save.mis','rb')
        dictionary = pickle.load(f)
        f.close()
        self.status = dictionary['status']
        self.name = dictionary['name']
        self.map = dictionary['map']
        self.vessel = dictionary['id']
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
    def __init__(self):
        self.alertmodule = AlertModule(self,0,100,100)
        self.stations = {1:{'name':'Commander','taken':False},2:{'name':'Navigations','taken':False},3:{'name':'Tactical','taken':False},4:{'name':'Operations','taken':False},5:{'name':'Engineer','taken':False},6:{'name':'Main View Screen','taken':False}}
class AlertModule:
    def __init__(self, parentmission, alertstatus, health, power, mindamage, minpower, breakdamage):
        self.parentmission = parentmission
        self.alertstatus = alertstatus
        self.health = health
        self.power = power
        self.mindamage = mindamage
        self.minpower = minpower
        self.breakdamage = breakdamage
    def changestatus(self,alertstatus):
        if self.health > mindamage and self.power > minpower:
            self.alertstatus = alertstatus
            if self.alertstatus == 0:
                parentmission.SaveGame()
            emit('alert',alertstatus,namespace="/station1")
            emit('alert',alertstatus,namespace="/station6")
            return True
        else:
            return False
    def action(self):
        pass
class AntennaModule:
    def __init__(self, parentmission, antennarange, health, power, mindamage, minpower, breakdamage):
        self.parentmission = parentmission
        self.antennarange = antennarange
        self.health = health
        self.power = power
        self.mindamage = mindamage
        self.minpower = minpower
        self.breakdamage = breakdamage
        self.scanlist = []
    def scan(self):
        del self.scanlist[:]
        for obj in self.parentmission.map.dictionary:
            if obj.type == "signal":
                self.scanlist.append(obj)
    def action(self):
        self.scan()
def allstationconnect(key):
    mission.join(key)
    emit('lobbystations',mission.GetStations(), namespace="/lobby")
    with open("static/js/station"+str(key)+".js","r") as myfile:
        emit('js',myfile.read())
    with open("static/html/station"+str(key)+".html") as myfile:
        emit('html',myfile.read())
def allstationdisconnect(key):
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
        send("not responding", namespace="/station1")
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