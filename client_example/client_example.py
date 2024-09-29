import requests
import clip_serve_models as models


if __name__ == "__main__":
    # Example usage of the ClipServe API
    API_URL = "http://localhost:8000"

    # Embed text
    text_request = models.TextRequest(text="A photo of a cat")
    response = requests.post(f"{API_URL}/embed-text", data=text_request.to_json())
    response_obj = models.TextEmbeddingResponse(**response.json())
    
    # Embed images
    sample_image = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAQAAAAEAAQMAAABmvDolAAAAA1BMVEW10NBjBBbqAAAAH0lEQVRoge3BAQ0AAADCoPdPbQ43oAAAAAAAAAAAvg0hAAABmmDh1QAAAABJRU5ErkJggg=="
    image_request = models.ImageRequest(image_b64=sample_image)
    response = requests.post(f"{API_URL}/embed-images", data=image_request.to_json())
    response_obj = models.ImageEmbeddingResponse(**response.json())

    # Zero-shot classification
    zsc_request = models.ZeroShotClassificationRequest(labels=["dog", "cat"], images_b64=[sample_image])
    response = requests.post(f"{API_URL}/zero-shot-classification", data=zsc_request.to_json())
    response_obj = models.ClassificationResponse(**response.json())