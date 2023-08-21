import tomli
import argparse


argParser = argparse.ArgumentParser()
argParser.add_argument("-c", "--config", help="Config file absolute path")
args = argParser.parse_args()

if not vars(args):
    argParser.print_help()
else:
    pass

CINEMA_ID_PATTERN = r"idcinema=(\d+)"
THEATERS_URL = "https://www.webtic.it/proxyWsl/Services/BoWtJsonServices.ashx?datasource=CREADW&wtid=webticEventsMc"
    
def configurator(section, value):
    
    with open(f"{args.config}", "rb") as f:
        toml_data = tomli.load(f)

    configuration = toml_data[section][value]
    return configuration