from flask import Flask, render_template, request, jsonify
import os
import uuid
import socket
import qrcode

from utils.predict import predict_image

app = Flask(__name__)

# creating folders......................

UPLOAD_FOLDER = "static/uploads"
QR_FOLDER = "static/qr"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(QR_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# uploads Cleanup.............................
def cleanup_uploads(max_files=3):
    files = []

    for filename in os.listdir(UPLOAD_FOLDER):
        path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.isfile(path):
            files.append(path)
            
    files.sort(key=os.path.getmtime, reverse=True)

    for old_file in files[max_files:]:
        try:
            os.remove(old_file)
        except:
            pass

# local ip...................................

def get_local_ip():
    s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"

    finally:
        s.close()
    return ip

# QR Generation.......................................
def generate_qr():
    try:
        local_ip = get_local_ip()
        url = f"https://{local_ip}:5000"
        qr = qrcode.make(url)
        
        qr.save(os.path.join(QR_FOLDER,"site_qr.png"))

        print(f"QR generated -> {url}")

    except Exception as e:

        print("QR generation failed:", e)


# Routes.....................................................
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/health")
def health():
    return {"status": "ok"}


# Prediction.............................................
@app.route("/predict",methods=["POST"])
def predict():
    if "file" not in request.files:
        return jsonify({"success": False, "message": "No file received."})

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"success": False,"message": "No file selected."})

    extension = os.path.splitext(file.filename)[1]
    filename = (f"{uuid.uuid4()}"f"{extension}")
    filepath = os.path.join(app.config["UPLOAD_FOLDER"],filename)
    file.save(filepath)

    try:
        result = predict_image(filepath)

        response = {
            "success": True,
            "top_prediction": result["top_prediction"],
            "predictions": result["predictions"],
            "component_info": result["component_info"],
            "prediction_time": result["prediction_time"],
            "gradcam_image": result["gradcam"]
        }

    except Exception as e:
        return jsonify({"success": False,"message": str(e)})

    finally:
        try:
            os.remove(filepath)
        except:
            pass

        cleanup_uploads()

    return jsonify(response)

# Run......................
if __name__ == "__main__":

    generate_qr()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
        ssl_context="adhoc"
    )