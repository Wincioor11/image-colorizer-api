import flask
from flask_cors import CORS
from flask_injector import FlaskInjector
from injector import inject

from PIL import Image
import io
import base64
import os
# from dotenv import load_dotenv


from resourcelayer.ImageColorizerService import ImageColorizerService
from dependencies import configure
from gdrive_download import download_file_from_google_drive




# initialize GPU for tensorflow (uncomment it only on local machine, not when deployed)
# import tensorflow as tf
# gpu = tf.config.experimental.list_physical_devices('GPU')
# tf.config.experimental.set_memory_growth(gpu[0], True)

app = flask.Flask(__name__)
CORS(app)
# load_dotenv()
app.config['DEBUG'] = os.environ.get('DEBUG')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['ACCESS_KEY'] = os.environ.get('ACCESS_KEY')
app.config['PORT'] = os.environ.get('PORT')

#Download large model file from google drive
MODEL_PATH = 'model/generator_model_256_v3.h5'
FILE_ID = os.environ.get('FILE_ID')
if not os.path.isfile(MODEL_PATH):
    print('Model not found')
    download_file_from_google_drive(FILE_ID,MODEL_PATH)

def verify_access(key: bytes):
    if key == app.config.get('ACCESS_KEY'):
        return True
    else:
        return False

@app.route('/', methods=['GET'])
def home():
    return "<h1>Api is working fine :)</h1>"

@inject
@app.route('/colorize', methods=['POST'])
def colorize(colorizer_service: ImageColorizerService):
    # check is ACCESS_KEY is valid
    key = flask.request.headers.get('ACCESS_KEY')#,as_bytes=True)
    if not verify_access(key=key):
        return flask.Response(status=401)
    else:
        file = flask.request.files['img']
        img = Image.open(file.stream)

        try:
            # colorizer = ImageColorizerService()
            img_colored = colorizer_service.colorize(img)
            image = Image.fromarray(img_colored.astype('uint8'))
            # img1 = io.FileIO()
            # image.save(img1, "PNG")
            # img1.seek(0)

            rawBytes = io.BytesIO()
            image.save(rawBytes, "JPEG")
            # rawBytes.seek(0)  # return to the start of the file

            b64 = base64.b64encode(rawBytes.getvalue())
            # b64 = base64.encodebytes(rawBytes)
            status_code = 200
        except Exception as ex:
            status_code = 500
            b64 = None
            # rawBytes = None

        # return flask.send_file(b64, mimetype='image/jpeg')
        return flask.Response(b64, status=status_code)

# setup flask dependency injection 
FlaskInjector(app=app, modules=[configure])

if __name__ == "__main__":
    # run api
    # app.run(port=os.environ.get('PORT', 33507))
    app.run(port=app.config.get('PORT'))