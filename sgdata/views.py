from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from django.template import RequestContext
from json import dumps

import numpy as np
import spacegrids as sg
import copy



def interpret(comstr,knownobs,obchain=[]):
    """
    e.g. knownobs = {'P':P,'E':E}
    """

  

    if '*' in comstr:
      mults = comstr.split('*')
      
      return [reduce(lambda x,y:interpret(x,knownobs,obchain=[])[-1]*interpret(y,knownobs,obchain=[])[-1], mults )]
    

    if '__' in comstr:
    
      chain = [interpret(e, knownobs,obchain=[])[-1] for e in comstr.split('__') ]
  
      return [reduce( lambda x,y:x[y], chain)]


   # print comstr          
    if '.' in comstr:
      split2 = comstr.split('.',1) # look at leftmost element

      if obchain:
        obchain=obchain+interpret(split2[0], knownobs,obchain)
        return interpret(split2[1], knownobs,obchain)
        

      else:
        # we're at the head of the chain
        if split2[0] in knownobs:
          obchain.append(knownobs[split2[0]])
          
        else:
          raise Exception('Parsing error')

      return interpret(split2[1], knownobs,obchain)

    else:


      if obchain:
        attrs = dir(obchain[-1])
      
        if comstr in attrs:
          # current piece is an attribute
          obchain.append(getattr(obchain[-1], comstr  )  )          
        else:
          raise Exception('Parsing error')      

      else:

        # we're at the head and end of the chain
        if comstr in knownobs:
          obchain.append(knownobs[comstr])        

        else:
          try:
            i=int(comstr)
            obchain.append(i)          
          except ValueError:
            obchain.append(comstr )                 


      return obchain



def find_mirror(fld):
  """Prepare field for orientation appropriate for client-side contour function.
  """
#  F.value = np.flipud(F.value)

  grid = fld.grid
  if hasattr(grid[0],'axis'):
    if grid[0].axis.name == 'Z':
      fld=grid[0].flip(fld)

#      fld.grid[0].value = -fld.grid[0].value 
 #     fld.grid[0].dual.value = -fld.grid[0].dual.value 

      yscale=1e-3
      fld.grid[0].value = yscale*np.flipud(fld.grid[0].value )
      fld.grid[0].dual.value = yscale*np.flipud(fld.grid[0].dual.value )

#      fld.grid[0].dual.value = np.concatenate([np.array([fld.grid[0].dual.value[0],]), fld.grid[0].dual.value])


    elif grid[1].axis.name == 'Z':
      fld=grid[1].flip(fld)


  return fld


def make_json(fld):
 
  M = np.nanmax(fld.value)
  m = np.nanmin(fld.value)

  ndim = fld.value.ndim 
  fld = find_mirror(fld)

  fld.value[np.isnan(fld.value)] = -999.

  msg = {'name':fld.name,'lname':fld.long_name,'value':fld.value.tolist() ,'M':str(M),'m':str(m) , 'ndim':ndim, 'units':fld.units }

  for i,coord in enumerate(fld.grid):
    msg['coord'+str(i)] = fld.grid[i].value.tolist()
    msg['coord'+str(i)+'_edges'] = fld.grid[i].dual.value.tolist()
    msg['coord'+str(i)+'_lname'] = fld.grid[i].long_name
    msg['coord'+str(i)+'_units'] = fld.grid[i].units
    msg['coord'+str(i)+'_axis'] = fld.grid[i].axis.name

  return dumps(msg)
  

def get_field(project,exp, field):


  D = sg.info_dict()
  P = sg.Project(D[project])
  P[exp].load(field)
  
  fld = sg.squeeze(P[exp][field])
 # print fld.value.shape

  #return HttpResponse(dumps(fld.json(types_allow=[sg.Gr,sg.Ax,sg.Coord])))

  return fld, P, P[exp]


# --------- views ------------

def index(request):

  context = RequestContext(request)
 
#  comstr = request.GET['grid']

#  fld,P,E = get_field('my_project','DPO', 'A_sat')

#  knownobs = {'P':P,'E':E}

    # bring axes and coords into main objects knownobs:
  
#  for a in knownobs['E'].axes:
#    knownobs[a.name] = a

#  for a in knownobs['E'].cstack:
#    knownobs[a.name] = a




#  print interpret(comstr,knownobs,obchain=[] )
 
  return render_to_response('sgdata/index.html', context)

def ret_field(request, project,exp, field):


  context = RequestContext(request)

#  print project
#  print exp
#  print field
  fld, _, _ = get_field(project,exp, field)


  msg = make_json(fld)
  return HttpResponse(msg)

def ret_field_op(request, project,exp, field, op):

  context = RequestContext(request)

  

  fld, _, _ = get_field(project,exp, field)
  fld = getattr(sg,op)(fld)
  msg = make_json(fld)
  return HttpResponse(msg)

def ret_field_method(request, project,exp, field, method):

  context = RequestContext(request)

  comstr = request.GET['args']

  fld, P, E = get_field(project,exp, field)

  knownobs = {'P':P,'E':E}

    # bring axes and coords into main objects knownobs:
  
  for a in knownobs['E'].axes:
    knownobs[a.name] = a

  for a in knownobs['E'].cstack:
    knownobs[a.name] = a


  args = interpret(comstr,knownobs,obchain=[] )[-1]

  print args

  fld = getattr(fld,method)(args)
  msg = make_json(fld)
  return HttpResponse(msg)



def gmaps(request):
	context = RequestContext(request)
	return render_to_response('sgdata/gmaps.html', context)

