iscaptain = true;
stationsocket.on("alert",function(json){
	if(json == "0"){
		document.getElementById("greenalertbutton").style['box-shadow'] = "0 0 30px #00FF00";
		document.getElementById("yellowalertbutton").style['box-shadow'] = "none";
		document.getElementById("redalertbutton").style['box-shadow'] = "none";
	}
	if(json == "1"){
		document.getElementById("greenalertbutton").style['box-shadow'] = "none";
		document.getElementById("yellowalertbutton").style['box-shadow'] = "0 0 30px #FFFF00";
		document.getElementById("redalertbutton").style['box-shadow'] = "none";
	}
	if(json == "2"){
		document.getElementById("greenalertbutton").style['box-shadow'] = "none";
		document.getElementById("yellowalertbutton").style['box-shadow'] = "none";
		document.getElementById("redalertbutton").style['box-shadow'] = "0 0 30px #FF0000";
	}
});
window['showalerts'] = function(){
	document.getElementById("alertspage").style.display = "initial";
	document.getElementById("communicationspage").style.display = "none";
	document.getElementById("objectivespage").style.display = "none";
	document.getElementById("alertstab").className = "active";
	document.getElementById("communicationstab").className = "";
	document.getElementById("objectivestab").className = "";
}
window['showcommunications'] = function(){
	document.getElementById("alertspage").style.display = "none";
	document.getElementById("communicationspage").style.display = "initial";
	document.getElementById("objectivespage").style.display = "none";
	document.getElementById("alertstab").className = "";
	document.getElementById("communicationstab").className = "active";
	document.getElementById("objectivestab").className = "";
}
window['showobjectives'] = function(){
	document.getElementById("alertspage").style.display = "none";
	document.getElementById("communicationspage").style.display = "none";
	document.getElementById("objectivespage").style.display = "initial";
	document.getElementById("alertstab").className = "";
	document.getElementById("communicationstab").className = "";
	document.getElementById("objectivestab").className = "active";
}