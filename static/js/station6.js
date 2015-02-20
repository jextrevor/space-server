theme = "0";
var alertinterval;
currentsong = 1;
exposition = false;
soundeffects = false;
currentmusic = new Audio("static/media/training.mp3");
currentmusic.addEventListener('ended', function() {
    newsong();
}, false);
currentmusic.play();
background = new Audio("static/media/background.mp3");
background.addEventListener('ended', function() {
    restartbackground();
}, false);
background.play();
stationsocket.on("theme",function(json){
playnewsong = false;
if(theme == "0" && json == "1"){
	playnewsong = true;
	exposition = true;
}
if(theme !="0" && json == "0"){
	playnewsong = true;
}
if(theme != "4" && json =="4"){
	playnewsong = true;
}
theme = json;
if(playnewsong){
	newsong();
}
});
stationsocket.on("alert",function(json){
	if(json == "0"){
		document.body.className = "";
	}
	if(json == "1"){
		document.body.className ="redalert";
	}
	if(json == "2"){
		document.body.className ="redalert";
	}
});
stationsocket.on("startwarp", function(json){
data = new Audio("static/media/warp.mp3");
data.play();
});
stationsocket.on("endwarp", function(json){
data = new Audio("static/media/warpout.mp3");
data.play();
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
    soundeffect = new Audio("static/media/victory.mp3");
    soundeffects = true;
    currentmusic.volume = 0;
    soundeffect.addEventListener('ended', function() {
    currentmusic.volume = 1;
    soundeffects = false;
}, false);
    soundeffect.play();
}
if(json == "4"){
    document.getElementById("controls").style.display = "none";
    document.getElementById("briefing").style.display = "initial";
    soundeffect = new Audio("static/media/defeat.wav");
    soundeffects = true;
    currentmusic.volume = 0;
    soundeffect.addEventListener('ended', function() {
    currentmusic.volume = 1;
    soundeffects = false;
}, false);
    soundeffect.play();
    if(iscaptain == true){
    document.getElementById("briefingcontent").innerHTML = "<h1>MISSION FAILED</h1><p>Please discuss why you failed with your crew, then select Restart.</p><button class='btn btn-warning btn-lg' onclick='stationsocket.emit(\"message\",\"restart\");'>Restart Mission</button>";
}
else{
    document.getElementById("briefingcontent").innerHTML = "<h1>MISSION FAILED</h1>";
}
}
});
window['restartbackground'] = function(){
	background = new Audio("static/media/background.mp3");
background.addEventListener('ended', function() {
    restartbackground();
}, false);
background.play();
}
window['newsong'] = function(){
  currentmusic.pause();
  prefix = ""
  suffix = ""
  if(theme == '0'){
  prefix = "training"
  }
  if(theme == '1'){
  prefix = "travel"
  }
  if(theme == '2'){
  prefix = "tense"
  }
  if(theme == '3'){
  prefix = "intense"
  }
  if(theme == "4"){
  prefix = "battle"
  }
  if(currentsong == 1){
  currentsong = 2;
  suffix = "2"
  }
  else if(currentsong == 2){
  currentsong = 3;
  suffix = "3"
  }
  else{
  	currentsong = 1;
  }
  if(exposition){
  	prefix = "exposition"
  	suffix = ""
  	exposition = false;
  }
  currentmusic = new Audio("static/media/"+prefix+suffix+".mp3");
  if(soundeffects == true){
  	currentmusic.volume = 0;
  }
  else{
  	currentmusic.volume = 1;
  }
  currentmusic.addEventListener('ended', function() {
    newsong();
  }, false);
  currentmusic.play();
}
