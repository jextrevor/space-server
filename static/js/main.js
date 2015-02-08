var joinid = -1;
var activemissions = new Array();
var stationsocket;
var conn_options = {
  'sync disconnect on unload':true
};
var shake;
var magnitude = 0;
var willstop = true;
var iscaptain = false;
var socket = io.connect('http://'+window.location.hostname+':'+window.location.port+'/lobby',conn_options);
socket.on('lobbyconnect', function(json) {
        document.getElementById("connecting").style.display ="none";
        if(json == "0"){
            document.getElementById("joinmission").style.display="none";
            document.getElementById("choosemission").style.display = "initial";
            document.getElementById("full").style.display = "none";
        }
        else if(json == "1"){
            document.getElementById("joinmission").style.display = "initial";
            document.getElementById("choosemission").style.display = "none";
            document.getElementById("full").style.display = "none";
        }
        else{
            document.getElementById("full").style.display = "initial";
            document.getElementById("joinmission").style.display = "none";
            document.getElementById("choosemission").style.display = "none";
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
stationsocket.on('message', function(data){
if(data == "not responding"){
    var data = new Audio("static/media/notresponding.mp3");
    data.play();
}
});
stationsocket.on('status', function(json){
if(json == "0"){
	document.getElementById("controls").style.display = "none";
	document.getElementById("briefing").style.display = "initial";
	document.getElementById("briefingcontent").innerHTML = "<h1>MISSION TERMINATED</h1>";
}
if(json == "1"){
    document.getElementById("missionstart").style.display = "none";
}
if(json == "1.5"){
    document.getElementById("missionstart").style.display = "initial";
}
if(json == "2"){
    document.getElementById("missionstart").style.display = "none";
	document.getElementById("briefing").style.display = "none";
	document.getElementById("controls").style.display = "initial";
}
if(json == "3"){
    document.getElementById("controls").style.display = "none";
    document.getElementById("briefing").style.display = "initial";
    document.getElementById("briefingcontent").innerHTML = "<h1>VICTORY!!!!</h1>";
}
if(json == "4"){
    document.getElementById("controls").style.display = "none";
    document.getElementById("briefing").style.display = "initial";
    if(iscaptain == true){
    document.getElementById("briefingcontent").innerHTML = "<h1>MISSION FAILED</h1><p>Please discuss why you failed with your crew, then select Restart.</p><button class='btn btn-warning btn-lg' onclick='stationsocket.emit(\"message\",\"restart\");'>Restart Mission</button>";
}
else{
    document.getElementById("briefingcontent").innerHTML = "<h1>MISSION FAILED</h1>";
}
}
});
stationsocket.on('html',function(json){
document.getElementById("stationpage").style.display = "initial";
document.getElementById("mainpage").style.display = "none";
document.getElementById("controls").innerHTML = json;
});
stationsocket.on('js',function(json){
eval(json);
});
stationsocket.on('briefingmessage',function(json){
document.getElementById("briefingcontent").innerHTML = json;
});
stationsocket.on('disconnect', function(){
document.getElementById("errordisconnect").style.display="initial";
});
stationsocket.on('connect', function(){
document.getElementById("errordisconnect").style.display="none";
});
stationsocket.on('explosion', function(json){
    willstop = json['stable'];
    if(willstop){magnitude += json['magnitude'];}
    else{magnitude = json['magnitude'];}
    clearInterval(shake);
    shake = setInterval(function(){doshake()},1);
})
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
function buttonsound(){
    var data = new Audio("static/media/button.wav");
    data.play();
}
function shortsound(){
    var data = new Audio("static/media/buttonshort.wav");
    data.play();
}
function doshake(){
    document.getElementById("briefingcontent").style["-webkit-filter"] = "blur("+magnitude/10+"px)";
    document.getElementById("briefingcontent").style["filter"] = "blur("+magnitude/10+"px)";
    document.getElementById("stationpage").style.top = randomIntFromInterval(magnitude * -1, magnitude)+'px';
    document.getElementById("stationpage").style.left = randomIntFromInterval(magnitude * -1, magnitude)+'px';
    document.getElementById("briefingcontent").style['-webkit-transform'] = "rotate("+randomIntFromInterval(magnitude * -1, magnitude)/50+'deg)';
    document.getElementById("briefingcontent").style['-moz-transform'] = "rotate("+randomIntFromInterval(magnitude * -1, magnitude)/50+'deg)';
    if(willstop){magnitude -= (magnitude+1)/400;}
    if(magnitude <= 0){
    magnitude = 0;
    clearInterval(shake);
    document.getElementById("stationpage").style.top = '0px';
    document.getElementById("stationpage").style.left = '0px';
    document.getElementById("briefingcontent").style["-webkit-filter"] = "blur(0px)";
    document.getElementById("briefingcontent").style["filter"] = "blur(0px)";
    document.getElementById("briefingcontent").style['-webkit-transform'] = "rotate(0deg)";
    document.getElementById("briefingcontent").style['-moz-transform'] = "rotate(0deg)";
    }
}
function randomIntFromInterval(min,max)
{
    return Math.floor(Math.random()*((max-min)+1)+min);
}