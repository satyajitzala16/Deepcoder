// admin_login.js
async function adminLogin(){

 let res = await fetch('/api/admin-login/',{
 method:'POST',
 headers:{'Content-Type':'application/json'},
 body:JSON.stringify({
 email:document.getElementById("email").value,
 password:document.getElementById("password").value
 })
 });

 let data = await res.json();

 if(data.status=="success"){

 // 🔥 redirect
 window.location.href = "/admin-dashboard/";

 }else{
 alert("Invalid Admin Login");
 }
}