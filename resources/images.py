import os
import traceback
from flask_restful import Resource
from flask_uploads import UploadNotAllowed
from flask import request, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity

from lib import image_helper
from schemas.image import ImageSchema

image_schema = ImageSchema()


class ImageUpload(Resource):
    @jwt_required
    def post(self):
        data = image_schema.load(request.files)  # type(request.files) => dict
        user_id = get_jwt_identity()
        folder = f"user_{user_id}"
        try:
            image_path = image_helper.save_image(data["image"], folder=folder)
            basename = image_helper.get_basename(image_path)
            return {'msg': "Image name '{}' is uploaded".format(basename)}, 201
        except UploadNotAllowed:
            ext = image_helper.get_extension(data["image"])
            return {'msg': "Invalid file format '{}'.".format(ext)}, 400


class Image(Resource):
    @jwt_required
    def get(self, filename):
        """Return the image if it exists. Users can only access their uploaded images, not others"""
        user_id = get_jwt_identity()
        folder = f"user_{user_id}"
        # check if filename is URL secure
        if not image_helper.is_filename_safe(filename):
            return {"message": "Bad File Name, '{}'.".format(filename)}, 400
        try:
            # try to send the requested file to the user with status code 200
            return send_file(image_helper.get_path(filename, folder=folder))
        except FileNotFoundError:
            return {"message": "Image File, '{}' not Found!!".format(filename)}, 404

    @jwt_required
    def delete(self, filename):
        user_id = get_jwt_identity()
        folder = f"user_{user_id}"
        if not image_helper.is_filename_safe(filename):
            return {'msg': "Bad File Name!! '{}'".format(filename)}, 400

        try:
            os.remove(image_helper.get_path(filename, folder=folder))
            return {'msg': "Image '{}' is deleted!".format(filename)}, 200
        except FileNotFoundError:
            return {'msg': "Image Not Found!"}, 404
        except:
            traceback.print_exc()
            return {'msg': "Internal Server Error. Delete Request Failed!"}, 500
