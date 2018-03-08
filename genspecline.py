import numpy

#################################################################################
# CEI-28G-VSR
# OIF-CEI-03.1
def gen_CEI28GVSR_RLd(self): # 13.3.7 eq 13-19
	fb = 28e9
	f1 = 50e6
	f2 = fb/7.0
	f3 = fb
	freq = numpy.linspace(f2,f3,100)
	dBspecLine = -6. + 9.2*numpy.log10(2.*freq/fb)
	self.frequency = numpy.append(numpy.array(f1),freq)
	dBspecLine = numpy.append(numpy.array(-11.),dBspecLine)
	self.specLine = 10**(dBspecLine/20)
	self.limitType = 'max'
def gen_CEI28GVSR_RLcd11(self): # 13.3.8 eq 13-20
	fb = 28e9
	f1 = 50e6
	f2 = fb/2.0
	f3 = fb
	freq12 = numpy.linspace(f1,f2,100)
	freq23 = numpy.linspace(f2,f3,100)
	db12 = -22. + 14.*(freq12/fb)
	db23 = -18. + 6.*(freq23/fb)
	self.frequency = numpy.append(freq12[:-1],freq23)
	dBspecLine = numpy.append(db12[:-1],db23)
	self.specLine = 10**(dBspecLine/20)
	self.limitType = 'max'
def gen_CEI28GVSR_RLdc22(self): # 13.3.8 eq 13-21
	fb = 28e9
	f1 = 50e6
	f2 = fb/2.0
	f3 = fb
	freq12 = numpy.linspace(f1,f2,100)
	freq23 = numpy.linspace(f2,f3,100)
	db12 = -25. + 20.*(freq12/fb)
	db23 = -18. + 6.*(freq23/fb)
	self.frequency = numpy.append(freq12[:-1],freq23)
	dBspecLine = numpy.append(db12[:-1],db23)
	self.specLine = 10**(dBspecLine/20)
	self.limitType = 'max'
def gen_CEI28GVSR_RLc(self):
	f1 = 250e6
	f2 = 30e9
	self.frequency = numpy.array([f1,f2])
	dBspecLine = numpy.array([1.,1.])*(-2.0)
	self.specLine = 10**(dBspecLine/20)
	self.limitType = 'max'
def gen_CEI28GVSR_IL_HCBref(self): # CEI 4.0 13.4.1.1 eq 13-6
	f1 = 50e9
	f2 = 28.1e9
	num_points = 201
	self.frequency = numpy.linspace(f1,f2,num_points)
	dBspecLine = 2.0*(0.001 - 0.096*numpy.sqrt(self.frequency/1e9) - 0.046*self.frequency/1e9)
	self.specLine = 10**(dBspecLine/20)
	self.limitType = 'ref'
def gen_CEI28GVSR_IL_MCBref(self): # CEI 4.0 13.4.1.1 eq 13-7
	f1 = 50e9
	f2 = 28.1e9
	num_points = 201
	self.frequency = numpy.linspace(f1,f2,num_points)
	dBspecLine = 1.25*(0.001 - 0.096*numpy.sqrt(self.frequency/1e9) - 0.046*self.frequency/1e9)
	self.specLine = 10**(dBspecLine/20)
	self.limitType = 'ref'
def gen_CEI28GVSR_RL_MTF(self): # CEI 4.0 13.4.1.2 eq 13-8
	f1 = 0
	f2 = 28.1e9
	num_points = 201
	self.frequency = numpy.linspace(f1,f2,num_points)
	dBspecLine = -18 + self.frequency/1e9 / 2
	dBspecLine[self.frequency>4e9] = -20 + self.frequency/1e9
	self.specLine = 10**(dBspecLine/20)
	self.limitType = 'max'
def gen_CEI28GVSR_ILdc_MTF(self): # CEI 4.0 13.4.1.2 eq 13-8
	f1 = 0
	f2 = 28.1e9
	num_points = 201
	self.frequency = numpy.linspace(f1,f2,num_points)
	dBspecLine = -35 + 1.07*self.frequency/1e9
	dBspecLine[self.frequency<14e9] = -20
	self.specLine = 10**(dBspecLine/20)
	self.limitType = 'max'
#################################################################################
# CEI-56G-VSR-PAM4
# OIF-CEI-04.0
def gen_CEI56GVSRPAM4_IL_MTFref(self): # CEI 4.0 16.4.1.1 eq 16-11
	f1 = 50e9
	f2 = 29e9
	num_points = 201
	self.frequency = numpy.linspace(f1,f2,num_points)
	dBspecLine = -(0.475*numpy.sqrt(self.frequency/1e9) + 0.1204*self.frequency/1e9 + 0.002*(self.frequency/1e9)**2)
	self.specLine = 10**(dBspecLine/20)
	self.limitType = 'ref'
#################################################################################
# 10GBASE-KR
# IEEE 802.3 Annex69B
def gen_10GKR_Amax(self):
	b1 = 2.0e-5
	b2 = 1.1e-10
	b3 = 3.2e-20
	b4 = -1.2e-30
	f1 = 1.0e9
	f2 = 6.0e9
	self.frequency = numpy.linspace(f1, f2, int((f2-f1)/10e6)+1)
	dBspecLine = -20*numpy.log10(numpy.exp(1))*(b1*numpy.sqrt(self.frequency) + b2*self.frequency +
		b3*self.frequency**2 + b4*self.frequency**3)
	self.specLine = 10**(dBspecLine/20)
	self.limitType = 'min'
def gen_10GKR_ILmax(self):
	b1 = 2.0e-5
	b2 = 1.1e-10
	b3 = 3.2e-20
	b4 = -1.2e-30
	f2 = 6.0e9
	fmin = 0.05e9
	fmax = 15.0e9
	self.frequency = numpy.linspace(fmin, fmax, int((fmax-fmin)/10e6)+1)
	dBspecLine = -20*numpy.log10(numpy.exp(1))*(b1*numpy.sqrt(self.frequency) + b2*self.frequency +
		b3*self.frequency**2 + b4*self.frequency**3) - 0.8 - 2.0e-10*self.frequency
	dBspecLine[self.frequency>f2] = dBspecLine[self.frequency>f2] - 1e-8*(self.frequency[self.frequency>f2]-f2)
	self.specLine = 10**(dBspecLine/20)
	self.limitType = 'min'
def gen_10GKR_ILDmin(self):
	f1 = 1.0e9
	f2 = 6.0e9
	self.frequency = numpy.linspace(f1, f2, int((f2-f1)/10e6)+1)
	dBspecLine = -(1.0 + 0.5e-9*self.frequency)
	self.specLine = 10**(dBspecLine/20)
	self.limitType = 'min'
def gen_10GKR_ILDmax(self):
	f1 = 1.0e9
	f2 = 6.0e9
	self.frequency = numpy.linspace(f1, f2, int((f2-f1)/10e6)+1)
	dBspecLine = (1.0 + 0.5e-9*self.frequency)
	self.specLine = 10**(dBspecLine/20)
	self.limitType = 'max'
def gen_10GKR_RLmin(self):
	f2 = 10312.5e6
	self.frequency = numpy.linspace(50e6, f2, int((f2-50e6)/12.5e6)+1)
	dBspecLine = -(12.0 - 6.75*numpy.log10(self.frequency/275e6))
	dBspecLine[self.frequency<275.0e6] = -12
	dBspecLine[self.frequency>3000.0e6] = -5
	self.specLine = 10**(dBspecLine/20)
	self.limitType = 'max'
def gen_10GKR_ICRmin(self):
	fa = 0.1e9
	fb = 5.15625e9
	self.frequency = numpy.linspace(fa, fb, 501)
	dBspecLine = 23.3 -  18.7*numpy.log10(self.frequency/5.0e9)
	self.specLine = 10**(dBspecLine/20)
	self.limitType = 'min'
#################################################################################
# chip-to-module CAUI4
# IEEE 802.3bm
def gen_ctmCAUI4_IL(self):
	self.frequency = numpy.linspace(10e6,18.75e9,int(18.75e9/10e6))
	dBspecLine = -(1.076*(-18 + 2*self.frequency/1e9))
	dBspecLine[self.frequency<14e9] = -(1.076*(0.075 +
		0.537*numpy.sqrt(self.frequency[self.frequency<14e9]/1e9) + 
		0.566*self.frequency[self.frequency<14e9]/1e9))
	self.specLine = 10**(dBspecLine/20)
	self.limitType = 'min'
def gen_ctmCAUI4_RLd(self):
	self.frequency = numpy.linspace(10e6,19e9,int(19e9/10e6))
	dBspecLine = -(4.75-7.4*numpy.log10(self.frequency/14e9))
	dBspecLine[self.frequency<8e9] = -(9.5 - 
		0.37*self.frequency[self.frequency<8e9]/1e9)
	self.specLine = 10**(dBspecLine/20)
	self.limitType = 'max'
def gen_ctmCAUI4_RLdc(self):
	self.frequency = numpy.linspace(10e6,19e9,int(19e9/10e6))
	dBspecLine = -(15-6*self.frequency/25.78e9)
	dBspecLine[self.frequency<12.89e9] = -(22 - 
		20*self.frequency[self.frequency<12.89e9]/1e9/25.78)
	self.specLine = 10**(dBspecLine/20)
	self.limitType = 'max'
#################################################################################
# 100GBASE-CR4
# IEEE 802.3bj 92.11
# Also used for chip-to-module CAUI4
def gen_100GCR4_IL_tfref(self): # 92.11.1.2 Test fixture insertion loss
	self.frequency = numpy.linspace(10e6,25e9,int(25e9/10e6))
	dBspecLine = -(-0.00144 + 0.13824*numpy.sqrt(self.frequency/1e9) + 0.06624*self.frequency/1e9)
	self.specLine = 10**(dBspecLine/20)
	self.limitType = 'ref'
def gen_100GCR4_IL_catf(self): # 92.11.2 Cable assembly test fixture
	self.frequency = numpy.linspace(10e6,25e9,int(25e9/10e6))
	dBspecLine = -(-0.00125 + 0.12*numpy.sqrt(self.frequency/1e9) + 0.0575*self.frequency/1e9)
	self.specLine = 10**(dBspecLine/20)
	self.limitType = 'min'
def gen_100GCR4_IL_MTFmax(self): # 92.11.3 Mated test fixtures
	self.frequency = numpy.linspace(10e6,25e9,int(25e9/10e6))
	dBspecLine = -(-4.25 + 0.66*self.frequency/1e9)
	dBspecLine[self.frequency<14e9] = -(0.12 +
		0.475*numpy.sqrt(self.frequency[self.frequency<14e9]/1e9) + 
		0.221*self.frequency[self.frequency<14e9]/1e9)
	self.specLine = 10**(dBspecLine/20)
	self.limitType = 'min'
def gen_100GCR4_IL_MTFmin(self): # 92.11.3 Mated test fixtures
	self.frequency = numpy.linspace(10e6,25e9,int(25e9/10e6))
	dBspecLine = -(0.0656*numpy.sqrt(self.frequency/1e9) + 0.164*self.frequency/1e9)
	self.specLine = 10**(dBspecLine/20)
	self.limitType = 'max'
def gen_100GCR4_RLd_MTF(self): # 92.11.3 Mated test fixtures
	self.frequency = numpy.linspace(10e6,25e9,int(25e9/10e6))
	dBspecLine = -(18 - 0.5*self.frequency/1e9)
	dBspecLine[self.frequency<4e9] = -(20 -
		1*self.frequency[self.frequency<4e9]/1e9)
	self.specLine = 10**(dBspecLine/20)
	self.limitType = 'max'
def gen_100GCR4_ILdc_MTF(self): # 92.11.3.3 Mated test fixtures common-mode conversion insertion loss
	self.frequency = numpy.linspace(10e6,25e9,int(25e9/10e6))
	dBspecLine = -(30 - 29/22*self.frequency/1e9)
	dBspecLine[self.frequency>=16.5e9] = -8.25
	self.specLine = 10**(dBspecLine/20)
	self.limitType = 'min'
def gen_100GCR4_RLc_MTF(self): # 92.11.3.3 Mated test fixtures common-mode conversion insertion loss
	self.frequency = numpy.linspace(10e6,25e9,int(25e9/10e6))
	dBspecLine = -(12 - 9*self.frequency/1e9)
	dBspecLine[self.frequency>=1e9] = -3
	self.specLine = 10**(dBspecLine/20)
	self.limitType = 'max'
def gen_100GCR4_RLdc_MTF(self): # 92.11.3.3 Mated test fixtures common-mode conversion insertion loss
	self.frequency = numpy.linspace(10e6,25e9,int(25e9/10e6))
	dBspecLine = -(18 - 6/25.78*self.frequency/1e9)
	dBspecLine[self.frequency<12.89e9] = -(30 -
		30/25.78*self.frequency[self.frequency<12.89e9]/1e9)
	self.specLine = 10**(dBspecLine/20)
	self.limitType = 'max'
#################################################################################
# 400GAUI-8 C2M
# IEEE 802.3bs 120E4.1
# Also used for 200GAUI-4
def gen_400GAUI8_IL_MTFref(self): # 120E-3 Test fixture insertion loss
	self.frequency = numpy.linspace(10e6,25e9,int(25e9/10e6))
	dBspecLine = -(0.471*numpy.sqrt(self.frequency/1e9) + 0.1194*self.frequency/1e9 + 0.002*(self.frequency/1e9)**2)
	self.specLine = 10**(dBspecLine/20)
	self.limitType = 'ref'
def gen_400GAUI8_IL_MTFmax(self): # 92.11.3 Mated test fixtures
	self.frequency = numpy.linspace(10e6,26.5625e9,int(26.5625e9/10e6))
	dBspecLine = -(-4.25 + 0.66*self.frequency/1e9)
	dBspecLine[self.frequency<14e9] = -(0.12 +
		0.475*numpy.sqrt(self.frequency[self.frequency<14e9]/1e9) + 
		0.221*self.frequency[self.frequency<14e9]/1e9)
	self.specLine = 10**(dBspecLine/20)
	self.limitType = 'min'
def gen_400GAUI8_IL_MTFmin(self): # 92.11.3 Mated test fixtures
	self.frequency = numpy.linspace(10e6,26.5625e9,int(26.5625e9/10e6))
	dBspecLine = -(0.0656*numpy.sqrt(self.frequency/1e9) + 0.164*self.frequency/1e9)
	self.specLine = 10**(dBspecLine/20)
	self.limitType = 'max'
def gen_400GAUI8_RLd_MTF(self): # 92.11.3 Mated test fixtures
	self.frequency = numpy.linspace(10e6,26.5625e9,int(26.5625e9/10e6))
	dBspecLine = -(18 - 0.5*self.frequency/1e9)
	dBspecLine[self.frequency<4e9] = -(20 -
		1*self.frequency[self.frequency<4e9]/1e9)
	self.specLine = 10**(dBspecLine/20)
	self.limitType = 'max'
def gen_400GAUI8_ILdc_MTF(self): # 92.11.3.3 Mated test fixtures common-mode conversion insertion loss
	self.frequency = numpy.linspace(10e6,26.5625e9,int(26.5625e9/10e6))
	dBspecLine = -(30 - 29/22*self.frequency/1e9)
	dBspecLine[self.frequency>=16.5e9] = -8.25
	self.specLine = 10**(dBspecLine/20)
	self.limitType = 'min'
def gen_400GAUI8_RLc_MTF(self): # 92.11.3.3 Mated test fixtures common-mode return loss
	self.frequency = numpy.linspace(10e6,26.5625e9,int(26.5625e9/10e6))
	dBspecLine = -(12 - 9*self.frequency/1e9)
	dBspecLine[self.frequency>=1e9] = -3
	self.specLine = 10**(dBspecLine/20)
	self.limitType = 'max'
def gen_400GAUI8_RLdc_MTF(self): # 92.11.3.3 Mated test fixtures common-mode to differential mode return loss
	self.frequency = numpy.linspace(10e6,26.5625e9,int(26.5625e9/10e6))
	dBspecLine = -(18 - 6/25.78*self.frequency/1e9)
	dBspecLine[self.frequency<12.89e9] = -(30 -
		30/25.78*self.frequency[self.frequency<12.89e9]/1e9)
	self.specLine = 10**(dBspecLine/20)
	self.limitType = 'max'
