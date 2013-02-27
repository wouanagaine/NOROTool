import urllib2
import time
import math

class FileDownloader:
	def __init__( self, url, fileName ):
		self.url = url
		self.fileName = fileName

	def Download(self, retries, reportingHandler ):
		request = urllib2.Request( self.url, None, {} )
		stream = None
		count = 0
		while count <= retries:
			# Establish connection
			try:
				data = urllib2.urlopen(request)
				break
			except (urllib2.HTTPError, ), err:
				raise
			# Retry
			count += 1
		if count > retries:
			reportingHandler.trouble(u'ERROR: giving up after %s retries' % retries)
			return False
		data_len = data.info().get('Content-length', None)
		if data_len is not None:
			data_len = long(data_len)
		byte_counter = 0 
		block_size = 1024
		start = time.time()
		while True:
			# Download and write
			before = time.time()
			data_block = data.read(block_size)
			after = time.time()
			if len(data_block) == 0:
				break
			byte_counter += len(data_block)
			# Open file just in time
			if stream is None:
				try:
					stream = open( self.fileName, "wb" )
				except (OSError, IOError), err:
					reportingHandler.trouble(u'ERROR: unable to open %s for writing: %s' %( self.fileName, str(err) ) )
					return False
			try:
				stream.write(data_block)
			except (IOError, OSError), err:
				reportingHandler.trouble(u'\nERROR: unable to write data: %s' % str(err))
				return False
			block_size = self.best_block_size(after - before, len(data_block))
			reportingHandler.progress( data_len, byte_counter, block_size, start, after )
		if stream is None:
			reportingHandler.trouble(u'\nERROR: Did not get any data blocks')
			return False
		stream.close()
		return True


	@staticmethod
	def best_block_size(elapsed_time, bytes):
		new_min = max(bytes / 2.0, 1.0)
		new_max = min(max(bytes * 2.0, 1.0), 4194304) # Do not surpass 4 MB
		if elapsed_time < 0.001:
			return long(new_max)
		rate = bytes / elapsed_time
		if rate > new_max:
			return long(new_max)
		if rate < new_min:
			return long(new_min)
		return long(rate)

class DlgStub:
	def trouble(self, message):
		print message
	def progress(self, totalLen, current, speed, startTime, now ):
		print '[download]', self.calc_percent( current, totalLen ), self.format_bytes( current ), 'out of', self.format_bytes( totalLen ), 'at', self.calc_speed( startTime, now, current )

	@staticmethod
	def calc_percent(byte_counter, data_len):
		if data_len is None:
			return '---.-%'
		return '%6s' % ('%3.1f%%' % (float(byte_counter) / float(data_len) * 100.0))

	@staticmethod
	def calc_speed(start, now, bytes):
		dif = now - start
		if bytes == 0 or dif < 0.001: # One millisecond
			return '%10s' % '---b/s'
		return '%10s' % ('%s/s' % Dlg.format_bytes(float(bytes) / dif))

	@staticmethod
	def format_bytes(bytes):
		if bytes is None:
			return 'N/A'
		if type(bytes) is str:
			bytes = float(bytes)
		if bytes == 0.0:
			exponent = 0
		else:
			exponent = long(math.log(bytes, 1024.0))
		suffix = 'bkMGTPEZY'[exponent]
		converted = float(bytes) / float(1024 ** exponent)
		return '%.2f%s' % (converted, suffix)


if 0:
	fd = FileDownloader( "http://www.fileden.com/files/2006/7/28/145206/MULC%20Estate%20Living%20Models.zip", "models.zip" )
	dlg = DlgStub()
	fd.Download( 5, dlg )