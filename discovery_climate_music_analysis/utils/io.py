from discovery_climate_music_analysis import PROJECT_DIR, logging
from yaml import safe_load

DEF_CONFIG_PATH = PROJECT_DIR / "discovery_climate_music_analysis/config"


def import_config(filename: str, path=DEF_CONFIG_PATH) -> dict:
    """Load a config .yaml file"""
    with open(path / filename, "r", encoding="utf-8") as yaml_file:
        config_dict = safe_load(yaml_file)
    return config_dict
