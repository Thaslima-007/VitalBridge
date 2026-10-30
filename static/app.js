
const heartRate = document.getElementById("heart-rate");
const temperature = document.getElementById("temperature");
const spo2 = document.getElementById("spo2");
const badge = document.getElementById("level-badge");
const statusMessage = document.getElementById("status-message");
const alertList = document.getElementById("alert-list");
const updatedAt = document.getElementById("updated-at");

function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, (char) => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#039;"
    }[char]));
}

function renderReading(reading) {
    if (!reading) return;

    heartRate.textContent = reading.heart_rate;

    temperature.textContent =
        Number(reading.temperature).toFixed(1);

    spo2.textContent = reading.spo2;

    badge.textContent = reading.level;

    badge.className =
        "level-badge " + reading.level.toLowerCase();

    statusMessage.textContent = reading.message;
}

function renderAlerts(alerts) {
    if (!alerts.length) {
        alertList.innerHTML =
            '<tr><td colspan="5">No activity yet.</td></tr>';
        return;
    }

    alertList.innerHTML = alerts.map((item) => {

        const readings =
            `${item.heart_rate} bpm · ${Number(item.temperature).toFixed(1)} °C · ${item.spo2}%`;

        let action = item.acknowledged
            ? '<span class="acknowledged">Acknowledged</span>'
            : '<span class="muted">—</span>';

        if (
            window.VITALBRIDGE_ROLE === "caregiver"
            && !item.acknowledged
        ) {
            action = `
                <button class="ack-button"
                    data-ack="${item.id}">
                    Acknowledge
                </button>
            `;
        }

        return `
            <tr>
                <td>${escapeHtml(item.created_at)}</td>

                <td>
                    <span class="table-level ${item.level.toLowerCase()}">
                        ${escapeHtml(item.level)}
                    </span>
                </td>

                <td>${escapeHtml(item.message)}</td>

                <td>${escapeHtml(readings)}</td>

                <td>${action}</td>
            </tr>
        `;

    }).join("");
}

async function loadState() {
    try {
        const response = await fetch("/api/state");

        if (!response.ok) {
            throw new Error("Could not load dashboard data.");
        }

        const data = await response.json();

        renderReading(data.latest);
        renderAlerts(data.alerts);

        updatedAt.textContent =
            "Updated " + new Date().toLocaleTimeString();

    } catch (error) {
        statusMessage.textContent = error.message;
    }
}

async function generateReading(scenario) {

    const buttons =
        document.querySelectorAll("[data-scenario]");

    buttons.forEach(button => button.disabled = true);

    try {
        const response = await fetch("/api/simulate", {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({ scenario })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.error || "Unable to generate a sample."
            );
        }

        await loadState();

    } catch (error) {
        alert(error.message);

    } finally {
        buttons.forEach(button => button.disabled = false);
    }
}

document.querySelectorAll("[data-scenario]").forEach(button => {

    button.addEventListener("click", () => {
        generateReading(button.dataset.scenario);
    });

});

alertList.addEventListener("click", async (event) => {

    const button = event.target.closest("[data-ack]");

    if (!button) return;

    const response = await fetch(
        `/api/alerts/${button.dataset.ack}/acknowledge`,
        { method: "POST" }
    );

    const data = await response.json();

    if (!response.ok) {
        alert(data.error || "Could not acknowledge alert.");
        return;
    }

    await loadState();
});

loadState();
