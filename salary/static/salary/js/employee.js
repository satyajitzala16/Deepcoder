// 🔐 LOGIN
async function login(){

 try{

 let email = document.getElementById("email").value;
 let password = document.getElementById("password").value;

 if(!email || !password){
 alert("Please enter email & password");
 return;
 }

 let res = await fetch('/api/employee-login/',{
 method:'POST',
 headers:{'Content-Type':'application/json'},
 body:JSON.stringify({email,password})
 });

 let data = await res.json();

 if(data.status=="success"){

 // save login
 localStorage.setItem("emp_id", data.employee_id);

 // UI change
 document.getElementById("loginBox").style.display="none";
 document.getElementById("userPanel").style.display="block";

 }else{
 alert(data.message || "Invalid Login");
 }

 }catch(err){
 console.log(err);
 alert("Server Error");
 }

}


// 💰 LOAD SALARY
async function loadUserSalary(){

 try{

 let month = document.getElementById("user_month").value;
 let emp_id = localStorage.getItem("emp_id");

 if(!emp_id){
 alert("Please login first");
 return;
 }

 if(!month){
 alert("Enter month");
 return;
 }

 let res = await fetch(`/api/employee-salary/?month=${month}&emp_id=${emp_id}`);
 let data = await res.json();

 let html = "<tr><th>Name</th><th>Final Salary</th></tr>";

 if(data.length === 0){
 html += "<tr><td colspan='2'>No Data Found</td></tr>";
 }else{
 data.forEach(e=>{
 html += `<tr><td>${e.name}</td><td>${e.final_salary}</td></tr>`;
 });
 }

 document.getElementById("userSalary").innerHTML = html;

 }catch(err){
 console.log(err);
 alert("Error loading salary");
 }

}


// 🚪 LOGOUT
function logout(){

 localStorage.removeItem("emp_id");

 document.getElementById("userPanel").style.display="none";
 document.getElementById("loginBox").style.display="block";

}