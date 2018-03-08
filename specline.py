# import some module functions
import sigint.dataseries
import sigint.genspecline
import numpy

def evaluateLimitLine(fddata, standard, specItem, format='dB'):
	limitLine = SpecLine(standard, specItem)
	# combine frequencies and interpolate between limits of limit line
	f0 = min(limitLine.frequency)
	f1 = max(limitLine.frequency)
	freq = fddata.frequency
	freq = numpy.append(freq, limitLine.frequency)
	freq = freq[freq>=f0]
	freq = freq[freq<=f1]
	freq = numpy.sort(numpy.unique(freq))
	data = sigint.fInterpolate(fddata.data, fddata.frequency, freq)
	limit = sigint.fInterpolate(limitLine.specLine, limitLine.frequency, freq)
	# format db
	if format=='dB':
		data = sigint.dB(data)
		limit = sigint.dB(limit)
	# margin = 
	# max limit - data
	# min data - limit
	# ref abs(data-limit)
	if limitLine.limitType == 'max':
		margin = limit - data
	elif limitLine.limitType == 'min':
		margin = data - limit
	elif limitLine.limitType == 'ref':
		margin = numpy.abs(data - limit)
	else:
		margin = numpy.zeros(len(data))
	# find min margin and freq
	worstcase = min(margin)
	worstcase_freq = freq[margin==worstcase][0]
	# return margin, wc and freq
	return (sigint.dataseries.FrequencyDomainData(margin,freq,label='margin'), worstcase, worstcase_freq)

class SpecLine(sigint.dataseries.FrequencyDomainData):
	def __init__(self,standard,specItem):
		sigint.dataseries.FrequencyDomainData.__init__(self)
		self.specItem = specItem
		self.standard = standard
		try:
			self.generatorMethod[standard][specItem](self)
		except KeyError:
			try:
				subdict = self.generatorMethod[standard]
				print("Spec item: '" + self.specItem + "' not implemented.")
				print("Valid items:")
				print("\t"+'\n\t'.join(subdict.keys()))
			except KeyError:
				print("Standard: '" + self.standard + "' not implemented.")
				print("Valid standards:")
				print ("\t"+'\n\t'.join(self.generatorMethod.keys()))
	# SpecLine generator methods dictionary
	generatorMethod = dict()
	
	#################################################################################
	# CEI-28G-VSR
	# OIF-CEI-03.1
	generatorMethod['CEI-28G-VSR'] = {
		'RLd':sigint.genspecline.gen_CEI28GVSR_RLd, # 13.3.7 eq.13-19 tables 13-1,13-2,13-4,13-5
		'RLcd':sigint.genspecline.gen_CEI28GVSR_RLcd11, # 13.3.8 eq.13-20 tables 13-1,13-2,13-4,13-5
		'RLdc':sigint.genspecline.gen_CEI28GVSR_RLdc22, # 13.3.8 eq.13-21 tables 13-1,13-2,13-4,13-5
		'RLc':sigint.genspecline.gen_CEI28GVSR_RLc} # 13.3.9 tables 13-1,13-4
	
	#################################################################################
	# 10GBASE-KR
	# IEEE 802.3 Annex69B
	generatorMethod['10GBASE-KR'] = {
		'Amax':sigint.genspecline.gen_10GKR_Amax, # 69B.4.2 Fitted attenuation
		'ILmax':sigint.genspecline.gen_10GKR_ILmax, # 69B.4.3 Insertion loss
		'ILDmin':sigint.genspecline.gen_10GKR_ILDmin, # 69B.4.4 Insertion loss deviation
		'ILDmax':sigint.genspecline.gen_10GKR_ILDmax, # 69B.4.4 Insertion loss deviation
		'RLmin':sigint.genspecline.gen_10GKR_RLmin, # 69B.4.5 Return loss
		'ICRmin':sigint.genspecline.gen_10GKR_ICRmin} # 69B.4.6 Crosstalk
	
	#################################################################################
	# chip-to-module CAUI4
	# IEEE 802.3bm
	# def sigint.genspecline.gen_ctmCAUI4_IL(self):
	generatorMethod['chip-to-module CAUI4'] = {
		'IL':sigint.genspecline.gen_ctmCAUI4_IL,
		'RLd':sigint.genspecline.gen_ctmCAUI4_RLd,
		'RLdc':sigint.genspecline.gen_ctmCAUI4_RLdc}

	#################################################################################
	# 100GBASE-CR4
	# IEEE 802.3bj 92.11
	# Also used for chip-to-module CAUI4
	generatorMethod['100GBASE-CR4'] = {
		'IL_tfref':sigint.genspecline.gen_100GCR4_IL_tfref, # 92.11.1.2 Test fixture insertion loss
		'IL_catf':sigint.genspecline.gen_100GCR4_IL_catf, # 92.11.2 Cable assembly test fixture
		'IL_MTFmax':sigint.genspecline.gen_100GCR4_IL_MTFmax, # 92.11.3 Mated test fixtures
		'IL_MTFmin':sigint.genspecline.gen_100GCR4_IL_MTFmin, # 92.11.3 Mated test fixtures
		'RLd_MTF':sigint.genspecline.gen_100GCR4_RLd_MTF, # 92.11.3 Mated test fixtures
		'ILdc_MTF':sigint.genspecline.gen_100GCR4_ILdc_MTF, # 92.11.3.3 Mated test fixtures common-mode conversion insertion loss
		'RLc_MTF':sigint.genspecline.gen_100GCR4_RLc_MTF, # 92.11.3.3 Mated test fixtures common-mode return loss
		'RLdc_MTF':sigint.genspecline.gen_100GCR4_RLdc_MTF} # 92.11.3.3 Mated test fixtures common-mode to differential mode return loss

	#################################################################################
	# 400GAUI-8 C2M
	# IEEE 802.3bs 120E.4.1
	# Also used for chip-to-module 200GAUI-4
	generatorMethod['400GAUI-8'] = {
		'IL_MTFref':sigint.genspecline.gen_400GAUI8_IL_MTFref, # 120E4.1 Test fixture reference insertion loss
		'IL_MTFmax':sigint.genspecline.gen_400GAUI8_IL_MTFmax, # 120E4.1 92.11.3 Mated test fixtures
		'IL_MTFmin':sigint.genspecline.gen_400GAUI8_IL_MTFmin, # 120E4.1 92.11.3 Mated test fixtures
		'RLd_MTF':sigint.genspecline.gen_400GAUI8_RLd_MTF, # 120E4.1 92.11.3 Mated test fixtures
		'ILdc_MTF':sigint.genspecline.gen_400GAUI8_ILdc_MTF, # 120E4.1 92.11.3.3 Mated test fixtures common-mode conversion insertion loss
		'RLc_MTF':sigint.genspecline.gen_400GAUI8_RLc_MTF, # 120E4.1 92.11.3.3 Mated test fixtures common-mode return loss
		'RLdc_MTF':sigint.genspecline.gen_400GAUI8_RLdc_MTF} # 120E4.1 92.11.3.3 Mated test fixtures common-mode to differential mode return loss
