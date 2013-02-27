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
f.write( "%s\n"%NOROVersion.NORO_VERSION )
for file in files:
	md5 = computeMd5Checksum( file )
	print file, md5
	f.write( "%s %s\n"%(file,md5 ) )
	FileHost.uploadFile( file )
f.close()

FileHost.uploadFile( "fileList.txt" )

	