# import some module functions
import numpy
import copy
import re
import matplotlib.pyplot
import sigint

class FrequencyDomainData:
	def __init__(self, data=None, frequency=None, label=None):
		if data is not None:
			self.__data = numpy.array(data) # data is array
		else:
			self.__data = None
		self.__frequency = frequency
		self.label = label
	
	# setters and getters
	@property
	def label(self):
		return self.__label
	
	@label.setter
	def label(self,label):
		self.__label = label
	
	@property
	def frequency(self):
		return self.__frequency.copy()
	
	@frequency.setter
	def frequency(self, frequency):
		if self.__frequency is not None:
			print("Warning: overwriting frequency!")
			# interpolate frequency
			self.__frequency = frequency
		else:
			self.__frequency = frequency
	
	@property
	def data(self):
		return self.__data.copy()
	
	def copy(self):
		return copy.deepcopy(self)
	
	def exportCSV(self, item='data', index=(), format='dB', output='', header=True, frequency=True):
		# try:
			if len(index) == 2:
				data = eval('self.' + item)[index[0], index[1]]
				if not output:
					regex = re.compile(r"[:,\n- )(]+")
					output = '_'.join([self.label, item, str(index[0]), str(index[1]), format])
					output = regex.sub('_', output) + '.csv'
				else:
					output += '.csv'
				outfile = open(output, 'w')
				if header:
					if frequency:
						outfile.write('frequency,')
					outfile.write('_'.join([item, str(index[0]), str(index[1]), format]) + '\n')
				numPoints = len(data)
				for ind in range(numPoints):
					if frequency:
						outfile.write(str(self.frequency[ind]) + ',')
					outfile.write(str(sigint.dB(data[ind])) + '\n')
				outfile.close()
			elif len(index) == 1:
				pass
			else:
				pass
		# except:
			# print("CSV output error")

	
		# def resampleFrequency(self,newFrequency):
		# newData = numpy.zeros((self.numPorts,self.numPorts,len(newFrequency)),dtype=complex)
		# for n in range(self.numPorts):
			# for m in range(self.numPorts):
				# newS[n,m,:] = sigint.fInterpolate(self.S[n,m,:],self.frequency,newFrequency)
		# self.__S = newS
		# self.__frequency = newFrequency
	

class SParameters(FrequencyDomainData):
	def __init__(self, data, label=None):
		# data: touchstone file
		# data: SParameter object
		# data: dict with 'S', 'frequency' (,'portZ', 'label')
		FrequencyDomainData.__init__(self, label=label)
		if isinstance(data,SParameters):
			self.__S = data.S
			self.__frequency = data.frequency
			self.__numPorts = data.numPorts
			self.__portZ = data.portZ
			self.__dataFile = data.dataFile
			if not label:
				self.label = data.label
		else:
			try: # data is touchstone file
				self.__dataFile = data
				self.__getSnp()
				# generate default label from filename
				pattern0 = re.compile('^.*/')
				pattern1 = re.compile('[.]s[0-9]*p')
				if not label:
					self.label  = pattern1.sub('',pattern0.sub('',self.dataFile))
			except: 
				try: # data is dict
					self.__S = data['S']
					self.__frequency = data['frequency']
					try:
						self.__numPorts = data['numPorts']
					except KeyError:
						self.__numPorts = self.S.shape[1]
					try:
						self.__portZ = data['portZ']
					except KeyError:
						self.__portZ = 50.
					try:
						self.__dataFile = data['dataFile']
					except KeyError:
						self.__dataFile = ''
					try:
						self.label = data['label']
					except KeyError:
						# generate default label from filename
						pattern0 = re.compile('^.*/')
						pattern1 = re.compile('[.]s[0-9]*p')
						if not label:
							self.label  = pattern1.sub('',pattern0.sub('',self.dataFile))
				except:
					print("No such file or data: {0}".format(data))
					raise 
			
	def __str__(self):
		return ("### SParameter object ###\n" +
				"Label:           " + self.label + "\n" +
				"Datafile:        " + self.dataFile + "\n" +
				"Number of ports: " + str(self.numPorts) + "\n" +
				"Port impedance:  " + str(self.portZ) + " Ohms\n" +
				"Frequency start: " + str(self.frequency[0]*1e-9) + " GHz\n" +
				"Frequency stop:  " + str(self.frequency[-1]*1e-9) + " GHz\n" +
				"Frequency steps: " + str(len(self.frequency)))
	
	# setters and getters
	@property
	def S(self):
		"""S-Parameters:
		S(row,col,freq)	- ndarray
			row:	destination port, index from 0
			col:	source port, index from 0
			freq:	frequency index, index from 0
		"""
		return self.__S.copy()
	
	def getS(self,in1=(1,1),in2=None,frequency=None):
		"""getS(index) for index=(n,m) indexed from 1,
		returns Snm as a vector over the frequency index
		Usage:
			getS(n,m[,frequency])  indices as separate args with optional frequency
			getS((n,m)[,frequency]) indices as a tuple with optional frequency
			frequency can be specified as a single value or list of values
		"""
		try:
			n = in1[0]-1
			m = in1[1]-1
			if frequency == None:
				frequency = in2
		except TypeError:
			n = in1 - 1
			m = in2 - 1

		data = self.S[n,m,:]
		freq = self.frequency

		if numpy.max(frequency)==None:
			return data
		else:
			freqreq = numpy.array(frequency) # requested frequencies
			if numpy.max(freqreq) <= numpy.max(freq) and numpy.min(freqreq) >= numpy.min(freq):
				if freqreq in freq: # 
					return data[freq==freqreq]
				else: # interpolate the values
					return sigint.fInterpolate(data,freq,freqreq)
			else:
				print("Frequency out of range")
	@property
	def Z(self):
		"""Z-Parameters:
		Z(row,col,freq)	- ndarray
			row:	destination port, index from 0
			col:	source port, index from 0
			freq:	frequency index, index from 0
		"""
		try:
			return self.__Z.copy()
		except:
			self.__s2z()
			return self.__Z.copy()
	
	def getZ(self,in1=(1,1),in2=None,frequency=None):
		"""getZ(index) for index=(n,m) indexed from 1,
		returns Znm as a vector over the frequency index
		Usage:
			getZ(n,m[,frequency])  indices as separate args with optional frequency
			getZ((n,m)[,frequency]) indices as a tuple with optional frequency
			frequency can be specified as a single value or list of values
		"""
		try:
			n = in1[0]-1
			m = in1[1]-1
			if frequency == None:
				frequency = in2
		except TypeError:
			n = in1 - 1
			m = in2 - 1

		data = self.Z[n,m,:]
		freq = self.frequency

		if numpy.max(frequency)==None:
			return data
		else:
			freqreq = numpy.array(frequency) # requested frequencies
			if numpy.max(freqreq) <= numpy.max(freq) and numpy.min(freqreq) >= numpy.min(freq):
				if freqreq in freq: # 
					return data[freq==freqreq]
				else: # interpolate the values
					return sigint.fInterpolate(data,freq,freqreq)
			else:
				print("Frequency out of range")

	@property
	def numPorts(self):
		return self.__numPorts
	
	@property
	def portZ(self):
		return self.__portZ
	
	@property
	def dataFile(self):
		return self.__dataFile
	
	# more functions
	def plotAll(self,matrix='S'):
		matplotlib.pyplot.figure(figsize=(12,10))
		N = getattr(self,matrix).shape[0]
		for n in range(N):
			for m in range(N):
				matplotlib.pyplot.subplot(N,N,(n)*N+m+1)
				matplotlib.pyplot.plot(self.frequency*1e-9,sigint.dB(getattr(self,matrix)[n,m,:]))
				matplotlib.pyplot.xlabel('GHz')
				matplotlib.pyplot.ylabel('dB')
				matplotlib.pyplot.title(matrix+'('+str(n+1)+','+str(m+1)+')')
				matplotlib.pyplot.grid(True)
		matplotlib.pyplot.tight_layout(pad=1.0, w_pad=1.0, h_pad=1.0)
		
	def reorderPorts(self,portOrder):
		"""portOrder is iterable of port indices indexed from 1"""
		####### check input
		portOrder = numpy.array(portOrder)-1
		self.__S = self.S[portOrder,:,:][:,portOrder,:]
		# set numPorts
		self.__numPorts = len(portOrder)
	
	def resampleFrequency(self,newFrequency):
		newS = numpy.zeros((self.numPorts,self.numPorts,len(newFrequency)),dtype=complex)
		for n in range(self.numPorts):
			for m in range(self.numPorts):
				newS[n,m,:] = sigint.fInterpolate(self.S[n,m,:],self.frequency,newFrequency)
		self.__S = newS
		self.__frequency = newFrequency
	
	def __getSnp(self):
		# local functions
		def getNextLine(fileID):
			while True:
				# read line with \n
				line = fileID.readline()
				# check if it is EOF, ''
				if line=='':
					return -1
				elif not(isComment(line)):
					# remove inline comments
					line = re.sub(r'!.*$','',line)
					# line without trailing whitespace and newline
					return line.rstrip()

		def isComment(line):
			# remove whitespace
			line = re.sub(r'\s+','',line)
			if not(bool(line)):
				return True
			elif line[0]=='!':
				return True
			else:
				return False

		print("Importing "+self.dataFile)
		# open file for read
		fileID = open(self.dataFile,'r')
		# read file
		# read header: # frequencyUnit networkFormat complexFormat R portZ (complex impedance terms not allowed)
		nextLine = getNextLine(fileID) # header line ### error check
		header = nextLine.split()
		frequencyUnit = header[1].upper()
		networkFormat = header[2].upper()
		complexFormat = header[3].upper()
		self.__portZ = float(header[5])
		#### check for errors in header line
		# read data
		# read all remaining lines
		lines = []
		nextLine = getNextLine(fileID)
		while nextLine != -1:
			lines.append(nextLine)
			nextLine = getNextLine(fileID)
		# close file
		fileID.close()
		# find how many lines per frequency point
		numLinesPerFrequencyPoint = 1
		numComplexValuesPerFrequencyPoint = 0
		if len(lines[0].split())%2 == 0:
			raise touchstoneFormatError # should be odd with freq value included with complex data
		numComplexValuesPerFrequencyPoint += (len(lines[0].split()) - 1)/2
		while len(lines[numLinesPerFrequencyPoint].split())%2 == 0:
			numLinesPerFrequencyPoint += 1
			numComplexValuesPerFrequencyPoint += len(lines[numLinesPerFrequencyPoint].split())/2
		# check that there are an expected number of total lines, i.e. numLinesPerFrequencyPoint * number of frequency points
		if len(lines)%numLinesPerFrequencyPoint != 0:
			raise touchstoneFormatError # some extra junk at end
		numFrequencyPoints = len(lines)//numLinesPerFrequencyPoint
		self.__numPorts = int(numpy.sqrt(numComplexValuesPerFrequencyPoint)) ### error check this
		# read and create data matrices
		frequency = numpy.zeros(numFrequencyPoints)
		networkData1 = numpy.zeros((self.numPorts,self.numPorts,numFrequencyPoints))
		networkData2 = numpy.zeros((self.numPorts,self.numPorts,numFrequencyPoints))
		for nf in range(numFrequencyPoints):
			frequency[nf] = float(lines[nf*numLinesPerFrequencyPoint].split()[0])
			dataItems = lines[nf*numLinesPerFrequencyPoint].split()[1:]
			for nlpfp in range(1,numLinesPerFrequencyPoint):
				dataItems.extend(lines[nf*numLinesPerFrequencyPoint+nlpfp].split())
			for n in range(self.numPorts): # row
				for m in range(self.numPorts): # column
					networkData1[n,m,nf] = float(dataItems[(n*self.numPorts+m)*2])
					networkData2[n,m,nf] = float(dataItems[(n*self.numPorts+m)*2+1])
		# scale frequency values to Hz
		if frequencyUnit == 'HZ':
			frequencyFactor = 1e0
		elif frequencyUnit == 'KHZ':
			frequencyFactor = 1e3
		elif frequencyUnit == 'MHZ':
			frequencyFactor = 1e6
		elif frequencyUnit == 'GHZ':
			frequencyFactor = 1e9
		self.frequency = frequencyFactor*frequency
		# generate complex valued data from input data format
		self.__S = numpy.zeros((self.numPorts,self.numPorts,numFrequencyPoints),dtype=complex)
		if complexFormat == 'RI':
			self.__S = networkData1 + networkData2*1j
		elif complexFormat == 'MA':
			self.__S = networkData1 * numpy.exp(1j*2*numpy.pi/360.0*networkData2)
		elif complexFormat == 'DB':
			self.__S = 10**(networkData1/20.0) * numpy.exp(1j*2*numpy.pi/360.0*networkData2)
	
	def export(self, dataFile='export', dataFormat='RI', numDigits=12, format='touchstone', frequencyFormat='GHZ'):
		regexp0 = re.compile(r"\.s[0-9]*p$")
		dataFile = regexp0.sub("",dataFile)
		dataFile = "{0}.s{1}p".format(dataFile,self.numPorts)
		
		print("Exporting " + dataFile)
		
		dataFormat = dataFormat.upper()
		if dataFormat == 'RI':
			data1 = numpy.real(self.S)
			data2 = numpy.imag(self.S)
		elif dataFormat == 'MA':
			data1 = numpy.abs(self.S)
			data2 = numpy.angle(self.S)
		elif dataFormat == 'DB':
			data1 = sigint.dB(self.S)
			data2 = numpy.angle(self.S)
		else:
			dataFormat = 'RI'
			data1 = numpy.real(self.S)
			data2 = numpy.imag(self.S)
			
		freq = self.frequency*1e-9
		fid = open(dataFile,'w')
		regexp1 = re.compile(r"\n") # add ! comment character to lines
		fid.write("! Touchstone data exported from sptools\n! " +
			regexp1.sub("\n! ",str(self)) )
		fid.write("\n# GHZ S {0} R {1}".format(dataFormat,self.portZ))
		for frequencyIndex in range(len(freq)):
			fid.write("\n{0:0.5f}\t".format(freq[frequencyIndex]))
			for n in range(self.numPorts):
				for m in range(self.numPorts):
					if (n*self.numPorts + m) != 0 and (n*self.numPorts + m) % 4 == 0:
						fid.write("\n\t\t")
					fid.write("{0:0.14g} {1:0.14g} ".format(data1[n,m,frequencyIndex],data2[n,m,frequencyIndex]))
		fid.write("\n")
		fid.close()
		
	def __s2z(self):
		if self.numPorts == 2:
			S11 = self.getS(1,1)
			S12 = self.getS(1,2)
			S21 = self.getS(2,1)
			S22 = self.getS(2,2)
			denom = (1-S11)*(1-S22) - S12*S21
			self.__Z = self.portZ * numpy.array([ 
				[ ((1+S11)*(1-S22)+S12*S21)/denom, 2*S21/denom ],
				[ 2*S21/denom, ((1-S11)*(1+S22) + S12*S21)/denom]
				])
		else:
			raise NumPortsError("Z matrix only implemented for 2-port networks")
				
	def cascade(self, other):
		"""Cascades the SParameters object with another SParameters object.
		Assumes port1-->port2, port3-->port4, etc.
		Returns the cascaded SParameters in a new SParameters object.
		"""
		pass
		
	def multiply(self, n):
		"""Cascades the SParameters object with itself n times.
		Assumes port1-->port2, port3-->port4, etc.
		Returns the cascaded SParameters in a new SParameters object.
		"""
		pass

class MixedModeSParameters(SParameters):
	def __init__(self, data, label=None):
		SParameters.__init__(self, data, label=label)
		self.__genSMM()
	
	def __str__(self):
		return ("### MixedModeSParameter object ###\n" +
				"Label:           " + self.label + "\n" +
				"Datafile:        " + self.dataFile + "\n" +
				"Number of ports: " + str(self.numPorts) + "\n" +
				"Port impedance:  " + str(self.portZ) + " Ohms\n" +
				"Frequency start: " + str(self.frequency[0]*1e-9) + " GHz\n" +
				"Frequency stop:  " + str(self.frequency[-1]*1e-9) + " GHz\n" +
				"Frequency steps: " + str(len(self.frequency)))
	
	# setters and getters
	@property
	def SMM(self):
		return self.__SMM.copy()
	
	def getSMM(self,in1=(1,1),in2=None,frequency=None):
		"""getSMM(index) for index=(n,m) indexed from 1,
		returns SMMnm as a vector over the frequency index
		Usage:
			getSMM(n,m[,frequency])  indices as separate args with optional frequency
			getSMM((n,m)[,frequency]) indices as a tuple with optional frequency
			frequency can be specified as a single value or list of values
		"""
		try:
			n = in1[0]-1
			m = in1[1]-1
			if frequency == None:
				frequency = in2
		except TypeError:
			n = in1 - 1
			m = in2 - 1

		data = self.SMM[n,m,:]
		freq = self.frequency

		if numpy.max(frequency)==None:
			return data
		else:
			freqreq = numpy.array(frequency) # requested frequencies
			if numpy.max(freqreq) <= numpy.max(freq) and numpy.min(freqreq) >= numpy.min(freq):
				if freqreq in freq: # 
					return data[freq==freqreq]
				else: # interpolate the values
					return sigint.fInterpolate(data,freq,freqreq)
			else:
				print("Frequency out of range")

	@property
	def SDD(self):
		return self.SMM[0::2,0::2]
	
	def getSDD(self,in1=(1,1),in2=None,frequency=None):
		"""getSDD(index) for index=(n,m) indexed from 1,
		returns SDDnm as a vector over the frequency index
		Usage:
			getSDD(n,m[,frequency])  indices as separate args with optional frequency
			getSDD((n,m)[,frequency]) indices as a tuple with optional frequency
			frequency can be specified as a single value or list of values
		"""
		try:
			n = in1[0]-1
			m = in1[1]-1
			if frequency == None:
				frequency = in2
		except TypeError:
			n = in1 - 1
			m = in2 - 1

		data = self.SDD[n,m,:]
		freq = self.frequency

		if numpy.max(frequency)==None:
			return data
		else:
			freqreq = numpy.array(frequency) # requested frequencies
			if numpy.max(freqreq) <= numpy.max(freq) and numpy.min(freqreq) >= numpy.min(freq):
				if freqreq in freq: # 
					return data[freq==freqreq]
				else: # interpolate the values
					return sigint.fInterpolate(data,freq,freqreq)
			else:
				print("Frequency out of range")

	@property
	def SDC(self):
		return self.SMM[0::2,1::2]
	
	def getSDC(self,in1=(1,1),in2=None,frequency=None):
		"""getSDC(index) for index=(n,m) indexed from 1,
		returns SDCnm as a vector over the frequency index
		Usage:
			getSDC(n,m[,frequency])  indices as separate args with optional frequency
			getSDC((n,m)[,frequency]) indices as a tuple with optional frequency
			frequency can be specified as a single value or list of values
		"""
		try:
			n = in1[0]-1
			m = in1[1]-1
			if frequency == None:
				frequency = in2
		except TypeError:
			n = in1 - 1
			m = in2 - 1

		data = self.SDC[n,m,:]
		freq = self.frequency

		if numpy.max(frequency)==None:
			return data
		else:
			freqreq = numpy.array(frequency) # requested frequencies
			if numpy.max(freqreq) <= numpy.max(freq) and numpy.min(freqreq) >= numpy.min(freq):
				if freqreq in freq: # 
					return data[freq==freqreq]
				else: # interpolate the values
					return sigint.fInterpolate(data,freq,freqreq)
			else:
				print("Frequency out of range")

	@property
	def SCD(self):
		return self.SMM[1::2,0::2]
	
	def getSCD(self,in1=(1,1),in2=None,frequency=None):
		"""getSCD(index) for index=(n,m) indexed from 1,
		returns SCDnm as a vector over the frequency index
		Usage:
			getSCD(n,m[,frequency])  indices as separate args with optional frequency
			getSCD((n,m)[,frequency]) indices as a tuple with optional frequency
			frequency can be specified as a single value or list of values
		"""
		try:
			n = in1[0]-1
			m = in1[1]-1
			if frequency == None:
				frequency = in2
		except TypeError:
			n = in1 - 1
			m = in2 - 1

		data = self.SCD[n,m,:]
		freq = self.frequency

		if numpy.max(frequency)==None:
			return data
		else:
			freqreq = numpy.array(frequency) # requested frequencies
			if numpy.max(freqreq) <= numpy.max(freq) and numpy.min(freqreq) >= numpy.min(freq):
				if freqreq in freq: # 
					return data[freq==freqreq]
				else: # interpolate the values
					return sigint.fInterpolate(data,freq,freqreq)
			else:
				print("Frequency out of range")

	@property
	def SCC(self):
		return self.SMM[1::2,1::2]
	
	def getSCC(self,in1=(1,1),in2=None,frequency=None):
		"""getSCC(index) for index=(n,m) indexed from 1,
		returns SCCnm as a vector over the frequency index
		Usage:
			getSCC(n,m[,frequency])  indices as separate args with optional frequency
			getSCC((n,m)[,frequency]) indices as a tuple with optional frequency
			frequency can be specified as a single value or list of values
		"""
		try:
			n = in1[0]-1
			m = in1[1]-1
			if frequency == None:
				frequency = in2
		except TypeError:
			n = in1 - 1
			m = in2 - 1

		data = self.SCC[n,m,:]
		freq = self.frequency

		if numpy.max(frequency)==None:
			return data
		else:
			freqreq = numpy.array(frequency) # requested frequencies
			if numpy.max(freqreq) <= numpy.max(freq) and numpy.min(freqreq) >= numpy.min(freq):
				if freqreq in freq: # 
					return data[freq==freqreq]
				else: # interpolate the values
					return sigint.fInterpolate(data,freq,freqreq)
			else:
				print("Frequency out of range")

	# other functions
	def copy(self):
		return copy.deepcopy(self)

	def __genSMM(self):
		if numpy.size(self.S,0)%2 != 0:
			raise MixedModeOddNumberOfPorts
		numPorts = numpy.size(self.S,0)//2 # mixed mode ports
		# construct transformation matrix
		if numPorts == 1: # add case for single mm port
			M = numpy.array([[1,-1],[1,1]])/numpy.sqrt(2)
		else:
			M0 = numpy.array([[1,0,-1],[1,0,1]])/numpy.sqrt(2)
			M = numpy.zeros((2*numPorts,2*numPorts))
			for n in range(0,numPorts,2):
				M[  2*n:2*n+2 ,   2*n:2*n+3] = M0
				M[2*n+2:2*n+4 , 2*n+1:2*n+4] = M0
		Mi = numpy.linalg.inv(M)
		self.__SMM = numpy.zeros_like(self.S)
		for n in range(numpy.size(self.S,2)):
			self.__SMM[:,:,n] = numpy.dot( M, numpy.dot(self.S[:,:,n],Mi) ) # M*S*Mi
	
	def reorderPorts(self,portOrder):
		SParameters.reorderPorts(self,portOrder)
		self.__genSMM()
	
	def resampleFrequency(self,newFrequency):
		SParameters.resampleFrequency(self,newFrequency)
		self.__genSMM()


def calculateLoss(data):
	(numPorts,_,numFrequencyPoints)=data.shape
	loss = numpy.ones((numPorts,numFrequencyPoints))
	power = numpy.zeros((numPorts,numFrequencyPoints))
	for m in range(numPorts):
		for n in range(numPorts):
			loss[m,:] -= numpy.abs(data[n,m,:])**2
			power[m,:] += numpy.abs(data[n,m,:])**2
	return numpy.sqrt(power)
