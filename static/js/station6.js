theme = 0;
currentsong = 1;
currentmusic = new Audio("static/media/training.mp3");
currentmusic.addEventListener('ended', function() {
    newsong();
}, false);
currentmusic.play();
stationsocket.on("theme",function(json){
theme = json;
});
window['newsong'] = function(){
  prefix = ""
  suffix = ""
  if(theme == 0){
  prefix = "training"
  }
  if(theme == 1){
  prefix = "travel"
  }
  if(theme == 2){
  prefix = "tense"
  }
  if(theme == 3){
  prefix = "intense"
  }
  if(theme == 4){
  prefix = "battle"
  }
  if(currentsong == 1){
  currentsong = 2;
  suffix = "2"
  }
  else{
  currentsong = 1;
  }
  currentmusic = new Audio("static/media/"+prefix+suffix+".mp3");
  currentmusic.addEventListener('ended', function() {
    newsong();
  }, false);
  currentmusic.play();
}
