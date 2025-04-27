import os


def get_icons_path():
    return os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "resources", "icons")
    )


def get_images_path():
    return os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "resources", "images")
    )
