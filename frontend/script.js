const API = "http://127.0.0.1:8000";

/* ---------- Inputs ---------- */
const name = document.getElementById("name");
const age = document.getElementById("age");
const gender = document.getElementById("gender");
const disease = document.getElementById("disease");

const pid = document.getElementById("pid");
const hr = document.getElementById("hr");
const spo2 = document.getElementById("spo2");
const sbp = document.getElementById("sbp");
const dbp = document.getElementById("dbp");
const rr = document.getElementById("rr");

const alloc_pid = document.getElementById("alloc_pid");

/* ---------- UI ---------- */
const loader = document.getElementById("loader");
const badge = document.getElementById("severityBadge");
const resultBox = document.getElementById("result");
const reasonList = document.getElementById("reasonList");
const explanationList = document.getElementById("explanationList");

/* ---------- Add Patient ---------- */
function addPatient() {
    fetch(`${API}/patients/add`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            name: name.value,
            age: Number(age.value),
            gender: gender.value,
            disease: disease.value
        })
    })
    .then(res => res.json())
    .then(data => {
        pid.value = data.patient_id;
        alloc_pid.value = data.patient_id;
        alert("Patient added with ID: " + data.patient_id);
    });
}

/* ---------- Add Vitals ---------- */
function addVitals() {
    fetch(`${API}/vitals/add`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            patient_id: Number(pid.value),
            heart_rate: Number(hr.value),
            spo2: Number(spo2.value),
            systolic_bp: Number(sbp.value),
            diastolic_bp: Number(dbp.value),
            respiration_rate: Number(rr.value)
        })
    })
    .then(() => alert("Vitals added"));
}

/* ---------- Allocate ICU ---------- */
function allocate() {
    loader.style.display = "block";
    badge.innerHTML = "";
    reasonList.innerHTML = "";
    explanationList.innerHTML = "";
    resultBox.innerText = "";

    fetch(`${API}/allocate/${alloc_pid.value}`, { method: "POST" })
        .then(res => res.json())
        .then(data => {
            loader.style.display = "none";

            /* Severity Badge */
            const severity = data.final_decision;
            badge.className = "severity-badge";

            if (severity === "Stable") {
                badge.classList.add("severity-stable");
                badge.innerText = "🟢 Stable";
            } else if (severity === "Moderate") {
                badge.classList.add("severity-moderate");
                badge.innerText = "🟡 Moderate";
            } else {
                badge.classList.add("severity-critical");
                badge.innerText = "🔴 Critical";
            }

            /* Reasons */
            data.reasons.forEach(r => {
                const li = document.createElement("li");
                li.innerText = r;
                reasonList.appendChild(li);
            });

            /* Explanation (Rule vs ML) */
            explanationList.innerHTML = `
                <li>Rule-based Severity: <b>${data.rule_based.severity}</b></li>
                <li>Rule-based Score: ${data.rule_based.score.toFixed(2)}</li>
                <li>ML Severity: <b>${data.ml_based.severity}</b></li>
                <li>ML Confidence: ${(data.ml_based.confidence * 100).toFixed(1)}%</li>
            `;

            /* Raw JSON (for viva) */
            resultBox.innerText = JSON.stringify(data, null, 2);

            loadICUStatus();
        })
        .catch(() => {
            loader.style.display = "none";
            alert("ICU allocation failed");
        });
}

/* ---------- ICU STATUS ---------- */
function loadICUStatus() {
    fetch(`${API}/icu/status`)
        .then(res => res.json())
        .then(data => {
            document.getElementById("bedsCount").innerText = data.beds_available;
            document.getElementById("ventsCount").innerText = data.ventilators_available;

            document.getElementById("bedsBar").style.width =
                Math.min(data.beds_available * 20, 100) + "%";
            document.getElementById("ventsBar").style.width =
                Math.min(data.ventilators_available * 20, 100) + "%";
        });
}

/* ---------- Dark Mode ---------- */
function toggleDarkMode() {
    document.body.classList.toggle("dark");
}

/* ---------- Auto Refresh ---------- */
window.onload = () => {
    loadICUStatus();
    setInterval(loadICUStatus, 5000);
};
/* ---------- Timeline ---------- */
function loadTimeline() {
    fetch(`${API}/allocate/timeline`)
        .then(res => res.json())
        .then(data => {
            const ul = document.getElementById("timeline");
            ul.innerHTML = "";

            data.forEach(r => {
                const li = document.createElement("li");
                li.innerText =
                    `Patient ${r.patient_id} → Bed ${r.bed_id} ` +
                    (r.ventilator_id ? `+ Ventilator ${r.ventilator_id}` : "") +
                    ` (Score: ${r.severity_score.toFixed(2)})`;
                ul.appendChild(li);
            });
        });
}

/* ---------- Patient History ---------- */
function loadPatientHistory() {
    fetch(`${API}/patients/history`)
        .then(res => res.json())
        .then(data => {
            const tbody = document.getElementById("patientTable");
            tbody.innerHTML = "";

            data.forEach(p => {
                const row = document.createElement("tr");
                row.innerHTML = `
                    <td>${p.patient_id}</td>
                    <td>${p.name}</td>
                    <td>${p.status}</td>
                `;
                tbody.appendChild(row);
            });
        });
}

/* ---------- Severity Chart ---------- */
let chart;
function loadSeverityChart() {
    fetch(`${API}/icu/severity-stats`)
        .then(res => res.json())
        .then(data => {
            const ctx = document.getElementById("severityChart");

            if (chart) chart.destroy();

            chart = new Chart(ctx, {
                type: "bar",
                data: {
                    labels: ["Stable", "Moderate", "Critical"],
                    datasets: [{
                        label: "Patients",
                        data: [
                            data.Stable,
                            data.Moderate,
                            data.Critical
                        ],
                        backgroundColor: ["#22c55e", "#eab308", "#ef4444"]
                    }]
                }
            });
        });
}
window.onload = () => {
    loadICUStatus();
    loadTimeline();
    loadPatientHistory();
    loadSeverityChart();

    setInterval(() => {
        loadICUStatus();
        loadTimeline();
        loadPatientHistory();
        loadSeverityChart();
    }, 5000);
};
