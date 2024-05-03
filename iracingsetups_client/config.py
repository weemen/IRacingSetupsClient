from os import environ

from configloader import ConfigLoader

environment = environ.get("APP_ENV", "development")

config = ConfigLoader()
config.update_from_yaml_file(f"config.{environment}.yaml")
