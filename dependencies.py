from injector import singleton

from resourcelayer.ImageColorizerService import ImageColorizerService

def configure(binder):
    binder.bind(ImageColorizerService, to=ImageColorizerService, scope=singleton)
