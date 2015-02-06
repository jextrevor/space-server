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
stationsocket.on("frequency",function(json){
	if(json == "0"){
		document.getElementById("publicfreqbutton").style['box-shadow'] = "0 0 30px #0000FF";
		document.getElementById("civfreqbutton").style['box-shadow'] = "none";
		document.getElementById("specialfreqbutton").style['box-shadow'] = "none";
	}
	if(json == "1"){
		document.getElementById("publicfreqbutton").style['box-shadow'] = "none";
		document.getElementById("civfreqbutton").style['box-shadow'] = "0 0 30px #0000FF";
		document.getElementById("specialfreqbutton").style['box-shadow'] = "none";
	}
	if(json == "2"){
		document.getElementById("publicfreqbutton").style['box-shadow'] = "none";
		document.getElementById("civfreqbutton").style['box-shadow'] = "none";
		document.getElementById("specialfreqbutton").style['box-shadow'] = "0 0 30px #0000FF";
	}
});
stationsocket.on("newmessage",function(json){
	document.getElementById("inbox").innerHTML+="<a class=\"list-group-item\" onclick='showinbox(this,"+JSON.stringify(json)+");buttonsound();'>"+json['from']+"</a>";
});
stationsocket.on("addmessage",function(json){
	document.getElementById("inbox").innerHTML+="<a class=\"list-group-item\" onclick='showinbox(this,"+JSON.stringify(json)+");buttonsound();'>"+json['from']+"</a>";
});
window['showinbox'] = function(obj,json){
	for(object in document.getElementById("inbox").childNodes){
		object.className = "list-group-item"
	}
	obj.className = "list-group-item active"
	//alert(data);
	//json = JSON.parse(data);
	//alert(json['message']);
	document.getElementById("messagebody").innerHTML = json['message'];
}
window['sendmessage'] = function(){
	alert('in progress');
}
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