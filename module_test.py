# import some module functions
import numpy
import sigint
import sigint.dataseries
import sigint.dataplot
import sigint.specline
import matplotlib.pyplot
import os
import re

def CAUI4ChipToModule(measurements, plot=True, outputFile='output', outputDir='output/', standard = 'CAUI4', label='', labels=None, f0=50e6, signal='RX'):
	"""Takes 2-port return loss measurements and compliance plots
	and outputs compliance data.  Input is a list of sp"""
	plot_size = (6,4)
	limit_line_styles = ['dashed', 'dashdot', 'dotted']
	if not os.path.isdir(outputDir):
		os.mkdir(outputDir)
	if not label:
		label = standard
	# init combined plots
	if standard=='CAUI4':
		if signal == 'RX':
			# plot title, quantity, limit lines (standard, quantity, label), plot limits (x1 x2 y1 y2)
			plotspecs = [	('Differential Output Return Loss (83E-3.1.3)', 'SDD', [('chip-to-module CAUI4','RLd','(83E-2)')], (0, 20, -25, None)),
							('Common to Differential Mode Conversion Return Loss (83E-3.1.3)', 'SDC', [('chip-to-module CAUI4','RLdc','(83E-3)')], (0, 20, -35, None)) ]
		elif signal == 'TX':
			# plot title, quantity, limit lines (standard, quantity, label), plot limits (x1 x2 y1 y2)
			plotspecs = [	('Differential Input Return Loss (83E.3.3.1)', 'SDD', [('chip-to-module CAUI4','RLd','(83E-5)')], (0, 20, -25, None)),
							('Differential to Common Mode Input Return Loss (83E.3.3.1)', 'SCD', [('chip-to-module CAUI4','RLdc','(83E-6)')], (0, 20, -35, None)) ]
	elif standard=='CEI-28G-VSR':
		if signal == 'RX':
			# plot title, quantity, limit lines (standard, quantity, label), plot limits (x1 x2 y1 y2)
			plotspecs = [	('Differential Return Loss (SDD22) (13.3.7)', 'SDD', [('CEI-28G-VSR','RLd','(13-2)')], (0, 30, -25, None)),
							('Common Mode to Differential Conversion (SDC22) (13.3.8)', 'SDC', [('CEI-28G-VSR','RLdc','(13-4)')], (0, 30, -35, None)),
							('Common Mode Return Loss (SCC22) (13.3.9)', 'SCC', [('CEI-28G-VSR','RLc','Table 13-4')], (0, 30, -35, None)) ]
		elif signal == 'TX':
			# plot title, quantity, limit lines (standard, quantity, label), plot limits (x1 x2 y1 y2)
			plotspecs = [	('Differential Return Loss (SDD11) (13.3.7)', 'SDD', [('CEI-28G-VSR','RLd','(13-2)')], (0, 30, -25, None)),
							('Differential to Common Mode Conversion (SCD11) (13.3.8)', 'SCD', [('CEI-28G-VSR','RLcd','(13-3)')], (0, 30, -35, None))]
	elif standard=='all':
		if signal == 'RX':
			# plot title, quantity, limit lines (standard, quantity, label), plot limits (x1 x2 y1 y2)
			plotspecs = [	('Differential Return Loss', 'SDD', [('CEI-28G-VSR','RLd','CEI-28G-VSR (13-2)'),('chip-to-module CAUI4','RLd','CAUI4 (83E-2)')], (0, 30, -25, None)),
							('Common Mode to Differential Conversion', 'SDC', [('CEI-28G-VSR','RLdc','CEI-28G-VSR (13-4)'),('chip-to-module CAUI4','RLdc','CAUI4 (83E-3)')], (0, 30, -35, None)),
							('Common Mode Return Loss', 'SCC', [('CEI-28G-VSR','RLc','CEI-28G-VSR Table 13-4')], (0, 30, -35, None)) ]
		elif signal == 'TX':
			# plot title, quantity, limit lines (standard, quantity, label), plot limits (x1 x2 y1 y2)
			plotspecs = [	('Differential Return Loss', 'SDD', [('CEI-28G-VSR','RLd','CEI-28G-VSR (13-2)'),('chip-to-module CAUI4','RLd','CAUI4 (83E-5)')], (0, 30, -25, None)),
							('Differential to Common Mode Conversion', 'SCD', [('CEI-28G-VSR','RLcd','CEI-28G-VSR (13-3)'),('chip-to-module CAUI4','RLdc','CAUI4 (83E-6)')], (0, 30, -35, None))]
	
	plots = []
	for plotspec in plotspecs:
		plots.append(sigint.dataplot.FrequencyDomainPlot(title=label+'\n'+plotspec[0]))
		for n, limit_line in enumerate(plotspec[2]):
			plots[-1].addItem(sigint.specline.SpecLine(limit_line[0],limit_line[1]), linestyle=limit_line_styles[n%len(limit_line_styles)], color='grey', linewidth=1, label=limit_line[2])
	
	# init output CSV
	outputFile = outputFile.replace('.csv', '')
	fid = open(outputDir + outputFile + '.csv', 'w')
	header1 = ['','','']
	header2 = ['signal', 'Rterm (Ohms)', 'Differential termination mismatch (%)']
	# add margin items to header
	for plotspec in plotspecs:
		for limit in plotspec[2]:
			header1.append(limit[0]+' '+limit[2])
			header1.append('')
			header2.append('margin (dB)')
			header2.append('at frequency (GHz)')
	fid.write(','.join(header1) + '\n')
	fid.write(','.join(header2) + '\n')
	# loop over sp files
	for n, spfile in enumerate(measurements):
		rl = sigint.dataseries.MixedModeSParameters(spfile)
		if (labels is not None) and (len(labels) == len(measurements)):
			rl.label = labels[n]
		# add to plots
		for m, plot in enumerate(plots):
			plot.addItem(rl, plotspecs[m][1], (1,1), label = rl.label)
		
		output_line = []
		Zterm , DZM = computeTerminationMismatch(rl, f0)
		output_line.extend([rl.label, '{:0.1f}'.format(Zterm) , '{:0.1f}'.format(DZM)])
		# evaluate margins
		for plotspec in plotspecs:
			for limit in plotspec[2]:
				margin, wc, wcf = sigint.specline.evaluateLimitLine(sigint.dataseries.FrequencyDomainData(eval('rl.'+plotspec[1]+'[0,0,:]'),rl.frequency),limit[0],limit[1])
				output_line.extend(['{:0.2f}'.format(wc), '{:0.1f}'.format(wcf*1e-9)])
		# add data to CSV
		fid.write(','.join(output_line) + '\n')

		# generate combined plots
	for m, plot in enumerate(plots):
		if plotspecs[m][3][0] is not None:
			plot.xlim(low=plotspecs[m][3][0])
		if plotspecs[m][3][1] is not None:
			plot.xlim(high=plotspecs[m][3][1])
		if plotspecs[m][3][2] is not None:
			plot.ylim(low=plotspecs[m][3][2])
		if plotspecs[m][3][3] is not None:
			plot.ylim(high=plotspecs[m][3][3])
		plot.generatePlot(plot_size=plot_size)
		matplotlib.pyplot.savefig(outputDir + outputFile + ' ' + plotspecs[m][0] + '.png')
		matplotlib.pyplot.close()
	# close output file
	fid.close()

def computeTerminationMismatch(sparam, f0):
	Zp = numpy.real(sparam.getZ((1,1), frequency=[f0]) - sparam.getZ((1,2), frequency=[f0]))[0]
	Zn = numpy.real(sparam.getZ((2,2), frequency=[f0]) - sparam.getZ((2,1), frequency=[f0]))[0]
	Zterm = Zp+Zn
	DZM = 2*numpy.abs(Zp-Zn)/(Zp+Zn)*100
	return (Zterm, DZM)