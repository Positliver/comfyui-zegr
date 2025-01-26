import os
from datetime import datetime
import folder_paths
from . import third_party as oss2

class ListFilesNode:
    """
    A node to list all files in a given directory.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "root_dir": ("STRING", {"default": "./models", "multiline": False}),
                "file_type": ("STRING", {"default": "loras", "options": ["loras", "checkpoints"]}),
                "checkpoint_name": (folder_paths.get_filename_list("checkpoints"), {"tooltip": "The name of the Checkpoint."}),
                "lora_name": (folder_paths.get_filename_list("loras"), {"tooltip": "The name of the lora."}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("file_path",)
    FUNCTION = "list_files"
    CATEGORY = "File Operations"

    def list_files(self, root_dir, file_type, checkpoint_name, lora_name):
        if not os.path.isdir(root_dir):
            return ("Invalid folder path",)
                
        model_name = checkpoint_name if file_type== "checkpoints" else lora_name
        path = folder_paths.get_full_path_or_raise(file_type, model_name)
        return (path,)


class UploadFileNode:
    """
    A node to upload a file using a provided path and key.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "file_path": ("STRING", {"default": "", "multiline": False}),
                "bk_name": ("STRING", {"default": "tempres", "multiline": False}),
                "key": ("STRING", {"default": "", "multiline": False}),
                "endpoint": ("STRING", {"default": "http://oss-cn-shanghai.aliyuncs.com", "multiline": False}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("upload_status",)
    FUNCTION = "upload_file"
    CATEGORY = "File Operations"

    def upload_file(self, file_path, bk_name, key, endpoint):
        if not os.path.isfile(file_path):
            return ("Upload failed: File not found",)

        try:
            parts = key.split(",")
            auth = oss2.Auth(parts[0], parts[1])
            bucket = oss2.Bucket(auth, endpoint, bk_name)
            today = datetime.today()
            today_str = today.strftime('%Y-%m-%d')
            base_name = os.path.basename(file_path)
            object_key = f"{today_str}/{base_name}"
            bucket.put_object_from_file(object_key, file_path)
            
            return (f"Upload successful: File '{os.path.basename(file_path)}' with key '{key}'", )
        except Exception:
            return ("Upload failed: An error occurred",)


NODE_CLASS_MAPPINGS = {
    "ZEGR_LF": ListFilesNode,
    "ZEGR_ALI_UF": UploadFileNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ZEGR_LF": "ZEGR_LF",
    "ZEGR_ALI_UF": "ZEGR_ALI_UF"
}
