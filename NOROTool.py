import wx
import utils
import sys
import os
import FileHost

class OverView( wx.Frame ):
	def __init__( self, parent, title, virtualSize, pos=wx.DefaultPosition, size=wx.DefaultSize,
				  style=wx.DEFAULT_FRAME_STYLE |wx.MINIMIZE_BOX |wx.MAXIMIZE_BOX ):
		wx.Frame.__init__(self, parent, -1, title, pos, size, style)

class SplashScreen(wx.SplashScreen):
	def __init__(self):
		bmp = wx.Image( os.path.join( basedir, "splash.jpg" ),wx.BITMAP_TYPE_JPEG).ConvertToBitmap()
		wx.SplashScreen.__init__(self, bmp,
								 wx.SPLASH_CENTRE_ON_SCREEN | wx.SPLASH_TIMEOUT,
								 1000, None, -1)
		self.Bind(wx.EVT_CLOSE, self.OnClose)

	def OnClose(self, evt):
		evt.Skip()
		self.Hide()
		self.ShowMain()

	def ShowMain(self):
		frame = OverView( None, "NOROTool Version 0.1", (600,600) )
		frame.Show()
		
class SC4App( wx.App ):
	def OnInit( self ):
		splash = SplashScreen()
		splash.Show()
		return True

def main():
	mainPath = sys.path[0]
	os.chdir(mainPath)
	app = SC4App( False )
	app.MainLoop()

#md5 = FileHost.uploadFile( "PlayerNames.txt" )
#print md5
#FileHost.downloadFile( "dlPlayerNames.txt",md5 )

if getattr(sys, 'frozen', None):
	basedir = sys._MEIPASS
else:
	basedir = os.path.dirname(__file__)

mainPath = sys.path[0]
os.chdir(mainPath)
main()
