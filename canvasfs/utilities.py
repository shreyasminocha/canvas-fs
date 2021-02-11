import enum
from datetime import datetime
import calendar

class Item(enum.Enum):
	FOLDER = 1
	FILE = 2

class Context(enum.Enum):
	COURSE = 'courses'
	USER = 'users'
	GROUP = 'groups'

	def __str__(self):
		return self.value

def iso_to_unix(iso):
	iso_format = '%Y-%m-%dT%H:%M:%SZ'

	return calendar.timegm(
		datetime.strptime(iso, iso_format).timetuple()
	)
