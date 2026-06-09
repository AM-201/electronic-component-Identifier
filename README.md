# Electronic Component Classifier

A deep learning web application that identifies common electronic components from images.

The project uses a fine-tuned EfficientNetV2-S model trained on a custom dataset containing both publicly available and self-collected images.

Users can:

- Upload images
- Capture images directly from a phone camera
- View top predictions with confidence scores
- See Grad-CAM visual explanations
- Access component descriptions and common uses
- Review prediction history

---

## Supported Components

- Capacitor
- Diode
- Fuse
- Heatsink
- IC
- Inductor
- LED
- Potentiometer
- Relay
- Resistor
- Transformer
- Transistor

---

## Features

### AI Classification

Identifies electronic components using a convolutional neural network based on EfficientNetV2-S.

### Unknown Detection

Predictions below a confidence threshold are labeled as:
Unkown component

to reduce false positives.

### Grad-CAM Explainability

Displays a heatmap showing which image regions contributed most to the model's decision.

### Mobile Camera Support

Users can capture components directly from a smartphone camera through the browser.

### Component Information

Displays a brief description and common applications for each detected component.

### Prediction History

Stores recent predictions locally in the browser.

---

## Model

Architecture:
EfficientNetV2-S

Transfer Learning:
ImageNet pretrained backbone

Classes:
12

Input Size:
224 × 224

Framework:
PyTorch

---

## Project Structure

project/
│
├── app.py
├── requirements.txt
│
├── templates/
│ └── index.html
│
├── static/
│ ├── css/
│ │ └── style.css
│ ├── js/
│ │ └── script.js
│ ├── uploads/
│ ├── gradcam/
│ └── qr/
│
├── utils/
│ ├── predict.py
│ ├── gradcam.py
│ └── component_info.py
│
├── component_classifier_efficientnet_final+.pth
└── class_names.json

---

## Installation

### Clone Repository

```bash
git clone https://github.com/AM-201/electronic-component-classifier.git

cd electronic-component-classifier
```
## Download Model

The trained model is not stored in the repository due to size limitations.

Download the trained model from:

```bash
https://github.com/AM-201/electronic-component-classifier/releases
```

and move it to the main folder next to "class_names.json"


### Install required libraries

```bash
pip install -r requirements.txt
```

### run system

```bash
python app.py
```

### Open dashboard

```bash
http://127.0.0.1:5000
```

---

## Example Workflow

1. Upload or capture a component image
2. Run inference
3. View predicted component
4. Inspect confidence scores
5. Review Grad-CAM heatmap
6. Read component information

---

## Author

Developed by:

Eng. Ahmed M. Ahmed

Electrical Engineering Student

Specialization:
Computer and Control Systems
