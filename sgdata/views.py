from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from django.template import RequestContext
from json import dumps

import numpy as np
import spacegrids as sg
import copy


def list_ops(P,E):

  knownobs = init_knownobs(P,E)
  _, oplist = make_ops(knownobs)

  return oplist

def build_knownobs(P,E):

  knownobs = init_knownobs(P,E)
  knownobs, _ = make_ops(knownobs)

  return knownobs

def make_ops(knownobs):
 
    new_keys=[]
    # create operators
    axnames=['X','Y','Z','T']
    opnames=["Prim","Integ","Mean"] 

    for opname in opnames:
      for an in axnames:
    
        opkey=opname+an
        new_keys.append(opkey)
        op=getattr(sg,opname)(knownobs[an])
        knownobs[opkey] = op

    
    return knownobs,new_keys

def init_knownobs(P,E):


  knownobs = {'P':P,'E':E}

    # bring axes and coords into main objects knownobs:
  
  for a in knownobs['E'].axes:
    knownobs[a.name] = a

  for a in knownobs['E'].cstack:
    knownobs[a.name] = a  

  return knownobs


def interpret_exp(comstr):

 # print comstr
  if '-' in comstr:
    members=comstr.split('-')
    return {'op':'minus','members':members[:2]}

  elif '+' in comstr:
    members=comstr.split('+')
    return {'op':'concat','members':members}

  return {'op':'none','members':[comstr]}


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


    elif (len(grid)>1) and (grid[1].axis.name == 'Z'):
      fld=grid[1].flip(fld)


  return fld


def make_msg(fld):
 
  M = np.nanmax(fld.value)
  m = np.nanmin(fld.value)

  ndim = fld.value.ndim 
  
  if ndim == 3:
    coord0 = fld.grid[0]
    fsliced = fld.regrid(coord0**2)
    msg = {'name':fld.name,'lname':fld.long_name,'M':str(M),'m':str(m), 'ndim':ndim, 'units':fld.units}
    
    msg["slices"] = [make_msg(e) for e in fsliced]
    msg["scoord"] = coord0.value.tolist()   
    
    return msg
  
  fld = find_mirror(fld)

  try:
    fld.value[np.isnan(fld.value)] = -9e20
  except:
    pass

  msg = {'name':fld.name,'lname':fld.long_name,'value':fld.value.tolist() ,'M':str(M),'m':str(m) , 'ndim':ndim, 'units':fld.units }

  for i,coord in enumerate(fld.grid):
    msg['coord'+str(i)] = fld.grid[i].value.tolist()
    msg['coord'+str(i)+'_edges'] = fld.grid[i].dual.value.tolist()
    msg['coord'+str(i)+'_lname'] = fld.grid[i].long_name
    msg['coord'+str(i)+'_units'] = fld.grid[i].units
    msg['coord'+str(i)+'_axis'] = fld.grid[i].axis.name

  return msg
  
def make_json(msg):
 
  msg = make_msg(msg)

  return dumps(msg)




def get_field(project,exp, field):
  "Field can be something like DPO-DPC"

  opob = interpret_exp(exp)

  D = sg.info_dict()
  P = sg.Project(D[project])

  if (opob is not None):
    for exp in opob['members']:
      P[exp].load(field)
  
    if (opob['op'] == 'none'):
      fld = P[opob['members'][0]][field]
    elif (opob['op'] == 'minus'):
      fld = P[opob['members'][0]][field] - P[opob['members'][1]][field]
    elif (opob['op'] == 'concat'):
      W=sg.Ax("exper")
      fld = sg.concatenate([P[m][field] for m in opob['members'] ] , ax=W ) 


  else:
    fld = None

 # print fld.value.shape

  return sg.squeeze(fld), P, P[exp]


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

def projects(request):

  context = RequestContext(request)

  idict = sg.info_dict()

  return HttpResponse(dumps(idict.keys()))

def list_exp(request,project,exp):

  context = RequestContext(request)
  D = sg.info_dict()
  P = sg.Project(D[project])
  E = P[exp]

  expers = P.expers.keys()
  axes = [ax.name for ax in P.expers.values()[0].axes]

  msg = {"vars":E.available(), "coords":[crd.name for crd in E.cstack]}

  return HttpResponse(dumps(msg))

def list_project(request,project):

  context = RequestContext(request)
  D = sg.info_dict()
  P = sg.Project(D[project])
  expers = P.expers.keys()
  axes = [ax.name for ax in P.expers.values()[0].axes]

  msg = {"expers":expers, "axes":axes}

  return HttpResponse(dumps(msg))


def return_list_ops(request,project):

  context = RequestContext(request)
  D = sg.info_dict()
  P = sg.Project(D[project])
  E = P.expers.values()[0]

#  axes = [ax.name for ax in P.expers.values()[0].axes]

  msg = list_ops(P,E)

 

  return HttpResponse(dumps(msg))




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

 # print args

  fld = getattr(fld,method)(args)
  msg = make_json(fld)
  return HttpResponse(msg)



def ret_field_ops(request, project,exp, field):
  """
  project: (str) project name
  exp: (str) experiment name 
  field: (str) field name
  """

  context = RequestContext(request)

  comstr = request.GET['ops']

  fld, P, E = get_field(project,exp, field)

  knownobs = build_knownobs(P,E)

  ops = interpret(comstr,knownobs,obchain=[] )[-1]

  print ops

#  fld = getattr(fld,method)(args)
  msg = make_json(ops(fld) )
  return HttpResponse(msg)






def gmaps(request):
	context = RequestContext(request)
	return render_to_response('sgdata/gmaps.html', context)

