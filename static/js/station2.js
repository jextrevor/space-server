window['showengines'] = function(){
	document.getElementById("enginespage").style.display = "initial";
	document.getElementById("radarpage").style.display = "none";
	document.getElementById("settingspage").style.display = "none";
	document.getElementById("enginestab").className = "active";
	document.getElementById("radartab").className = "";
	document.getElementById("settingstab").className = "";
}
window['showradar'] = function(){
	document.getElementById("enginespage").style.display = "none";
	document.getElementById("radarpage").style.display = "initial";
	document.getElementById("settingspage").style.display = "none";
	document.getElementById("enginestab").className = "";
	document.getElementById("radartab").className = "active";
	document.getElementById("settingstab").className = "";
}
window['showsettings'] = function(){
	document.getElementById("enginespage").style.display = "none";
	document.getElementById("radarpage").style.display = "none";
	document.getElementById("settingspage").style.display = "initial";
	document.getElementById("enginestab").className = "";
	document.getElementById("radartab").className = "";
	document.getElementById("settingstab").className = "active";
}
window['setwarp'] = function(number){
	stationsocket.emit("setwarp",number);
}
window['setimpulse'] = function(number){
	stationsocket.emit("setimpulse",number);
}
window['changepitch'] = function(number,number2){
	stationsocket.emit("changepitch",{"pitch":number,"yaw":number2});
}
window['setcourse'] = function(){
	document.getElementById("x").className = "form-control";
	document.getElementById("y").className = "form-control";
	document.getElementById("z").className = "form-control";
	x = parseFloat(document.getElementById("x").value)
	y = parseFloat(document.getElementById("y").value)
	z = parseFloat(document.getElementById("z").value)
	if(isNaN(x)){
		document.getElementById("x").className = "form-control error";
	}
	else if(isNaN(y)){
		document.getElementById("y").className = "form-control error";
	}
	else if(isNaN(z)){
		document.getElementById("z").className = "form-control error";
	}
	else{
		stationsocket.emit("setcourse",{"x":x,"y":y,"z":z});
	}
}
stationsocket.on("course",function(json){
	document.getElementById("cx").innerHTML = json['x'];
	document.getElementById("cy").innerHTML = json['y'];
	document.getElementById("cz").innerHTML = json['z'];
});
stationsocket.on("impulsespeed",function(json){
	if(json == 0){
		document.getElementById("impulse0button").style['box-shadow'] = "0 0 30px #CCCCCC";
		document.getElementById("impulsehalfbutton").style['box-shadow'] = "none";
		document.getElementById("impulsefullbutton").style['box-shadow'] = "none";
	}
	if(json == 0.5){
		document.getElementById("impulse0button").style['box-shadow'] = "none";
		document.getElementById("impulsehalfbutton").style['box-shadow'] = "0 0 30px #0000FF";
		document.getElementById("impulsefullbutton").style['box-shadow'] = "none";
	}
	if(json == 1){
		document.getElementById("impulse0button").style['box-shadow'] = "none";
		document.getElementById("impulsehalfbutton").style['box-shadow'] = "none";
		document.getElementById("impulsefullbutton").style['box-shadow'] = "0 0 30px #00FF00";
	}
});
stationsocket.on("warpspeed",function(json){
	if(json == 0){
		document.getElementById("warp0button").style['box-shadow'] = "0 0 30px #CCCCCC";
		document.getElementById("warp1button").style['box-shadow'] = "none";
		document.getElementById("warp2button").style['box-shadow'] = "none";
		document.getElementById("warp3button").style['box-shadow'] = "none";
		document.getElementById("warp4button").style['box-shadow'] = "none";
		document.getElementById("warp5button").style['box-shadow'] = "none";
		document.getElementById("warp6button").style['box-shadow'] = "none";
		document.getElementById("warp7button").style['box-shadow'] = "none";
		document.getElementById("warp8button").style['box-shadow'] = "none";
		document.getElementById("warp9button").style['box-shadow'] = "none";
		document.getElementById("warp99button").style['box-shadow'] = "none";
	}
	if(json == 1){
		document.getElementById("warp0button").style['box-shadow'] = "none";
		document.getElementById("warp1button").style['box-shadow'] = "0 0 30px #00FF00";
		document.getElementById("warp2button").style['box-shadow'] = "none";
		document.getElementById("warp3button").style['box-shadow'] = "none";
		document.getElementById("warp4button").style['box-shadow'] = "none";
		document.getElementById("warp5button").style['box-shadow'] = "none";
		document.getElementById("warp6button").style['box-shadow'] = "none";
		document.getElementById("warp7button").style['box-shadow'] = "none";
		document.getElementById("warp8button").style['box-shadow'] = "none";
		document.getElementById("warp9button").style['box-shadow'] = "none";
		document.getElementById("warp99button").style['box-shadow'] = "none";
	}
	if(json == 2){
		document.getElementById("warp0button").style['box-shadow'] = "none";
		document.getElementById("warp1button").style['box-shadow'] = "none";
		document.getElementById("warp2button").style['box-shadow'] = "0 0 30px #00FF00";
		document.getElementById("warp3button").style['box-shadow'] = "none";
		document.getElementById("warp4button").style['box-shadow'] = "none";
		document.getElementById("warp5button").style['box-shadow'] = "none";
		document.getElementById("warp6button").style['box-shadow'] = "none";
		document.getElementById("warp7button").style['box-shadow'] = "none";
		document.getElementById("warp8button").style['box-shadow'] = "none";
		document.getElementById("warp9button").style['box-shadow'] = "none";
		document.getElementById("warp99button").style['box-shadow'] = "none";
	}
	if(json == 3){
		document.getElementById("warp0button").style['box-shadow'] = "none";
		document.getElementById("warp1button").style['box-shadow'] = "none";
		document.getElementById("warp2button").style['box-shadow'] = "none";
		document.getElementById("warp3button").style['box-shadow'] = "0 0 30px #00FF00";
		document.getElementById("warp4button").style['box-shadow'] = "none";
		document.getElementById("warp5button").style['box-shadow'] = "none";
		document.getElementById("warp6button").style['box-shadow'] = "none";
		document.getElementById("warp7button").style['box-shadow'] = "none";
		document.getElementById("warp8button").style['box-shadow'] = "none";
		document.getElementById("warp9button").style['box-shadow'] = "none";
		document.getElementById("warp99button").style['box-shadow'] = "none";
	}
	if(json == 4){
		document.getElementById("warp0button").style['box-shadow'] = "none";
		document.getElementById("warp1button").style['box-shadow'] = "none";
		document.getElementById("warp2button").style['box-shadow'] = "none";
		document.getElementById("warp3button").style['box-shadow'] = "none";
		document.getElementById("warp4button").style['box-shadow'] = "0 0 30px #0000FF";
		document.getElementById("warp5button").style['box-shadow'] = "none";
		document.getElementById("warp6button").style['box-shadow'] = "none";
		document.getElementById("warp7button").style['box-shadow'] = "none";
		document.getElementById("warp8button").style['box-shadow'] = "none";
		document.getElementById("warp9button").style['box-shadow'] = "none";
		document.getElementById("warp99button").style['box-shadow'] = "none";
	}
	if(json == 5){
		document.getElementById("warp0button").style['box-shadow'] = "none";
		document.getElementById("warp1button").style['box-shadow'] = "none";
		document.getElementById("warp2button").style['box-shadow'] = "none";
		document.getElementById("warp3button").style['box-shadow'] = "none";
		document.getElementById("warp4button").style['box-shadow'] = "none";
		document.getElementById("warp5button").style['box-shadow'] = "0 0 30px #0000FF";
		document.getElementById("warp6button").style['box-shadow'] = "none";
		document.getElementById("warp7button").style['box-shadow'] = "none";
		document.getElementById("warp8button").style['box-shadow'] = "none";
		document.getElementById("warp9button").style['box-shadow'] = "none";
		document.getElementById("warp99button").style['box-shadow'] = "none";
	}
	if(json == 6){
		document.getElementById("warp0button").style['box-shadow'] = "none";
		document.getElementById("warp1button").style['box-shadow'] = "none";
		document.getElementById("warp2button").style['box-shadow'] = "none";
		document.getElementById("warp3button").style['box-shadow'] = "none";
		document.getElementById("warp4button").style['box-shadow'] = "none";
		document.getElementById("warp5button").style['box-shadow'] = "none";
		document.getElementById("warp6button").style['box-shadow'] = "0 0 30px #0000FF";
		document.getElementById("warp7button").style['box-shadow'] = "none";
		document.getElementById("warp8button").style['box-shadow'] = "none";
		document.getElementById("warp9button").style['box-shadow'] = "none";
		document.getElementById("warp99button").style['box-shadow'] = "none";
	}
	if(json == 7){
		document.getElementById("warp0button").style['box-shadow'] = "none";
		document.getElementById("warp1button").style['box-shadow'] = "none";
		document.getElementById("warp2button").style['box-shadow'] = "none";
		document.getElementById("warp3button").style['box-shadow'] = "none";
		document.getElementById("warp4button").style['box-shadow'] = "none";
		document.getElementById("warp5button").style['box-shadow'] = "none";
		document.getElementById("warp6button").style['box-shadow'] = "none";
		document.getElementById("warp7button").style['box-shadow'] = "0 0 30px #FFFF00";
		document.getElementById("warp8button").style['box-shadow'] = "none";
		document.getElementById("warp9button").style['box-shadow'] = "none";
		document.getElementById("warp99button").style['box-shadow'] = "none";
	}
	if(json == 8){
		document.getElementById("warp0button").style['box-shadow'] = "none";
		document.getElementById("warp1button").style['box-shadow'] = "none";
		document.getElementById("warp2button").style['box-shadow'] = "none";
		document.getElementById("warp3button").style['box-shadow'] = "none";
		document.getElementById("warp4button").style['box-shadow'] = "none";
		document.getElementById("warp5button").style['box-shadow'] = "none";
		document.getElementById("warp6button").style['box-shadow'] = "none";
		document.getElementById("warp7button").style['box-shadow'] = "none";
		document.getElementById("warp8button").style['box-shadow'] = "0 0 30px #FFFF00";
		document.getElementById("warp9button").style['box-shadow'] = "none";
		document.getElementById("warp99button").style['box-shadow'] = "none";
	}
	if(json == 9){
		document.getElementById("warp0button").style['box-shadow'] = "none";
		document.getElementById("warp1button").style['box-shadow'] = "none";
		document.getElementById("warp2button").style['box-shadow'] = "none";
		document.getElementById("warp3button").style['box-shadow'] = "none";
		document.getElementById("warp4button").style['box-shadow'] = "none";
		document.getElementById("warp5button").style['box-shadow'] = "none";
		document.getElementById("warp6button").style['box-shadow'] = "none";
		document.getElementById("warp7button").style['box-shadow'] = "none";
		document.getElementById("warp8button").style['box-shadow'] = "none";
		document.getElementById("warp9button").style['box-shadow'] = "0 0 30px #FF0000";
		document.getElementById("warp99button").style['box-shadow'] = "none";
	}
	if(json == 9.9){
		document.getElementById("warp0button").style['box-shadow'] = "none";
		document.getElementById("warp1button").style['box-shadow'] = "none";
		document.getElementById("warp2button").style['box-shadow'] = "none";
		document.getElementById("warp3button").style['box-shadow'] = "none";
		document.getElementById("warp4button").style['box-shadow'] = "none";
		document.getElementById("warp5button").style['box-shadow'] = "none";
		document.getElementById("warp6button").style['box-shadow'] = "none";
		document.getElementById("warp7button").style['box-shadow'] = "none";
		document.getElementById("warp8button").style['box-shadow'] = "none";
		document.getElementById("warp9button").style['box-shadow'] = "none";
		document.getElementById("warp99button").style['box-shadow'] = "0 0 30px #FF0000";
	}
});