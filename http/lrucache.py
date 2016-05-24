import collections
import os

#Main class implementing the LRU cache logic on the HTTP replica
class LRUCache:
	def __init__(self, max_capacity):
		self.max_capacity = max_capacity
		self.size = 0
		self.cache = collections.OrderedDict()

	#Add the file to the LRUcache
	def add_file_to_cache(self, filepath, filesize):
		# remove the first (least-used) file from the cache
		print "-----------ADDING TO CACHE-----------"
		while(self.size + filesize >= self.max_capacity):
			# consider the map as FIFO and remove the first element that was inserted
			poppedfile, poppedsize = self.cache.popitem(last=False)
			# remove file from the system
			os.remove(poppedfile)
			# reduce the size of the cache
			self.size = self.size - poppedsize
		# add file to cache and update the size of the cache
		self.size += filesize
		self.cache.update({filepath:filesize})
		print self.cache
		print "-----------FINISHED ADDING TO CACHE-----------"

	#Method to Update the cache 
	def update_cache(self, filename):
		# Remove the file from the middle of the list and put it 
		# in the end since it is most recently used
		print "-----------UPDATING CACHE-----------"
		filesize = self.cache[filename]
		del self.cache[filename]
		self.cache.update({filename:filesize})
		print self.cache
		print "-----------FINISHED UPDATING CACHE-----------"

	#Create a new cache directory if it does'nt exists
	def create_cache_directory(self, cachedir):
		if not os.path.exists(cachedir):
			os.makedirs(cachedir)

	#Read the file from the cache directory
	def read_files_from_cache(self, cachedir):
		files = os.listdir(cachedir)
		# print files
		for f in files:
			filepath = os.path.join(os.getcwd(),cachedir,f)
			filesize = os.stat(filepath).st_size
			self.cache.update({f:filesize})
			self.size += filesize
