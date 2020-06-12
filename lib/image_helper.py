import os
import re
from werkzeug.datastructures import FileStorage

from flask_uploads import UploadSet, IMAGES

IMAGE_SET = UploadSet("images", IMAGES)  # set name and allowed extensions. "images" is like a key


def save_image(image, folder=None, name=None):
    """Take FileStorage and save in the folder"""
    return IMAGE_SET.save(image, folder, name)


def get_path(filename, folder):
    """Take image name, folder and return fill path"""
    return IMAGE_SET.path(filename, folder)


def find_image_any_format(filename, folder):
    """Take a filename and return image of any accepted format"""
    for _format in IMAGES:
        image = f"{filename}.{_format}"
        image_path = IMAGE_SET.path(filename=image, folder=folder)
        # getFileName('user_2')
        if os.path.isfile(image_path):
            return image_path
    return None


def _retrieve_image(file):
    """Take a FileStorage and return a file name"""
    if isinstance(file, FileStorage):
        return file.filename
    return file


def is_filename_safe(file):
    """Check the regex and return whether match or not"""
    filename = _retrieve_image(file)
    allowed_format = "|".join(IMAGES)
    regex = f"^[a-zA-Z0-9][a-zA-Z0-9_()-\.]*\.({allowed_format})$"
    return re.match(regex, filename) is not None  # check if the filename matches the regex


def get_basename(file):
    """Return full name of the image in path"""
    filename = _retrieve_image(file)
    return os.path.split(filename)[1]  # get last part of the path. Eg. "c:/downloads/a.jpg => a.jpg


def get_extension(file):
    """Return file extension"""
    filename = _retrieve_image(file)
    return os.path.splitext(filename)[1]  # get the extension of filename from path
