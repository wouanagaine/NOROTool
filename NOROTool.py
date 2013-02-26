import wx
import utils
import sys
import os
import FileHost
import Image
import QuestionDialog

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

			self.UpdateDrawing()	
		else:
			self.buffer = None
		if event:
			event.Skip()
	def ShowLocked( self, dc, city, cities, mode = wx.SOLID, fromMouse = False ):
		if fromMouse:
			dc = self.UpdateDrawing( finish = False )
		self.HighlightCity( dc, self.parent.region, city, wx.Colour( 255,128,128), mode, wx.OR )
		for c in cities:
			self.HighlightCity( dc, self.parent.region, c, wx.Colour( 128,128,128), mode )
		if fromMouse:
			dc.EndDrawing()
	def UpdateDrawing( self, finish = True):
		dc = wx.BufferedDC( None, self.buffer)
		dc.BeginDrawing()
		dc.SetBackground(wx.Brush( wx.Colour( 64,128,64 ),wx.SOLID))
		dc.Clear()			
		dc.DrawBitmap( self.backImg, 0, 0,  False )
		self.AddOverlay( dc, self.parent.region )
		for player in self.parent.players:
			if self.parent.mainTiles[player]:
				if player == self.parent.playerName:
					self.ShowLocked( dc, self.parent.mainTiles[player], self.parent.Tiles[player], wx.CROSS_HATCH )
				else:
					self.ShowLocked( dc, self.parent.mainTiles[player], self.parent.Tiles[player], wx.CROSSDIAG_HATCH )
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
	def HighlightCity( self, dc, region, city, colour, mode = wx.CROSSDIAG_HATCH, op = wx.XOR, fromMouse = False ):
		if fromMouse:
			dc = self.UpdateDrawing( finish = False )
		sizes = [ 0,16,32,0,64 ]
		#for city in region.allCities:
			#if pos[0] >= city.cityXPos and pos[0] < city.cityXPos+city.cityXSize and pos[1] >= city.cityYPos and pos[1] < city.cityYPos+city.cityYSize :
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
		#break
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
		self.playerName = ""

		md5 = FileHost.md5Checksum( "PlayerNames.txt" )
		FileHost.downloadFile( "Players.txt", md5 )
		playerFile = open( "Players.txt", "rt" )
		players = playerFile.readlines()
		playerFile.close()
		self.players = [ x.strip("\n").strip() for x in players ]
		self.mainTiles = {}
		self.Tiles = {}
		print players
		for player in self.players:
			self.mainTiles[ player ] = None
			self.Tiles[ player ] = []
			md5 = FileHost.md5Checksum( "player_"+player+".txt" )
			FileHost.downloadFile( "player_"+player+".txt", md5 )
			playerFile = open( "player_"+player+".txt", "rt" )
			lines = playerFile.readlines()
			playerFile.close()
			if len( lines ) > 0 :
				coord = [ int( line.strip("\n").strip() ) for line in lines ]
				print player, coord
				mainTile = self.region.GetCityUnder( coord )
				self.mainTiles[ player ] = mainTile
				self.Tiles[ player ] = self.GetImpactedCities( mainTile )
		self.back = OverViewCanvas(self, -1,size=(self.region.imgSize))
		self.back.SetBackgroundColour("WHITE")
		self.box = wx.BoxSizer( wx.VERTICAL )
		self.box.Add(self.back, 1, wx.EXPAND)
		self.box.Fit(self)
		self.SetSizer(self.box)
		self.Center()
		self.back.Bind( wx.EVT_MOTION, self.OnMouseMove )
		self.back.Bind( wx.EVT_RIGHT_DOWN, self.OnRightDown )
		self.back.Bind( wx.EVT_LEFT_DOWN, self.OnLeftDown )

	def PlayerSelection( self ):
		if os.path.exists( "name.txt" ):
			f = open( "name.txt" ,"rt")
			self.playerName = f.read().strip("\n").strip()
			f.close()
		if self.playerName not in self.players:
			self.playerName = QuestionDialog.questionDialog( "Who are you?",self.players,"Select player")
			f = open( "name.txt","wt")
			f.write( self.playerName )
			f.close()
		self.SetTitle( "NOROTool Version 0.2 - "+self.playerName )

	def OnLeftDown( self, event ):
		event.Skip()
		try:
			if self.mainTiles[ self.playerName ] != None:
				return
		except KeyError:
			return
		newpos = (event.GetX(), event.GetY())			
		newpos = [ newpos[0]/16,newpos[1]/16 ]
		city = self.region.GetCityUnder( newpos )
		cities = self.GetImpactedCities( city )
		bValid = True
		for player in self.players:
			for city2 in cities:
				if city2 in self.Tiles[player]:
					bValid = False
					break	
			if bValid == False:
				break
		if bValid:
			self.mainTiles[ self.playerName ] = city
			self.Tiles[ self.playerName ] = cities
			self.back.UpdateDrawing()			
			self.back.wait = True
			self.back.Refresh( False )
			wx.BeginBusyCursor()
			playerFile = open( "player_"+self.playerName+".txt", "wt" )
			playerFile.write( "%d\n%d"%(city.cityXPos,city.cityYPos) )
			playerFile.close()
			FileHost.uploadFile( "player_"+self.playerName+".txt" )
			wx.EndBusyCursor()

	def OnRightDown( self, event ):
		event.Skip()
		try:
			if self.mainTiles[ self.playerName ] == None:
				return
		except KeyError:
			return
		self.mainTiles[ self.playerName ] = None
		self.Tiles[ self.playerName ] = []
		self.back.UpdateDrawing()			
		self.back.wait = True
		self.back.Refresh( False )
		wx.BeginBusyCursor()
		playerFile = open( "player_"+self.playerName+".txt", "wt" )
		playerFile.close()
		FileHost.uploadFile( "player_"+self.playerName+".txt" )
		wx.EndBusyCursor()

	def OnMouseMove( self, event ):
		event.Skip()
		if self.back.wait == True:
			pass
		try:
			if self.mainTiles[ self.playerName ] != None:
				return
		except KeyError:
			return
		bValid = True
		newpos = (event.GetX(), event.GetY())			
		newpos = [ newpos[0]/16,newpos[1]/16 ]
		city = self.region.GetCityUnder( newpos )
		cities = self.GetImpactedCities( city )
		for player in self.players:
			for city2 in cities:
				if city2 in self.Tiles[player]:
					bValid = False
					break	
			if bValid == False:
				break
		if bValid:
			self.back.ShowLocked( 0, city, cities, wx.CROSS_HATCH, True )
		else:
			self.back.HighlightCity( 0, self.region, city, wx.Colour( 255,0,0 ), wx.SOLID, wx.OR, True)
		self.back.wait = True
		self.back.Refresh( False )

	def GetImpactedCities( self, city ):
		firstRing = self.region.GetAdjacentCities( city )
		secondRing = []
		for c in firstRing :
			secondRing += self.region.GetAdjacentCities( c )
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
		return firstRing+secondRing

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
		frame = OverView( None, "NOROTool Version 0.2", (600,600) )
		frame.Show()
		wx.CallAfter( frame.PlayerSelection )

		
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
