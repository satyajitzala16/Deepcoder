let salaryData = []; // 🔥 store data


// 🔥 Load Months (Financial Year)
function loadMonths(){

 const monthDropdown = document.getElementById("month");

 monthDropdown.innerHTML = `<option value="">Select Month</option>`;

 const months = [
     "April","May","June","July","August","September",
     "October","November","December","January","February","March"
 ];

 let currentYear = new Date().getFullYear();

 for(let y = currentYear; y <= currentYear + 1; y++){

     months.forEach((m, index) => {

         let year = (index >= 9) ? y + 1 : y;

         let value = `${m} ${year}`;

         monthDropdown.innerHTML += `<option value="${value}">${value}</option>`;
     });
 }
}


// 🔥 Auto Select Current Month
function setCurrentMonth(){

 let now = new Date();

 let months = [
     "January","February","March","April","May","June",
     "July","August","September","October","November","December"
 ];

 let currentMonth = months[now.getMonth()] + " " + now.getFullYear();

 let dropdown = document.getElementById("month");

 for(let i=0; i<dropdown.options.length; i++){
     if(dropdown.options[i].value === currentMonth){
         dropdown.selectedIndex = i;
         break;
     }
 }
}


// 🔥 Load Salary
async function loadSalary(){

 let m = document.getElementById("month").value;

 if(!m){
     alert("Select month");
     return;
 }

 let res = await fetch(`/api/employee-salary/?month=${m}`);
 let data = await res.json();

 salaryData = data;

 let totalSalary = 0;

 let html = `
 <tr>
   <th>Name</th>
   <th>Email</th>
   <th>Salary</th>
   <th>Month</th>
   <th>Total Leaves</th>
   <th>Paid Leaves</th>
   <th>Unpaid Leaves</th>
   <th>Cut Amount</th>
   <th>Tax</th>   // 🔥 NEW
   <th>Final Salary</th>
   <th>Slip</th>
 </tr>
 `;

 if(data.length === 0){
   html += `<tr><td colspan="9">No Data Found</td></tr>`;
 }else{

   data.forEach(e=>{

     totalSalary += parseFloat(e.final_salary);

     html += `
     <tr>
       <td>${e.name}</td>
       <td>${e.email}</td>
       <td>${e.salary}</td>
       <td>${e.month}</td>
       <td>${e.total_leaves}</td>
       <td>${e.paid_leaves}</td>
       <td>${e.unpaid_leaves}</td>
       <td>${e.cut_amount}</td>
       <td>${e.tax}</td>   // 🔥 NEW
       <td>${e.final_salary}</td>
       <td>
         <button onclick="downloadSlip('${e.id}', '${e.month}')">
            Download
         </button>
        </td>
     </tr>
     `;
   });

   // 🔥 Footer Row
   html += `
   <tr style="background:#f1f5f9;font-weight:bold;">
       <td colspan="9">Total Salary</td>
       <td>${totalSalary.toFixed(2)}</td>
   </tr>
   `;
 }

 document.getElementById("salaryTable").innerHTML = html;
}


// 🔍 Search Filter
function filterTable(){

 let input = document.getElementById("search").value.toLowerCase();
 let rows = document.querySelectorAll("#salaryTable tr");

 rows.forEach((row, index) => {

     if(index === 0) return;

     let name = row.children[0]?.innerText.toLowerCase();

     if(name && name.includes(input)){
         row.style.display = "";
     }else{
         row.style.display = "none";
     }
 });
}


// 📥 Export CSV
function exportCSV(){

 if(salaryData.length === 0){
     alert("No data to export");
     return;
 }

 let csv = "Name,Final Salary\n";

 salaryData.forEach(e=>{
     csv += `${e.name},${e.final_salary}\n`;
 });

 let blob = new Blob([csv], { type: "text/csv" });
 let url = window.URL.createObjectURL(blob);

 let a = document.createElement("a");
 a.href = url;

 let month = document.getElementById("month").value;
 a.download = `salary_${month}.csv`;

 a.click();

 window.URL.revokeObjectURL(url);
}


// 📊 Export Excel
function exportExcel(){

 if(salaryData.length === 0){
     alert("No data");
     return;
 }

 let data = [["Name", "Final Salary"]];

 salaryData.forEach(e=>{
     data.push([e.name, e.final_salary]);
 });

 let wb = XLSX.utils.book_new();
 let ws = XLSX.utils.aoa_to_sheet(data);

 XLSX.utils.book_append_sheet(wb, ws, "Salary");

 let month = document.getElementById("month").value;

 XLSX.writeFile(wb, `salary_${month}.xlsx`);
}

function downloadSlip(empId, month){
    window.open(`/download-slip/${empId}/${month}/`);
}

// 🔥 Page Load
loadMonths();
setCurrentMonth();