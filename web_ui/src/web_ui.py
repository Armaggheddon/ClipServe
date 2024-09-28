import gradio as gr
import models
import base64
import requests
import io

# create a gradio interface that takes in input one or more images
# and a list of labels, returning the classification results

def zero_shot_classification(image, text):
    # Convert the image in-memory to jpeg
    mem_buffer = io.BytesIO()
    image.save(mem_buffer, format="JPEG")
    mem_buffer.seek(0)

    # Convert the image to base64 and add the data URI prefix
    image_b64 = base64.b64encode(mem_buffer.getvalue()).decode("utf-8")
    image_b64 = f"data:image/jpeg;base64,{image_b64}"

    input_labels = [label.strip() for label in text.split(",")]
    request_labels = []
    request_labels.extend([f"a photo of a {label}" for label in input_labels])

    # create the request object
    request = models.ZeroShotClassificationRequest(labels=request_labels, images_b64=[image_b64])

    # make the request to the API
    response = requests.post("http://api:8000/zero-shot-classification", data=request.to_json())

    # convert the response to the response object
    response = models.RedisResponseItem(**response.json())
    
    labels = input_labels
    softmax_outputs = response.classification_result.softmax_outputs[0].softmax_scores

    return { label: score for label, score in zip(labels, softmax_outputs) }


with gr.Blocks() as demo:
    images = gr.Image(label="Image", type="pil")
    labels = gr.Textbox(label="Labels", info="Enter labels separated by commas", placeholder="cat, dog, bird")

    button = gr.Button(value="Classify")

    output = gr.Label(label="Output")

    button.click(zero_shot_classification, inputs=[images, labels], outputs=[output])

demo.launch(server_name="0.0.0.0", server_port=7860)
