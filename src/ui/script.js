// --- ESTADO GLOBAL Y PERSISTENCIA ---
const state = {
    username: localStorage.getItem('username'),
    updateInterval: null
};

document.addEventListener('DOMContentLoaded', () => {
    // Si ya hay sesión en el navegador, entramos directo
    if (state.username) {
        showDashboard(state.username);
    }
});

// --- SISTEMA DE LOGIN ---
async function handleLogin() {
    const user = document.getElementById('username').value.trim();
    const pass = document.getElementById('password').value;
    const errorDiv = document.getElementById('login-error');

    try {
        const response = await fetch('/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: user, password: pass })
        });

        const data = await response.json();

        if (data.success) {
            // Guardar sesión
            localStorage.setItem('username', user);
            state.username = user;
            showDashboard(user);
        } else {
            showError("Credenciales incorrectas");
        }
    } catch (err) {
        showError("Servidor fuera de línea");
    }
}

function showDashboard(username) {
    document.getElementById('user-display').innerText = `Admin: ${username}`;
    document.getElementById('login-section').style.display = 'none';
    document.getElementById('dashboard-section').style.display = 'flex';
    
    loadTable();
    startRealTimeClock(); // ¡Iniciamos el segundero!
}

// --- CARGA Y RENDERIZADO ---
async function loadTable() {
    const tableBody = document.getElementById('registry-table');
    
    try {
        const response = await fetch('/get_infants');
        const infants = await response.json();

        tableBody.innerHTML = ''; 

        infants.forEach(inf => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td><strong>${inf.infant_name}</strong><br><small>${inf.gender}</small></td>
                <td class="age-timer" data-birth="${inf.birth_date}">Calculando...</td>
                <td>P: ${inf.father_name}<br>M: ${inf.mother_name}</td>
                <td><span class="badge">${inf.blood_type}</span> | ${inf.weight}kg</td>
                <td>
                    <button class="btn btn-danger" style="padding: 0.3rem; font-size: 0.7rem;">Eliminar</button>
                </td>
            `;
            tableBody.appendChild(row);
        });
    } catch (err) {
        console.error("Error al cargar tabla:", err);
    }
}

// --- MOTOR DEL RELOJ (Tu especialidad) ---
function startRealTimeClock() {
    if (state.updateInterval) clearInterval(state.updateInterval);
    
    state.updateInterval = setInterval(() => {
        const timers = document.querySelectorAll('.age-timer');
        const now = new Date();

        timers.forEach(td => {
            const birth = new Date(td.getAttribute('data-birth'));
            if (isNaN(birth)) return;

            const diff = now - birth;
            const totalSecs = Math.floor(diff / 1000);

            if (totalSecs < 0) {
                td.innerText = "Recién nacido";
                return;
            }

            const y = Math.floor(totalSecs / 31536000);
            const d = Math.floor((totalSecs % 31536000) / 86400);
            const h = Math.floor((totalSecs % 86400) / 3600);
            const m = Math.floor((totalSecs % 3600) / 60);
            const s = totalSecs % 60;

            td.innerText = `${y}a ${d}d | ${h.toString().padStart(2,'0')}:${m.toString().padStart(2,'0')}:${s.toString().padStart(2,'0')}`;
        });
    }, 1000);
}

// --- REGISTRO DE DATOS ---
async function saveData() {
    const payload = {
        infant: document.getElementById('infant_name').value.trim(),
        gender: document.getElementById('gender').value,
        birth_date: document.getElementById('birth_date').value,
        father: document.getElementById('father_name').value.trim(),
        mother: document.getElementById('mother_name').value.trim(),
        bt_i: document.getElementById('blood_type').value,
        weight: parseFloat(document.getElementById('weight').value) || 0,
        size: parseFloat(document.getElementById('size').value) || 0
    };

    if (!payload.infant || !payload.birth_date) {
        alert("Nombre y fecha obligatorios");
        return;
    }

    try {
        const res = await fetch('/add_infant', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (res.ok) {
            alert("✅ Guardado en GS Digital");
            location.reload(); // Recarga para limpiar y actualizar todo
        }
    } catch (err) {
        alert("Error de conexión");
    }
}

function logout() {
    localStorage.clear();
    location.reload();
}

function showError(msg) {
    const errDiv = document.getElementById('login-error');
    errDiv.innerText = msg;
    errDiv.style.display = 'block';
    setTimeout(() => errDiv.style.display = 'none', 3000);
}