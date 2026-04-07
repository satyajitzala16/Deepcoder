let selectedTech = [];

// 🔥 Toggle dropdown
function toggleDropdown() {
    document.getElementById("techDropdown").classList.toggle("show");
}

// 🔥 Load Technologies
async function loadTechnologies() {
    let res = await fetch('/api/technologies/');
    let data = await res.json();

    let box = document.getElementById("techDropdown");
    box.innerHTML = "";

    data.forEach(t => {
        box.innerHTML += `
            <label>
                <input type="checkbox" value="${t.id}" onchange="selectTech(this)">
                ${t.name}
            </label>
        `;
    });
}

// 🔥 Select tech
function selectTech(el) {
    let val = el.value;

    if (el.checked) {
        if (!selectedTech.includes(val)) selectedTech.push(val);
    } else {
        selectedTech = selectedTech.filter(i => i !== val);
    }
}

// 🔥 Add Employee
async function addEmployee() {

    let data = {
        employee_id: document.getElementById("employee_id").value,
        name: document.getElementById("name").value,
        email: document.getElementById("email").value,
        password: document.getElementById("password").value,
        salary: document.getElementById("salary").value,
        date_of_joining: document.getElementById("date_of_joining").value,
        role_id: document.getElementById("role").value,
        technology_ids: selectedTech
    };

    if (!data.employee_id || !data.name || !data.email || !data.password || !data.salary || !data.date_of_joining) {
        alert("All fields required!");
        return;
    }

    await fetch('/api/add-employee/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    });

    alert("Employee Added");

    resetForm();
    loadEmployees();
}

// 🔥 Reset Form
function resetForm() {
    document.getElementById("employee_id").value = "";
    document.getElementById("name").value = "";
    document.getElementById("email").value = "";
    document.getElementById("password").value = "";
    document.getElementById("salary").value = "";
    document.getElementById("date_of_joining").value = "";
    document.getElementById("role").value = "";

    selectedTech = [];
    document.querySelectorAll("#techDropdown input").forEach(cb => cb.checked = false);
}

// 🔥 Load Roles
async function loadRoles() {
    let res = await fetch('/api/roles/');
    let data = await res.json();

    let role = document.getElementById("role");
    role.innerHTML = `<option value="">Select Role</option>`;

    data.forEach(r => {
        role.innerHTML += `<option value="${r.id}">${r.name}</option>`;
    });
}

// 🔥 Load Employees
async function loadEmployees() {

    let res = await fetch('/api/employees/');
    let data = await res.json();

    let html = `
    <tr>
        <th>ID</th>
        <th>Emp ID</th>
        <th>Name</th>
        <th>Email</th>
        <th>Password</th>
        <th>Salary</th>
        <th>DOJ</th>
        <th>Role</th>
        <th>Tech</th>
        <th>Action</th>
    </tr>`;

    data.forEach(e => {
        html += `
        <tr id="row-${e.id}">
            <td>${e.id}</td>
            <td>${e.employee_id || '-'}</td>
            <td>${e.name}</td>
            <td>${e.email}</td>
            <td>${e.password}</td>
            <td>${e.salary}</td>
            <td>${e.date_of_joining || '-'}</td>
            <td>${e.role}</td>
            <td>${e.technologies.join(", ")}</td>
            <td class="action-col">
                <button class="edit-btn" onclick="editRow(${e.id})">Edit</button>
                <button class="delete-btn" onclick="deleteEmployee(${e.id})">Delete</button>
            </td>
        </tr>`;
    });

    document.getElementById("empTable").innerHTML = html;
}

// 🔥 Edit Row (FIXED)
function editRow(id) {

    let row = document.getElementById(`row-${id}`);
    let cols = row.children;

    let doj = cols[6].innerText !== '-' ? cols[6].innerText : "";

    row.innerHTML = `
        <td>${id}</td>
        <td><input value="${cols[1].innerText}"></td>
        <td><input value="${cols[2].innerText}"></td>
        <td><input value="${cols[3].innerText}"></td>
        <td><input value="${cols[4].innerText}"></td>
        <td><input value="${cols[5].innerText}"></td>
        <td><input type="date" value="${doj}"></td>
        <td>-</td>
        <td>-</td>
        <td class="action-col">
            <button class="save-btn" onclick="updateEmployee(${id}, this)">Save</button>
            <button class="cancel-btn" onclick="loadEmployees()">Cancel</button>
        </td>
    `;
}

// 🔥 Update Employee
async function updateEmployee(id, btn) {

    let row = btn.closest("tr");
    let inputs = row.querySelectorAll("input");

    await fetch(`/api/update-employee/${id}/`, {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            employee_id: inputs[0].value,
            name: inputs[1].value,
            email: inputs[2].value,
            password: inputs[3].value,
            salary: inputs[4].value,
            date_of_joining: inputs[5].value
        })
    });

    loadEmployees();
}

// 🔥 Delete
async function deleteEmployee(id) {
    if (!confirm("Delete?")) return;

    await fetch(`/api/delete-employee/${id}/`, {
        method: 'DELETE'
    });

    loadEmployees();
}

// 🔥 Close dropdown
document.addEventListener("click", function(e){
    let box = document.getElementById("techDropdown");
    let select = document.querySelector(".multi-select");

    if (!select.contains(e.target)) {
        box.classList.remove("show");
    }
});

// 🔥 Init
window.onload = function () {
    loadEmployees();
    loadRoles();
    loadTechnologies();
};