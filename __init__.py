# imports
import scipy.interpolate
import numpy

# general funtions
def dB(val):
	return 20*numpy.log10(numpy.abs(val))

def fInterpolate(data,f,fnew):
	"""Interpolates complex-valued data over fnew using magnitude and phase interpolation.
	Returns the interpolated data.
	"""
	magnitude = numpy.abs(data)
	phase = numpy.unwrap(numpy.angle(data))
	newMagnitude = scipy.interpolate.pchip_interpolate(f,magnitude,fnew)
	newPhase = scipy.interpolate.pchip_interpolate(f,phase,fnew)
	newData = newMagnitude*numpy.exp(1j*newPhase)
	return newData

