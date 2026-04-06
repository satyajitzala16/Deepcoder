// 🔥 Add Employee
async function addEmployee() {
    await fetch('/api/add-employee/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            name: document.getElementById("name").value,
            email: document.getElementById("email").value,
            password: document.getElementById("password").value,
            salary: document.getElementById("salary").value
        })
    });
    alert("Employee Added");
    loadEmployees();
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
        <th>Yearly Leaves</th>
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
            <td>${e.yearly_paid_leaves}</td>
            <td>${e.role}</td>
            <td>${e.technologies.join(", ")}</td>
            <td>
                <button onclick="editRow(${e.id})">Edit</button>
                <button onclick="deleteEmployee(${e.id})">Delete</button>
            </td>
        </tr>`;
    });

    document.getElementById("empTable").innerHTML = html;
}

// 🔥 Inline Edit
function editRow(id) {
    let row = document.getElementById(`row-${id}`);
    let cols = row.children;

    let name = cols[1].innerText;
    let email = cols[2].innerText;
    let password = cols[3].innerText;
    let salary = cols[4].innerText;
    let leaves = cols[5].innerText;
    let role = cols[6].innerText;
    let tech = cols[7].innerText;

    row.innerHTML = `
        <td>${id}</td>
        <td><input style="width:100%" id="name-${id}" value="${name}"></td>
        <td><input style="width:100%" id="email-${id}" value="${email}"></td>
        <td><input style="width:100%" id="password-${id}" value="${password}"></td>
        <td><input style="width:100%" id="salary-${id}" value="${salary}"></td>
        <td>${leaves}</td>
        <td>${role}</td>
        <td>${tech}</td>
        <td>
            <button class="save-btn" onclick="updateEmployee(${id})">Save</button>
            <button class="cancel-btn" onclick="loadEmployees()">Cancel</button>
        </td>
    `;
}

// 🔥 Update Employee
async function updateEmployee(id) {
    let name = document.getElementById(`name-${id}`).value;
    let email = document.getElementById(`email-${id}`).value;
    let password = document.getElementById(`password-${id}`).value;
    let salary = document.getElementById(`salary-${id}`).value;

    await fetch(`/api/update-employee/${id}/`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, email, password, salary })
    });

    alert("Updated");
    loadEmployees();
}

// 🔥 Delete Employee
async function deleteEmployee(id) {
    if (!confirm("Are you sure?")) return;

    await fetch(`/api/delete-employee/${id}/`, { method: 'DELETE' });
    alert("Deleted");
    loadEmployees();
}

// 🔥 Page Load
loadEmployees();