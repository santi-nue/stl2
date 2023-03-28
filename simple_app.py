import openai
import urllib.request
from PIL import Image
import streamlit as st



openai.api_key = st.text_input("openai api key")

def image_generation(image_description):
    img_response = openai.Image.create(
        prompt = image_description,
        n=1,
        size="256x256")    # 256x256, 512x512, 1024x1024

    img_url = img_response['data'][0]['url']

    urllib.request.urlretrieve(img_url, 'image.png')

    img =Image.open('image.png')

    return img


# Streamlit page title
st.title("Image Generation ")

#text input
img_description =st.text_input("Image Description")

if st.button("Generate Image"):
    generated_img =image_generation(img_description)
    st.image(generated_img)
