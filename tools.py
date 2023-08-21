import tomli
import argparse
import sys

argParser = argparse.ArgumentParser()
argParser.add_argument("-c", "--config", help="Config file absolute path")

if len(sys.argv)==1:
    argParser.print_help(sys.stderr)
    sys.exit(1)

args = argParser.parse_args()



CINEMA_ID_PATTERN = r"idcinema=(\d+)"
THEATERS_URL = "https://www.webtic.it/proxyWsl/Services/BoWtJsonServices.ashx?datasource=CREADW&wtid=webticEventsMc"
    
def configurator(section, value):
    
    with open(f"{args.config}", "rb") as f:
        toml_data = tomli.load(f)

    configuration = toml_data[section][value]
    return configuration