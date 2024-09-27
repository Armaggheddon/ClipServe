import redis
import torch
import os
import numpy as np
import PIL
import uuid
from redis_models import RedisRequestItem, RedisResponseItem, TextEmbedding, ImageEmbedding, ClassificationResult, SoftmaxOutput
from transformers import CLIPProcessor, CLIPModel, CLIPTokenizerFast

def run_inference():
    # pool = redis.ConnectionPool.from_url(url='redis://redis:6379', decode_responses=True)
    _redis_client = redis.Redis.from_url(url='redis://redis:6379', decode_responses=False)

    device = "cuda" if torch.cuda.is_available() else "cpu"

    model_name = "openai/clip-vit-base-patch32"

    tokenizer = CLIPTokenizerFast.from_pretrained(model_name, device_map="auto")
    model = CLIPModel.from_pretrained(model_name, device_map="auto").to(device)
    processor = CLIPProcessor.from_pretrained(model_name, device_map="auto")
        
    print(f"Ping successful: {_redis_client.ping()}")

    while True:
        # Result is a 2 element tuple of (queue_id, value)
        result = _redis_client.brpop("requests", timeout=1)
        if not result:
            continue

        queue_item = RedisRequestItem.from_json(result[1])

        response = RedisResponseItem()

        if not queue_item.images:
            txt_list = [txt_item.text for txt_item in queue_item.texts]
            inputs = tokenizer(txt_list, return_tensors="pt", padding=True).to(device)
            outputs = model.get_text_features(**inputs)
            model_embeddings = outputs.cpu().detach().numpy().tolist()

            response.text_embeddings = [
                TextEmbedding(text=txt, embedding=embedding) 
                for txt, embedding in zip(txt_list, model_embeddings)]

        elif not queue_item.texts:
            img_list = [PIL.Image.open(image.image_path) for image in queue_item.images]
            inputs = processor(images=img_list, return_tensors="pt").to(device)
            outputs = model.get_image_features(**inputs)
            model_embeddings = outputs.cpu().detach().numpy().tolist()

            response.image_embeddings = [
                ImageEmbedding(image_id=str(uuid.uuid4()), embedding=embedding)
                for embedding in model_embeddings]

        else:
            # classify the images based on the provided text labels
            txt_list = [txt_item.text for txt_item in queue_item.texts]
            img_list = [PIL.Image.open(image.image_path) for image in queue_item.images]

            inputs = processor(
                text=txt_list,
                images=img_list,
                return_tensors="pt",
                padding=True
            ).to(device)

            outputs = model(**inputs)

            logits_per_image = outputs.logits_per_image
            probs = logits_per_image.softmax(dim=1).detach().cpu().numpy().tolist()

            text_embeddings = outputs.text_embeds.cpu().detach().numpy().tolist()
            image_embeddings = outputs.image_embeds.cpu().detach().numpy().tolist()

            response.text_embeddings = [
                TextEmbedding(text=txt, embedding=embedding) 
                for txt, embedding in zip(txt_list, text_embeddings)
            ]

            img_uuids = [str(uuid.uuid4()) for _ in range(len(img_list))]

            response.image_embeddings = [
                ImageEmbedding(image_id=img_uuid, embedding=embedding)
                for img_uuid, embedding in zip(img_uuids, image_embeddings)
            ]

            softmax_outputs = [
                SoftmaxOutput(image_id=img_uuid, softmax_scores=probs[idx])
                for idx, img_uuid in enumerate(img_uuids)
            ]

            response.classification_result = ClassificationResult(
                labels=txt_list,
                softmax_outputs=softmax_outputs
            )
            

        # remove the image files
        for img_item in queue_item.images:
            img_path = img_item.image_path
            os.remove(img_path)

        redis_response_key = f"{queue_item.job_id}-response"

        _redis_client.lpush(
            redis_response_key,
            response.to_json()
        )


if __name__ == "__main__":
    print(f"It looks like CUDA is {'' if torch.cuda.is_available() else 'not '}available!")
    run_inference()