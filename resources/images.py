import os
from datetime import datetime
import traceback
from flask_restful import Resource
from flask_uploads import UploadNotAllowed
from flask import request, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt_claims

from lib import image_helper
from schemas.image import ImageSchema

image_schema = ImageSchema()


class ImageUpload(Resource):

    @classmethod
    @jwt_required
    def post(cls):
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
    @classmethod
    @jwt_required
    def get(cls, filename):
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

    @classmethod
    @jwt_required
    def delete(cls, filename):
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


class AvatarUpload(Resource):

    # Upload/Change User Profile Avatar
    """ 
        Upload : A new image will be uploaded and saved to the destination with file name (eg: user_1.png).
        Change : A newly uploaded avartar will overwrite the existing old profile avatar with same file name.
        File name : For example. user_1.png
    """
    @classmethod
    @jwt_required
    def put(cls):
        data = image_schema.load(request.files)
        user_id = get_jwt_identity()
        filename = f"user_{user_id}"   # !!! eg: user_{user_id}
        folder = "avatars"
        avatar_path = image_helper.find_image_any_format(filename, folder)
        # Check if the file exists
        if avatar_path:
            try:
                # Delete the old profile avatar so that a new avatar can be saved with same name
                os.remove(avatar_path)
            except:
                return {'msg': "Internal Server Error. Request Failed!"}, 500
        # !!! get the file extention from the requests
        ext = image_helper.get_extension(data["image"].filename)
        try:
            avatar = filename+ext  # user_{id}.ext
            # !!! save the new avatar
            avatar_path = image_helper.save_image(data["image"], folder=folder, name=avatar)
            basename = image_helper.get_basename(avatar_path)
            return {'msg': "Avatar, '{}' Uploaded Successfully!".format(basename)}, 201
        except UploadNotAllowed:
            return {'msg': "Invalid File Format '{}' is not allowed!".format(ext)}, 400


class Avatar(Resource):
    # Return the user avatar by the User ID
    @classmethod
    def get(cls, _id_):
        folder = "avatars"
        filename = f"user_{_id_}"  # user_{user_id}.ext
        try:
            return send_file(image_helper.find_image_any_format(filename, folder))
        except:
            return {'msg': "File Not Found!"}, 400
