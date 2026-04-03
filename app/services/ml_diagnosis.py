from PIL import Image

def predict_crop_image(image_path):
    """
    Placeholder ML image diagnosis.
    Later replace with a real TensorFlow or PyTorch model.
    """
    try:
        img = Image.open(image_path)
        img.verify()
        return {
            "label": "Possible fungal infection",
            "confidence": 0.72,
            "recommendation": "Inspect leaves closely and consider approved fungicide treatment."
        }
    except Exception:
        return {
            "label": "Image unreadable",
            "confidence": 0.0,
            "recommendation": "Please upload a clearer image."
        }