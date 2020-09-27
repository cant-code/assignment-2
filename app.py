from flask import Flask
from flask_restful import Resource, Api, reqparse
import werkzeug
from PIL import Image, ImageChops

app = Flask(__name__)
api = Api(app)


def get_color(im):
    q = im.quantize(colors=2,method=2)
    return q.getpalette()[:6]


def check_border(im):
    bg = Image.new(im.mode, im.size, im.getpixel((0,0)))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        return all((bbox[0], bbox[1], (bbox[0] + bbox[2]) <= im.size[0], (bbox[1] + bbox[3]) <= im.size[1]))
    else:
        return None


class Images(Resource):
    def post(self):
        parse = reqparse.RequestParser()
        parse.add_argument('file', type=werkzeug.datastructures.FileStorage, location='files')
        args = parse.parse_args()
        image_file = args['file']
        img = Image.open(image_file.stream)
        borders = check_border(img)
        colors = get_color(img)
        secondary_color = colors[:len(colors)//2]
        primary_color = colors[len(colors)//2:]
        return {'borders': borders, 'colors': {'Primary': primary_color, 'Secondary': secondary_color}}, 200

api.add_resource(Images, '/image')

if __name__ == '__main__':
    app.run(debug=True)
