# imageprocessing.py

import os
import tempfile
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from PIL import Image

def generate_image(prompt: str) -> str:
    """
    Generate an image from a text prompt via Hugging Face InferenceClient.
    Returns the path to a temporary .png file.
    """
    # only load your HF_TOKEN when actually needed
    load_dotenv()
    hf_token = os.getenv("HUGGING_FACE_TOKEN")
    if not hf_token:
        raise RuntimeError("HF_TOKEN not set in environment")

    client = InferenceClient(token=hf_token)

    # --- drop raw_response and use `prompt=` only ---
    result = client.text_to_image(
        model="stabilityai/stable-diffusion-2",
        prompt=prompt
    )

    # result may be a single PIL.Image or a list
    img = result[0] if isinstance(result, list) else result

    # save to a temp file
    tf = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    img.save(tf.name, format="PNG")
    tf.close()
    return tf.name
