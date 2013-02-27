import wx
import utils
import sys
import os
import FileHost
import Image
import QuestionDialog
import hashlib
import NOROVersion

def computeMd5Checksum(filePath):
	m = hashlib.md5()
	f = open( filePath, "rb" )
	m.update( f.read() )
	f.close()
	return m.hexdigest()

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

		config = Image.open( "config.bmp" )
		class dlgstub:
			def __init__( self ):
				pass
			def Update( self, x, y ):
				print x, y
				pass
		self.region = utils.SC4Region( dlgstub(), config )
		self.region.show( dlgstub() )
		self.playerName = ""

		
		playerFile = open( "PlayerNames.txt", "rt" )
		players = playerFile.readlines()
		playerFile.close()
		self.players = [ x.strip("\n").strip() for x in players ]
		self.mainTiles = {}
		self.Tiles = {}
		print players
		for player in self.players:
			self.mainTiles[ player ] = None
			self.Tiles[ player ] = []
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
		self.Bind(wx.EVT_CLOSE, self.OnClose)

	def OnClose(self, evt):
		evt.Skip()
		print 'closing'
		

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
		self.SetTitle( "NOROTool Version "+NOROVersion.NORO_VERSION+" - "+self.playerName )

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
				if city2 == self.mainTiles[player]:
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
				if city2 == self.mainTiles[player]:
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

class BaseSplashScreen( wx.Frame ):
	def __init__(self, parent, ID=-1, title="SplashScreen",
				 style=wx.SIMPLE_BORDER|wx.STAY_ON_TOP,
				 duration=1500, bitmapfile="bitmaps/splashscreen.bmp",
				 ):
		'''
		parent, ID, title, style -- see wx.Frame
		duration -- milliseconds to display the splash screen
		bitmapfile -- absolute or relative pathname to image file
		'''
		bmp = wx.Image(bitmapfile, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
		size = (bmp.GetWidth(), bmp.GetHeight())
		# size of screen
		width = wx.SystemSettings_GetMetric(wx.SYS_SCREEN_X)
		height = wx.SystemSettings_GetMetric(wx.SYS_SCREEN_Y)
		pos = ((width-size[0])/2, (height-size[1])/2)

		# check for overflow...
		if pos[0] < 0:
			size = (wx.SystemSettings_GetSystemMetric(wx.SYS_SCREEN_X), size[1])
		if pos[1] < 0:
			size = (size[0], wx.SystemSettings_GetSystemMetric(wx.SYS_SCREEN_Y))
		wx.Frame.__init__(self, parent, ID, title, pos, size, style)
		static = wx.StaticBitmap( self, wx.ID_ANY, bmp )
		sizer = wx.BoxSizer( wx.VERTICAL )
		sizer.Add( static, 1, wx.EXPAND|wx.ALL, 0 )
		self.SetSizer( sizer )
		self.Layout()
		
		self.sb = wx.StatusBar(self)
		self.SetStatusBar(self.sb)
		self.sb.SetFieldsCount(1)
		self.sb.SetStatusWidths([-1])
		
		self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseClick)
		self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
		self.Bind(wx.EVT_TIMER, self.OnSplashExitDefault )
		self.Show(True)
		self.timer = wx.Timer(self,duration)
		self.timer.Start(duration, 1) # one-shot only

	def OnSplashExitDefault(self, event=None):
		self.Close(True)

	def OnCloseWindow(self, event=None):
		wx.FutureCall( 500, self.OnCloseWindowFinal )
		
	def OnCloseWindowFinal(self, event=None):
		self.Show(False)
		self.timer.Stop()
		del self.timer
		self.Destroy()

	def OnMouseClick(self, event):
		self.timer.Notify()
		
	def SetStatusText( self, text, i=0):
		self.sb.SetStatusText( text, i )
		wx.Yield()
		
class SplashScreen(BaseSplashScreen):
	def __init__(self, parent = None ):
		BaseSplashScreen.__init__( self, parent, bitmapfile="splash.jpg", title = "NOROTool Version "+NOROVersion.NORO_VERSION, duration=1000 )
		wx.CallAfter( self.SetStatusText, ( "Initializing..." ) )		
		self.Bind(wx.EVT_CLOSE, self.OnClose)

	def OnClose(self, evt):
		evt.Skip()
		self.ShowMain()

	def ShowMain(self):
		if self.AutoUpdate():
			frame = OverView( None, "NOROTool Version "+NOROVersion.NORO_VERSION, (600,600) )
			frame.PlayerSelection()
			frame.Show()

	def AutoUpdate( self ):
		self.SetStatusText( "Checking for update..." );
		wx.Yield()
		self.SetStatusText( "Downloading list files" );
		wx.Yield()				
		try:
			FileHost.downloadFile( "fileList.txt" )
			fileList = open( "fileList.txt","rt" )
			files = fileList.readlines()
			fileList.close()
			version = files[0].strip("\n").strip()
			if version != NOROVersion.NORO_VERSION:
				dlg = wx.MessageDialog(None, "You don't have the correct version\nPlease download and reinstall the latest one",
										 'Error',
									 wx.OK | wx.ICON_ERROR
									 )
				dlg.ShowModal()
				dlg.Destroy()
				return False
			downloadFiles = [ f.strip("\n").strip() for f in files[1:] ]		
			for downloadMD5 in downloadFiles:
				infos = downloadMD5.split()
				download = infos[0]
				md5 = infos[1]
				toDownload = False
				if os.path.exists( download ):
					md5HD = computeMd5Checksum( download )
					if md5HD != md5:
						toDownload = True
				if not os.path.exists( download ):
					toDownload = True
				if toDownload == True:
					self.SetStatusText( "Downloading %s"%download );
					wx.Yield()				
					FileHost.downloadFile( download )
					
			playerFile = open( "PlayerNames.txt", "rt" )
			players = playerFile.readlines()
			playerFile.close()
			players = [ x.strip("\n").strip() for x in players ]
			for player in players:
				playerFile = "player_"+player+".txt"
				self.SetStatusText( "Downloading %s"%playerFile );
				wx.Yield()				
				FileHost.downloadFile( "player_"+player+".txt" )
			self.SetStatusText( "Startup..." );
			wx.Yield()				
			return True
		except:
			dlg = wx.MessageDialog(None, "Problem while downloading files\nCheck you have an open internet connection",
							 'Error',
						 wx.OK | wx.ICON_ERROR
						 )
			dlg.ShowModal()
			dlg.Destroy()
			return False

		
	
		
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

#FileHost.uploadFile( "fileList.txt" )
#FileHost.uploadFile( "Background.jpg" )
#md5 = FileHost.uploadFile( "Config.bmp" )
#print md5
#md5 = FileHost.uploadFile( "PlayerNames.txt" )
#print md5


if getattr(sys, 'frozen', None):
	basedir = sys._MEIPASS
else:
	basedir = os.path.dirname(__file__)

mainPath = sys.path[0]
os.chdir(mainPath)
main()
