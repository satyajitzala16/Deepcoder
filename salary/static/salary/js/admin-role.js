let isEdit = false;

// 🔥 Load Roles
async function loadRoles(){
    let res = await fetch('/api/roles/');
    let data = await res.json();

    let html = `<tr>
        <th>ID</th>
        <th>Name</th>
        <th>Action</th>
    </tr>`;

    data.forEach(r => {
        html += `<tr id="row-${r.id}">
            <td>${r.id}</td>
            <td>${r.name}</td>
            <td>
                <button class="role-btn edit-btn" onclick="editRole(${r.id}, '${r.name}')">Edit</button>
                <button class="role-btn delete-btn" onclick="deleteRole(${r.id})">Delete</button>
            </td>
        </tr>`;
    });

    document.getElementById("roleTable").innerHTML = html;
}

// 🔥 Add or Update Role
async function saveRole(){
    let name = document.getElementById("role_name").value;
    if(!name){ alert("Enter Role Name"); return; }

    if(isEdit){
        await fetch(`/api/update-role/${isEdit}/`, {
            method:'PUT',
            headers:{'Content-Type':'application/json'},
            body: JSON.stringify({name})
        });
        alert("Role updated");
    } else {
        await fetch('/api/add-role/', {
            method:'POST',
            headers:{'Content-Type':'application/json'},
            body: JSON.stringify({name})
        });
        alert("Role added");
    }

    resetForm();
    loadRoles();
}

// 🔥 Edit Role → fill input
function editRole(id, name){
    document.getElementById("role_name").value = name;
    document.querySelector(".card button").innerText = "Update Role";
    isEdit = id;
}

// 🔥 Delete Role
async function deleteRole(id){
    if(!confirm("Are you sure?")) return;

    await fetch(`/api/delete-role/${id}/`, { method:'DELETE' });
    alert("Role deleted");
    loadRoles();
}

// 🔥 Reset Form
function resetForm(){
    document.getElementById("role_name").value = "";
    document.querySelector(".card button").innerText = "Add Role";
    isEdit = false;
}

// 🔥 Page Load
loadRoles();