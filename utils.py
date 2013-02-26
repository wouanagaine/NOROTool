import wx
import sys
import struct
import time
import numpy as Numeric
import Image
import ImageDraw
import math
from math import *

class CityProxy( object ):
	"""A proxy for an empty city"""
	def __init__( self, xPos, yPos, xSize, ySize ):
		self.cityXPos = xPos
		self.cityYPos = yPos
		self.cityXSize = xSize
		self.cityYSize = ySize
		self.cityName = 'Not created yet'
		self.ySize = self.cityYSize * 64 +1                
		self.xSize = self.cityXSize * 64 +1
		self.xPos = self.cityXPos * 64
		self.yPos = self.cityYPos * 64
		self.fileName = None

	def AtPos( self, x,y ):
		"""check if the city is at a specific coordinate ( in config.bmp coordinate )"""
		return x == self.cityXPos and y == self.cityYPos
	
def WorkTheconfig( config, waterLevel ):
	"""Read the config.bmp, verify it, and create the city proxies for it"""
	verified = Numeric.zeros( config.size, Numeric.int8 )
	def Redish( value ):
		"""True for small city"""
		(r,g,b) = value
		if r > g and r > b and r > 250 :
			return True
		return False
	def Greenish( value ):
		"""True for medium city"""
		(r,g,b) = value
		if g > r and g > b and g > 250:
			return True
		return False
	def Blueish( value ):
		"""True for big city"""
		(r,g,b) = value
		if b > r and b > g  and b > 250:
			return True
		return False
	def VerifyMedium( x,y ):
		"""Verify the 2x2 pixels from x,y are green"""
		rgbs = (config.getpixel( (x+1, y) ), config.getpixel( (x, y+1)), config.getpixel( (x+1, y+1) ) )
		for rgb in rgbs:
			if not Greenish( rgb ):
				assert 0
		verified[ x,y ]=1
		verified[ x+1,y ]=1
		verified[ x,y+1 ]=1
		verified[ x+1,y+1 ]=1
	def VerifyLarge( x,y ):
		"""Verify the 4x4 pixels from x,y are blue"""
		rgbs = (
		 config.getpixel( (x+1, y) ),config.getpixel( (x+2, y) ),config.getpixel( (x+3, y) ),
		 config.getpixel( (x, y+1) ),config.getpixel( (x+1, y+1) ),config.getpixel( (x+2, y+1) ),config.getpixel( (x+3, y+1) ),
		 config.getpixel( (x, y+2) ),config.getpixel( (x+1, y+2) ),config.getpixel( (x+2, y+2) ),config.getpixel( (x+3, y+2) ),
		 config.getpixel( (x, y+3) ),config.getpixel( (x+1, y+3) ),config.getpixel( (x+2, y+3) ),config.getpixel( (x+3, y+3) )
		 )
		for rgb in rgbs:
			if not Blueish( rgb ):
				assert 0
		for j in xrange(4):
			for i in xrange(4):
				verified[ x+i,y+j ]=1
	big = 0
	bigs = []
	small = 0
	smalls = []
	medium = 0
	mediums = []	
	for y in xrange( config.size[1] ):
		for x in xrange( config.size[0] ):
			if verified[ x,y ] == 0:
				rgb = config.getpixel( (x,y) )
				if Blueish( rgb ):    
					try:                
						VerifyLarge( x,y )
						bigs.append( (x,y) )                    
						big += 1
					except:
						print x,y, "not blue"
						raise
				if Greenish( rgb ):
					try:                
						VerifyMedium( x,y )
						mediums.append( (x,y) )
						medium += 1
					except:
						print x,y, "not green"
						raise
				if Redish( rgb ):
					smalls.append( (x,y ) )
					small += 1
	print "big cities = ", big
	print "medium cities = ", medium
	print "small cities = ", small
	cities = [ CityProxy( waterLevel, c[0],c[1], 1,1 ) for c in smalls ] + [ CityProxy( waterLevel, c[0],c[1], 2,2 ) for c in mediums ] + [ CityProxy( waterLevel, c[0],c[1], 4,4 ) for c in bigs ]
	return cities


class SC4Region( object ):
	"a SC4 region, contains cities, layout and height map"
	def __init__( self, dlg, config ):
		self.config = config
		self.allCities = [] 
		
		self.config = self.config.convert( 'RGB' )
		self.originalConfig = self.config.copy()
		self.allCities = WorkTheconfig( self.config, waterLevel )
			
		self.config = self.BuildConfig()
		self.originalConfig = self.BuildConfig()  
		if dlg is not None: dlg.Update( 1, "Please wait while loading the region" )
	
	def BuildConfig( self ):
		"""Build a nice config.bmp with slight colors changes, also fill the missingCities"""
		sizeX = sizeY = 0
		bigs = []
		smalls = []
		mediums = []
		for city in ( self.allCities ):
			if city.cityXSize == 4:
				bigs.append( (city.cityXPos,city.cityYPos ) )
			if city.cityXSize == 2:
				mediums.append( (city.cityXPos,city.cityYPos ) )
			if city.cityXSize == 1:
				smalls.append( (city.cityXPos,city.cityYPos ) )
			if city.cityXPos + city.cityXSize > sizeX:
				sizeX = city.cityXPos + city.cityXSize
			if city.cityYPos + city.cityYSize > sizeY:
				sizeY = city.cityYPos + city.cityYSize
		if self.originalConfig :	
			sizeX = self.originalConfig.size[0]
			sizeY = self.originalConfig.size[1]
		config = Image.new( "RGB", (sizeX,sizeY) )
		draw = ImageDraw.Draw(config)
		for c in smalls:
			reds = ( "#FF7777", "#FF0000" )
			color = c[0]+c[1]      
			draw.rectangle( [ c, (c[0],c[1])], fill=reds[color%2] )
		for c in mediums:
			colors = ( "#00FF00","#99FF00","#00FF99","#55FF55" )
			color = c[0]+c[1]      
			draw.rectangle( [ c, (c[0]+1,c[1]+1)], fill=colors[color%4] )
		for c in bigs:
			colors = ( "#0000FF","#4000FF","#8000FF","#C000FF","#0040FF","#4040FF","#8040FF","#C040FF",
		  			   "#0080FF","#4080FF","#8080FF","#C080FF","#00C0FF","#40C0FF","#80C0FF","#C0C0FF", )
			color = c[0]+c[1]      
			draw.rectangle( [ c, (c[0]+3,c[1]+3)], fill=colors[color%16] )
		self.missingCities = []
		for y in xrange( sizeY ):
			for x in xrange( sizeX ):
				if self.GetCityUnder( (x,y) ) == None:
					self.missingCities.append( (x,y ) )	
		return config

	def DeleteCityAt( self, pos ):
		"find the city at a certain x,y and remove it"
		for i,city in enumerate( self.allCities ):
			if pos[0] >= city.cityXPos and pos[0] < city.cityXPos+city.cityXSize and pos[1] >= city.cityYPos and pos[1] < city.cityYPos+city.cityYSize :
				self.allCities = self.allCities[:i]+self.allCities[i+1:]
				break

	def GetCityUnder( self, pos ):
		"find the city at a certain x,y"
		for city in ( self.allCities ):
			if pos[0] >= city.cityXPos and pos[0] < city.cityXPos+city.cityXSize and pos[1] >= city.cityYPos and pos[1] < city.cityYPos+city.cityYSize :
				return city
		return None

	def GetCitiesUnder( self, pos, size ):
		"find all cities under rect"
		cities = []
		for city in ( self.allCities ):
			def collide( x1,y1,w1,h1,x2,y2,w2,h2 ):
				return not (x1 >= x2+w2 or x1+w1 <= x2 or y1 >= y2+h2 or y1+h1 <= y2)
			if collide( pos[0],pos[1],size,size, city.cityXPos, city.cityYPos, city.cityXSize, city.cityYSize ):
				cities.append( city )
		return cities

	def IsValid( self ):
		"the region is valid if there is at least one city or the config.bmp is ok"
		return len( self.allCities ) > 0 or self.config != None

	def show( self, dlg, readFiles = False ):
		"compute size/shape and load the heightmap if readFiles is True"
		imgSize = [0,0]
		if self.config:
			imgSize[0] = self.config.size[0]
			imgSize[1] = self.config.size[1]
		for city in self.allCities:
			x = city.cityXPos + city.cityXSize
			y = city.cityYPos + city.cityYSize
			if imgSize[0] < x :
				imgSize[0] = x
			if imgSize[1] < y :
				imgSize[1] = y
		self.imgSize = [ a * 64 + 1 for a in imgSize ]              
		self.shape = [self.imgSize[1],self.imgSize[0]]


