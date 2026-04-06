let isEdit = false;

// 🔥 Load Employees Dropdown
async function loadEmployees() {
    let res = await fetch('/employees/');
    let data = await res.json();

    let dropdown = document.getElementById("emp_id");
    dropdown.innerHTML = `<option value="">Select Employee</option>`;

    data.forEach(emp => {
        dropdown.innerHTML += `<option value="${emp.id}">${emp.name}</option>`;
    });
}

// 🔥 Load Months (Financial Year)
function loadMonths() {
    const monthDropdown = document.getElementById("month");

    // 🔥 Reset first
    monthDropdown.innerHTML = `<option value="">Select Month</option>`;

    const months = [
        "April","May","June","July","August","September",
        "October","November","December","January","February","March"
    ];

    let currentYear = new Date().getFullYear();

    for(let y = currentYear; y <= currentYear + 1; y++) {
        months.forEach((m, index) => {
            let year;
            if(index >= 9){ // Jan-Feb-Mar next year
                year = y + 1;
            } else {
                year = y;
            }
            let value = `${m} ${year}`;
            monthDropdown.innerHTML += `<option value="${value}">${value}</option>`;
        });
    }
}

// 🔥 Save OR Update Leave
async function saveLeave() {

    let id = document.getElementById("leave_id").value;
    let emp_id = document.getElementById("emp_id").value;
    let month = document.getElementById("month").value;
    let total = document.getElementById("total").value;
    let paid = document.getElementById("paid").value;
    let comp = document.getElementById("comp").value || 0;  // default 0

    if(!emp_id || !month) {
        alert("Employee & Month required");
        return;
    }

    if(isEdit) {
        // 🔥 Update leave
        let res = await fetch(`/update-leave/${id}/`, {
            method: 'PUT',
            headers: {'Content-Type':'application/json'},
            body: JSON.stringify({
                total_leaves: total,
                paid_leaves: paid,
                comp_off_leaves: comp
            })
        });
        let data = await res.json();
        if(data.error) alert(data.error); 
        else alert("Leave Updated");

    } else {
        // 🔥 Add new leave
        let res = await fetch('/add-leave/', {
            method: 'POST',
            headers: {'Content-Type':'application/json'},
            body: JSON.stringify({
                employee_id: emp_id,
                month: month,
                total_leaves: total,
                paid_leaves: paid,
                comp_off_leaves: comp
            })
        });
        let data = await res.json();
        if(data.error) alert(data.error);
        else alert(data.message || "Leave Saved");
    }

    resetForm();
    loadLeaves();
}

// 🔥 Load Leaves Table
async function loadLeaves() {

    let res = await fetch('/leave-list/');
    let data = await res.json();

    let table = document.getElementById("leaveTable");
    table.innerHTML = "";

    data.forEach(i => {
        table.innerHTML += `
        <tr>
            <td>${i.id}</td>
            <td>${i.employee_name}</td>
            <td>${i.month}</td>
            <td>${i.total_leaves}</td>
            <td>${i.paid_leaves}</td>
            <td>${i.comp_off_leaves}</td>
            <td>
                <button onclick="editLeave(${i.id}, ${i.employee_id}, '${i.month}', ${i.total_leaves}, ${i.paid_leaves}, ${i.comp_off_leaves})">Edit</button>
            </td>
        </tr>
        `;
    });
}

// 🔥 Edit → Fill Form
function editLeave(id, emp_id, month, total, paid, comp) {
    document.getElementById("leave_id").value = id;
    document.getElementById("emp_id").value = emp_id;
    document.getElementById("month").value = month;
    document.getElementById("total").value = total;
    document.getElementById("paid").value = paid;
    document.getElementById("comp").value = comp;

    document.getElementById("saveBtn").innerText = "Update";
    isEdit = true;
}

// 🔥 Reset Form
function resetForm() {
    document.getElementById("leave_id").value = "";
    document.getElementById("emp_id").value = "";
    document.getElementById("month").value = "";
    document.getElementById("total").value = "";
    document.getElementById("paid").value = "";
    document.getElementById("comp").value = "";

    document.getElementById("saveBtn").innerText = "Save";
    isEdit = false;
}

// 🔥 Page Load
loadEmployees();
loadMonths();
loadLeaves();