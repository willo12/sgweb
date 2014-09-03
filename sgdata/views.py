from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from django.template import RequestContext
from json import dumps

import numpy as np
import spacegrids as sg

def prepare_hor_field(F):
  """Prepare field for orientation appropriate for client-side contour function.
  """
#  F.value = np.flipud(F.value)
  return F.transpose()


def get_field(request, project,exp, field):

  context = RequestContext(request)

  D = sg.info_dict()
  P = sg.Project(D[project])
  P[exp].load(field)
  
  fld = sg.finer_field(sg.squeeze(P[exp][field]))
 # print fld.value.shape
 
  M = np.nanmax(fld.value)
  m = np.nanmin(fld.value)

  fld.value[np.isnan(fld.value)] = -999.

  msg = {'name':fld.name,'value':fld.value.tolist() ,'coord0':fld.grid[0].value.tolist(), 'coord1':fld.grid[1].value.tolist(),'coord0_edges':fld.grid[0].dual.value.tolist(), 'coord1_edges':fld.grid[1].dual.value.tolist(),'M':str(M),'m':str(m) }

  #return HttpResponse(dumps(fld.json(types_allow=[sg.Gr,sg.Ax,sg.Coord])))

  return HttpResponse(dumps(msg))



def make_json(fld):
 
  M = np.nanmax(fld.value)
  m = np.nanmin(fld.value)

  fld.value[np.isnan(fld.value)] = -999.

  msg = {'name':fld.name,'value':fld.value.tolist() ,'coord0':fld.grid[0].value.tolist(), 'coord1':fld.grid[1].value.tolist(),'coord0_edges':fld.grid[0].dual.value.tolist(), 'coord1_edges':fld.grid[1].dual.value.tolist(),'M':str(M),'m':str(m) }

  return dumps(msg)
  

def get_field(project,exp, field):


  D = sg.info_dict()
  P = sg.Project(D[project])
  P[exp].load(field)
  
  fld = sg.squeeze(P[exp][field])
 # print fld.value.shape

  #return HttpResponse(dumps(fld.json(types_allow=[sg.Gr,sg.Ax,sg.Coord])))

  return fld


# --------- views ------------

def index(request):

  context = RequestContext(request)
 
 
  return render_to_response('sgdata/index.html', context)

  return HttpResponse('test')

def ret_field(request, project,exp, field):

  context = RequestContext(request)

  fld = get_field(project,exp, field)
  msg = make_json(fld)
  return HttpResponse(msg)

def ret_field_op(request, project,exp, field, op):

  context = RequestContext(request)

  

  fld = get_field(project,exp, field)
  fld = getattr(sg,op)(fld)
  msg = make_json(fld)
  return HttpResponse(msg)

def ret_field_method(request, project,exp, field, method):

  context = RequestContext(request)

  fld = get_field(project,exp, field)
  fld = getattr(field,method)(args)
  msg = make_json(fld)
  return HttpResponse(msg)



def gmaps(request):
	context = RequestContext(request)
	return render_to_response('sgdata/gmaps.html', context)
