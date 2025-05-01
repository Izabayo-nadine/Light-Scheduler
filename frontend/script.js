class LightScheduler {
  constructor() {
    this.ws = null;
    this.connected = false;
    this.initializeElements();
    this.initializeWebSocket();
    this.setupEventListeners();
  }

  initializeElements() {
    this.onTimeInput = document.getElementById("onTime");
    this.offTimeInput = document.getElementById("offTime");
    this.submitButton = document.getElementById("submitSchedule");
    this.connectionStatus = document.getElementById("connectionStatus");
    this.lightStatus = document.getElementById("lightStatus");
    this.currentSchedule = document.getElementById("currentSchedule");
  }

  initializeWebSocket() {
    this.ws = new WebSocket("ws://localhost:8765");

    this.ws.onopen = () => {
      this.connected = true;
      this.updateConnectionStatus();
    };

    this.ws.onclose = () => {
      this.connected = false;
      this.updateConnectionStatus();
      // Attempt to reconnect after 5 seconds
      setTimeout(() => this.initializeWebSocket(), 5000);
    };

    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.handleWebSocketMessage(data);
    };

    this.ws.onerror = (error) => {
      console.error("WebSocket error:", error);
      this.connected = false;
      this.updateConnectionStatus();
    };
  }

  setupEventListeners() {
    this.submitButton.addEventListener("click", () => this.handleSubmit());
  }

  handleSubmit() {
    if (!this.connected) {
      alert("Not connected to server. Please wait for connection.");
      return;
    }

    const onTime = this.onTimeInput.value;
    const offTime = this.offTimeInput.value;

    if (!onTime || !offTime) {
      alert("Please select both ON and OFF times");
      return;
    }

    const schedule = {
      type: "schedule",
      onTime: onTime,
      offTime: offTime,
    };

    this.ws.send(JSON.stringify(schedule));
    this.updateCurrentSchedule(onTime, offTime);
  }

  handleWebSocketMessage(data) {
    switch (data.type) {
      case "status":
        this.updateLightStatus(data.state === "on");
        break;
      case "error":
        alert(`Error: ${data.message}`);
        break;
    }
  }

  updateConnectionStatus() {
    this.connectionStatus.textContent = this.connected
      ? "Connected"
      : "Disconnected";
    this.connectionStatus.className = this.connected ? "connected" : "";
  }

  updateLightStatus(isOn) {
    this.lightStatus.className = `light-bulb ${isOn ? "on" : "off"}`;
  }

  updateCurrentSchedule(onTime, offTime) {
    this.currentSchedule.innerHTML = `
            <p>Current Schedule:</p>
            <p>ON: ${onTime}</p>
            <p>OFF: ${offTime}</p>
        `;
  }
}

// Initialize the application when the DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  new LightScheduler();
});
