import errno
import os

import requests
from dotenv import load_dotenv

load_dotenv()

CANVAS_URL = os.getenv('CANVAS_URL')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
API_URL = f'{CANVAS_URL}/api/v1'

class CanvasCourseFiles():
	def __init__(self, course_id):
		self.api = requests.Session()
		self.api.headers.update(
			{'Authorization': f'Bearer {ACCESS_TOKEN}'}
		)
		self.course_id = course_id

	def resolve_path(self, path):
		url = f'{API_URL}/courses/{self.course_id}/folders/by_path/{path}'
		response = self.api.get(url)

		if response.status_code == requests.codes.unauthorized:
			raise ConnectionError()

		if response.status_code == requests.codes.not_found:
			raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), '$filename')

		return response.json()[-1]

	def _ls_files(self, path):
		resolved_path = self.resolve_path(path)
		files = self.api.get(resolved_path['files_url'])

		return files.json()

	def _ls_folders(self, path):
		resolved_path = self.resolve_path(path)
		folders = self.api.get(resolved_path['folders_url'])

		return folders.json()

	def ls(self, path):
		files = self._ls_files(path)
		folders = self._ls_folders(path)

		return files + folders

	def get_file(self, path):
		resolved_path = self.resolve_path(path)

math211 = CanvasCourseFiles(34541)
print(math211.ls('/'))
