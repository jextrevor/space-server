var joinid = -1;
var activemissions = new Array();
var stationsocket;
var conn_options = {
  'sync disconnect on unload':true
};
var socket = io.connect('http://'+window.location.hostname+':'+window.location.port+'/lobby',conn_options);
socket.on('lobbyconnect', function(json) {
        document.getElementById("connecting").style.display ="none";
        if(json == "0"){
            document.getElementById("joinmission").style.display="none";
            document.getElementById("choosemission").style.display = "initial";
        }
        else if(json == "1"){
            document.getElementById("joinmission").style.display = "initial";
            document.getElementById("choosemission").style.display = "none";
        }
        else{
            document.getElementById("connecting").style.display="initial";
        }
    });
socket.on('lobbymissionlist', function(json) {
        for(i in json){
        document.getElementById("missionselect").innerHTML += "<option value=\""+i+"\">"+json[i]+"</option>";
       }
    });
socket.on('lobbyname', function(json) {
    document.getElementById("missionname").innerHTML = "Mission Name: "+json;
    });
socket.on('lobbystations', function(json) {
    document.getElementById("stationselect").innerHTML = "";
        for(i in json){
        if(json[i]['taken'] != true){
        document.getElementById("stationselect").innerHTML+="<option value=\""+i+"\">"+json[i]['name']+"</option>";
        }
        }
    if(document.getElementById("stationselect").innerHTML == ""){
        document.getElementById("joindiv").innerHTML = "<p>The mission is full.</p>";
    }
    });
socket.on('lobbyjoin', function(json) {
    joinstation(json);
    });
socket.on('disconnect', function(json){
	document.getElementById("joinmission").style.display = "none";
    document.getElementById("choosemission").style.display = "none";
	document.getElementById("connecting").style.display ="initial";
	});

function joinstation(data){
socket.disconnect();
socket = null;
stationsocket = io.connect('http://'+window.location.hostname+':'+window.location.port+'/station'+data,conn_options);
stationsocket.on('status', function(json){
if(json == "0"){
	document.getElementById("controls").style.display = "none";
	document.getElementById("briefing").style.display = "initial";
	document.getElementById("briefing").innerHTML = "<h1>MISSION TERMINATED</h1>"
}
if(json == "1"){
    document.getElementById("missionstart").style.display = "none";
}
if(json == "1.5"){
    document.getElementById("missionstart").style.display = "initial";
}
if(json == "2"){
	document.getElementById("briefing").style.display = "none";
	document.getElementById("controls").style.display = "initial";
}
});
stationsocket.on('html',function(json){
document.getElementById("stationpage").style.display = "initial";
document.getElementById("mainpage").style.display = "none";
document.getElementById("controls").innerHTML = json;
});
stationsocket.on('disconnect', function(){
document.getElementById("errordisconnect").style.display="initial";
});
stationsocket.on('connect', function(){
document.getElementById("errordisconnect").style.display="none";
});
}
function selectmission(){
    var e = document.getElementById("missionselect");
    var strUser = e.options[e.selectedIndex].value;
    socket.emit('lobbychoose',strUser);
}
function selectstation(){
    var e = document.getElementById("stationselect");
    var strUser = e.options[e.selectedIndex].value;
    socket.emit('lobbyjoin',strUser);
}