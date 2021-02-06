import errno
import os
import enum

import requests
from dotenv import load_dotenv

load_dotenv()

CANVAS_URL = os.getenv('CANVAS_URL')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
API_URL = f'{CANVAS_URL}/api/v1'

class Item(enum.Enum):
	FOLDER = 1
	FILE = 2

class CanvasCourseFiles():
	def __init__(self, course_id):
		self.api = requests.Session()
		self.api.headers.update(
			{'Authorization': f'Bearer {ACCESS_TOKEN}'}
		)
		self.course_id = course_id

	def get_folder(self, folder_id):
		url = f'{API_URL}/courses/{self.course_id}/folders/{folder_id}'
		response = self.api.get(url)

		if response.status_code == requests.codes.unauthorized:
			raise ConnectionError()

		if response.status_code == requests.codes.not_found:
			raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), '$filename')

		return response.json()

	def get_file(self, file_id):
		url = f'{API_URL}/courses/{self.course_id}/files/{file_id}'
		response = self.api.get(url)

		if response.status_code == requests.codes.unauthorized:
			raise ConnectionError()

		if response.status_code == requests.codes.not_found:
			raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), '$filename')

		return response.json()

	def get_item(self, item_id):
		try:
			return self.get_folder(item_id)
		except FileNotFoundError:
			try:
				return self.get_file(item_id)
			except FileNotFoundError:
				return None

	@staticmethod
	def item_type(item):
		if 'name' in item:
			return Item.FOLDER
		if 'filename' in item:
			return Item.FILE

		return None

	def _ls_files(self, folder_id):
		resolved_path = self.get_folder(folder_id)
		files = self.api.get(resolved_path['files_url'])

		return files.json()

	def _ls_folders(self, folder_id):
		resolved_path = self.get_folder(folder_id)
		folders = self.api.get(resolved_path['folders_url'])

		return folders.json()

	def ls(self, folder_id):
		files = self._ls_files(folder_id)
		folders = self._ls_folders(folder_id)

		return files + folders
