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
