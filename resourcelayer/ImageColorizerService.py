from keras.models import load_model
import numpy as np
import cv2

class ImageColorizerService():
    def __init__(self, generator_path: str ='static/trained_models/places365/generator_model_256_v3.h5'):
        self.generator = load_model(generator_path)
        self.generator.trainable = False
    
    def colorize(self, img):
        img = np.asarray(img)
        # swap shape, because numpy's shape is transposed
        org_size = img.shape[1], img.shape[0] 
        resize_flag = False
        img_gray_org, _ = self.rgb2lab(img)
        if (org_size != (256,256)):
            resize_flag = True
            img = self.resize_image(img, size=(256,256))
        img_gray, _ = self.rgb2lab(img)
        img_generated = self.generator.predict(np.expand_dims(img_gray,axis=0))
        # transform to rgb
        img_rgb = self.lab2rgb(img_l=img_gray,img_ab=img_generated[0], size=(256,256,3))
        if (resize_flag):
            img_rgb = self.resize_image(img_rgb, size=org_size)
        # replace L layer to orginal one -> avoid quality loss
        img_gray, img_ab = self.rgb2lab(img_rgb)
        img_rgb = self.lab2rgb(img_l=img_gray_org,img_ab=img_ab, size=img_rgb.shape)
        return img_rgb

    def resize_image(self, img: np.ndarray, size=(256,256)):
        img = cv2.resize(img, size, interpolation=cv2.INTER_LINEAR)
        return img
    
    def rgb2lab(self, img: np.ndarray, normalize=True):
        # transform to lab
        img_lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
        img_l = np.zeros((img_lab.shape[0],img_lab.shape[1],1))
        img_ab  = np.zeros((img_lab.shape[0],img_lab.shape[1],2))
        if normalize:
            # normalize
            img_l[:, :, 0] = (img_lab[:, :, 0]-127.5 )/127.5
            img_ab[:, :, :] = (img_lab[:, :, 1:]-127.5)/127.5
        else:
            # do not normalize
            img_l[:, :, 0] = img_lab[:, :, 0]
            img_ab[:, :, :] = img_lab[:, :, 1:]
        return img_l, img_ab # l, ab
    
    def lab2rgb(self, img_l: np.ndarray, img_ab: np.ndarray, size=(256,256,3)):
        # Initializing img array with zeros
        img = np.zeros(size)
        # Scaling from [-1,-1] to [0,255]
        img[:, :, 0] = (img_l[:, :, 0] + 1.0) / 2.0 *255.
        img[:, :, 1:] = (img_ab + 1.0) / 2.0 *255.
        img = img.astype('uint8')
        # Change coolor space to matplotlib rgb
        img = cv2.cvtColor(img, cv2.COLOR_LAB2RGB)
        return img
