import os
import time
import uuid

import cv2
import torch
import torch.nn as nn

from PIL import Image
from torchvision import models
from torchvision import transforms

from utils.component_info import COMPONENT_INFO
from utils.gradcam import generate_gradcam


# Device.............................................
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# Classes..........................................
CLASS_NAMES = [
    "Capacitor",
    "Diode",
    "Fuse",
    "Heatsink",
    "IC",
    "Inductor",
    "LED",
    "Potentiometer",
    "Relay",
    "Resistor",
    "Transformer",
    "Transistor"
]

# Model.............................................
model = models.efficientnet_v2_s(weights=None)

in_features = model.classifier[1].in_features

model.classifier[1] = nn.Sequential(nn.Dropout(p=0.5),nn.Linear(in_features, len(CLASS_NAMES)))

model.load_state_dict(
    torch.load("component_classifier_efficientnet_v1.0.pth", map_location=device)
    )

model.to(device)
model.eval()

# Transform........................


transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

# GradCAM Folder...................
HEATMAP_FOLDER = "static/gradcam"

os.makedirs(HEATMAP_FOLDER, exist_ok=True)

# Prediction.............................................
def predict_image(image_path):
    start_time = time.perf_counter()

    image = Image.open(image_path).convert("RGB")
    
    image_tensor = transform(image)
    image_tensor = image_tensor.unsqueeze(0)
    image_tensor = image_tensor.to(device)

    with torch.no_grad():
        outputs = model(image_tensor)
        probabilities = torch.softmax(outputs,dim=1)[0]

    prediction_time = round((time.perf_counter() - start_time) * 1000, 1)

    top_probs, top_indices = torch.topk(probabilities,k=3)
    predictions = []

    for prob, idx in zip(top_probs.cpu().numpy(), top_indices.cpu().numpy()):
        predictions.append({
            "class": CLASS_NAMES[idx],
            "confidence": round(float(prob) * 100, 2)
        })

    top_prediction = predictions[0]

    # Unknown Detection........................................
    if top_prediction["confidence"] < 50:
        top_prediction = {
            "class": "Unknown Component",
            "confidence": top_prediction["confidence"]
        }
        
        component_info = COMPONENT_INFO[
            "Unknown Component"
        ]
        
    else:
        component_info = COMPONENT_INFO.get(top_prediction["class"],COMPONENT_INFO["Unknown Component"])


    # Grad-CAM............................................
    heatmap_url = None
    
    try:
        heatmap = generate_gradcam(
            model=model,
            image_path=image_path,
            target_layer=model.features[-1],
            device=device
        )

        heatmap_name = (str(uuid.uuid4()) + ".jpg")

        heatmap_path = os.path.join(HEATMAP_FOLDER, heatmap_name)

        cv2.imwrite(heatmap_path, heatmap)

        heatmap_url = ("/static/gradcam/" + heatmap_name)

    except Exception as e:
        print("GradCAM error:", e)

    # Return...............................................................
    

    return {
        "top_prediction": top_prediction,
        "predictions": predictions,
        "component_info": component_info,
        "prediction_time": prediction_time,
        "gradcam": heatmap_url
    }
