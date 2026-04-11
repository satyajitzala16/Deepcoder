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

 let res = await fetch(`/api/employee-salary/?month=${encodeURIComponent(m)}`);
 let data = await res.json();

 if(!res.ok || data.error){
     alert(data.error || "Unable to load salary records");
     return;
 }

 salaryData = data;

 let totalSalary = 0;
 let totalDeductions = 0;
 let totalNetPay = 0;

 let html = `
 <tr>
   <th>Emp ID</th>
   <th>Name</th>
   <th>Month</th>
   <th>Role</th>
   <th>Gross</th>
   <th>Pay Days</th>
   <th>Total Leaves</th>
   <th>Paid Leaves</th>
   <th>Comp Off</th>
   <th>Unpaid Leaves</th>
   <th>Total Earnings</th>
   <th>Total Deductions</th>
   <th>Net Pay</th>
   <th>Slip</th>
 </tr>
 `;

 if(data.length === 0){
   html += `<tr><td colspan="14">No Data Found</td></tr>`;
 }else{

   data.forEach(e=>{

     totalSalary += parseFloat(e.total_earnings);
     totalDeductions += parseFloat(e.total_deductions);
     totalNetPay += parseFloat(e.final_salary);

     html += `
     <tr>
       <td>${e.employee_id}</td>
       <td>${e.name}</td>
       <td>${e.month}</td>
       <td>${e.role}</td>
       <td>${e.salary}</td>
       <td>${e.pay_days}/${e.total_days}</td>
       <td>${e.total_leaves}</td>
       <td>${e.paid_leaves}</td>
       <td>${e.comp_off_leaves}</td>
       <td>${e.unpaid_leaves}</td>
       <td>${e.total_earnings}</td>
       <td>${e.total_deductions}</td>
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
       <td colspan="10">Totals</td>
       <td>${totalSalary.toFixed(2)}</td>
       <td>${totalDeductions.toFixed(2)}</td>
       <td>${totalNetPay.toFixed(2)}</td>
       <td>-</td>
   </tr>
   `;
 }

 document.getElementById("salarySummary").innerText =
     `Records: ${salaryData.length} | Total Earnings: ${totalSalary.toFixed(2)} | Total Deductions: ${totalDeductions.toFixed(2)} | Total Net Pay: ${totalNetPay.toFixed(2)}`;

 document.getElementById("salaryTable").innerHTML = html;
}


// 🔍 Search Filter
function filterTable(){

 let input = document.getElementById("search").value.toLowerCase();
 let rows = document.querySelectorAll("#salaryTable tr");

 rows.forEach((row, index) => {

     if(index === 0) return;

     let name = row.children[1]?.innerText.toLowerCase();

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

 let csv = "Employee ID,Name,Month,Gross Salary,Total Earnings,Total Deductions,Net Pay\n";

 salaryData.forEach(e=>{
     csv += `${e.employee_id},${e.name},${e.month},${e.salary},${e.total_earnings},${e.total_deductions},${e.final_salary}\n`;
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

 let data = [[
     "Employee ID",
     "Name",
     "Month",
     "Gross Salary",
     "Total Earnings",
     "Total Deductions",
     "Net Pay"
 ]];

 salaryData.forEach(e=>{
     data.push([
         e.employee_id,
         e.name,
         e.month,
         e.salary,
         e.total_earnings,
         e.total_deductions,
         e.final_salary
     ]);
 });

 let wb = XLSX.utils.book_new();
 let ws = XLSX.utils.aoa_to_sheet(data);

 XLSX.utils.book_append_sheet(wb, ws, "Salary");

 let month = document.getElementById("month").value;

 XLSX.writeFile(wb, `salary_${month}.xlsx`);
}

function downloadSlip(empId, month){
    window.open(`/download-slip/${empId}/${encodeURIComponent(month)}/`);
}

// 🔥 Page Load
loadMonths();
setCurrentMonth();
