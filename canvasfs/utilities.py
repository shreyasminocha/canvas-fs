from datetime import datetime
import calendar

def iso_to_unix(iso):
	iso_format = '%Y-%m-%dT%H:%M:%SZ'

	return calendar.timegm(
		datetime.strptime(iso, iso_format).timetuple()
	)
