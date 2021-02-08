import os
import stat
import errno

import pyfuse3

from .canvas_files import CanvasCourseFiles, Item
from .utilities import iso_to_unix

class CanvasFs(pyfuse3.Operations):
	def __init__(self, course_id):
		super(CanvasFs, self).__init__()
		self.course = CanvasCourseFiles(course_id)

	async def getattr(self, inode, ctx=None, **kwargs):
		entry = pyfuse3.EntryAttributes()

		if inode == pyfuse3.ROOT_INODE:
			entry.st_mode = (stat.S_IFDIR | 0o755)
			entry.st_size = 0

			entry.st_atime_ns = int(1 * 1e9)
			entry.st_mtime_ns = int(1 * 1e9)
			entry.st_ctime_ns = int(1 * 1e9)

		else:
			item = kwargs.get('item') or self.course.get_item(inode)
			item_type = CanvasCourseFiles.item_type(item)

			if item_type == Item.FOLDER:
				entry.st_mode = (stat.S_IFDIR | 0o755)
				entry.st_size = 0
			elif item_type == Item.FILE:
				entry.st_mode = (stat.S_IFREG | 0o644)
				entry.st_size = item['size']

			updated = item['updated_at']
			modified = item.get('modified_at') or item.get('updated_at')
			created = item['created_at']

			entry.st_atime_ns = int(iso_to_unix(updated) * 1e9)
			entry.st_mtime_ns = int(iso_to_unix(modified) * 1e9)
			entry.st_ctime_ns = int(iso_to_unix(created) * 1e9)

		entry.st_gid = os.getgid()
		entry.st_uid = os.getuid()
		entry.st_ino = inode

		return entry

	async def lookup(self, parent_inode, name, ctx=None):
		if parent_inode == pyfuse3.ROOT_INODE:
			parent_inode = 'root'

		parent_folder_files = self.course._ls_files(parent_inode)

		found_file = None
		for file in parent_folder_files:
			if file['filename'] == name.decode('utf-8'):
				found_file = file
				break

		if found_file is None:
			raise pyfuse3.FUSEError(errno.ENOENT)

		return await self.getattr(found_file['id'], item=found_file)

	async def opendir(self, inode, ctx):
		if inode == pyfuse3.ROOT_INODE:
			return inode

		try:
			item = self.course.get_item(inode)
			item_type = CanvasCourseFiles.item_type(item)
		except FileNotFoundError:
			raise pyfuse3.FUSEError(errno.ENOENT)

		if item_type == Item.FOLDER:
			return inode

		raise pyfuse3.FUSEError(errno.ENOENT)

	async def readdir(self, fh, start_id, token):
		if fh == pyfuse3.ROOT_INODE:
			fh = 'root'

		ls = self.course.ls(fh)

		for i in range(start_id, len(ls)):
			item = ls[i]
			name = item.get('name') or item.get('filename')

			pyfuse3.readdir_reply(
				token,
				bytes(name, 'utf-8'),
				await self.getattr(item['id'], item=item),
				i + 1
			)

	async def open(self, inode, flags, ctx):
		try:
			file = self.course.get_file(inode)
		except:
			raise pyfuse3.FUSEError(errno.ENOENT)

		if flags & os.O_RDWR or flags & os.O_WRONLY:
			raise pyfuse3.FUSEError(errno.EACCES)

		return pyfuse3.FileInfo(fh=inode)

	async def read(self, fh, off, size):
		try:
			file = self.course.get_file(fh)
		except:
			raise pyfuse3.FUSEError(errno.ENOENT)

		file_url = file['url']
		downloaded_file = await self.course.download_file(file_url)

		return downloaded_file[off:off+size]

	async def release(self, fd):
		pass