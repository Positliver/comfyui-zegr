import importlib

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

mod = importlib.import_module(f".nodes_zegr", package=__name__)
NODE_CLASS_MAPPINGS.update(mod.NODE_CLASS_MAPPINGS)
NODE_DISPLAY_NAME_MAPPINGS.update(mod.NODE_DISPLAY_NAME_MAPPINGS)
