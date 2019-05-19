import json, logging, sys

# Create a custom logger
misc_logger = logging.getLogger("rcgcdw.misc")

data_template = {"rcid": 99999999999,
                 "daily_overview": {"edits": None, "new_files": None, "admin_actions": None, "bytes_changed": None,
                                    "new_articles": None, "unique_editors": None, "day_score": None}}


def generate_datafile():
	"""Generate a data.json file from a template."""
	try:
		with open("data.json", 'w') as data:
			data.write(json.dumps(data_template, indent=4))
	except PermissionError:
		misc_logger.critical("Could not create a data file (no permissions). No way to store last edit.")
		sys.exit(1)


def load_datafile() -> object:
	"""Read a data.json file and return a dictionary with contents
	:rtype: object
	"""
	try:
		with open("data.json") as data:
			return json.loads(data.read())
	except FileNotFoundError:
		generate_datafile()
		misc_logger.info("The data file could not be found. Generating a new one...")
		return data_template


def save_datafile(data):
	"""Overwrites the data.json file with given dictionary"""
	try:
		with open("data.json", "w") as data_file:
			data_file.write(json.dumps(data, indent=4))
	except PermissionError:
		misc_logger.critical("Could not modify a data file (no permissions). No way to store last edit.")
		sys.exit(1)
