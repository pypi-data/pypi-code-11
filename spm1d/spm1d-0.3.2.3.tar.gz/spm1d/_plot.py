
'''
This module contains classes for low-level plotting.

Users should access plotting functions through spm1d.plot (not spm1d._plot).
'''

# Copyright (C) 2016  Todd Pataky
# _plot.py version: 0.3.2 (2016/01/03)


from copy import copy,deepcopy
import numpy as np
from scipy import ndimage
import matplotlib
from matplotlib import pyplot, cm as colormaps
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection



eps    = np.finfo(float).eps   #smallest float, used to avoid divide-by-zero errors




def p2string(p):
	return 'p < 0.001' if p<0.0005 else 'p = %.03f'%p




class DataPlotter(object):
	def __init__(self, ax=None):
		self.ax        = self._gca(ax)
		self.x         = None
		
	# def _getQ(x, Q):
	# 	return np.arange(Q) if x is None else x
	
	def _gca(self, ax):
		return pyplot.gca() if ax is None else ax
	
	def _set_axlim(self):
		self._set_xlim()
		self._set_ylim()
	
	def _set_x(self, x, Q):
		self.x         = np.arange(Q) if x is None else x

	def _set_xlim(self):
		pyplot.setp(self.ax, xlim=(self.x.min(), self.x.max())  )

	def _set_ylim(self, pad=0.075):
		def minmax(x):
			return np.ma.min(x), np.ma.max(x)
		ax          = self.ax
		ymin,ymax   = +1e10, -1e10
		for line in ax.lines:
			y0,y1   = minmax( line.get_data()[1] )
			ymin    = min(y0, ymin)
			ymax    = max(y1, ymax)
		for collection in ax.collections:
			datalim = collection.get_datalim(ax.transData)
			y0,y1   = minmax(  np.asarray(datalim)[:,1]  )
			ymin    = min(y0, ymin)
			ymax    = max(y1, ymax)
		for text in ax.texts:
			r       = matplotlib.backend_bases.RendererBase()
			bbox    = text.get_window_extent(r)
			y0,y1   = ax.transData.inverted().transform(bbox)[:,1]
			ymin    = min(y0, ymin)
			ymax    = max(y1, ymax)
		dy = 0.075*(ymax-ymin)
		ax.set_ylim(ymin-dy, ymax+dy)
	
	def plot(self, y, **kwdargs):
		return self.ax.plot(y, **kwdargs)
	
	def plot_cloud(self, Y, facecolor='0.8', edgecolor='0.8', alpha=0.5):
		### create patches:
		y0,y1       = Y
		x,y0,y1     = self.x.tolist(), y0.tolist(), y1.tolist()
		x           = [x[0]]  + x  + [x[-1]]
		y0          = [y0[0]] + y0 + [y0[-1]]
		y1          = [y1[0]] + y1 + [y1[-1]]
		y1.reverse()
		### concatenate:
		x1          = np.copy(x).tolist()
		x1.reverse()
		x,y         = x + x1, y0 + y1
		patches     = PatchCollection([Polygon(zip(x,y))], edgecolors=None)
		### plot:
		self.ax.add_collection(patches)
		pyplot.setp(patches, facecolor=facecolor, edgecolor=edgecolor, alpha=alpha)
		return patches

	def plot_datum(self):
		self.ax.axhline(0, color='k', lw=1, linestyle=':')

	def plot_roi(self, roi, ylim=None, facecolor='b', edgecolor='w', alpha=0.5):
		L,n       = ndimage.label(roi)
		y0,y1     = self.ax.get_ylim() if ylim is None else ylim
		poly      = []
		for i in range(n):
			x0,x1 = np.argwhere(L==(i+1)).flatten()[[0,-1]]
			verts = [(x0,y0), (x1,y0), (x1,y1), (x0,y1)]
			poly.append( Polygon(verts) )
			pyplot.setp(poly, facecolor=facecolor, edgecolor=edgecolor, alpha=alpha)
		self.ax.add_collection( PatchCollection(poly, match_original=True) )





class SPMPlotter(DataPlotter):
	def __init__(self, spm, ax=None):
		self.ax        = self._gca(ax)
		self.x         = np.arange(spm.Q)
		self.spm       = spm
		self.z         = None
		self.zma       = None   #masked
		self.ismasked  = None
		self.set_data()
		
	def _get_statstr(self):
		return 't' if self.spm.STAT=='T' else self.spm.STAT
	
	def plot(self, color='k', lw=3, label=None):
		self.plot_field(color=color, lw=lw, label=label)
		self.plot_datum()
		self._set_ylim()

	def plot_design(self, factor_labels=None, fontsize=10):
		def scaleColumns(X):
			mn,mx     = np.min(X,axis=0) , np.max(X,axis=0)
			Xs        = (X-mn)/(mx-mn+eps)
			Xs[np.isnan(Xs)] = 1   #if the whole column is a constant
			return Xs
		X             = self.spm.X
		vmin,vmax     = None, None
		if np.all(X==1):
			vmin,vmax = 0, 1
		self.ax.imshow(scaleColumns(X), cmap=colormaps.gray, interpolation='nearest', vmin=vmin, vmax=vmax)
		if factor_labels != None:
			gs        = X.shape
			tx        = [self.ax.text(i, -0.05*gs[0], label)   for i,label in enumerate(factor_labels)]
			pyplot.setp(tx, ha='center', va='bottom', color='k', fontsize=fontsize)
		self.ax.axis('normal')
		self.ax.axis('off')
	
	def plot_field(self, **kwdargs):
		keys   = kwdargs.keys()
		if 'color' not in keys:
			kwdargs.update( dict(color='k') )
		if ('lw' not in keys) and ('linewidth' not in keys):
			kwdargs.update( dict(lw=2) )
		ax,x    = self.ax, self.x
		if self.ismasked:
			ax.plot(x, self.zma, **kwdargs)
		else:
			ax.plot(x, self.z, **kwdargs)
	
	def plot_ylabel(self):
		self.ax.set_ylabel('SPM{%s}'%self._get_statstr(), size=16)
	
	def set_data(self):
		if isinstance(self.spm.z, np.ma.MaskedArray):
			self.zma      = deepcopy(self.spm.z)
			self.z        = np.asarray(self.spm.z, dtype=float)
			self.ismasked = True
		else:
			self.z        = self.spm.z
			self.ismasked = False





class SPMiPlotter(SPMPlotter):
	def __init__(self, spmi, ax=None):
		super(SPMiPlotter, self).__init__(spmi, ax)
	
	def plot(self, color='k', lw=3, facecolor='0.7', thresh_color='k', label=None):
		self.plot_field(color=color, lw=lw, label=label)
		self.plot_datum()
		self.plot_threshold(color=thresh_color)
		self.plot_cluster_patches(facecolor=facecolor)
		self._set_ylim()

	def plot_cluster_patches(self, facecolor='0.8'):
		if self.spm.nClusters > 0:
			polyg      = []
			for cluster in self.spm.clusters:
				x,z    = cluster.get_patch_vertices()
				polyg.append(  Polygon(zip(x,z))  )
				if cluster.iswrapped:
					x,z    = cluster._other.get_patch_vertices()
					polyg.append(  Polygon(zip(x,z))  )
			patches    = PatchCollection(polyg, edgecolors=None)
			self.ax.add_collection(patches)
			pyplot.setp(patches, facecolor=facecolor, edgecolor=facecolor)

	def plot_p_values(self, size=8, offsets=None, offset_all_clusters=None):
		n          = len(self.spm.p)
		if offsets is None:
			if offset_all_clusters is None:
				offsets = [(0,0)]*n
			else:
				offsets = [offset_all_clusters]*n
		if len(offsets) < n:
			print('WARNING:  there are fewer offsets than clusters.  To set offsets for all clusters use the offset_all_clusters keyword.')
		h          = []
		for cluster,offset in zip(self.spm.clusters, offsets):
			x,y    = cluster.xy[0] if cluster.iswrapped else cluster.xy
			x     += offset[0]
			y     += offset[1]
			s      = p2string(cluster.P)
			hh     = self.ax.text(x, y, s, size=size, ha='center', va='center', bbox=dict(facecolor='w', alpha=0.3))
			h.append(hh)
		return h

	def plot_threshold(self, color='k'):
		ax,zs,spmi = self.ax, self.spm.zstar, self.spm
		if spmi.roi is None:
			h      = [ax.axhline(zs)]
			if spmi.two_tailed:
				h.append( ax.axhline(-zs) )
		else:
			if spmi.roi.dtype == bool:
				zz     = np.ma.masked_array([zs]*spmi.Q, np.logical_not(spmi.roi))
				h      = [ax.plot(self.x, zz)]
				if spmi.two_tailed:
					h.append( ax.plot(self.x, -zz) )
			else:  #directional ROI
				h          = []
				if np.any(spmi.roi>0):
					zz     = np.ma.masked_array([zs]*spmi.Q, np.logical_not(spmi.roi>0))
					h.append( ax.plot(self.x, zz) )
				if np.any(spmi.roi<0):
					zz     = np.ma.masked_array([-zs]*spmi.Q, np.logical_not(spmi.roi<0))
					h.append( ax.plot(self.x, zz) )
		pyplot.setp(h, color=color, lw=1, linestyle='--')
		return h

	def plot_threshold_label(self, lower=False, pos=None, **kwdargs):
		spmi      = self.spm
		if pos is None:
			x0,x1 = self.x.min(), self.x.max()
			y0,y1 = self.ax.get_ylim()
			x     = x0 + 0.4*(x1-x0)
			if lower and spmi.two_tailed:
				y     = -spmi.zstar + 0.005*(y1-y0)
			else:
				y     = spmi.zstar + 0.005*(y1-y0)
		else:
			x,y   = pos
		if 'color' not in kwdargs.keys():
			kwdargs.update( dict(color='r') )
		s         = r'$\alpha$=%.2f:  $%s^*$=%.3f' %(spmi.alpha, self._get_statstr(), spmi.zstar)
		h         = self.ax.text(x, y, s, **kwdargs)
		return h



