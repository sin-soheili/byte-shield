from collections import defaultdict
import os

def Tree():
    return defaultdict(Tree)


user_pocket = Tree()


def clear_user_state(user_id):
    user_pocket[user_id]["state"] = "start_state"


def find_local_image(image_path):
    # image_path might be "/media/product_image/filename.jpg" or "product_image/filename.jpg"
    filename = os.path.basename(image_path)
    # Adjust this path to your actual project structure
    local_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../uploads/product_image"))
    local_path = os.path.join(local_dir, filename)
    if os.path.exists(local_path):
        return local_path
    return None
