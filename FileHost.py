'''
THIS IS AN EXTENSION OF THE NOTEPAD.CC WRAPPER.

EXAMPLE OF USE:

TO UPLOAD A FILE USE THE uploadFile FUNCTION, WHEN THE
UPLOAD IS FINISHED THE FUNCTION RETURN AN MD5 STRING.
THAT STRING IS THE UNIQUE ID OF THE FILE AND YOU
NEED IT FOR DOWNLOADING THE FILE.
YOU CAN DOWNLOAD THE FILE WITH THE FUNCTION downloadFile.

FUNCTIONS:

uploadFile(FILE_PATH)

downloadFile(FILE_NAME, MD5_STRING)


print "UPLOAD..."
filemd5= uploadFile("EXAMPLEFILE.zip")
print "DOWNLOAD..."
downloadFile("EXAMPLEFILE2.zip",filemd5)

IT UPLOAD THE FILE 'EXAMPLEFILE.zip' AND THEN
DOWNLOAD THAT FILE WITH THE NAME 'EXAMPLEFILE2.zip'

'''
import urllib, urllib2, hashlib
class Note:
	def __init__(self,id):
		self.id=id
		print "http://notepad.cc/"+id
		self.page=urllib.urlopen("http://notepad.cc/"+id).read()
		pezzi=self.page.split('<textarea name="contents" id="contents" class="contents " spellcheck="true">')
		p=pezzi[1].split("</textarea>")
		self.cont=p[0]
	def getNote(self):
		return self.cont
	def setNote(self, note):
		url = 'http://notepad.cc/ajax/update_contents/'+self.id
		values = {'contents' : note
		}

		data = urllib.urlencode(values)
		req = urllib2.Request(url, data)
		response = urllib2.urlopen(req)
		the_page = response.read()
def md5Checksum(filePath):
	m = hashlib.md5()
	m.update( "NOROTOOL/"+filePath)
	return 'NOROTOOL_'+m.hexdigest()
def uploadFile(file, md5 = None):
	if md5 == None:
		md5=md5Checksum(file)
	f=open(file,'rb')
	fNote=Note(md5)
	fNote.setNote(f.read())
	f.close()
	return md5
def downloadFile(filename,md5 = None):
	if md5 == None:
		md5 = md5Checksum( filename )
	fNote=Note(md5)
	f=open(filename,'wb')
	f.write(fNote.getNote())
	f.close()
	
