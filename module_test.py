# import some module functions
import numpy
import sigint
import sigint.dataseries
import sigint.dataplot
import sigint.specline
import matplotlib.pyplot
import os
import re

def CAUI4ChipToModule(measurements, plot=True, outputFile='output', outputDir='output/', label='CAUI4', labels=None, f0=50e6, signal='RX'):
	"""Takes 2-port return loss measurements and compliance plots
	and outputs compliance data.  Input is a list of sp"""
	if not os.path.isdir(outputDir):
		os.mkdir(outputDir)
	# init combined plots
	if signal == 'RX':
		RLdPlot = sigint.dataplot.FrequencyDomainPlot(title=label+'\n'+'Differential Output Return Loss (83E-3.1.3)')
		RLdcPlot = sigint.dataplot.FrequencyDomainPlot(title=label+'\n'+'Common to Differential Mode Conversion Return Loss (83E-3.1.3)')
		RLdPlot.addItem(sigint.specline.SpecLine('chip-to-module CAUI4','RLd'), linestyle='dashed', color='grey', linewidth=1, label='(83E-2)')
		RLdcPlot.addItem(sigint.specline.SpecLine('chip-to-module CAUI4','RLdc'), linestyle='dashed', color='grey', linewidth=1, label='(83E-3)')
		
	elif signal == 'TX':
		RLdPlot = sigint.dataplot.FrequencyDomainPlot(title=label+'\n'+'Differential Input Return Loss (83E.3.3.1)')
		RLdcPlot = sigint.dataplot.FrequencyDomainPlot(title=label+'\n'+'Differential to Common Mode Input Return Loss (83E.3.3.1)')
		RLdPlot.addItem(sigint.specline.SpecLine('chip-to-module CAUI4','RLd'), linestyle='dashed', color='grey', linewidth=1, label='(83E-5)')
		RLdcPlot.addItem(sigint.specline.SpecLine('chip-to-module CAUI4','RLdc'), linestyle='dashed', color='grey', linewidth=1, label='(83E-6)')
	
	# init output CSV
	outputFile = outputFile.replace('.csv', '')
	fid = open(outputDir + outputFile + '.csv', 'w')
	header = ['signal', 'Rterm (Ohms)', 'Differential termination mismatch (%)']
	fid.write(','.join(header) + '\n')
	# loop over sp files
	for n, spfile in enumerate(measurements):
		rl = sigint.dataseries.MixedModeSParameters(spfile)
		if (labels is not None) and (len(labels) == len(measurements)):
			rl.label = labels[n]
		# add to plots
		RLdPlot.addItem(rl, 'SDD', (1,1))
		if signal == 'RX':
			RLdcPlot.addItem(rl, 'SDC', (1,1))
		elif signal == 'TX':
			RLdcPlot.addItem(rl, 'SCD', (1,1))
		# compute additional data
		Zp = numpy.real(rl.getZ((1,1), frequency=[f0]) - rl.getZ((1,2), frequency=[f0]))[0]
		Zn = numpy.real(rl.getZ((2,2), frequency=[f0]) - rl.getZ((2,1), frequency=[f0]))[0]
		Zterm = Zp+Zn
		DZM = 2*numpy.abs(Zp-Zn)/(Zp+Zn)*100
		# add data to CSV
		fid.write(rl.label + ',{:0.1f},{:0.1f}\n'.format(Zterm, DZM))
		# generate individual plot
	# generate combined plots
	RLdPlot.xlim(0,20)
	# RLdcPlot.xlim(0,20)
	RLdcPlot.xlim(0,0.1)
	RLdPlot.ylim(low=-25)
	RLdcPlot.ylim(high=-45)
	#RLdcPlot.ylim(low=-30)
	RLdPlot.generatePlot()
	RLdcPlot.generatePlot()
	# close output file
	fid.close()
