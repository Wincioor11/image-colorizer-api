import flask
from flask_cors import CORS
from flask_injector import FlaskInjector
from injector import inject

from PIL import Image
import io
import base64
import os
from dotenv import load_dotenv

from resourcelayer.ImageColorizerService import ImageColorizerService
from dependencies import configure
from gdrive_download import download_file_from_google_drive
# initialize GPU for tensorflow (comment it when using machine without NVIDIA GPU)
import tensorflow as tf
gpu = tf.config.experimental.list_physical_devices('GPU')
tf.config.experimental.set_memory_growth(gpu[0], True)

# Initialize flask app
app = flask.Flask(__name__)
# Enable CORS
CORS(app)
# Load variables from .env file as environment variables
load_dotenv()
# Set app config from env vars
app.config['DEBUG'] = os.environ.get('DEBUG')
app.config['ACCESS_KEY'] = os.environ.get('ACCESS_KEY')
app.config['PORT'] = os.environ.get('PORT')

# Download large model file from google drive if doesn't exist
# MODEL_PATH = 'static/trained_models/places365/generator_model_256_v3.h5'
# FILE_ID = os.environ.get('FILE_ID')
# if not os.path.isfile(MODEL_PATH):
#     print('Model not found')
#     download_file_from_google_drive(FILE_ID,MODEL_PATH)
#     print('Model loaded from google drive')

def verify_access(key: bytes):
    if key == app.config.get('ACCESS_KEY'):
        return True
    else:
        return False

@inject
@app.route('/colorize', methods=['POST'])
def colorize(colorizer_service: ImageColorizerService):
    # check access
    key = flask.request.headers.get('Authorization')#,as_bytes=True)
    if not verify_access(key=key):
        return flask.Response(status=401)
    else:
        file = flask.request.files['img']
        img = Image.open(file.stream)

        try:
            # colorizer = ImageColorizerService()
            img_colored = colorizer_service.colorize(img)
            image = Image.fromarray(img_colored.astype('uint8'))

            rawBytes = io.BytesIO()
            image.save(rawBytes, "JPEG")

            b64 = base64.b64encode(rawBytes.getvalue())
            status_code = 200
        except Exception as ex:
            print(ex)
            status_code = 500
            b64 = None

        return flask.Response(b64, status=status_code)

# setup flask dependency injection 
FlaskInjector(app=app, modules=[configure])

if __name__ == "__main__":
    # run api
    app.run(port=app.config.get('PORT'))