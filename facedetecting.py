#import required libraries
import asyncio
import io
import glob
import os
import sys
import time
import uuid
import requests
from urllib.parse import urlparse
from io import BytesIO
# To install this module, run:
# python -m pip install Pillow
from PIL import Image, ImageDraw
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.face.models import TrainingStatusType, Person

#get credential and setup client
def get_face_client():
    """Create an authenticated FaceClient."""
    #SUBSCRIPTION_KEY = os.environ['COGNITIVE_SERVICE_KEY']
    SUBSCRIPTION_KEY = "1641749b53cd4d469a3ac60183d9ac91"
    #ENDPOINT = os.environ["COGNITIVE_SERVICE_ENDPOINT"]
    ENDPOINT = "https://faceapi1101.cognitiveservices.azure.com/"
    credential = CognitiveServicesCredentials(SUBSCRIPTION_KEY)
    return FaceClient(ENDPOINT, credential)

#call the client 
face_client = get_face_client()

url = "https://picturefolder.blob.core.windows.net/face/facetest1101.png"

#detect face locatioin
detected_faces_location = face_client.face.detect_with_url(url,detection_model='detection_03')

if not detected_faces_location:
    raise Exception('No face detected from image {}'.format(single_image_name))

#display the faceID detected
print('Detected face ID from', ':')
for face in detected_faces_location: print(face.face_id)
print()
#below code detect face from a single face picture,singel_face_url
#use find_similar method to detect the face from single face picture
# Convert width height to a point in a rectangle
def getRectangle(faceDictionary):
    rect = faceDictionary.face_rectangle
    left = rect.left
    top = rect.top
    right = left + rect.width
    bottom = top + rect.height
    
    return ((left, top), (right, bottom))

# Download the image from the url
response = requests.get(url)
img = Image.open(BytesIO(response.content))

# For each face returned use the face rectangle and draw a colored box.
print('Drawing rectangle around face... see popup for results.')
draw = ImageDraw.Draw(img)

#single face detection
singel_face_url = 'https://picturefolder.blob.core.windows.net/face/singleface002.png'
detected_face = face_client.face.detect_with_url(singel_face_url,detection_model='detection_03')
if not detected_face:
    raise Exception('No face detected from image')
#save the faceID
single_face_ID = detected_face[0].face_id

#save the faceIDs in the second multi-faces picture
second_face_IDs = list(map(lambda x: x.face_id, detected_faces_location))
# Next, find similar face IDs like the one detected in the first image.
similar_faces = face_client.face.find_similar(face_id=single_face_ID,face_ids=second_face_IDs)

if not similar_faces:
    print('No similar faces found in')
# Print the details of the similar faces detected
else:
    print('Similar faces found in')
    for face in similar_faces:
        first_image_face_ID = face.face_id
        # The similar face IDs of the single face image and the group image do not need to match, 
        # they are only used for identification purposes in each image.
        # The similar faces are matched using the Cognitive Services algorithm in find_similar().
        face_info = next(x for x in detected_faces_location if x.face_id == first_image_face_ID)
        if face_info:
            print('  Face ID: ', first_image_face_ID)
            print('  Face rectangle:')
            print('    Left: ', str(face_info.face_rectangle.left))
            print('    Top: ', str(face_info.face_rectangle.top))
            print('    Width: ', str(face_info.face_rectangle.width))
            print('    Height: ', str(face_info.face_rectangle.height))
            draw.rectangle(getRectangle(face_info), outline='red')
    print('circle out completed.')

# Display the image in the users default image browser.
img.show()
