const apiBase = "http://localhost:8000";
const operatingRoomSelect = document.getElementById("or-select");
const connectButton = document.getElementById("connect-btn");
const vitalsGrid = document.getElementById("vitals-grid");
const alertsList = document.getElementById("alerts-list");
const connectionStatus = document.getElementById("connection-status");
const sessionInfo = document.getElementById("session-info");

const vitalsTemplate = document.getElementById("vital-card-template");
let monitoringInterval = null;

async function fetchOperatingRooms() {
  const response = await fetch(`${apiBase}/operating-rooms`);
  if (!response.ok) throw new Error("无法加载手术间");
  const rooms = await response.json();
  renderOperatingRooms(rooms);
}

function renderOperatingRooms(rooms) {
  if (!rooms.length) {
    operatingRoomSelect.innerHTML = "<option disabled>暂无手术间</option>";
    connectButton.disabled = true;
    return;
  }
  operatingRoomSelect.innerHTML = rooms
    .map((room) => `<option value="${room.id}">${room.name}</option>`)
    .join("");
  connectButton.disabled = false;
}

async function simulateVitals() {
  const parameters = [
    { id: 1, name: "心率", unit: "bpm", base: 78, variance: 10 },
    { id: 2, name: "收缩压", unit: "mmHg", base: 118, variance: 15 },
    { id: 3, name: "血氧饱和度", unit: "%", base: 98, variance: 2 },
  ];

  parameters.forEach((param) => {
    const card = vitalsTemplate.content.cloneNode(true);
    card.querySelector(".vital-card").dataset.parameterId = param.id;
    card.querySelector(".vital-name").textContent = param.name;
    card.querySelector(".vital-unit").textContent = param.unit;
    vitalsGrid.appendChild(card);
  });

  monitoringInterval = setInterval(() => {
    parameters.forEach((param) => {
      const newValue = Math.round(
        param.base + (Math.random() - 0.5) * param.variance * 2
      );
      updateVitalCard(param.id, newValue, param);
    });
  }, 3500);
}

function updateVitalCard(parameterId, value, definition) {
  const card = vitalsGrid.querySelector(
    `.vital-card[data-parameter-id="${parameterId}"]`
  );
  if (!card) return;

  card.querySelector(".vital-value").textContent = value;
  const isAlert =
    (definition.name === "心率" && (value < 50 || value > 120)) ||
    (definition.name === "收缩压" && (value < 80 || value > 160)) ||
    (definition.name === "血氧饱和度" && value < 92);

  card.classList.toggle("alert", isAlert);

  if (isAlert) {
    const item = document.createElement("li");
    item.innerHTML = `<strong>${definition.name}</strong> 当前值 ${value}${definition.unit}`;
    alertsList.prepend(item);
  }
}

function connectMonitoring() {
  const selected = operatingRoomSelect.options[operatingRoomSelect.selectedIndex];
  if (!selected) return;

  connectionStatus.textContent = "监测中";
  connectionStatus.style.borderColor = "rgba(48, 227, 202, 0.8)";
  sessionInfo.textContent = `正在监测：${selected.text}`;
  vitalsGrid.innerHTML = "";
  alertsList.innerHTML = "";
  if (monitoringInterval) {
    clearInterval(monitoringInterval);
  }
  simulateVitals();
}

connectButton.addEventListener("click", connectMonitoring);

fetchOperatingRooms()
  .catch((error) => {
    console.error("Failed to load operating rooms", error);
    connectionStatus.textContent = "离线模式";
    connectionStatus.style.borderColor = "rgba(250, 204, 21, 0.8)";
    renderOperatingRooms([
      { id: "sim-or-1", name: "模拟手术间 A" },
      { id: "sim-or-2", name: "模拟手术间 B" },
    ]);
  });
