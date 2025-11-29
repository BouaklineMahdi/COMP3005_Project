// app/static/main.js

// --- Basic "session" stored in localStorage ---
// Keys: role, token, user_id, email

function setSession({ role, token, user_id, email }) {
    localStorage.setItem("role", role);
    localStorage.setItem("token", token);
    localStorage.setItem("user_id", String(user_id));
    localStorage.setItem("email", email);
}

function clearSession() {
    localStorage.removeItem("role");
    localStorage.removeItem("token");
    localStorage.removeItem("user_id");
    localStorage.removeItem("email");
}

function getSession() {
    const role = localStorage.getItem("role");
    const token = localStorage.getItem("token");
    const user_id = localStorage.getItem("user_id");
    const email = localStorage.getItem("email");
    if (!role || !token || !user_id || !email) {
        return null;
    }
    return { role, token, user_id: parseInt(user_id, 10), email };
}

// Update nav on each page
function updateNav() {
    const session = getSession();
    const navRole = document.getElementById("nav-role");
    const navEmail = document.getElementById("nav-email");
    const navLogin = document.getElementById("nav-login");
    const navLogout = document.getElementById("nav-logout");

    if (!navRole || !navEmail || !navLogin || !navLogout) return;

    if (session) {
        navRole.textContent = `[${session.role}]`;
        navEmail.textContent = session.email;
        navLogin.style.display = "none";
        navLogout.style.display = "inline-block";
    } else {
        navRole.textContent = "";
        navEmail.textContent = "";
        navLogin.style.display = "inline-block";
        navLogout.style.display = "none";
    }
}

// Call backend with Authorization header
async function apiFetch(path, options = {}) {
    const session = getSession();
    const headers = options.headers ? { ...options.headers } : {};

    if (session?.token) {
        headers["Authorization"] = `Bearer ${session.token}`;
    }
    headers["Content-Type"] = headers["Content-Type"] || "application/json";

    const response = await fetch(path, {
        ...options,
        headers,
    });

    if (!response.ok) {
        let detail = `HTTP ${response.status}`;
        try {
            const data = await response.json();
            if (data.detail) detail = data.detail;
        } catch (e) {
            // ignore
        }
        throw new Error(detail);
    }

    // Try JSON; fall back to text
    const text = await response.text();
    try {
        return JSON.parse(text);
    } catch {
        return text;
    }
}

// --- Login page logic ---
function initLoginPage() {
    const form = document.getElementById("login-form");
    if (!form) return; // not on login page

    const roleInput = document.getElementById("login-role");
    const emailInput = document.getElementById("login-email");
    const passwordInput = document.getElementById("login-password");
    const errorElem = document.getElementById("login-error");

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        errorElem.textContent = "";

        const role = roleInput.value;
        const email = emailInput.value.trim();
        const password = passwordInput.value;

        if (!role || !email || !password) {
            errorElem.textContent = "Please fill in all fields.";
            return;
        }

        try {
            const data = await apiFetch(`/auth/${role}-login`, {
                method: "POST",
                body: JSON.stringify({ email, password }),
            });

            // data expected: { role, user_id, email, token }
            setSession(data);

            // Redirect to correct dashboard
            if (role === "member") {
                window.location.href = "/ui/dashboard/member";
            } else if (role === "trainer") {
                window.location.href = "/ui/dashboard/trainer";
            } else if (role === "admin") {
                window.location.href = "/ui/dashboard/admin";
            }
        } catch (err) {
            console.error(err);
            errorElem.textContent = err.message || "Login failed";
        }
    });
}

// --- Member dashboard logic ---
async function loadMemberDashboard() {
    const summaryDiv = document.getElementById("member-summary");
    if (!summaryDiv) return; // not member dashboard

    const session = getSession();
    if (!session || session.role !== "member") {
        window.location.href = "/ui/login/member";
        return;
    }

    try {
        const dashboard = await apiFetch(`/members/${session.user_id}/dashboard`);
        // Assuming dashboard corresponds to member_dashboard_view
        summaryDiv.innerHTML = `
            <p><strong>Name:</strong> ${dashboard.name}</p>
            <p><strong>Email:</strong> ${dashboard.email}</p>
            <p><strong>Latest Metric:</strong> ${
                dashboard.latest_metric_type || "N/A"
            } = ${dashboard.latest_metric_value ?? "N/A"}</p>
            <p><strong>Total Classes Registered:</strong> ${
                dashboard.total_classes_registered
            }</p>
            <p><strong>Upcoming PT Sessions:</strong> ${
                dashboard.upcoming_pt_sessions
            }</p>
        `;
    } catch (err) {
        summaryDiv.textContent = `Error loading dashboard: ${err.message}`;
    }

    // PT sessions can also be shown from the same view, or via dedicated endpoint.
    const ptDiv = document.getElementById("member-pt-sessions");
    if (ptDiv) {
        ptDiv.textContent = "See 'Upcoming PT Sessions' count above.";
    }

    // Class registration form
    const regForm = document.getElementById("member-class-register-form");
    const regResult = document.getElementById("member-class-register-result");
    if (regForm && regResult) {
        regForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            regResult.textContent = "";

            const classIdInput = document.getElementById("member-class-id");
            const classId = parseInt(classIdInput.value, 10);
            if (!classId) {
                regResult.textContent = "Please enter a valid class ID.";
                return;
            }

            try {
                // Adjust URL if your endpoint name differs:
                // e.g. /members/{member_id}/classes/register
                await apiFetch(`/members/${session.user_id}/classes/register`, {
                    method: "POST",
                    body: JSON.stringify({ class_id: classId }),
                });
                regResult.textContent = `Successfully registered for class ${classId}.`;
            } catch (err) {
                regResult.textContent = `Error: ${err.message}`;
            }
        });
    }
}

// --- Trainer dashboard logic ---
async function loadTrainerDashboard() {
    const scheduleDiv = document.getElementById("trainer-schedule");
    if (!scheduleDiv) return; // not trainer dashboard

    const session = getSession();
    if (!session || session.role !== "trainer") {
        window.location.href = "/ui/login/trainer";
        return;
    }

    // Load schedule
    try {
        const schedule = await apiFetch(`/trainers/${session.user_id}/schedule`);
        if (Array.isArray(schedule) && schedule.length > 0) {
            scheduleDiv.innerHTML = `
                <ul>
                    ${schedule
                        .map(
                            (item) => `
                        <li>
                            Class/Session at ${item.start_time} 
                            ${item.end_time ? `– ${item.end_time}` : ""}
                            (room: ${item.room_name || item.room_id})
                        </li>`
                        )
                        .join("")}
                </ul>
            `;
        } else {
            scheduleDiv.textContent = "No sessions scheduled.";
        }
    } catch (err) {
        scheduleDiv.textContent = `Error loading schedule: ${err.message}`;
    }

    // Availability form
    const availForm = document.getElementById("trainer-availability-form");
    const availResult = document.getElementById("trainer-availability-result");
    if (availForm && availResult) {
        availForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            availResult.textContent = "";

            const start = document.getElementById("trainer-availability-start").value;
            const end = document.getElementById("trainer-availability-end").value;

            if (!start || !end) {
                availResult.textContent = "Please fill in both start and end time.";
                return;
            }

            try {
                await apiFetch(`/trainers/${session.user_id}/availability`, {
                    method: "POST",
                    body: JSON.stringify({
                        start_time: start,
                        end_time: end,
                    }),
                });
                availResult.textContent = "Availability slot added.";
            } catch (err) {
                availResult.textContent = `Error: ${err.message}`;
            }
        });
    }
}

// --- Admin dashboard logic ---
async function loadAdminDashboard() {
    const roomResult = document.getElementById("admin-room-result");
    const roomForm = document.getElementById("admin-room-form");
    const classResult = document.getElementById("admin-class-result");
    const classForm = document.getElementById("admin-class-form");
    const classesList = document.getElementById("admin-classes-list");
    const refreshBtn = document.getElementById("admin-refresh-classes");

    if (!roomForm && !classForm && !classesList) return; // not admin dashboard

    const session = getSession();
    if (!session || session.role !== "admin") {
        window.location.href = "/ui/login/admin";
        return;
    }

    // Room form
    if (roomForm && roomResult) {
        roomForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            roomResult.textContent = "";

            const name = document.getElementById("admin-room-name").value.trim();
            const capacity = parseInt(
                document.getElementById("admin-room-capacity").value,
                10
            );

            if (!name || !capacity) {
                roomResult.textContent = "Please fill in room name and capacity.";
                return;
            }

            try {
                await apiFetch("/admins/rooms", {
                    method: "POST",
                    body: JSON.stringify({ name, capacity }),
                });
                roomResult.textContent = "Room created.";
            } catch (err) {
                roomResult.textContent = `Error: ${err.message}`;
            }
        });
    }

    // Class form
    if (classForm && classResult) {
        classForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            classResult.textContent = "";

            const name = document.getElementById("admin-class-name").value.trim();
            const start = document.getElementById("admin-class-start").value.trim();
            const capacity = parseInt(
                document.getElementById("admin-class-capacity").value,
                10
            );
            const trainerId = parseInt(
                document.getElementById("admin-class-trainer-id").value,
                10
            );
            const roomId = parseInt(
                document.getElementById("admin-class-room-id").value,
                10
            );

            if (!name || !start || !capacity || !trainerId || !roomId) {
                classResult.textContent = "Please fill in all fields.";
                return;
            }

            try {
                await apiFetch("/admins/classes", {
                    method: "POST",
                    body: JSON.stringify({
                        name,
                        start_time: start,
                        capacity,
                        trainer_id: trainerId,
                        room_id: roomId,
                    }),
                });
                classResult.textContent = "Class created.";
            } catch (err) {
                classResult.textContent = `Error: ${err.message}`;
            }
        });
    }

    // Classes list
    async function refreshClasses() {
        if (!classesList) return;
        classesList.textContent = "Loading classes...";
        try {
            // Adjust this endpoint if yours differs:
            // Could be GET /admins/classes or GET /classes
            const classes = await apiFetch("/admins/classes");
            if (!Array.isArray(classes) || classes.length === 0) {
                classesList.textContent = "No classes.";
                return;
            }
            classesList.innerHTML = `
                <ul>
                    ${classes
                        .map(
                            (c) => `
                        <li>
                            [${c.class_id}] ${c.name} – ${c.start_time},
                            capacity ${c.capacity}, trainer ${c.trainer_id}, room ${c.room_id}
                        </li>`
                        )
                        .join("")}
                </ul>
            `;
        } catch (err) {
            classesList.textContent = `Error: ${err.message}`;
        }
    }

    if (refreshBtn) {
        refreshBtn.addEventListener("click", refreshClasses);
        // Load once on page load
        refreshClasses();
    }
}

// --- Logout link ---
function initLogoutLink() {
    const logoutLink = document.getElementById("nav-logout");
    if (!logoutLink) return;
    logoutLink.addEventListener("click", () => {
        clearSession();
        // Let the server redirect to /ui/, then nav will be updated
    });
}

// --- Init on every page ---
document.addEventListener("DOMContentLoaded", () => {
    updateNav();
    initLogoutLink();
    initLoginPage();
    loadMemberDashboard();
    loadTrainerDashboard();
    loadAdminDashboard();
});
