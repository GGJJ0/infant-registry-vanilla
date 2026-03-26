// --- ESTADO GLOBAL Y PERSISTENCIA ---
const state = {
    username: localStorage.getItem('username'),
    updateInterval: null,
    charts: { gender: null, blood: null } // Para poder actualizar las gráficas
};

document.addEventListener('DOMContentLoaded', () => {
    if (state.username) {
        showDashboard(state.username);
    }
});

// --- SISTEMA DE LOGIN ---
async function handleLogin() {
    const user = document.getElementById('username').value.trim();
    const pass = document.getElementById('password').value;

    try {
        const response = await fetch('/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: user, password: pass })
        });

        const data = await response.json();

        if (data.success) {
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
    cargarGraficas(); // Nueva función
    startRealTimeClock();
}

// --- CARGA Y RENDERIZADO CON ETAPAS DE VIDA ---
async function loadTable() {
    const tableBody = document.getElementById('registry-table');
    
    try {
        const response = await fetch('/api/infants'); // Ajustado a la nueva ruta del main.py
        const infants = await response.json();

        tableBody.innerHTML = ''; 

        infants.forEach(inf => {
            const row = document.createElement('tr');
            // Usamos los nombres de columna que vimos en tu DB: nombre, genero, etc.
            row.innerHTML = `
                <td><strong>${inf.nombre}</strong><br><small>${inf.genero}</small></td>
                <td class="age-timer" data-birth="${inf.fecha_nacimiento}">Calculando...</td>
                <td>P: ${inf.padre}<br>M: ${inf.madre}</td>
                <td><span class="badge">${inf.tipo_sangre}</span> | ${inf.peso}kg | ${inf.estado}</td>
                <td>
                    <button class="btn btn-danger" onclick="eliminarRegistro(${inf.id})" style="padding: 0.3rem; font-size: 0.7rem;">Eliminar</button>
                </td>
            `;
            tableBody.appendChild(row);
        });
    } catch (err) {
        console.error("Error al cargar tabla:", err);
    }
}

// --- ELIMINACIÓN DE REGISTROS ---
async function eliminarRegistro(id) {
    if (confirm('¿Seguro que deseas eliminar este registro de GS Digital?')) {
        try {
            const res = await fetch(`/api/infants/${id}`, { method: 'DELETE' });
            if (res.ok) {
                loadTable();
                cargarGraficas(); // Actualizamos gráficas al borrar
            }
        } catch (err) {
            alert("No se pudo eliminar el registro");
        }
    }
}

// --- MOTOR DEL RELOJ Y ETAPAS DE VIDA ---
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

            // Lógica de etapas pedida
            let etapa = "";
            if (y >= 60) etapa = "Anciano";
            else if (y >= 26) etapa = "Adulto";
            else if (y >= 18) etapa = "Adulto Joven";
            else if (y >= 14) etapa = "Adolescente";
            else if (y >= 12) etapa = "Preadolescente";
            else if (y >= 2) etapa = "Niño";
            else if (totalSecs >= 2419200) etapa = "Bebé"; // > 28 días
            else etapa = "Recién Nacido";

            td.innerHTML = `<strong>${etapa}</strong><br>${y}a ${d}d | ${h.toString().padStart(2,'0')}:${m.toString().padStart(2,'0')}:${s.toString().padStart(2,'0')}`;
        });
    }, 1000);
}

// --- SISTEMA DE GRÁFICAS (Chart.js) ---
async function cargarGraficas() {
    try {
        const res = await fetch('/api/stats');
        const stats = await res.json();

        // Destruir gráficas anteriores si existen para evitar errores de renderizado
        if (state.charts.gender) state.charts.gender.destroy();
        if (state.charts.blood) state.charts.blood.destroy();

        // Gráfica de Géneros
        state.charts.gender = new Chart(document.getElementById('graficaGeneros'), {
            type: 'pie',
            data: {
                labels: Object.keys(stats.generos),
                datasets: [{
                    data: Object.values(stats.generos),
                    backgroundColor: ['#3498db', '#f1c40f', '#e74c3c']
                }]
            },
            options: { responsive: true, plugins: { title: { display: true, text: 'Hombres vs Mujeres' } } }
        });

        // Gráfica de Sangre
        state.charts.blood = new Chart(document.getElementById('graficaSangre'), {
            type: 'bar',
            data: {
                labels: Object.keys(stats.sangre),
                datasets: [{
                    label: 'Cantidad',
                    data: Object.values(stats.sangre),
                    backgroundColor: '#e74c3c'
                }]
            },
            options: { responsive: true, plugins: { title: { display: true, text: 'Tipos de Sangre' } } }
        });
    } catch (err) {
        console.error("Error cargando gráficas:", err);
    }
}

// --- REGISTRO DE DATOS ---
async function saveData() {
    const payload = {
        nombre: document.getElementById('infant_name').value.trim(),
        genero: document.getElementById('gender').value,
        fecha_nacimiento: document.getElementById('birth_date').value,
        padre: document.getElementById('father_name').value.trim(),
        madre: document.getElementById('mother_name').value.trim(),
        tipo_sangre: document.getElementById('blood_type').value,
        peso: parseFloat(document.getElementById('weight').value) || 0,
        talla: parseFloat(document.getElementById('size').value) || 0
    };

    if (!payload.nombre || !payload.fecha_nacimiento) {
        alert("Nombre y fecha obligatorios");
        return;
    }

    try {
        const res = await fetch('/api/infants', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (res.ok) {
            alert("✅ Guardado en GS Digital");
            loadTable();
            cargarGraficas();
            // Limpiar formulario
            document.querySelectorAll('input').forEach(i => i.value = '');
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
    if (errDiv) {
        errDiv.innerText = msg;
        errDiv.style.display = 'block';
        setTimeout(() => errDiv.style.display = 'none', 3000);
    }
}