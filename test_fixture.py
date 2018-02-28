# import some module functions
import numpy
import sigint
import sigint.dataseries
import sigint.dataplot
import sigint.specline
import matplotlib.pyplot
import os
import re

class MatedTestFixture:
	# IEEE 802.3 92.11
	def __init__(self, sparam, standard='400GAUI-8', label=''):
		self.__thru = sparam
		self.__NEXT = []
		self.__FEXT = []
		self.standard = standard
		self.label = label
	
	@property
	def label(self):
		return self.__label
	
	@label.setter
	def label(self,label):
		self.__label = label
	
	@property
	def thru(self):
		return self.__thru.copy()
	
	def addNEXT(self, data):
		if isinstance(data, sigint.dataseries.MixedModeSParameters):
			self.__NEXT.append(sigint.dataseries.FrequencyDomainData(data.getSDD(2,1), data.frequency))
		elif isinstance(data, sigint.dataseries.SParameters):
			self.__NEXT.append(sigint.dataseries.FrequencyDomainData(data.getS(2,1), data.frequency))
		elif isinstance(data, sigint.dataseries.FrequencyDomainData):
			self.__NEXT.append(data)
	
	def addFEXT(self, data):
		if isinstance(data, sigint.dataseries.MixedModeSParameters):
			self.__FEXT.append(sigint.dataseries.FrequencyDomainData(data.getSDD(2,1), data.frequency))
		elif isinstance(data, sigint.dataseries.SParameters):
			self.__FEXT.append(sigint.dataseries.FrequencyDomainData(data.getS(2,1), data.frequency))
		elif isinstance(data, sigint.dataseries.FrequencyDomainData):
			self.__FEXT.append(data)
	
	def __calcILD(self): ####
		if self.standard == '100GBASE-CR4':
			f_1 = 0.01e9
			f_2 = 25e9
			self.FOM_ILDmax = 0.13
		elif self.standard == '400GAUI-8':
			f_1 = 0.01e9
			f_2 = 26.5625e9
			self.FOM_ILDmax = 0.1
		f_b = 25.78125e9
		T_t = 9.6e-12
		f_r = 0.75*f_b
		f_t = 0.2365/T_t
		
		fi = numpy.linspace(f_1, f_2, 501)
		IL = -sigint.dB(sigint.fInterpolate(self.thru.SDD[1,0,:], self.thru.frequency, fi))
		F0 = 10**(-IL/20)
		F = F0
		F = numpy.append(F, numpy.sqrt(fi)*F0)
		F = numpy.append(F, fi*F0)
		F = numpy.append(F, fi**2*F0)
		F.shape = (4, len(fi))
		F = F.transpose()
		L = IL*F0
		L.shape = (len(fi), 1)
		a = numpy.matmul(numpy.matmul(numpy.linalg.inv(numpy.matmul(F.transpose(),F)),F.transpose()),L)
		ILfitted = a[0] + a[1]*numpy.sqrt(fi) + a[2]*fi + a[3]*fi**2
		ILfittedMag = 10**(-ILfitted/20)
		ILD = IL - ILfitted
		ILDMag = 10**(-ILD/20)
		W = (numpy.sinc(fi/f_b))**2 * 1/(1+(fi/f_t)**4) * 1/(1+(fi/f_r)**8)
		self.FOM_ILD = numpy.sqrt(1/len(fi) * numpy.sum(W * ILD**2))
		self.ILD = sigint.dataseries.FrequencyDomainData(ILDMag, fi)
		self.ILfitted = sigint.dataseries.FrequencyDomainData(ILfittedMag, fi)

	def __calcXT(self): ####
		if self.standard == '100GBASE-CR4':
			f_1 = 0.05e9
			f_2 = 19e9
			delta_f_max = 10e6
			self.MDFEXTmax = 4.8e-3
			self.MDNEXTmax = 1.8e-3
			self.ICNmax = 5e-3 # ?
			f_b = 25.78125e9
			Ant = 600e-3
			Aft = 600e-3
			Tnt = 9.6e-12
			Tft = 9.6e-12
			fr = 18.75e9
		elif self.standard == '400GAUI-8':
			f_1 = 0.05e9
			f_2 = 19e9
			delta_f_max = 10e6
			self.MDFEXTmax = 4.2e-3
			self.MDNEXTmax = 1.5e-3
			self.ICNmax = 4.4e-3
			f_b = 25.78125e9 
			Ant = 600e-3
			Aft = 600e-3
			Tnt = 9.6e-12
			Tft = 9.6e-12
			fr = 18.75e9
		
		fnt = 0.2365 / Tnt
		fft = 0.2365 / Tft
		
		num_points = numpy.ceil((f_2-f_1)/delta_f_max) + 1
		fi = numpy.linspace(f_1, f_2, num_points)
		delta_f = (f_2 - f_1) / (num_points - 1)
		FEXT = []
		NEXT = []
		for agg in self.__FEXT:
			FEXT.append(sigint.dB(sigint.fInterpolate(agg.data, agg.frequency, fi)))
		for agg in self.__NEXT:
			NEXT.append(sigint.dB(sigint.fInterpolate(agg.data, agg.frequency, fi)))
		
		if len(NEXT) == 0:
			MDNEXTloss = 1e3*numpy.ones(len(fi))
		else:
			MDNEXTlossMag = numpy.zeros(len(fi))
			for agg in NEXT:
				MDNEXTlossMag += 10**(agg/10)
			MDNEXTloss = -10*numpy.log10(MDNEXTlossMag)
		if len(FEXT) == 0:
			MDFEXTloss = 1e3*numpy.ones(len(fi))
		else:
			MDFEXTlossMag = numpy.zeros(len(fi))
			for agg in FEXT:
				MDFEXTlossMag += 10**(agg/10)
			MDFEXTloss = -10*numpy.log10(MDFEXTlossMag)
		self.MDNEXTloss = sigint.dataseries.FrequencyDomainData(MDNEXTloss, fi)
		self.MDFEXTloss = sigint.dataseries.FrequencyDomainData(MDFEXTloss, fi)
		
		Wnt = Ant**2/f_b * (numpy.sinc(fi/f_b))**2 * 1/(1+(fi/fnt)**4) * 1/(1+(fi/fr)**8) # 92-44
		Wft = Aft**2/f_b * (numpy.sinc(fi/f_b))**2 * 1/(1+(fi/fft)**4) * 1/(1+(fi/fr)**8) # 92-45
		
		sigma_nx = numpy.sqrt(2*delta_f * numpy.sum(Wnt*10**(-MDNEXTloss/10))) # 92-46
		sigma_fx = numpy.sqrt(2*delta_f * numpy.sum(Wft*10**(-MDFEXTloss/10))) # 92-47
		sigma_x = numpy.sqrt(sigma_nx**2 + sigma_fx**2) # 92-48
		self.sigma_nx = sigma_nx
		self.sigma_fx = sigma_fx
		self.sigma_x = sigma_x
		
	
	def evaluate(self, eval_xt=False):
		self.__calcILD()
		self.__calcXT()
		
	
	def plotAll(self):
		if self.label:
			title_str = self.label + '\n'
		else:
			title_str = ''
		if not os.path.isdir("output"):
			os.mkdir("output")
		regex = re.compile(r"[:,\n- )(]+")
		ilplot = sigint.dataplot.FrequencyDomainPlot()
		mtfref = sigint.specline.SpecLine(self.standard,'IL_MTFref')
		mtfmax = sigint.specline.SpecLine(self.standard,'IL_MTFmax')
		mtfmin = sigint.specline.SpecLine(self.standard,'IL_MTFmin')
		ilplot.addItem(mtfmin, linestyle='dashed', color='grey', linewidth=1, label=r'$IL_{\mathrm{MTFmin}}$')
		ilplot.addItem(mtfmax, linestyle='dashed', color='grey', linewidth=1, label=r'$IL_{\mathrm{MTFmax}}$')
		ilplot.addItem(mtfref, linestyle='dotted', color='grey', linewidth=1, label=r'$IL_{\mathrm{ref}}$')
		if self.ILfitted:
			ilplot.addItem(self.ILfitted.data, self.ILfitted.frequency, label=r'$IL_{\mathrm{fitted}}$', linestyle=':', linewidth=1, color='green')
		ilplot.addItem(self.thru, 'SDD', (2,1), linewidth=2, label='SDD21')
		ilplot.addItem(self.thru, 'SDD', (1,2), linewidth=2, label='SDD12')
		ilplot.xlim(0,30)
		ilplot.title = title_str + 'Mated Test Fixtures: Insertion Loss 92.11.3.1'
		ilplot.generatePlot()
		matplotlib.pyplot.savefig('output/' + regex.sub('_', ilplot.title) + '.png')
		matplotlib.pyplot.close()
		
		ildplot = sigint.dataplot.FrequencyDomainPlot()
		ildplot.addItem(self.ILD.data, self.ILD.frequency, label='insertion loss deviation')
		ildplot.xlim(0,30)
		ildplot.ylim(-1,1)
		ildplot.title = title_str + 'Mated Test Fixtures: Insertion Loss Deviation 92.11.3.1'
		ildplot.generatePlot()
		matplotlib.pyplot.text(1,-0.75,r"$FOM_{ILD} = $" + "{:0.2f} dB (max {:0.1f} dB)".format(self.FOM_ILD, self.FOM_ILDmax), fontsize=16, bbox = dict(facecolor='white', alpha=0.5))
		matplotlib.pyplot.savefig('output/' + regex.sub('_', ildplot.title) + '.png')
		matplotlib.pyplot.close()
		
		rlplot = sigint.dataplot.FrequencyDomainPlot()
		rldmtf = sigint.specline.SpecLine(self.standard,'RLd_MTF')
		rlplot.addItem(self.thru, 'SDD', (1,1), label='SDD11')
		rlplot.addItem(self.thru, 'SDD', (2,2), label='SDD22')
		rlplot.addItem(rldmtf, linestyle='dashed', color='grey', linewidth=1, label='return loss max')
		rlplot.title = title_str + 'Mated Test Fixtures: Return Loss 92.11.3.2'
		rlplot.xlim(0,30)
		rlplot.ylim(-30,0)
		rlplot.generatePlot()
		matplotlib.pyplot.savefig('output/' + regex.sub('_', rlplot.title) + '.png')
		matplotlib.pyplot.close()
		
		cmcilplot = sigint.dataplot.FrequencyDomainPlot()
		ildcmtf = sigint.specline.SpecLine(self.standard,'ILdc_MTF')
		cmcilplot.addItem(self.thru, 'SDC', (2,1), label='SDC21')
		cmcilplot.addItem(self.thru, 'SDC', (1,2), label='SDC12')
		cmcilplot.addItem(ildcmtf, linestyle='dashed', color='grey', linewidth=1, label='conversion loss max')
		cmcilplot.xlim(0,30)
		cmcilplot.ylim(-40,0)
		cmcilplot.title = title_str + 'Mated Test Fixtures: Common-Mode Conversion Insertion Loss 92.11.3.3'
		cmcilplot.generatePlot()
		matplotlib.pyplot.savefig('output/' + regex.sub('_', cmcilplot.title) + '.png')
		matplotlib.pyplot.close()
		
		cmrlplot = sigint.dataplot.FrequencyDomainPlot()
		rlcmtf = sigint.specline.SpecLine(self.standard,'RLc_MTF')
		cmrlplot.addItem(self.thru, 'SCC', (1,1), label='HCB common-mode return loss')
		cmrlplot.addItem(self.thru, 'SCC', (2,2), label='MCB common-mode return loss')
		cmrlplot.addItem(rlcmtf, linestyle='dashed', color='grey', linewidth=1, label='common-mode return loss max')
		cmrlplot.xlim(0,30)
		cmrlplot.ylim(-15,0)
		cmrlplot.title = title_str + 'Mated Test Fixtures: Common-Mode Return Loss 92.11.3.4'
		cmrlplot.generatePlot()
		matplotlib.pyplot.savefig('output/' + regex.sub('_', cmrlplot.title) + '.png')
		matplotlib.pyplot.close()
		
		cmdmrlplot = sigint.dataplot.FrequencyDomainPlot()
		rldcmtf = sigint.specline.SpecLine(self.standard,'RLdc_MTF')
		cmdmrlplot.addItem(self.thru, 'SCD', (1,1), label='HCB common-mode to differential-mode return loss')
		cmdmrlplot.addItem(self.thru, 'SCD', (2,2), label='MCB common-mode to differential-mode return loss')
		cmdmrlplot.addItem(rldcmtf, linestyle='dashed', color='grey', linewidth=1, label='common-mode to differential-mode return loss max')
		cmdmrlplot.xlim(0,30)
		cmdmrlplot.ylim(-35,-10)
		cmdmrlplot.title = title_str + 'Mated Test Fixtures: Common-Mode to Differential-Mode Return Loss 92.11.3.5'
		cmdmrlplot.generatePlot()
		matplotlib.pyplot.savefig('output/' + regex.sub('_', cmdmrlplot.title) + '.png')
		matplotlib.pyplot.close()
		
		
		mdxtlossplot = sigint.dataplot.FrequencyDomainPlot()
		mdxtlossplot.addItem(10**(-self.MDNEXTloss.data/20), self.MDNEXTloss.frequency, label=r'$MDNEXT_{loss}$')
		mdxtlossplot.addItem(10**(-self.MDFEXTloss.data/20), self.MDFEXTloss.frequency, label=r'$MDFEXT_{loss}$')
		for n, xt in enumerate(self.__FEXT):
			mdxtlossplot.addItem(xt, label='FEXT'+str(n+1))
		for n, xt in enumerate(self.__NEXT):
			mdxtlossplot.addItem(xt, label='NEXT'+str(n+1))
		mdxtlossplot.xlim(0,20)
		mdxtlossplot.ylim(-60,-20)
		mdxtlossplot.title = title_str + 'Mated Test Fixtures: Multiple Disturber Crosstalk Loss 92.11.3.6'
		mdxtlossplot.generatePlot()
		matplotlib.pyplot.text(5,-30,r"$\sigma_{nx} = $" + "{:0.2f} mV (max {:0.1f} mV)".format(self.sigma_nx*1e3, self.MDNEXTmax*1e3) +
			'\n' + r"$\sigma_{fx} = $" + "{:0.2f} mV (max {:0.1f} mV)".format(self.sigma_fx*1e3, self.MDFEXTmax*1e3) +
			'\n' + r"$\sigma_{x} = $" + "{:0.2f} mV (max {:0.1f} mV)".format(self.sigma_x*1e3, self.ICNmax*1e3),
			fontsize=16, bbox = dict(facecolor='white', alpha=0.5))
		matplotlib.pyplot.savefig('output/' + regex.sub('_', mdxtlossplot.title) + '.png')
		matplotlib.pyplot.close()


