import tomli

CINEMA_ID_PATTERN = r"idcinema=(\d+)"
    
def configurator(section, value):
    
    with open("config.toml", "rb") as f:
        toml_data = tomli.load(f)

    configuration = toml_data[section][value]
    return configuration