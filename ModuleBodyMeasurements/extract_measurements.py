

import numpy as np
import sys
import os
from . import utils

# 🔹 Base directory of this module
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, "data")


# loading data: file_list, vertex, mean, std
#def obj2npy(label="male"):
#    
#  OBJ_DIR = os.path.join(DATA_DIR, "obj")
#  
#  obj_file_dir = os.path.join(OBJ_DIR, label)
##  print("File directory = ",obj_file_dir)
#  file_list = os.listdir(obj_file_dir)
#
#  # load original data
#  vertex = []
#  for i, obj in enumerate(file_list):
#    sys.stdout.write('\r>> Converting %s body %d\n'%(label, i))
#    sys.stdout.flush()
#    f = open(os.path.join(obj_file_dir, obj), 'r')
#    j = 0
#    for line in f:
#      if line[0] == '#':
#        continue
#      elif "v " in line:
#        line.replace('\n', ' ')
#        tmp = list(map(float, line[1:].split()))
#        vertex.append(tmp)
#        j += 1
#      else:
#        break
# 
#  vertex = np.array(vertex).reshape(len(file_list), utils.V_NUM, 3)#utils.V_NUM
##  print("Vertex are of type = ",type(vertex)) 
##  print("vertex = ",vertex)
#
#  return vertex



# read control  points(CP) from text file
def convert_cp():
    
  f = open(os.path.join(DATA_DIR, 'customBodyPoints.txt'), "r")

  tmplist = []
  cp = []
  for line in f:
    if '#' in line:
      if len(tmplist) != 0:
        cp.append(tmplist)
        tmplist = []
    elif len(line.split()) == 1:
      continue
    else:
      tmplist.append(list(map(float, line.strip().split())))
  cp.append(tmplist)


  return cp


# calculate measure data from given vertex by control points
def calc_measure(cp, vertex,height):#, facet):
  measure_list = []
  
  for measure in cp:
#    print("#########################",measure)  
#    print("@@@@@@@@@@@@")

    length = 0.0
    p2 = vertex[int(measure[0][1]), :]

    for i in range(0, len(measure)):#1
      p1 = p2
      if measure[i][0] == 1:
        p2 = vertex[int(measure[i][1]), :]  
        
      elif measure[i][0] == 2:
        p2 = vertex[int(measure[i][1]), :] * measure[i][3] + \
        vertex[int(measure[i][2]), :] * measure[i][4]
#        print("if 2 Measurement",int(measure[i][1]))
        
      else:
        p2 = vertex[int(measure[i][1]), :] * measure[i][4] + \
          vertex[int(measure[i][2]), :] * measure[i][5] + \
          vertex[int(measure[i][3]), :] * measure[i][6]
      length += np.sqrt(np.sum((p1 - p2)**2.0))

    measure_list.append(length * 100)# * 1000
  
  measure_list = float(height)*(measure_list/measure_list[0])
#  print("measure list = ",float(height)*(measure_list/measure_list[0])) 
  measure_list[8] = measure_list[8] * 0.36#reducing the error in measurement added due to unarranged vertices
  measure_list[3] = measure_list[3] * 0.6927
#  print("measure list = ",float(height)*(measure_list/measure_list[0]))
#  measure_list = float(height)*(measure_list/measure_list[0])
  return np.array(measure_list).reshape(utils.M_NUM, 1)


##added code: extract body measurements given a .obj model in data.
def extract_measurements(height, vertices):
    genders = ["male"]
    measure = []

    cp = convert_cp()
    measure = calc_measure(cp, vertices, height)

    # give body measurements one by one
    for i in range(utils.M_NUM):
        print("%s: %f" % (utils.M_STR[i], measure[i]))

    # Save 3D mesh as OBJ
    face_path = os.path.join(BASE_DIR, 'src', 'tf_smpl', 'smpl_faces.npy')
    faces = np.load(face_path)

    obj_mesh_name = os.path.join(BASE_DIR, 'test.obj')
    with open(obj_mesh_name, 'w') as fp:
        for v in vertices:
            fp.write('v %f %f %f\n' % (v[0], v[1], v[2]))
        for f in faces:
            fp.write('f %d %d %d\n' % (f[0] + 1, f[1] + 1, f[2] + 1))

    print("Model Saved...")
    # RETURN results as dict
    return {utils.M_STR[i]: float(measure[i]) for i in range(utils.M_NUM)}

#if __name__ == "__main__":
#  extract_measurements()
  
