# import some module functions
import numpy

class BackplaneEthernetChannel:
	# Annex 69B
	
	# constants
	f_min = 0.05e9
	f_max = 15.00e9
	def __init__(self,standard='10GBASE-KR'):
		self.__thru = {}
		self.__returnLoss = []
		self.__NEXT = []
		self.__FEXT = []
		if standard=='10GBASE-KR':
			self.f_1 = 1.0e9
			self.f_2 = 6.0e9
			self.f_a = 0.1e9
			self.f_b = 5.15625e9
	@property
	def thru(self):
		return self.__thru.copy()
	
	def addThru(self,data,frequency,index=(2,1)):	# with 2 port S params or thru, add RL if available
		if len(data.shape) == 1:
			self.__thru = {'data':data,'frequency':frequency}
		elif len(data.shape) == 3:
			self.__thru = {'data':data[1,0,:],'frequency':frequency}
			self.__returnLoss.append({'data':data[0,0,:],'frequency':frequency})
			self.__returnLoss.append({'data':data[1,1,:],'frequency':frequency})
	
	def addRL(self,data,frequency):	# add RL
		self.__returnLoss.append({'data':data,'frequency':frequency})
	
	def addNEXT(self,data,frequency):
		if len(data.shape) == 1:
			self.__NEXT.append({'data':data,'frequency':frequency})
		elif len(data.shape) == 3:
			self.__NEXT.append({'data':data[1,0,:],'frequency':frequency})
	
	def addFEXT(self,data,frequency):
		if len(data.shape) == 1:
			self.__FEXT.append({'data':data,'frequency':frequency})
		elif len(data.shape) == 3:
			self.__FEXT.append({'data':data[1,0,:],'frequency':frequency})
	
	def __calcILD(self):
		fi = numpy.linspace(self.f_1, self.f_2, 501)
		IL = -dB(fInterpolate(self.__thru['data'], self.__thru['frequency'], fi))
		f_avg = numpy.sum(fi)/len(fi)
		IL_avg = numpy.sum(IL)/len(IL)
		m_A = sum((fi-f_avg)*(IL-IL_avg)) / sum((fi-f_avg)**2)
		b_A = IL_avg - m_A*f_avg
		AdB = -(m_A*self.__thru['frequency'] + b_A)
		self.__thru['A'] = 10**(AdB/20)
		self.__thru['A'][self.__thru['frequency'] < self.f_1] = numpy.nan
		self.__thru['A'][self.__thru['frequency'] > self.f_2] = numpy.nan
		self.__thru['ILD'] = 10**(-(dB(self.thru['data']) - dB(self.thru['A']))/20)
		
	def __calcXT(self):
		# need to interpolate the data if necessary
		# all PS*XT expressed as mag: use dB to represent
		# all quantities
		xtsum = numpy.zeros(len(self.thru['frequency']))
		for xt in self.__NEXT:
			xtsum += 10**(dB(xt['data'])/10)
		self.PSNEXT = 10**(10*numpy.log10(xtsum)/20)
		xtsum = numpy.zeros(len(self.thru['frequency']))
		for xt in self.__FEXT:
			xtsum += 10**(dB(xt['data'])/10)
		self.PSFEXT = 10**(10*numpy.log10(xtsum)/20)
		self.PSXT = 10**(10*numpy.log10(10**(dB(self.PSNEXT)/10) + 10**(dB(self.PSFEXT)/10))/20)
		
	def __calcICR(self):
		ICRdB = dB(self.thru['data']) - dB(self.PSXT)
		fi = numpy.linspace(self.f_a, self.f_b, 501)
		f_avg = numpy.sum(fi)/len(fi)
		#ICRavg = 1/
	# fitted Attenuation
	# IL
	# RL
	# ILD
	# PSNEXT
	# PSFEXT
	# PSXT
	# ICR
	
	def evaluate(self):
		self.__calcILD()
		self.__calcXT()
		self.__calcICR()

def limitMargin(data,limit,dataFormat='dB'):
	"""Evaluates the margin to limit and returns the minimum margin or maximum
	violation and the frequency at which it occurs.
	
	limitMargin(data,limit,dataFormat='dB')
	
	Arguments:
	data -- (data,freq) e.g. (x.getSDD(2,1),x.frequency)
	limit -- SpecLine object
	dataFormat -- how to represent margin (default='dB')
	
	returns tuple of (margin, frequency)
	"""
	freq = data[1]
	
	# interpolate the values
	# truncate data frequency to spec range
	# find difference
	# evaluate margin , frequency (use lowest)
	#