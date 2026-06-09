import cv2
import numpy as np
import torch

from PIL import Image
from torchvision import transforms


def generate_gradcam(model, image_path, target_layer, device):
    activations = []
    gradients = []

    def forward_hook(module, inp, out):
        activations.append(out)

    def backward_hook(module, grad_in, grad_out):
        gradients.append(grad_out[0])

    h1 = target_layer.register_forward_hook(forward_hook)

    h2 = target_layer.register_full_backward_hook(
        backward_hook
    )

    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])

    image = Image.open(
        image_path
    ).convert("RGB")

    tensor = transform(
        image
    ).unsqueeze(0).to(device)

    output = model(tensor)

    pred_class = output.argmax(dim=1)

    model.zero_grad()

    output[
        0,
        pred_class
    ].backward()

    grads = gradients[0]

    acts = activations[0]

    weights = torch.mean(
        grads,
        dim=(2, 3),
        keepdim=True
    )

    cam = torch.sum(
        weights * acts,
        dim=1
    ).squeeze()

    cam = torch.relu(cam)

    cam = cam.detach().cpu().numpy()

    cam = cv2.resize(
        cam,
        (224, 224)
    )

    cam = (
        cam - cam.min()
    ) / (
        cam.max() - cam.min() + 1e-8
    )

    original = cv2.imread(image_path)

    original = cv2.resize(
        original,
        (224, 224)
    )

    heatmap = np.uint8(
        255 * cam
    )

    heatmap = cv2.applyColorMap(
        heatmap,
        cv2.COLORMAP_JET
    )

    overlay = cv2.addWeighted(
        original,
        0.6,
        heatmap,
        0.4,
        0
    )

    h1.remove()
    h2.remove()

    return overlay