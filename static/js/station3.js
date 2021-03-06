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
var raycaster;
var mouse;
var camera;
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
camera = new THREE.PerspectiveCamera( 75, 500/500, 0.1, 1000 );
raycaster = new THREE.Raycaster();
mouse = new THREE.Vector2();
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
camera.position.set(0,50,50);
camera.lookAt(new THREE.Vector3());
//var light2 = new THREE.AmbientLight( 0x404040 ); // soft white light
//scene.add( light2 );
var render = function () { requestAnimationFrame( render ); updateObjects(); renderer.render(scene, camera); }; render();
},2000);
window['clickObject'] = function(gCanvasElement){
var x;
var y;
if (event.pageX || event.pageY) {
x = event.pageX;
y = event.pageY;
}
else {
x = event.clientX + document.body.scrollLeft + document.documentElement.scrollLeft;
y = event.clientY + document.body.scrollTop + document.documentElement.scrollTop;
}
x -= gCanvasElement.offsetLeft;
y -= gCanvasElement.offsetTop;
mouse.x = x;
mouse.y = y;
raycaster.setFromCamera( mouse, camera );
var intersects = raycaster.intersectObjects( objects );
if ( intersects.length > 0 ) {
    console.log("hey");
if(intersects[0].object.name.startsWith("object")){
for(var i = 0; i < objects.length; i++){
  console.log("hey");
var selectedObject = scene.getObjectByName("object"+objects[i]);
selectedObject.material.color.setHex(0x0000ff);
if(intersects[0].object.name == "object"+objects[i]){
document.getElementById("radarinfodiv").innerHTML = "<p>Object Coordinates - X: "+coords[i][0]+" Y: "+coords[i][1]+" Z: "+coords[i][2]+"</p>";
}
}
intersects[0].object.material.color.setHex(0xff0000);
}
}
}
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
var selectedObject = scene.getObjectByName("object"+objects[i]);
selectedObject.position.set(x*100,y*100,z*-100)
}
}
window['setshields'] = function(boolean){
stationsocket.emit("setshields",boolean);
}
window['showtarget'] = function(){
document.getElementById("targetpage").style.display = "initial";
document.getElementById("weaponpage").style.display = "none";
document.getElementById("securitypage").style.display = "none";
document.getElementById("targettab").className = "active";
document.getElementById("weapontab").className = "";
document.getElementById("securitytab").className = "";
}
window['showweapon'] = function(){
document.getElementById("targetpage").style.display = "none";
document.getElementById("weaponpage").style.display = "initial";
document.getElementById("securitypage").style.display = "none";
document.getElementById("targettab").className = "";
document.getElementById("weapontab").className = "active";
document.getElementById("securitytab").className = "";
}
window['showsecurity'] = function(){
document.getElementById("targetpage").style.display = "none";
document.getElementById("weaponpage").style.display = "none";
document.getElementById("securitypage").style.display = "initial";
document.getElementById("targettab").className = "";
document.getElementById("weapontab").className = "";
document.getElementById("securitytab").className = "active";
}
stationsocket.on("shields",function(json){
  if(json == true){
document.getElementById("shieldupbutton").style['box-shadow'] = "0 0 30px #0000FF";
document.getElementById("shielddownbutton").style['box-shadow'] = "none";
}
else{
  document.getElementById("shieldupbutton").style['box-shadow'] = "none";
document.getElementById("shielddownbutton").style['box-shadow'] = "0 0 30px #FF0000";
}
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
