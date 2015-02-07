iscaptain = true;
listofmessages = [];
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
	if(json == "1"){
		document.getElementById("publicfreqbutton").style['box-shadow'] = "0 0 30px #0000FF";
		document.getElementById("civfreqbutton").style['box-shadow'] = "none";
		document.getElementById("specialfreqbutton").style['box-shadow'] = "none";
	}
	if(json == "80"){
		document.getElementById("publicfreqbutton").style['box-shadow'] = "none";
		document.getElementById("civfreqbutton").style['box-shadow'] = "0 0 30px #0000FF";
		document.getElementById("specialfreqbutton").style['box-shadow'] = "none";
	}
	if(json == "3000"){
		document.getElementById("publicfreqbutton").style['box-shadow'] = "none";
		document.getElementById("civfreqbutton").style['box-shadow'] = "none";
		document.getElementById("specialfreqbutton").style['box-shadow'] = "0 0 30px #0000FF";
	}
});
stationsocket.on("newmessage",function(json){
	listofmessages.push(json);

	document.getElementById("inbox").innerHTML = "<a class=\"list-group-item\" onclick='showinbox(this,"+listofmessages.indexOf(json)+");buttonsound();'>"+json['from']+"</a>" + document.getElementById("inbox").innerHTML;
	commmessage();
});
stationsocket.on("addmessage",function(json){
	listofmessages.push(json);
	document.getElementById("inbox").innerHTML ="<a class=\"list-group-item\" onclick='showinbox(this,"+listofmessages.indexOf(json)+");buttonsound();'>"+json['from']+"</a>" + document.getElementById("inbox").innerHTML;
});
window['showinbox'] = function(obj,json){
	for(i = 0; i < document.getElementById("inbox").children.length; i++){
		//object.removeAttribute("class")
		document.getElementById("inbox").children[i].className = "list-group-item";
	}
	obj.className = "list-group-item active"
	//alert(data);
	//json = JSON.parse(data);
	//alert(json['message']);
	document.getElementById("messagebody").innerHTML = listofmessages[json]['message'];
}
window['commmessage'] = function(){
	var data = new Audio("static/media/contact.mp3");
    data.play();
}
window['sendmessage'] = function(){
	document.getElementById("toaddress").className = "form-control";
	if(document.getElementById("toaddress").value == ""){
		stationsocket.emit("sendmessage",{'to':0,'message':document.getElementById("messagetosend").value});
	}
	else{
		address = parseInt(document.getElementById("toaddress").value)
		if(address == NaN){
			document.getElementById("toaddress").className = "form-control has-error";
		}
		else{
			stationsocket.emit("sendmessage",{'to':address,'message':document.getElementById("messagetosend").value});
		}
	}
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
