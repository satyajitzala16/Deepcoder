let selectedTech = [];

// 🔥 Toggle Dropdown
function toggleDropdown() {
    document.getElementById("techDropdown").classList.toggle("show");
}

// 🔥 Load Technologies (FIXED)
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

// 🔥 Select Tech
function selectTech(el) {
    let value = el.value;

    if (el.checked) {
        if (!selectedTech.includes(value)) {
            selectedTech.push(value);
        }
    } else {
        selectedTech = selectedTech.filter(id => id !== value);
    }
}

// 🔥 Add Employee
async function addEmployee() {

    let name = document.getElementById("name").value.trim();
    let email = document.getElementById("email").value.trim();
    let password = document.getElementById("password").value.trim();
    let salary = document.getElementById("salary").value.trim();
    let role = document.getElementById("role").value;

    if (!name || !email || !password || !salary) {
        alert("All fields required!");
        return;
    }

    await fetch('/api/add-employee/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            name,
            email,
            password,
            salary,
            role_id: role,
            technology_ids: selectedTech
        })
    });

    alert("Employee Added");

    // 🔥 Reset form
    document.getElementById("name").value = "";
    document.getElementById("email").value = "";
    document.getElementById("password").value = "";
    document.getElementById("salary").value = "";
    document.getElementById("role").value = "";
    selectedTech = [];

    // uncheck all checkboxes
    document.querySelectorAll("#techDropdown input").forEach(cb => cb.checked = false);

    loadEmployees();
}

// 🔥 Load Roles
async function loadRoles() {
    let res = await fetch('/api/roles/');
    let data = await res.json();

    let role = document.getElementById("role");
    role.innerHTML = `<option value="">Role</option>`;

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
        <th>Name</th>
        <th>Email</th>
        <th>Password</th>
        <th>Salary</th>
        <th>Role</th>
        <th>Tech</th>
        <th>Action</th>
    </tr>`;

    data.forEach(e => {
        html += `
        <tr id="row-${e.id}">
            <td>${e.id}</td>
            <td>${e.name}</td>
            <td>${e.email}</td>
            <td>${e.password}</td>
            <td>${e.salary}</td>
            <td>${e.role}</td>
            <td>${e.technologies.join(", ")}</td>
            <td>
                <i class="fa fa-edit icon-btn" onclick="editRow(${e.id})"></i>
                <i class="fa fa-trash icon-btn" onclick="deleteEmployee(${e.id})"></i>
            </td>
        </tr>`;
    });

    document.getElementById("empTable").innerHTML = html;
}

// 🔥 Edit
function editRow(id) {

    let row = document.getElementById(`row-${id}`);
    let cols = row.children;

    row.innerHTML = `
        <td>${id}</td>
        <td><input id="n-${id}" value="${cols[1].innerText}"></td>
        <td><input id="e-${id}" value="${cols[2].innerText}"></td>
        <td><input id="p-${id}" value="${cols[3].innerText}"></td>
        <td><input id="s-${id}" value="${cols[4].innerText}"></td>
        <td colspan="3">
            <button onclick="updateEmployee(${id})">Save</button>
            <button onclick="loadEmployees()">Cancel</button>
        </td>
    `;
}

// 🔥 Update
async function updateEmployee(id) {

    await fetch(`/api/update-employee/${id}/`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            name: document.getElementById(`n-${id}`).value,
            email: document.getElementById(`e-${id}`).value,
            password: document.getElementById(`p-${id}`).value,
            salary: document.getElementById(`s-${id}`).value
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

// 🔥 Load all
window.onload = function () {
    loadEmployees();
    loadRoles();
    loadTechnologies();
};

document.addEventListener("click", function(e){
    let box = document.getElementById("techDropdown");
    let select = document.querySelector(".multi-select");

    if (!select.contains(e.target)) {
        box.classList.remove("show");
    }
});