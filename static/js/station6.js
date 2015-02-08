theme = "0";
currentsong = 1;
exposition = false;
currentmusic = new Audio("static/media/training.mp3");
currentmusic.addEventListener('ended', function() {
    newsong();
}, false);
currentmusic.play();
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
  else{
  currentsong = 1;
  }
  if(exposition){
  	prefix = "exposition"
  	suffix = ""
  	exposition = false;
  }
  currentmusic = new Audio("static/media/"+prefix+suffix+".mp3");
  currentmusic.addEventListener('ended', function() {
    newsong();
  }, false);
  currentmusic.play();
}
