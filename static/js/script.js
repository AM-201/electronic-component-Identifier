const imageInput = document.getElementById("imageInput");
const browseBtn = document.getElementById("browseBtn");
const predictBtn = document.getElementById("predictBtn");

const previewImage = document.getElementById("previewImage");
const dropZone = document.getElementById("dropZone");

const topClass = document.getElementById("topClass");
const topConfidence = document.getElementById("topConfidence");
const predictionTime = document.getElementById("predictionTime");

const predictionBars = document.getElementById("predictionBars");

const componentDescription = document.getElementById("componentDescription");

const componentUses = document.getElementById("componentUses");

const historyContainer = document.getElementById("historyContainer");

const clearHistoryBtn = document.getElementById("clearHistoryBtn");

const cameraBtn = document.getElementById("cameraBtn");

const cameraModal = document.getElementById("cameraModal");

const cameraVideo = document.getElementById("cameraVideo");

const captureBtn = document.getElementById("captureBtn");

const closeCameraBtn = document.getElementById("closeCameraBtn");

const gradcamImage = document.getElementById("gradcamImage");

let selectedFile = null;
let currentStream = null;

/* =====================================================
   Browse
===================================================== */

browseBtn.addEventListener("click", () => {
  imageInput.click();
});

imageInput.addEventListener("change", () => {
  if (!imageInput.files.length) return;

  selectedFile = imageInput.files[0];

  previewImage.src = URL.createObjectURL(selectedFile);

  previewImage.style.display = "block";

  predictBtn.style.display = "block";
});

/* =====================================================
   Drag & Drop
===================================================== */

dropZone.addEventListener("dragover", (e) => {
  e.preventDefault();

  dropZone.classList.add("dragover");
});

dropZone.addEventListener("dragleave", () => {
  dropZone.classList.remove("dragover");
});

dropZone.addEventListener("drop", (e) => {
  e.preventDefault();

  dropZone.classList.remove("dragover");

  if (!e.dataTransfer.files.length) return;

  selectedFile = e.dataTransfer.files[0];

  previewImage.src = URL.createObjectURL(selectedFile);

  previewImage.style.display = "block";

  predictBtn.style.display = "block";
});

/* =====================================================
   Camera Open
===================================================== */

cameraBtn.addEventListener("click", async () => {
  try {
    currentStream = await navigator.mediaDevices.getUserMedia({
      video: {
        facingMode: "environment",
      },
    });

    cameraVideo.srcObject = currentStream;

    cameraModal.style.display = "flex";
  } catch (err) {
    console.error(err);

    alert("Unable to access camera.");
  }
});

/* =====================================================
   Camera Close
===================================================== */

closeCameraBtn.addEventListener("click", stopCamera);

function stopCamera() {
  if (currentStream) {
    currentStream.getTracks().forEach((track) => track.stop());
  }

  cameraModal.style.display = "none";
}

/* =====================================================
   Capture
===================================================== */

captureBtn.addEventListener("click", () => {
  const canvas = document.createElement("canvas");

  const vw = cameraVideo.videoWidth;

  const vh = cameraVideo.videoHeight;

  const cropSize = Math.min(vw, vh) * 0.55;

  const startX = (vw - cropSize) / 2;

  const startY = (vh - cropSize) / 2;

  canvas.width = cropSize;
  canvas.height = cropSize;

  const ctx = canvas.getContext("2d");

  ctx.drawImage(
    cameraVideo,
    startX,
    startY,
    cropSize,
    cropSize,
    0,
    0,
    cropSize,
    cropSize,
  );

  canvas.toBlob((blob) => {
    selectedFile = new File([blob], "capture.jpg", {
      type: "image/jpeg",
    });

    previewImage.src = URL.createObjectURL(selectedFile);

    previewImage.style.display = "block";

    predictBtn.style.display = "block";
  }, "image/jpeg");

  stopCamera();
});

/* =====================================================
   Predict
===================================================== */

predictBtn.addEventListener("click", async () => {
  if (!selectedFile) return;

  const formData = new FormData();

  formData.append("file", selectedFile);

  try {
    predictBtn.disabled = true;
    predictBtn.textContent = "Predicting...";

    const response = await fetch("/predict", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();

    predictBtn.disabled = false;
    predictBtn.textContent = "Predict Component";

    if (!data.success) {
      alert(data.message);

      return;
    }

    renderResults(data);
  } catch (err) {
    console.error(err);

    alert("Prediction failed.");

    predictBtn.disabled = false;
    predictBtn.textContent = "Predict Component";
  }
});

/* =====================================================
   Render Results
===================================================== */

function renderResults(data) {
  predictionBars.innerHTML = "";

  topClass.textContent = data.top_prediction.class;

  topConfidence.textContent = `${data.top_prediction.confidence}% confidence`;

  predictionTime.textContent = `Prediction Time: ${data.prediction_time} ms`;

  data.predictions.forEach((item) => {
    const row = document.createElement("div");

    row.className = "prediction-row";

    row.innerHTML = `
            <div class="prediction-label">
                <span>${item.class}</span>
                <span>${item.confidence}%</span>
            </div>

            <div class="progress">
                <div
                    class="progress-fill"
                    style="width:${item.confidence}%"
                ></div>
            </div>
        `;

    predictionBars.appendChild(row);
  });

  if (data.component_info) {
    componentDescription.textContent = data.component_info.description;

    componentUses.innerHTML = "";

    data.component_info.uses.forEach((item) => {
      const li = document.createElement("li");

      li.textContent = item;

      componentUses.appendChild(li);
    });
  }

  if (data.gradcam_image) {
    gradcamImage.src = data.gradcam_image + "?t=" + new Date().getTime();

    gradcamImage.style.display = "block";
  }

  addToHistory(data.top_prediction.class, data.top_prediction.confidence);
}

/* =====================================================
   History
===================================================== */

function addToHistory(component, confidence) {
  let history = JSON.parse(localStorage.getItem("history")) || [];

  history.unshift({
    component,
    confidence,
  });

  history = history.slice(0, 20);

  localStorage.setItem("history", JSON.stringify(history));

  loadHistory();
}

function loadHistory() {
  let history = JSON.parse(localStorage.getItem("history")) || [];

  historyContainer.innerHTML = "";

  history.forEach((item) => {
    const div = document.createElement("div");

    div.className = "history-item";

    div.innerHTML = `<strong>${item.component}</strong>
             (${item.confidence}%)`;

    historyContainer.appendChild(div);
  });
}

clearHistoryBtn.addEventListener("click", () => {
  localStorage.removeItem("history");

  loadHistory();
});

loadHistory();
