const protocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
const ws = new WebSocket(protocol + window.location.host + '/ws');

ws.onopen = () => {
    console.log("WebSocket Connected");
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === "radio_state") {
        updateUI(data);
    }
};

ws.onclose = () => {
    document.getElementById("conn-status").innerText = "DISCONNECTED";
    document.getElementById("conn-status").style.color = "#ff5252";
};

function updateUI(state) {
    // Frequency
    const mhz = (state.frequencyHz / 1000000).toFixed(6);
    document.getElementById("freq-display").innerText = mhz + " MHz";

    // Mode buttons
    document.querySelectorAll('.mode-btn').forEach(btn => {
        if (btn.innerText === state.mode) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });

    // Signal Meter
    const sig = state.signalStrength;
    const blocks = Math.round((sig / 255) * 12);
    let meterStr = "█".repeat(blocks) + "░".repeat(12 - blocks);
    document.getElementById("signal-meter").innerText = meterStr;

    // Squelch state
    const badge = document.getElementById("sql-badge");
    if (state.squelchOpen) {
        badge.className = "sql-badge sql-open";
        badge.innerText = "SQL OPEN";
    } else {
        badge.className = "sql-badge sql-closed";
        badge.innerText = "SQL CLOSED";
    }

    // Squelch slider
    document.getElementById("sql-slider").value = state.squelch;
    document.getElementById("sql-val").innerText = state.squelch;

    // Volume
    document.getElementById("vol-slider").value = state.volume;
    document.getElementById("vol-val").innerText = state.volume;

    // Connection
    const connEl = document.getElementById("conn-status");
    if (state.connected) {
        connEl.innerText = "CONNECTED";
        connEl.style.color = "#00e676";
    } else {
        connEl.innerText = "IC-R6 DISCONNECTED";
        connEl.style.color = "#ff5252";
    }
}

function changeFrequency() {
    let current = document.getElementById("freq-display").innerText;
    let input = prompt("Enter Frequency in MHz (e.g., 118.200000):", parseFloat(current));
    if (input) {
        let hz = Math.round(parseFloat(input) * 1000000);
        ws.send(JSON.stringify({ action: "set_freq", frequencyHz: hz }));
    }
}

function setMode(mode) {
    ws.send(JSON.stringify({ action: "set_mode", mode: mode }));
}

function valChangeTimeout = null;
function updateSquelch(val) {
    document.getElementById("sql-val").innerText = val;
    clearTimeout(valChangeTimeout);
    valChangeTimeout = setTimeout(() => {
        ws.send(JSON.stringify({ action: "set_squelch", squelch: parseInt(val) }));
    }, 200);
}
