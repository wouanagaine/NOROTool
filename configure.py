import hashlib
import FileHost
import NOROVersion

def computeMd5Checksum(filePath):
	m = hashlib.md5()
	f = open( filePath, "rb" )
	m.update( f.read() )
	f.close()
	return m.hexdigest()

files = [("Config.bmp","http://dl.dropboxusercontent.com/u/230005956/NoroTool/Config.bmp"),("Background.jpg","http://dl.dropboxusercontent.com/u/230005956/NoroTool/Background.jpg"),("PlayerNames.txt","") ]

f = open( "fileList.txt", "wt" )
f.write( "%s %s\n"%(NOROVersion.NORO_VERSION,"http://dl.dropboxusercontent.com/u/230005956/NoroTool/NOROTool.exe" ) )
for file,url in files:
	md5 = computeMd5Checksum( file )
	print file, md5
	f.write( "%s %s %s\n"%(file,md5,url ) )
	if url == "":
		FileHost.uploadFile( file )
f.close()

FileHost.uploadFile( "fileList.txt" )

	