let isEdit = false;

// 🔹 Add Technology
async function addTechnology(){
    let name = document.getElementById("tech_name").value.trim();
    if(!name) return alert("Technology name required");

    await fetch('/api/add-technology/',{
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify({name})
    });

    alert("Technology Added");
    document.getElementById("tech_name").value = "";
    loadTechnologies();
}

// 🔹 Load Technologies
async function loadTechnologies(){
    let res = await fetch('/api/technologies/');
    let data = await res.json();

    let html = `<tr>
        <th>ID</th>
        <th>Name</th>
        <th>Action</th>
    </tr>`;

    data.forEach(t=>{
        html += `<tr id="row-${t.id}">
            <td>${t.id}</td>
            <td>${t.name}</td>
            <td>
                <button class="edit-btn" onclick="editTech(${t.id},'${t.name}')">Edit</button>
                <button class="delete-btn" onclick="deleteTech(${t.id})">Delete</button>
            </td>
        </tr>`;
    });

    document.getElementById("techTable").innerHTML = html;
}

// 🔹 Edit Technology
function editTech(id, name){
    let row = document.getElementById(`row-${id}`);
    row.innerHTML = `<td>${id}</td>
        <td><input id="tech-${id}" value="${name}"></td>
        <td>
            <button class="save-btn" onclick="updateTech(${id})">Save</button>
            <button class="cancel-btn" onclick="loadTechnologies()">Cancel</button>
        </td>`;
}

// 🔹 Update Technology
async function updateTech(id){
    let name = document.getElementById(`tech-${id}`).value.trim();
    if(!name) return alert("Technology name required");

    await fetch(`/api/update-technology/${id}/`,{
        method:'PUT',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify({name})
    });

    alert("Updated");
    loadTechnologies();
}

// 🔹 Delete Technology
async function deleteTech(id){
    if(!confirm("Are you sure?")) return;

    await fetch(`/api/delete-technology/${id}/`,{ method:'DELETE' });

    alert("Deleted");
    loadTechnologies();
}

// 🔹 Page Load
loadTechnologies();