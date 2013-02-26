import wx
import utils
import sys
import os
import FileHost
import Image

class OverViewCanvas( wx.Panel):
	def __init__(self, parent, id = -1, size = wx.DefaultSize):
		wx.Panel.__init__(self, parent, id, size=size, style=wx.SUNKEN_BORDER|wx.FULL_REPAINT_ON_RESIZE)
		self.parent = parent
		self.buffer = None
		self.wait = False
		im = wx.Image( "Background.jpg" )
		im.Rescale( self.parent.region.imgSize[0],self.parent.region.imgSize[1] )
		self.backImg = wx.BitmapFromImage( im )
		self.Bind(wx.EVT_PAINT, self.OnPaint)
		self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
		self.Bind(wx.EVT_SIZE, self.OnSize)
		self.OnSize( None )
	def OnEraseBackground( self, event ):
		pass
	def OnSize(self,event):
		size  = self.ClientSize
		if event:
			size = event.GetSize()
		if self.parent.region:
			if self.buffer == None or ( self.buffer.GetWidth() != size[0] or self.buffer.GetHeight() != size[1] ):
				self.buffer = wx.EmptyBitmap(*size)

			self.UpdateDrawing( newSize = size )	
		else:
			self.buffer = None
		if event:
			event.Skip()
	def ShowLocked( self, dc, city, mode = wx.SOLID ):
		self.HighlightCity( dc, self.parent.region, (city.cityXPos,city.cityYPos), wx.Colour( 255,128,128), mode, wx.OR )
		firstRing = self.parent.region.GetAdjacentCities( city )
		secondRing = []
		for c in firstRing :
			secondRing += self.parent.region.GetAdjacentCities( c )
		secondRing = list( set( secondRing ) )
		try:
			secondRing.remove( city )
		except ValueError:
			pass
		for c in firstRing :
			try:
				secondRing.remove( c )
			except ValueError:
				pass
		for c in firstRing+secondRing:
			self.HighlightCity( dc, self.parent.region, (c.cityXPos,c.cityYPos), wx.Colour( 128,128,128), mode )

	def UpdateDrawing( self, pos = None, newSize = None, finish = True):
		dc = wx.BufferedDC( None, self.buffer)
		dc.BeginDrawing()
		dc.SetBackground(wx.Brush( wx.Colour( 64,128,64 ),wx.SOLID))
		dc.Clear()			
		dc.DrawBitmap( self.backImg, 0, 0,  False )
		#self.AddGrid( dc, self.parent.region )
		self.AddOverlay( dc, self.parent.region )
		city = self.parent.region.GetCityUnder( (7,15) )
		self.ShowLocked( dc, city )
		city = self.parent.region.GetCityUnder( (32,25) )
		self.ShowLocked( dc, city, wx.CROSSDIAG_HATCH )
		if finish:
			dc.EndDrawing()		
		self.wait = True
		wx.CallAfter( self.Refresh, False )
		if finish == False:
			return dc		
	def AddGrid( self, dc, region ):
		lines=[]
		s = (region.shape[1],region.shape[0])
		for y in xrange( s[1]/16 ):
			lines.append( [ 0,y*16,region.originalConfig.size[0]*16,y*16 ] )
		for x in xrange( s[0]/16 ):
			lines.append( [ x*16,0,x*16,region.originalConfig.size[1]*16 ] )
		dc.SetPen( wx.Pen( "Light Gray" ) )
		dc.DrawLineList( [ (x1,y1,x2,y2) for x1,y1,x2,y2 in lines ] )
	def AddOverlay( self, dc, region ):
		dc.SetPen(wx.Pen("WHITE"))
		dc.SetBrush(wx.Brush( "WHITE",wx.TRANSPARENT ) )
		colours = [ 0, wx.Colour( 255,0,0 ), wx.Colour( 0,255,0 ), 0, wx.Colour( 0,0,255 ) ]
		sizes = [ 0,16,32,0,64 ]
		for city in region.allCities:
			x = int( city.cityXPos*16 )
			y = int( city.cityYPos*16 )
			width = sizes[city.cityXSize]
			height = sizes[city.cityYSize]
			dc.SetPen(wx.Pen("WHITE"))				
			dc.SetBrush(wx.Brush( "WHITE",wx.TRANSPARENT ) )
			dc.SetPen( wx.Pen(colours[city.cityXSize]) )
			dc.SetBrush(wx.Brush( colours[city.cityXSize],wx.TRANSPARENT ) )
			self.DrawRectangle( dc, x,y,width,height )
			self.DrawRectangle( dc, x+1,y+1,width-2,height-2 )
	def HighlightCity( self, dc, region, pos, colour, mode = wx.CROSSDIAG_HATCH, op = wx.XOR, fromMouse = False ):
		if fromMouse:
			dc = self.UpdateDrawing( finish = False )
		sizes = [ 0,16,32,0,64 ]
		for city in region.allCities:
			if pos[0] >= city.cityXPos and pos[0] < city.cityXPos+city.cityXSize and pos[1] >= city.cityYPos and pos[1] < city.cityYPos+city.cityYSize :
				x = int( city.cityXPos*16 )
				y = int( city.cityYPos*16 )
				width = sizes[city.cityXSize]
				height = sizes[city.cityYSize]
				dc.SetLogicalFunction( op )
				dc.SetPen(wx.Pen( colour ))
				dc.SetBrush(wx.Brush( colour,mode) )		
				self.DrawRectangle( dc, x+1,y+1,width-2,height-2 )
				self.DrawRectangle( dc, x,y,width,height )
				self.DrawRectangle( dc, x-1,y-1,width+2,height+2 )
				dc.SetLogicalFunction( wx.COPY )
				break
		if fromMouse:
			dc.EndDrawing()
	def DrawRectangle( self, dc, x, y, width, height ):
		dc.DrawRectangle( x, y, width, height )	
	def OnPaint(self, event):
		if self.buffer is None:
			self.clear = False
			self.wait = False
			dc = wx.PaintDC(self)
			self.DoPrepareDC(dc)
			dc.SetBackground(wx.Brush(self.GetBackgroundColour()))			
			dc.Clear()			
		if self.buffer is not None:
			self.wait = False
			dc = wx.BufferedPaintDC(self, self.buffer, wx.BUFFER_CLIENT_AREA )

class OverView( wx.Frame ):
	def __init__( self, parent, title, virtualSize, pos=wx.DefaultPosition, size=wx.DefaultSize,
				  style=wx.DEFAULT_FRAME_STYLE |wx.MINIMIZE_BOX |wx.MAXIMIZE_BOX ):
		wx.Frame.__init__(self, parent, -1, title, pos, size, style)

		config = Image.open( "NoroConfig.bmp" )
		class dlgstub:
			def __init__( self ):
				pass
			def Update( self, x, y ):
				print x, y
				pass
		self.region = utils.SC4Region( dlgstub(), config )
		self.region.show( dlgstub() )
		self.back = OverViewCanvas(self, -1,size=(self.region.imgSize))
		self.back.SetBackgroundColour("WHITE")
		self.box = wx.BoxSizer( wx.VERTICAL )
		self.box.Add(self.back, 1, wx.EXPAND)
		self.box.Fit(self)
		self.SetSizer(self.box)
		self.Center()


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

#FileHost.uploadFile( "Background.jpg" )
#md5 = FileHost.uploadFile( "Config.bmp" )
#print md5
#md5 = FileHost.uploadFile( "PlayerNames.txt" )
#print md5


if not os.path.exists( "NoroConfig.bmp" ):
	md5 = FileHost.md5Checksum( "Config.bmp" )
	FileHost.downloadFile( "NoroConfig.bmp", md5 )

if not os.path.exists( "Background.jpg" ):
	FileHost.downloadFile( "Background.jpg" )


if getattr(sys, 'frozen', None):
	basedir = sys._MEIPASS
else:
	basedir = os.path.dirname(__file__)

mainPath = sys.path[0]
os.chdir(mainPath)
main()
