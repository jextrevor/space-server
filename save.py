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
        self.map.dictionary[self.vessel].parent = self
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
        self.map.dictionary[self.vessel].parent = self
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
    def __init__(self, parentmission, alertstatus, health, power):
        self.parentmission = parentmission
        self.alertstatus = alertstatus
        self.health = health
        self.power = power
    def changestatus(self,alertstatus):
        if self.health > 5 and self.power > 5:
            self.alertstatus = alertstatus
            if self.alertstatus == 0:
                parentmission.SaveGame()
        else:
            self.alertstatus = 2 #red alert
class AntennaModule:
    def __init__(self, parentmission, antennarange, health, power):
        self.parentmission = parentmission
        self.antennarange = antennarange
        self.health = health
        self.power = power
        self.scanlist = []
    def scan(self):
        del scanlist[:]
        for obj in parentmission.parent.map.dictionary:
            if obj.type == "signal":
                pass
newmap = Map()
newid = newmap.Add(Vessel())
dictionary = {'status':0, 'name':'It\'s Mine', 'map':newmap, 'id':newid, 'obj':None}
f = open('missions/Trevor.mis','wb')
pickle.dump(dictionary,f)
f.close()
