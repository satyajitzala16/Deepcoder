async function loadDashboard(){

 let res = await fetch('/api/employees/');
 let data = await res.json();

 document.getElementById("totalEmp").innerText = data.length;
}

loadDashboard();