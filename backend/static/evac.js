// static/evac.js
(async () => {
  const video = document.getElementById("evacVideo");
  const startBtn = document.getElementById("startEvac");
  const results = document.getElementById("evacResults");
  let running = false;

  async function startCamera() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      video.srcObject = stream;
    } catch (e) {
      results.innerText = "Camera error: " + e.message;
    }
  }

  startBtn.addEventListener("click", async () => {
    if (running) return;
    running = true;
    results.innerText = "Evac mode running (demo only) — no recognition yet.";
    // place recognition loop here later
  });

  startCamera();
})();
