# Canvas LMS FUSE Filesystem

![A Canvas "Files" page on one side and `ls -l` showing the same files on the other side](media/screenshot.png)

This is, at the moment, just a proof-of-concept.

## Features

- [x] read
- [ ] write
- [x] mount courses
- [ ] mount groups
- [ ] mount users

## Getting started

Until I get this on PyPi:

- `git clone https://github.com/shreyasminocha/canvas-fs.git`
- `cd canvas-fs`
- `cp .env.example .env`, `chmod 600 .env`
- Create and activate a virtualenv [optional]
- `pip install -r requirements.txt`
- On canvas, go to "Account" → "Settings", and under "Approved Integrations:" click "+ New Access Token"
  - Set the purpose to "canvasfs"
  - Set an expiration date [optional, but recommended]
  - Click "Generate" and copy the "Token:" field
- Open `.env` and set the values of `CANVAS_URL` and `ACCESS_TOKEN`
- Find the course ID of the course you wish to mount — `https://canvas.example.edu/courses/[course_id]`
- Create a directory, say `/mnt/canvas/comp182`, and make sure your user owns it
- `python -m canvasfs [course_id] /mnt/canvas/comp182`

## Platforms

Tested with fuse3 on Arch Linux. It *should* also work on macOS with [macFuse](https://osxfuse.github.io). Apparently [FUSE for Windows](http://www.secfs.net/winfsp) is a thing, but I don't know if this will work with it.

## License

Licensed under the [MIT License](https://l.shreyasminocha.me/mit/2021-)


## Contributions

… are welcome.

- [Canvas files API docs](https://canvas.instructure.com/doc/api/files.html)
- [pyfuse3 docs](https://www.rath.org/pyfuse3-docs)
