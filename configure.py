import hashlib
import FileHost
import NOROVersion

def computeMd5Checksum(filePath):
	m = hashlib.md5()
	f = open( filePath, "rb" )
	m.update( f.read() )
	f.close()
	return m.hexdigest()

files = ["Config.bmp","Background.jpg","PlayerNames.txt" ]

f = open( "fileList.txt", "wt" )
f.write( "%s %s\n"%(NOROVersion.NORO_VERSION,"http://www.fileden.com/files/2006/7/28/145206/NOROTool-0.3.ex_" ) )
for file in files:
	md5 = computeMd5Checksum( file )
	print file, md5
	f.write( "%s %s\n"%(file,md5 ) )
	FileHost.uploadFile( file )
f.close()

FileHost.uploadFile( "fileList.txt" )

	