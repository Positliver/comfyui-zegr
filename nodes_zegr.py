import os
from datetime import datetime
import folder_paths
from . import third_party as oss2


ZEGR_MODEL_TYEPS = [
"loras", "checkpoints", "unet"
]
class ListFilesNode:
    """
    A node to list all files in a given directory.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "file_type": (ZEGR_MODEL_TYEPS, {"default": ZEGR_MODEL_TYEPS[0]}),
                "custom_file_type": ("STRING", {"default":"", "multiline": False}),
                "checkpoint_name": (folder_paths.get_filename_list("checkpoints"), {"tooltip": "The name of the Checkpoint."}),
                "unet_name": (folder_paths.get_filename_list("unet"), {"tooltip": "The name of the unet."}),
                "lora_name": (folder_paths.get_filename_list("loras"), {"tooltip": "The name of the lora."}),
            }
        }

    RETURN_TYPES = ("STRING", )
    RETURN_NAMES = ("file_path", )
    OUTPUT_IS_LIST = (False, )
    FUNCTION = "list_files"
    CATEGORY = "File Operations"

    def list_files(self, file_type, custom_file_type, checkpoint_name, unet_name, lora_name):
        cur_file_type = custom_file_type if custom_file_type else file_type

        if cur_file_type == "checkpoints":
            model_name = checkpoint_name
        elif cur_file_type == "unet":
            model_name = unet_name
        else:
            model_name = lora_name
        path = folder_paths.get_full_path_or_raise(cur_file_type, model_name)
        return (path, )


class WalkDirNode:
    """
    A node to walk through a directory and list all files with their sizes.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "root_dir": ("STRING", {"default": "./models", "multiline": False}),
                "depth": ("INT", {"default": 0, "min": 0, "tooltip": "0 for unlimited depth, 1 for one level, etc."}),
                "folders_only": ("BOOLEAN", {"default": False, "tooltip": "If true, only folders will be listed."}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("files_and_sizes",)
    OUTPUT_IS_LIST = (False, )

    FUNCTION = "walk_dir"
    CATEGORY = "File Operations"

    def walk_dir(self, root_dir, depth, folders_only):
        if not os.path.isdir(root_dir):
            return ["Invalid folder path"]

        result= []
        max_items = 10000

        def walk(current_dir, current_depth):
            nonlocal result
            if depth > 0 and current_depth > depth:
                return

            with os.scandir(current_dir) as entries:
                for entry in entries:
                    if len(result) >= max_items:
                        return

                    if entry.is_dir():
                        result.append(f"{os.path.relpath(entry.path, root_dir)} - dir")
                        walk(entry.path, current_depth + 1)
                    elif not folders_only and entry.is_file():
                        file_size_bytes = entry.stat().st_size
                        if file_size_bytes >= 1 << 30:  # GB threshold
                            file_size = f"{file_size_bytes / (1 << 30):.2f} GB"
                        else:
                            file_size = f"{file_size_bytes / (1 << 20):.2f} MB"
                        result.append(f"{os.path.relpath(entry.path, root_dir)} - {file_size}")

        walk(root_dir, 1)

        return (str(len(result)) + "\n\n" + "\n".join(result), )

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
    "ZEGR_WD": WalkDirNode,
    "ZEGR_ALI_UF": UploadFileNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ZEGR_LF": "ZEGR_LF",
    "ZEGR_WD": "ZEGR_WD",
    "ZEGR_ALI_UF": "ZEGR_ALI_UF"
}
