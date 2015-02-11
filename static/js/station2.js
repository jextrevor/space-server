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