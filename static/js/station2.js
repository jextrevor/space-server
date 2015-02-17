places = [];
objects = [];
radars = [];
coords = {};
yourx = 0;
youry = 0;
yourz = 0;
yourpitch = 0;
youryaw = 0;
var scene;
window['addarrow'] = function(object){
	scene.add(object);
}
window['toDegrees'] = function(angle) {
  return angle * (180 / Math.PI);
}
window['toRadians'] = function(angle) {
  return angle * (Math.PI / 180);
}
setTimeout(function(){
scene = new THREE.Scene();
var camera = new THREE.PerspectiveCamera( 75, 500/500, 0.1, 1000 );
var parameters = {"canvas":document.getElementById("radarcanvas")};
function webglAvailable() { try { var canvas = document.createElement( 'canvas' ); return !!( window.WebGLRenderingContext && ( canvas.getContext( 'webgl' ) || canvas.getContext( 'experimental-webgl' ) ) ); } catch ( e ) { return false; } } if ( webglAvailable() ) { renderer = new THREE.WebGLRenderer(parameters); } else { renderer = new THREE.CanvasRenderer(parameters); }
//var renderer = new THREE.CanvasRenderer(parameters);
renderer.setSize(500,500);
var loader = new THREE.OBJLoader();
loader.load("static/media/arrow.obj",addarrow);
var geometry = new THREE.BoxGeometry( 10, 10, 10 ); 
var material = new THREE.MeshBasicMaterial( { color: 0xcccccc } ); var cube = new THREE.Mesh( geometry, material ); scene.add( cube ); 
var linematerial = new THREE.LineBasicMaterial({
        color: 0xffffff
    });
var linegeometry = new THREE.Geometry();
    linegeometry.vertices.push(new THREE.Vector3(0, 0, 5000));
    linegeometry.vertices.push(new THREE.Vector3(0, 0, -5000));
    var line = new THREE.Line(linegeometry,linematerial);
    scene.add(line);
    //var light = new THREE.PointLight( 0xffffff, 1, 100 ); light.position.set( 0, 5, 0 ); scene.add( light );
    camera.position.set(0,100,100); 
    camera.lookAt(new THREE.Vector3());
    //var light2 = new THREE.AmbientLight( 0x404040 ); // soft white light 
    //scene.add( light2 );
    var render = function () { requestAnimationFrame( render ); updateObjects(); renderer.render(scene, camera); }; render();
},2000);
window['updateObjects'] = function(){
	for(var i = 0; i < objects.length; i++){
		x = coords[objects[i]][0];
		y = coords[objects[i]][1];
		z = coords[objects[i]][2];
		x -= yourx;
		y -= youry;
		z -= yourz;
		/*distance = Math.sqrt(x*x+y*y+z*z)
		if(distance != 0){
			x = x/distance;
			y = y/distance;
			z = z/distance;
		}
		pitch = Math.acos(z);
		if(Math.sin(pitch) != 0){
			yaw = Math.acos(x/Math.sin(pitch));
		}
		else{
			yaw = Math.acos(y/Math.cos(pitch));
		}
		pitch -= toRadians(yourpitch);
		yaw -= toRadians(youryaw);
		x = Math.sin(pitch) * Math.cos(yaw) * distance;
		y = Math.sin(pitch) * Math.sin(yaw) * distance;
		x = Math.cos(pitch) * distance;*/
		console.log("Coords:"+x+","+y+","+z);
		var selectedObject = scene.getObjectByName("object"+objects[i]);
		selectedObject.position.set(x*100,y*100,z*-100)
	}
}
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
	document.getElementById("xerror").className = "";
	document.getElementById("yerror").className = "";
	document.getElementById("zerror").className = "";
	x = parseFloat(document.getElementById("x").value)
	y = parseFloat(document.getElementById("y").value)
	z = parseFloat(document.getElementById("z").value)
	if(isNaN(x)){
		document.getElementById("xerror").className = "has-error";
	}
	else if(isNaN(y)){
		document.getElementById("yerror").className = "has-error";
	}
	else if(isNaN(z)){
		document.getElementById("zerror").className = "has-error";
	}
	else{
		stationsocket.emit("setcourse",{"x":x,"y":y,"z":z});
	}
}
window['search'] = function(){
	document.getElementById("placeinfo").innerHTML = "";
	document.getElementById("results").innerHTML = "";
	for(var i=0; i < places.length; i++){
		if(places[i]['placename'].indexOf(document.getElementById("mapsearch").value) > -1){
			document.getElementById("results").innerHTML += "<a class=\"list-group-item\" onclick='showsearchinfo(this,"+i+");buttonsound();'>"+places[i]['placename']+"</a>";
		}

	}
}
window['showsearchinfo'] = function(obj,json){
	for(i = 0; i < document.getElementById("results").children.length; i++){
		//object.removeAttribute("class")
		document.getElementById("results").children[i].className = "list-group-item";
	}
	obj.className = "list-group-item active"
	//alert(data);
	//json = JSON.parse(data);
	//alert(json['message']);
	document.getElementById("placeinfo").innerHTML = places[json]['placeinfo'];
}
stationsocket.on("course",function(json){
	document.getElementById("cx").innerHTML = json['x'];
	document.getElementById("cy").innerHTML = json['y'];
	document.getElementById("cz").innerHTML = json['z'];
});
stationsocket.on("places",function(json){
	places = json['places'];
});
stationsocket.on("add",function(json){
	objects.push(json);
	var geometry = new THREE.SphereGeometry( 2.5, 32, 32 ); 
	var material = new THREE.MeshBasicMaterial( { color: 0x0000ff } ); 
	var object = new THREE.Mesh( geometry, material ); 
	object.name = "object"+json; 
	scene.add( object ); 
});
stationsocket.on("coords", function(json){
	yourx = json['x'];
	youry = json['y'];
	yourz = json['z'];
})
stationsocket.on("degrees",function(json){
	yourpitch = json['pitch'];
	youryaw = json['yaw'];
});
stationsocket.on("update",function(json){
	console.log("hi");
	coords[json['id']] = [json['x'],json['y'],json['z']];
});
stationsocket.on("remove",function(json){
	var index = objects.indexOf(json);
if (index >= 0) {
  objects.splice( index, 1 );
  scene.remove(radars[index]);
  radars.splice(index,1);
}
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
