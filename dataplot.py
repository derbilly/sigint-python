# import some module functions
import numpy
import matplotlib.pyplot
import sigint.dataseries
import sigint.specline

class DataPlot:
	def __init__(self):
		pass
		
	def xlim(self,low=None,high=None):
		self._xlimits = (low,high)
	
	def ylim(self,low=None,high=None):
		self._ylimits = (low,high)

class FrequencyDomainPlot(DataPlot):
	# data format: dB, magnitude, phase, degrees
	# xlimits
	# ylimits reset for change type
	# title
	# list of data items, line formats and legend labels
	def __init__(self,dataFormat='dB',title=''):
		DataPlot.__init__(self)
		self.dataFormat = dataFormat
		self.title = title
		self._dataList = []
		self._frequencyList = []
		self.labelList = []
		self.plotKwargs = []
		
	def addItem(self,data,arg2='S',arg3=(1,1),label=None, **kwargs):
		# (dataObj, dataItem, index)
		# (data, frequency, label)
		# interpret input arguments
		if isinstance(data,sigint.dataseries.FrequencyDomainData):
			if isinstance(data,sigint.dataseries.SParameters):
				self._dataList.append(eval("data."+arg2)[arg3[0]-1,arg3[1]-1,:])
				self._frequencyList.append(data.frequency)
				if label:
					self.labelList.append(label)
				else:
					self.labelList.append(data.label + " " + arg2 + str(arg3))
				self.plotKwargs.append(kwargs)
			elif isinstance(data,sigint.specline.SpecLine):
				self._dataList.append(data.specLine)
				self._frequencyList.append(data.frequency)
				if label:
					self.labelList.append(label)
				else:
					self.labelList.append(data.standard + " " + data.specItem)
				self.plotKwargs.append(kwargs)
			else:
				self._dataList.append(data.data)
				self._frequencyList.append(data.frequency)
				if label:
					self.labelList.append(label)
				else:
					self.labelList.append(' ')
				self.plotKwargs.append(kwargs)
		elif type(data) == numpy.ndarray:
			self._dataList.append(data)
			self._frequencyList.append(arg2)
			if label:
				self.labelList.append(label)
			else:
				self.labelList.append(arg3)
			self.plotKwargs.append(kwargs)

	def generatePlot(self, legend_loc = 0, plot_size=(10,7.5)):
		matplotlib.pyplot.figure(figsize=plot_size)
		matplotlib.pyplot.hold(True)
		try:
			xlimits = self._xlimits
			if xlimits[0] == None:
				xlow = 0.
			else:
				xlow = xlimits[0]*1e9
			if xlimits[1] == None:
				xhigh = 1000e9
			else:
				xhigh = self._xlimits[1]*1e9
		except AttributeError:
			xlow = 0.
			xhigh = 1000e9
		for n in range(len(self._dataList)):
			if self.dataFormat == 'dB':
				matplotlib.pyplot.plot(self._frequencyList[n][numpy.logical_and(self._frequencyList[n]>=xlow, self._frequencyList[n]<=xhigh)]*1e-9,
					20*numpy.log10(numpy.abs((self._dataList[n][numpy.logical_and(self._frequencyList[n]>=xlow, self._frequencyList[n]<=xhigh)]))),
					**self.plotKwargs[n])
			elif self.dataFormat == 'radians':
				matplotlib.pyplot.plot(self._frequencyList[n][numpy.logical_and(self._frequencyList[n]>=xlow, self._frequencyList[n]<=xhigh)]*1e-9,
					numpy.angle(self._dataList[n][numpy.logical_and(self._frequencyList[n]>=xlow, self._frequencyList[n]<=xhigh)]),
					**self.plotKwargs[n])
			elif self.dataFormat == 'degrees':
				matplotlib.pyplot.plot(self._frequencyList[n][numpy.logical_and(self._frequencyList[n]>=xlow, self._frequencyList[n]<=xhigh)]*1e-9,
					180/numpy.pi*numpy.angle(self._dataList[n][numpy.logical_and(self._frequencyList[n]>=xlow, self._frequencyList[n]<=xhigh)]),
					**self.plotKwargs[n])
			elif self.dataFormat == 'unwrapped':
				matplotlib.pyplot.plot(self._frequencyList[n][numpy.logical_and(self._frequencyList[n]>=xlow, self._frequencyList[n]<=xhigh)]*1e-9,
					180/numpy.pi*numpy.unwrap(numpy.angle(self._dataList[n][numpy.logical_and(self._frequencyList[n]>=xlow, self._frequencyList[n]<=xhigh)])),
					**self.plotKwargs[n])
			elif self.dataFormat == 'magnitude':
				matplotlib.pyplot.plot(self._frequencyList[n][numpy.logical_and(self._frequencyList[n]>=xlow, self._frequencyList[n]<=xhigh)]*1e-9,
					numpy.abs(self._dataList[n][numpy.logical_and(self._frequencyList[n]>=xlow, self._frequencyList[n]<=xhigh)]),
					**self.plotKwargs[n])
		matplotlib.pyplot.hold(False)
		try:
			matplotlib.pyplot.xlim(self._xlimits)
		except (ValueError, AttributeError): 
			pass
		try:
			matplotlib.pyplot.ylim(self._ylimits)
		except (ValueError, AttributeError): 
			pass
		matplotlib.pyplot.xlabel('GHz')
		matplotlib.pyplot.ylabel(self.dataFormat)
		matplotlib.pyplot.title(self.title)
		legnd = matplotlib.pyplot.legend(self.labelList,fontsize='small', loc=legend_loc)
		if legnd:
			legnd.draggable()
		matplotlib.pyplot.grid(True)
