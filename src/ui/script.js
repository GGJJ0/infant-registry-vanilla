// Estado global de la aplicación
const state = {
    currentRole: localStorage.getItem('role'),
    username: localStorage.getItem('username'),
    updateInterval: null
};

// --- INICIALIZACIÓN ---
document.addEventListener('DOMContentLoaded', () => {
    // Si ya hay una sesión guardada, saltamos el login
    if (state.username && state.currentRole) {
        showDashboard(state.username);
    }
});

// --- SISTEMA DE LOGIN ---
document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = e.target.querySelector('button');
    btn.disabled = true; // Evita doble clic
    btn.innerText = "Verificando...";

    const payload = {
        username: document.getElementById('username').value.trim(),
        password: document.getElementById('password').value
    };

    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (response.ok && data.status === 'success') {
            // Guardar en almacenamiento local para persistencia
            localStorage.setItem('role', data.role);
            localStorage.setItem('username', data.username);
            state.currentRole = data.role;
            state.username = data.username;
            
            showDashboard(data.username);
        } else {
            showError("Usuario o clave incorrectos");
        }
    } catch (err) {
        showError("Servidor fuera de línea");
    } finally {
        btn.disabled = false;
        btn.innerText = "Entrar al Sistema";
    }
});

// --- MOTOR DEL DASHBOARD ---
async function showDashboard(username) {
    document.getElementById('login-section').classList.add('hidden');
    document.getElementById('dashboard-section').classList.remove('hidden');
    document.getElementById('user-info').classList.remove('hidden');
    document.getElementById('current-user-display').innerText = `Operador: ${username}`;

    if (state.currentRole === 'admin') {
        document.getElementById('btn-add-infant').classList.remove('hidden');
    }
    
    await loadInfants();
    startRealTimeClock();
}

// --- CARGA Y RENDERIZADO ---
async function loadInfants() {
    const tbody = document.getElementById('infants-body');
    tbody.innerHTML = '<tr><td colspan="5">Cargando registros...</td></tr>';

    try {
        const response = await fetch('/api/infants');
        if (!response.ok) throw new Error();
        
        const infants = await response.json();
        tbody.innerHTML = ''; // Limpiar

        if (infants.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5">No hay infantes registrados.</td></tr>';
            return;
        }

        infants.forEach(inf => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td><strong>${inf.infant_name}</strong></td>
                <td>${inf.gender === 'M' ? '♂️ Masc' : '♀️ Fem'}</td>
                <td class="age-timer" data-birth="${inf.birth_date}">---</td>
                <td><span class="status-pill ${inf.status.toLowerCase()}">${inf.status}</span></td>
                <td><button class="btn-sm" onclick="viewDetails(${inf.id})">Detalles</button></td>
            `;
            tbody.appendChild(row);
        });
    } catch (err) {
        tbody.innerHTML = '<tr><td colspan="5" class="error">Error al conectar con la base de datos</td></tr>';
    }
}

// --- CÁLCULO DE TIEMPO REAL ---
function startRealTimeClock() {
    if (state.updateInterval) clearInterval(state.updateInterval);
    
    state.updateInterval = setInterval(() => {
        const timers = document.querySelectorAll('.age-timer');
        const now = new Date();

        timers.forEach(td => {
            const birth = new Date(td.getAttribute('data-birth'));
            const diff = now - birth;

            if (isNaN(birth)) {
                td.innerText = "Fecha inválida";
                return;
            }

            // Cálculos matemáticos puros
            const totalSecs = Math.floor(diff / 1000);
            const y = Math.floor(totalSecs / 31536000);
            const d = Math.floor((totalSecs % 31536000) / 86400);
            const h = Math.floor((totalSecs % 86400) / 3600);
            const m = Math.floor((totalSecs % 3600) / 60);
            const s = totalSecs % 60;

            td.innerText = `${y}a ${d}d | ${h.toString().padStart(2,'0')}:${m.toString().padStart(2,'0')}:${s.toString().padStart(2,'0')}`;
        });
    }, 1000);
}

// --- GUARDADO SEGURO ---
document.getElementById('infant-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const payload = {
        infant: document.getElementById('infant_name').value.trim(),
        gender: document.getElementById('gender').value,
        birth_date: document.getElementById('birth_date').value,
        father: document.getElementById('father_name').value.trim(),
        mother: document.getElementById('mother_name').value.trim(),
        weight: parseFloat(document.getElementById('weight').value) || 0,
        size: parseFloat(document.getElementById('size').value) || 0
    };

    // Validación básica antes de enviar
    if (!payload.infant || !payload.birth_date) {
        alert("El nombre y la fecha son obligatorios");
        return;
    }

    try {
        const res = await fetch('/api/infants', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (res.ok) {
            alert("✅ Registro guardado con éxito");
            e.target.reset();
            hideRegisterForm();
            loadInfants();
        }
    } catch (err) {
        alert("Error al guardar");
    }
});

// --- UTILIDADES ---
function showError(msg) {
    const errDiv = document.getElementById('login-error');
    errDiv.innerText = msg;
    setTimeout(() => errDiv.innerText = "", 3000);
}

function showRegisterForm() {
    document.getElementById('dashboard-section').classList.add('hidden');
    document.getElementById('register-infant-section').classList.remove('hidden');
}

function hideRegisterForm() {
    document.getElementById('register-infant-section').classList.add('hidden');
    document.getElementById('dashboard-section').classList.remove('hidden');
}

function logout() {
    localStorage.clear();
    location.reload();
}