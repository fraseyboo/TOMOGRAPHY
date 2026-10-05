import numpy as np
from matplotlib import pyplot as plt
import os
import sys


import matplotlib
matplotlib.use('Qt5agg')

import pathlib
from tqdm import tqdm

try:
    plt.rcParams.update({
    "text.usetex": True,
    "font.family": "serif",
    'font.size': 12,
    })
except:
    print('Could not Latexify labels')


#variables 

material_dict = dict()
material_dict.update({'A005.obj':'Germanium'})
material_dict.update({'A005_small.obj':'Germanium'})

#definitions
def make_vertex_string(x, y, z, index, unique_name='v', unit='mm'):

    x = float(x)
    y = float(y)
    z = float(z)
    

    vstring = '    <position name="%s%i" x="%.3f" y="%.3f" z="%.3f" unit="%s"/>\n' % (unique_name, index, x, y, z, unit)

    # print(vstring)

    return vstring


def make_faces_string(p1, p2, p3,  unique_name='v', type='ABSOLUTE'):

    print('p1:', p1)
    print('p2:', p2)
    print('p3:', p3)

    split1 = p1.split('//')[0]
    split2 = p2.split('//')[0]
    split3 = p3.split('//')[0]

    p1 = split1
    p2 = split2
    p3 = split3

    p1 = int(p1)
    p2 = int(p2)
    p3 = int(p3)

    fstring = '        <triangular vertex1="%s%i" vertex2="%s%i" vertex3="%s%i" type="%s"/>\n' % (unique_name, p1, unique_name, p2, unique_name, p3, type)

    # print(fstring)

    return fstring






def read_obj(filepath, filename, unique_name=None, line_limit=10,):

    if unique_name is None:
        unique_name = filename[:-4] + '_v'

    vertex_count=1 

    lines_read = 0
    if line_limit is None:
        line_limit = np.inf
        print('line limit not specified, reading full file')

    vertex_string_list = list()
    faces_string_list = list()

    with open(filepath) as openfileobject:
        for line in tqdm(openfileobject, desc='Reading %s' %filename):

            # print(line, end=" ")
            
            #if condition to find vertices (values start with v)
            if line[0:2] == "v ":
                values= line[2:].split()
                # print("These are your values:", values)
                output_vertex_string = make_vertex_string(values[0], values[1], values[2], vertex_count, unique_name=unique_name)
                vertex_string_list.append(output_vertex_string)
                vertex_count = vertex_count +1 

            if line[0:1] == "f":
                values= line[2:].split()
                # print("These are your values:", values)
                output_faces_string = make_faces_string(values[0], values[1], values[2], unique_name=unique_name)
                faces_string_list.append(output_faces_string)


            lines_read += 1

    # print(vertex_string_list)
    # print(faces_string_list)



    return vertex_string_list, faces_string_list

def write_GDML(output_filename, vertex_string_list, faces_string_list, material = 'LaBr3'):

    print('Writing to', output_filename) 

    volume_name = output_filename[:-5] + "_vol"
    tessellated_name = output_filename[:-5] + "_tess"

    material_line = "		<materialref ref=\"%s\"/>\n" % (material)
    tesselated_line = "    <tessellated name=\"%s\">\n" % (tessellated_name) 
    volume_line = "    <volume name=\"%s\">\n" % (volume_name)
    solidref_line = "           <solidref ref=\"%s\"/>\n" % (tessellated_name)
    volumeref_line = "			<volumeref ref=\"%s\"/>\n" % (volume_name)
    with open(output_filename, 'w') as output_file:

        output_file.write(header_string)
        for vertex_line in vertex_string_list:
            output_file.write(vertex_line)
        output_file.write(header_string2)
        output_file.write(header_string3)

        output_file.write(tesselated_line)
        for faces_line in faces_string_list:
            output_file.write(faces_line)
        output_file.write(header_string4)
        output_file.write(volume_line)
        output_file.write(material_line)
        output_file.write(solidref_line)
        output_file.write(header_string5)
        output_file.write(volumeref_line)
        output_file.write(header_string6)
    print('File written')


def read_directory(folderpath):

    file_list = sorted(os.listdir(folderpath))

    volume_names = list()
    tessellated_names = list()
    materials = list()
    vertex_string_list_list = list()
    faces_string_list_list = list()

    for filename in file_list:
        if filename.endswith('.obj'):
            file_path = folderpath + os.sep + filename

            volume_name = filename[:-4] + "_vol"
            tessellated_name = filename[:-4] + "_tess"
            material = material_dict[filename]

            vertex_string_list, faces_string_list = read_obj(file_path, filename=filename)

            volume_names.append(volume_name)
            tessellated_names.append(tessellated_name)
            materials.append(material)
            vertex_string_list_list.append(vertex_string_list)
            faces_string_list_list.append(faces_string_list)

    return vertex_string_list_list, faces_string_list_list, volume_names, tessellated_names, materials


def write_multi_GDML(output_filename, vertex_string_list_list, faces_string_list_list, tessellated_names, volume_names, materials):

    print('Writing to', output_filename) 

    # volume_name = output_filename[:-5] + "_vol"
    # tessellated_name = output_filename[:-5] + "_tess"

    # material_line = "		<materialref ref=\"%s\"/>\n" % (material)
    # volume_line = "    <volume name=\"%s\">\n" % (volume_name)
    # solidref_line = "           <solidref ref=\"%s\"/>\n" % (tessellated_name)
    

    with open(output_filename, 'w') as output_file:

        output_file.write(header_string)
        for vertex_string_list in vertex_string_list_list:
            for vertex_line in vertex_string_list:
                output_file.write(vertex_line)
            output_file.write('\n')
        output_file.write(header_string2)
        output_file.write(header_string3)


        for tessellated_name, faces_string_list in zip(tessellated_names, faces_string_list_list):
        
            output_file.write("    <tessellated name=\"%s\">\n" % (tessellated_name))
            for faces_line in faces_string_list:
                output_file.write(faces_line)
            output_file.write('    </tessellated>\n')
            output_file.write('\n')

            
        output_file.write(header_string4)



        for tessellated_name, volume_name, material in zip(tessellated_names, volume_names, materials):
       
            volume_chunk1 ="    <volume name=\"%s\">\n	   <materialref ref=\"%s\"/>\n           <solidref ref=\"%s\"/>\n" % (volume_name, material, tessellated_name)
            volume_chunk2 ="    </volume>\n" 
            output_file.write(volume_chunk1)
            if "sensitive" in tessellated_name:
                print('Sensitive volume to be written:', tessellated_name)
                output_file.write("           <auxiliary auxtype=\"SensDet\" auxvalue=\"Tracker_%s\"/>\n           <auxiliary auxtype=\"Color\" auxvalue=\"Blue\"/>\n" % tessellated_name)
            if "reflective" in tessellated_name:
                print('Reflective volume to be written:', tessellated_name)
                output_file.write("           <auxiliary auxtype=\"Reflective\" auxvalue=\"%s\"/>\n" % material)

            output_file.write(volume_chunk2)

        # output_file.write(volume_line)
        # output_file.write(material_line)
        # output_file.write(solidref_line)


        output_file.write(header_string5)

        for volume_name in volume_names:
            output_file.write("		<physvol>\n")
            output_file.write("			<volumeref ref=\"%s\"/>\n" % (volume_name))
            output_file.write("			<position name=\"posref_%s\" x=\"0.0\" y=\"0.0\" z=\"0.0\"/>\n" % (volume_name))
            output_file.write("		</physvol>\n")

        output_file.write(header_string6)
    print('File written')


def main():

    vertex_string_list_list, faces_string_list_list, volume_names, tessellated_names, materials = read_directory(folderpath='/home/grtdaq/Documents/PROJECTS/TOMOGRAPHY')

    write_multi_GDML('joined_small.gdml', vertex_string_list_list, faces_string_list_list, volume_names, tessellated_names, materials)






header_string = r"""<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
<gdml xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://service-spi.web.cern.ch/service-spi/app/releases/GDML/schema/gdml.xsd">

<define>

    <matrix coldim="2" name="AIRRINDEX" values="2.034*eV 1 2.068*eV 1 2.103*eV 1 2.139*eV 1 2.177*eV 1 2.216*eV 1 2.256*eV 1 2.298*eV 1 2.341*eV 1 2.386*eV 1 2.433*eV 1 2.481*eV 1 2.532*eV 1 2.585*eV 1 2.64*eV 1 2.697*eV 1 2.757*eV 1 2.82*eV 1 2.885*eV 1 2.954*eV 1 3.026*eV 1 3.102*eV 1 3.181*eV 1 3.265*eV 1 3.353*eV 1 3.446*eV 1 3.545*eV 1 3.649*eV 1 3.76*eV 1 3.877*eV 1 4.002*eV 1 4.136*eV 1"/>
    <matrix coldim="2" name="REFLECTIVITY" values="2.034*eV 0.3 4.136*eV 0.5"/>
    <matrix coldim="2" name="EFFICIENCY" values="2.034*eV 0.8 4.136*eV 1"/>
    <matrix coldim="2" name="WATERRINDEX" values="2.034*eV 1.3435 2.068*eV 1.344 2.103*eV 1.3445 2.139*eV 1.345 2.177*eV 1.3455 2.216*eV 1.346 2.256*eV 1.3465 2.298*eV 1.347 2.341*eV 1.3475 2.386*eV 1.348 2.433*eV 1.3485 2.481*eV 1.3492 2.532*eV 1.35 2.585*eV 1.3505 2.64*eV 1.351 2.697*eV 1.3518 2.757*eV 1.3522 2.82*eV 1.353 2.885*eV 1.3535 2.954*eV 1.354 3.026*eV 1.3545 3.102*eV 1.355 3.181*eV 1.3555 3.265*eV 1.356 3.353*eV 1.3568 3.446*eV 1.3572 3.545*eV 1.358 3.649*eV 1.3585 3.76*eV 1.359 3.877*eV 1.3595 4.002*eV 1.36 4.136*eV 1.3608"/>
    <matrix coldim="2" name="WATERMIEHG" values="1.56962*eV 1.67024e+08 1.58974*eV 1.58727e+08 1.61039*eV 1.50742e+08 1.63157*eV 1.43062e+08 1.65333*eV 1.3568e+08 1.67567*eV 1.28587e+08 1.69863*eV 1.21776e+08 1.72222*eV 1.1524e+08 1.74647*eV 1.0897e+08 1.77142*eV 1.02959e+08 1.7971*eV 9.72004e+07 1.82352*eV 9.16869e+07 1.85074*eV 8.64113e+07 1.87878*eV 8.13668e+07 1.90769*eV 7.65464e+07 1.93749*eV 7.19435e+07 1.96825*eV 6.75513e+07 1.99999*eV 6.33634e+07 2.03278*eV 5.93732e+07 2.06666*eV 5.55746e+07 2.10169*eV 5.19612e+07 2.13793*eV 4.8527e+07 2.17543*eV 4.52659e+07 2.21428*eV 4.21719e+07 2.25454*eV 3.92394e+07 2.29629*eV 3.64625e+07 2.33962*eV 3.38357e+07 2.38461*eV 3.13534e+07 2.43137*eV 2.90103e+07 2.47999*eV 2.6801e+07 2.53061*eV 2.47204e+07 2.58333*eV 2.27634e+07 2.63829*eV 2.09249e+07 2.69565*eV 1.92001e+07 2.75555*eV 1.75842e+07 2.81817*eV 1.60724e+07 2.88371*eV 1.46604e+07 2.95237*eV 1.33435e+07 3.02438*eV 1.21173e+07 3.09999*eV 1.09777e+07 3.17948*eV 9.92042e+06 3.26315*eV 8.94141e+06 3.35134*eV 8.03671e+06 3.44444*eV 7.20247e+06 3.54285*eV 6.43493e+06 3.64705*eV 5.73043e+06 3.75757*eV 5.08542e+06 3.87499*eV 4.49647e+06 3.99999*eV 3.96021e+06 4.13332*eV 3.47341e+06 4.27585*eV 3.03294e+06 4.42856*eV 2.63575e+06 4.59258*eV 2.27891e+06 4.76922*eV 1.95959e+06 4.95999*eV 1.67506e+06 5.16665*eV 1.42271e+06 5.39129*eV 1.2e+06 5.63635*eV 1.00453e+06 5.90475*eV 833967 6.19998*eV 686106"/>
    <matrix coldim="2" name="WATERABSLENGTH" values="2.034*eV 3448 2.068*eV 4082 2.103*eV 6329 2.139*eV 9174 2.177*eV 12346 2.216*eV 13889 2.256*eV 15152 2.298*eV 17241 2.341*eV 18868 2.386*eV 20000 2.433*eV 26316 2.481*eV 35714 2.532*eV 45455 2.585*eV 47619 2.64*eV 52632 2.697*eV 52632 2.757*eV 55556 2.82*eV 52632 2.885*eV 52632 2.954*eV 47619 3.026*eV 45455 3.102*eV 41667 3.181*eV 37037 3.265*eV 33333 3.353*eV 30000 3.446*eV 28500 3.545*eV 27000 3.649*eV 24500 3.76*eV 22000 3.877*eV 19500 4.002*eV 17500 4.136*eV 14500"/>
    <matrix coldim="2" name="WATERSCINTILLATIONCOMPONENT1" values="2.034*eV 1 2.068*eV 1 2.103*eV 1 2.139*eV 1 2.177*eV 1 2.216*eV 1 2.256*eV 1 2.298*eV 1 2.341*eV 1 2.386*eV 1 2.433*eV 1 2.481*eV 1 2.532*eV 1 2.585*eV 1 2.64*eV 1 2.697*eV 1 2.757*eV 1 2.82*eV 1 2.885*eV 1 2.954*eV 1 3.026*eV 1 3.102*eV 1 3.181*eV 1 3.265*eV 1 3.353*eV 1 3.446*eV 1 3.545*eV 1 3.649*eV 1 3.76*eV 1 3.877*eV 1 4.002*eV 1 4.136*eV 1"/>
    <matrix coldim="2" name="WATERSCINTILLATIONCOMPONENT2" values="2.034*eV 0.01 2.068*eV 1 2.103*eV 2 2.139*eV 3 2.177*eV 4 2.216*eV 5 2.256*eV 6 2.298*eV 7 2.341*eV 8 2.386*eV 9 2.433*eV 8 2.481*eV 7 2.532*eV 6 2.585*eV 4 2.64*eV 3 2.697*eV 2 2.757*eV 1 2.82*eV 0.01 2.885*eV 1 2.954*eV 2 3.026*eV 3 3.102*eV 4 3.181*eV 5 3.265*eV 6 3.353*eV 7 3.446*eV 8 3.545*eV 9 3.649*eV 8 3.76*eV 7 3.877*eV 6 4.002*eV 5 4.136*eV 4"/>
    <matrix coldim="1" name="WATERMIEHG_FORWARD" values="0.99"/>
    <matrix coldim="1" name="WATERMIEHG_BACKWARD" values="0.99"/>
    <matrix coldim="1" name="WATERMIEHG_FORWARD_RATIO" values="0.8"/>
    <matrix coldim="1" name="WATERSCINTILLATIONYIELD" values="50"/>
    <matrix coldim="1" name="WATERRESOLUTIONSCALE" values="1"/>
    <matrix coldim="1" name="WATERSCINTILLATIONTIMECONSTANT1" values="1"/>
    <matrix coldim="1" name="WATERSCINTILLATIONTIMECONSTANT2" values="10"/>
    <matrix coldim="1" name="WATERSCINTILLATIONYIELD1" values="0.8"/>
    <matrix coldim="1" name="WATERSCINTILLATIONYIELD2" values="0.2"/>
  
    <matrix coldim="2" name="LABR3INDEX" values="1.77375*eV 2.02640 1.77629*eV 2.02640 1.77884*eV 2.02640 1.78140*eV 2.02664 1.78396*eV 2.02691 1.78653*eV 2.02718 1.78911*eV 2.02735 1.79169*eV 2.02749 1.79429*eV 2.02763 1.79689*eV 2.02789 1.79949*eV 2.02818 1.80211*eV 2.02846 1.80473*eV 2.02872 1.80736*eV 2.02897 1.81000*eV 2.02922 1.81265*eV 2.02949 1.81530*eV 2.02975 1.81796*eV 2.03002 1.82063*eV 2.03028 1.82331*eV 2.03054 1.82600*eV 2.03079 1.82869*eV 2.03103 1.83139*eV 2.03119 1.83410*eV 2.03134 1.83682*eV 2.03152 1.83954*eV 2.03176 1.84228*eV 2.03200 1.84502*eV 2.03224 1.84777*eV 2.03255 1.85052*eV 2.03287 1.85329*eV 2.03320 1.85607*eV 2.03352 1.85885*eV 2.03397 1.86164*eV 2.03443 1.86444*eV 2.03488 1.86725*eV 2.03527 1.87006*eV 2.03547 1.87289*eV 2.03567 1.87572*eV 2.03587 1.87856*eV 2.03606 1.88141*eV 2.03629 1.88427*eV 2.03652 1.88714*eV 2.03675 1.89002*eV 2.03702 1.89290*eV 2.03738 1.89580*eV 2.03774 1.89870*eV 2.03810 1.90161*eV 2.03852 1.90453*eV 2.03895 1.90746*eV 2.03939 1.91040*eV 2.03982 1.91335*eV 2.04022 1.91631*eV 2.04061 1.91928*eV 2.04101 1.92225*eV 2.04141 1.92524*eV 2.04183 1.92823*eV 2.04226 1.93123*eV 2.04270 1.93425*eV 2.04313 1.93727*eV 2.04338 1.94030*eV 2.04360 1.94334*eV 2.04382 1.94639*eV 2.04403 1.94945*eV 2.04427 1.95252*eV 2.04451 1.95560*eV 2.04475 1.95869*eV 2.04500 1.96179*eV 2.04525 1.96490*eV 2.04550 1.96802*eV 2.04575 1.97115*eV 2.04598 1.97429*eV 2.04621 1.97743*eV 2.04644 1.98059*eV 2.04668 1.98376*eV 2.04693 1.98694*eV 2.04718 1.99013*eV 2.04748 1.99333*eV 2.04801 1.99654*eV 2.04855 1.99976*eV 2.04908 2.00299*eV 2.04962 2.00623*eV 2.05016 2.00948*eV 2.05069 2.01275*eV 2.05098 2.01602*eV 2.05123 2.01930*eV 2.05148 2.02260*eV 2.05174 2.02590*eV 2.05199 2.02922*eV 2.05224 2.03254*eV 2.05255 2.03588*eV 2.05303 2.03923*eV 2.05351 2.04259*eV 2.05399 2.04596*eV 2.05440 2.04934*eV 2.05478 2.05273*eV 2.05516 2.05614*eV 2.05553 2.05955*eV 2.05589 2.06298*eV 2.05625 2.06642*eV 2.05661 2.06987*eV 2.05703 2.07333*eV 2.05747 2.07680*eV 2.05790 2.08029*eV 2.05833 2.08378*eV 2.05877 2.08729*eV 2.05920 2.09081*eV 2.05964 2.09434*eV 2.06007 2.09789*eV 2.06048 2.10144*eV 2.06089 2.10501*eV 2.06131 2.10859*eV 2.06174 2.11218*eV 2.06231 2.11579*eV 2.06288 2.11940*eV 2.06345 2.12303*eV 2.06402 2.12668*eV 2.06459 2.13033*eV 2.06516 2.13400*eV 2.06573 2.13768*eV 2.06634 2.14137*eV 2.06698 2.14507*eV 2.06761 2.14879*eV 2.06813 2.15252*eV 2.06848 2.15626*eV 2.06884 2.16002*eV 2.06920 2.16379*eV 2.06960 2.16757*eV 2.06999 2.17137*eV 2.07039 2.17518*eV 2.07079 2.17900*eV 2.07130 2.18284*eV 2.07187 2.18669*eV 2.07244 2.19055*eV 2.07294 2.19443*eV 2.07342 2.19832*eV 2.07390 2.20222*eV 2.07438 2.20614*eV 2.07483 2.21007*eV 2.07529 2.21402*eV 2.07574 2.21798*eV 2.07616 2.22196*eV 2.07654 2.22595*eV 2.07692 2.22995*eV 2.07735 2.23397*eV 2.07799 2.23800*eV 2.07862 2.24205*eV 2.07925 2.24611*eV 2.07964 2.25018*eV 2.07999 2.25428*eV 2.08035 2.25838*eV 2.08086 2.26250*eV 2.08158 2.26664*eV 2.08230 2.27079*eV 2.08302 2.27496*eV 2.08360 2.27914*eV 2.08417 2.28334*eV 2.08474 2.28755*eV 2.08533 2.29178*eV 2.08600 2.29602*eV 2.08667 2.30028*eV 2.08733 2.30456*eV 2.08785 2.30885*eV 2.08836 2.31316*eV 2.08888 2.31748*eV 2.08940 2.32182*eV 2.08997 2.32618*eV 2.09054 2.33055*eV 2.09111 2.33494*eV 2.09169 2.33934*eV 2.09229 2.34376*eV 2.09289 2.34820*eV 2.09349 2.35266*eV 2.09402 2.35713*eV 2.09454 2.36162*eV 2.09505 2.36613*eV 2.09557 2.37065*eV 2.09623 2.37519*eV 2.09692 2.37975*eV 2.09761 2.38433*eV 2.09831 2.38892*eV 2.09898 2.39354*eV 2.09963 2.39817*eV 2.10028 2.40281*eV 2.10093 2.40748*eV 2.10172 2.41216*eV 2.10257 2.41686*eV 2.10342 2.42159*eV 2.10428 2.42632*eV 2.10509 2.43108*eV 2.10579 2.43586*eV 2.10648 2.44065*eV 2.10717 2.44547*eV 2.10787 2.45030*eV 2.10863 2.45515*eV 2.10938 2.46002*eV 2.11014 2.46491*eV 2.11090 2.46982*eV 2.11160 2.47475*eV 2.11231 2.47970*eV 2.11302 2.48467*eV 2.11372 2.48966*eV 2.11443 2.49467*eV 2.11523 2.49970*eV 2.11606 2.50475*eV 2.11689 2.50982*eV 2.11772 2.51491*eV 2.11859 2.52002*eV 2.11948 2.52516*eV 2.12037 2.53031*eV 2.12127 2.53548*eV 2.12237 2.54068*eV 2.12369 2.54590*eV 2.12501 2.55114*eV 2.12633 2.55640*eV 2.12702 2.56168*eV 2.12772 2.56698*eV 2.12841 2.57231*eV 2.12910 2.57765*eV 2.12984 2.58302*eV 2.13060 2.58842*eV 2.13136 2.59383*eV 2.13212 2.59927*eV 2.13293 2.60473*eV 2.13384 2.61021*eV 2.13475 2.61572*eV 2.13566 2.62125*eV 2.13658 2.62680*eV 2.13773 2.63238*eV 2.13899 2.63798*eV 2.14024 2.64361*eV 2.14149 2.64926*eV 2.14258 2.65493*eV 2.14367 2.66063*eV 2.14477 2.66635*eV 2.14586 2.67209*eV 2.14687 2.67787*eV 2.14776 2.68366*eV 2.14865 2.68948*eV 2.14954 2.69533*eV 2.15045 2.70120*eV 2.15144 2.70710*eV 2.15243 2.71302*eV 2.15342 2.71897*eV 2.15441 2.72495*eV 2.15536 2.73095*eV 2.15631 2.73698*eV 2.15726 2.74303*eV 2.15821 2.74912*eV 2.15945 2.75523*eV 2.16097 2.76136*eV 2.16249 2.76753*eV 2.16401 2.77372*eV 2.16538 2.77994*eV 2.16667 2.78618*eV 2.16795 2.79246*eV 2.16924 2.79876*eV 2.17049 2.80509*eV 2.17168 2.81146*eV 2.17286 2.81784*eV 2.17405 2.82426*eV 2.17525 2.83071*eV 2.17650 2.83719*eV 2.17776 2.84370*eV 2.17901 2.85023*eV 2.18029 2.85680*eV 2.18161 2.86340*eV 2.18293 2.87003*eV 2.18425 2.87669*eV 2.18583 2.88338*eV 2.18741 2.89010*eV 2.18900 2.89685*eV 2.19058 2.90363*eV 2.19197 2.91045*eV 2.19329 2.91730*eV 2.19461 2.92418*eV 2.19601 2.93109*eV 2.19769 2.93804*eV 2.19937 2.94502*eV 2.20105 2.95203*eV 2.20270 2.95907*eV 2.20434 2.96615*eV 2.20599 2.97327*eV 2.20756 2.98041*eV 2.20903 2.98759*eV 2.21050 2.99481*eV 2.21202 3.00206*eV 2.21373 3.00935*eV 2.21543 3.01667*eV 2.21714 3.02403*eV 2.21891 3.03142*eV 2.22074 3.03885*eV 2.22256 3.04632*eV 2.22438 3.05382*eV 2.22620 3.06136*eV 2.22819 3.06894*eV 2.23018 3.07656*eV 2.23217 3.08421*eV 2.23408 3.09190*eV 2.23579 3.09963*eV 2.23750 3.10740*eV 2.23921 3.11521*eV 2.24113 3.12305*eV 2.24318 3.13094*eV 2.24523 3.13886*eV 2.24728 3.14683*eV 2.24934 3.15484*eV 2.25161 3.16289*eV 2.25389 3.17098*eV 2.25617 3.17911*eV 2.25834 3.18728*eV 2.26034 3.19549*eV 2.26233 3.20375*eV 2.26432 3.21205*eV 2.26678 3.22039*eV 2.26944 3.22878*eV 2.27209 3.23721*eV 2.27470 3.24568*eV 2.27730 3.25420*eV 2.27990 3.26277*eV 2.28248 3.27138*eV 2.28504 3.28003*eV 2.28760 3.28873*eV 2.29019 3.29748*eV 2.29312 3.30627*eV 2.29604 3.31511*eV 2.29897 3.32400*eV 2.30199 3.33293*eV 2.30503 3.34192*eV 2.30802 3.35095*eV 2.31063 3.36003*eV 2.31323 3.36916*eV 2.31583 3.37834*eV 2.31844 3.38757*eV 2.32104 3.39685*eV 2.32364 3.40619*eV 2.32695 3.41557*eV 2.33060 3.42500*eV 2.33424 3.43449*eV 2.33788 3.44403*eV 2.34140 3.45363*eV 2.34368 3.46327*eV 2.34596 3.47297*eV 2.34824 3.48273*eV 2.35051 3.49254*eV 2.35283 3.50241*eV 2.35586 3.51233*eV 2.35890 3.52231*eV 2.36221 3.53234*eV 2.36620 3.54243*eV 2.36831"/>
    <matrix coldim="2" name="LABR3MIEHG" values="2.43*eV 198.08 2.44*eV 197.72 2.45*eV 196.47 2.46*eV 195.28 2.47*eV 194.21 2.48*eV 193.06 2.49*eV 191.99 2.50*eV 190.67 2.51*eV 189.40 2.52*eV 188.29 2.53*eV 187.02 2.55*eV 185.42 2.56*eV 184.33 2.57*eV 183.26 2.58*eV 181.99 2.59*eV 180.73 2.60*eV 179.64 2.61*eV 178.35 2.62*eV 177.14 2.64*eV 176.04 2.65*eV 174.88 2.66*eV 173.74 2.67*eV 172.49 2.68*eV 171.25 2.69*eV 170.15 2.71*eV 168.84 2.72*eV 167.87 2.73*eV 166.58 2.74*eV 165.35 2.75*eV 164.23 2.77*eV 163.00 2.78*eV 161.78 2.79*eV 160.59 2.81*eV 159.52 2.82*eV 158.41 2.83*eV 157.22 2.85*eV 156.07 2.86*eV 154.82 2.87*eV 153.59 2.89*eV 152.47 2.90*eV 151.18 2.91*eV 150.21 2.93*eV 148.42 2.95*eV 147.32 2.96*eV 146.13 2.98*eV 144.82 2.99*eV 143.67 3.01*eV 142.49 3.02*eV 141.43 3.04*eV 140.23 3.05*eV 139.01 3.07*eV 137.83 3.08*eV 136.57 3.10*eV 135.33 3.11*eV 134.19 3.13*eV 133.15 3.15*eV 132.09 3.16*eV 130.73 3.18*eV 129.65 3.20*eV 128.45 3.21*eV 127.21 3.23*eV 126.07 3.25*eV 124.79 3.26*eV 123.81 3.28*eV 122.54 3.30*eV 121.25 3.32*eV 120.16 3.34*eV 118.96 3.35*eV 117.65 3.37*eV 116.56 3.39*eV 115.42 3.41*eV 114.30 3.43*eV 113.11 3.46*eV 111.63 3.47*eV 110.72 3.49*eV 109.47 3.51*eV 108.33 3.53*eV 107.18 3.55*eV 106.02 3.57*eV 104.86 3.59*eV 103.60 3.61*eV 102.38 3.64*eV 101.23"/>
    <matrix coldim="2" name="LABR3ABSLENGTH" values="2.034*eV 3448 2.068*eV 4082 2.103*eV 6329 2.139*eV 9174 2.177*eV 12346 2.216*eV 13889 2.256*eV 15152 2.298*eV 17241 2.341*eV 18868 2.386*eV 20000 2.433*eV 26316 2.481*eV 35714 2.532*eV 45455 2.585*eV 47619 2.64*eV 52632 2.697*eV 52632 2.757*eV 55556 2.82*eV 52632 2.885*eV 52632 2.954*eV 47619 3.026*eV 45455 3.102*eV 41667 3.181*eV 37037 3.265*eV 33333 3.353*eV 30000 3.446*eV 28500 3.545*eV 27000 3.649*eV 24500 3.76*eV 22000 3.877*eV 19500 4.002*eV 17500 4.136*eV 14500"/>
    
    <matrix coldim="2" name="LABR3SCINTILLATIONCOMPONENT1" values="2.82*eV 0.00 2.83*eV 0.00 2.84*eV 0.00 2.84*eV 0.00 2.85*eV 0.00 2.86*eV 0.00 2.86*eV 0.00 2.87*eV 0.01 2.88*eV 0.01 2.88*eV 0.01 2.89*eV 0.01 2.90*eV 0.02 2.90*eV 0.02 2.91*eV 0.02 2.92*eV 0.03 2.92*eV 0.04 2.93*eV 0.05 2.94*eV 0.06 2.95*eV 0.07 2.95*eV 0.08 2.96*eV 0.10 2.97*eV 0.12 2.97*eV 0.15 2.98*eV 0.18 2.99*eV 0.21 2.99*eV 0.25 3.00*eV 0.30 3.01*eV 0.35 3.02*eV 0.41 3.02*eV 0.48 3.03*eV 0.56 3.04*eV 0.64 3.05*eV 0.74 3.05*eV 0.85 3.06*eV 0.96 3.07*eV 1.09 3.08*eV 1.23 3.08*eV 1.38 3.09*eV 1.54 3.10*eV 1.71 3.11*eV 1.88 3.12*eV 2.06 3.12*eV 2.25 3.13*eV 2.44 3.14*eV 2.63 3.15*eV 2.82 3.15*eV 3.01 3.16*eV 3.18 3.17*eV 3.35 3.18*eV 3.50 3.19*eV 3.64 3.20*eV 3.76 3.20*eV 3.85 3.21*eV 3.93 3.22*eV 3.97 3.23*eV 3.99 3.24*eV 3.98 3.25*eV 3.94 3.25*eV 3.87 3.26*eV 3.78 3.27*eV 3.66 3.28*eV 3.52 3.29*eV 3.36 3.30*eV 3.18 3.31*eV 2.98 3.32*eV 2.78 3.32*eV 2.56 3.33*eV 2.35 3.34*eV 2.13 3.35*eV 1.92 3.36*eV 1.71 3.37*eV 1.51 3.38*eV 1.33 3.39*eV 1.15 3.40*eV 0.99 3.41*eV 0.84 3.42*eV 0.71 3.43*eV 0.60 3.43*eV 0.49 3.44*eV 0.40 3.45*eV 0.33 3.46*eV 0.26 3.47*eV 0.21 3.48*eV 0.16 3.49*eV 0.13 3.50*eV 0.10 3.51*eV 0.07 3.52*eV 0.06 3.53*eV 0.04 3.54*eV 0.03 3.55*eV 0.02 3.56*eV 0.02 3.57*eV 0.01 3.58*eV 0.01 3.59*eV 0.01 3.60*eV 0.00 3.61*eV 0.00 3.63*eV 0.00 3.64*eV 0.00 3.65*eV 0.00 3.66*eV 0.00 3.67*eV 0.00 3.68*eV 0.00 3.69*eV 0.00 3.70*eV 0.00 3.71*eV 0.00 3.72*eV 0.00 3.73*eV 0.00 3.75*eV 0.00 3.76*eV 0.00"/>
    <matrix coldim="2" name="LABR3SCINTILLATIONCOMPONENT2" values="2.82*eV 0.00 2.83*eV 0.00 2.84*eV 0.00 2.84*eV 0.00 2.85*eV 0.00 2.86*eV 0.00 2.86*eV 0.00 2.87*eV 0.00 2.88*eV 0.00 2.88*eV 0.00 2.89*eV 0.00 2.90*eV 0.00 2.90*eV 0.00 2.91*eV 0.00 2.92*eV 0.00 2.92*eV 0.00 2.93*eV 0.00 2.94*eV 0.00 2.95*eV 0.00 2.95*eV 0.00 2.96*eV 0.00 2.97*eV 0.00 2.97*eV 0.00 2.98*eV 0.00 2.99*eV 0.00 2.99*eV 0.00 3.00*eV 0.00 3.01*eV 0.00 3.02*eV 0.00 3.02*eV 0.00 3.03*eV 0.00 3.04*eV 0.00 3.05*eV 0.00 3.05*eV 0.00 3.06*eV 0.00 3.07*eV 0.00 3.08*eV 0.00 3.08*eV 0.00 3.09*eV 0.00 3.10*eV 0.00 3.11*eV 0.00 3.12*eV 0.00 3.12*eV 0.00 3.13*eV 0.00 3.14*eV 0.00 3.15*eV 0.00 3.15*eV 0.01 3.16*eV 0.01 3.17*eV 0.01 3.18*eV 0.02 3.19*eV 0.02 3.20*eV 0.03 3.20*eV 0.04 3.21*eV 0.05 3.22*eV 0.07 3.23*eV 0.09 3.24*eV 0.12 3.25*eV 0.15 3.25*eV 0.19 3.26*eV 0.24 3.27*eV 0.30 3.28*eV 0.38 3.29*eV 0.46 3.30*eV 0.57 3.31*eV 0.69 3.32*eV 0.83 3.32*eV 0.99 3.33*eV 1.17 3.34*eV 1.37 3.35*eV 1.59 3.36*eV 1.82 3.37*eV 2.08 3.38*eV 2.34 3.39*eV 2.62 3.40*eV 2.89 3.41*eV 3.17 3.42*eV 3.43 3.43*eV 3.68 3.43*eV 3.90 3.44*eV 4.09 3.45*eV 4.25 3.46*eV 4.36 3.47*eV 4.42 3.48*eV 4.43 3.49*eV 4.39 3.50*eV 4.30 3.51*eV 4.16 3.52*eV 3.97 3.53*eV 3.74 3.54*eV 3.48 3.55*eV 3.20 3.56*eV 2.90 3.57*eV 2.60 3.58*eV 2.29 3.59*eV 1.99 3.60*eV 1.71 3.61*eV 1.45 3.63*eV 1.20 3.64*eV 0.99 3.65*eV 0.80 3.66*eV 0.64 3.67*eV 0.50 3.68*eV 0.38 3.69*eV 0.29 3.70*eV 0.22 3.71*eV 0.16 3.72*eV 0.11 3.73*eV 0.08 3.75*eV 0.06 3.76*eV 0.04"/>
    <matrix coldim="1" name="LABR3MIEHG_FORWARD" values="0.99"/>
    <matrix coldim="1" name="LABR3MIEHG_BACKWARD" values="0.99"/>
    <matrix coldim="1" name="LABR3MIEHG_FORWARD_RATIO" values="0.8"/>
    <matrix coldim="1" name="LABR3SCINTILLATIONYIELD" values="63./keV"/>

    <matrix coldim="1" name="LABR3RESOLUTIONSCALE" values="1"/>

    <matrix coldim="1" name="LABR3SCINTILLATIONTIMECONSTANT1" values="16"/>
    <matrix coldim="1" name="LABR3SCINTILLATIONTIMECONSTANT2" values="16"/>
    <matrix coldim="1" name="LABR3SCINTILLATIONYIELD1" values="0.56"/>
    <matrix coldim="1" name="LABR3SCINTILLATIONYIELD2" values="0.44"/>

    <matrix coldim="2" name="PTFERINDEX" values="1.77*eV 1.38 3.54*eV 1.39"/>
    <matrix coldim="1" name="PTFEREFLECTIVITY" values="1"/>
    <matrix coldim="1" name="PTFETRANSMITTANCE" values="0"/>

    <matrix coldim="2" name="SIRINDEX" values="1.49993*eV 3.67800 1.52502*eV 3.69600 1.55000*eV 3.70460 1.57500*eV 3.71600 1.60000*eV 3.72280 1.62496*eV 3.73240 1.65004*eV 3.74230 1.67501*eV 3.76310 1.72512*eV 3.75300 1.73004*eV 3.77390 1.74995*eV 3.78510 1.77501*eV 3.79600 1.80000*eV 3.80840 1.82491*eV 3.82050 1.84996*eV 3.83300 1.87514*eV 3.85890 1.92492*eV 3.84500 1.93014*eV 3.87230 1.95005*eV 3.88600 1.97490*eV 3.90000 2.00007*eV 3.91440 2.02489*eV 3.92910 2.05000*eV 3.94410 2.07505*eV 3.97700 2.12484*eV 3.96000 2.13000*eV 3.99500 2.14989*eV 4.01200 2.17516*eV 4.02900 2.19986*eV 4.04900 2.22513*eV 4.06800 2.25017*eV 4.08900 2.27494*eV 4.13100 2.32485*eV 4.10900 2.33984*eV 4.15300 2.34997*eV 4.17700 2.37518*eV 4.20000 2.40000*eV 4.22400 2.42488*eV 4.25200 2.44980*eV 4.28100 2.47523*eV 4.33700 2.52514*eV 4.30900 2.53019*eV 4.36800 2.55007*eV 4.40200 2.57496*eV 4.43500 2.59979*eV 4.47100 2.62512*eV 4.51000 2.64980*eV 4.54900 2.67496*eV 4.63100 2.72493*eV 4.59100 2.73000*eV 4.67700 2.74970*eV 4.72200 2.77494*eV 4.77000 2.80000*eV 4.82500 2.82488*eV 4.87200 2.85021*eV 4.93300 2.87533*eV 5.05600 2.92485*eV 4.99400 2.93022*eV 5.12600 2.94990*eV 5.19700 2.97467*eV 5.27900 2.99986*eV 5.35600 3.02474*eV 5.45000 3.05004*eV 5.54300 3.07500*eV 5.76400 3.12539*eV 5.64900 3.13038*eV 5.89700 3.15001*eV 6.04100 3.17501*eV 6.19100 3.19959*eV 6.36900 3.22540*eV 6.54800 3.24991*eV 6.73500 3.27481*eV 7.00400 3.32486*eV 6.89900 3.33009*eV 6.98900 3.35002*eV 6.82100 3.37464*eV 6.56300 3.39962*eV 6.25100 3.42498*eV 5.96700 3.44976*eV 5.75200 3.47489*eV 5.48700 3.52528*eV 5.60100 3.53040*eV 5.42900 3.54950*eV 5.36300 3.57509*eV 5.31000 3.60001*eV 5.27700 3.62527*eV 5.24700 3.64981*eV 5.21800 3.67469*eV 5.15900 3.72549*eV 5.17700 3.73992*eV 5.13500 3.75028*eV 5.12000 3.77540*eV 5.09100 3.79970*eV 5.06600 3.82549*eV 5.06800 3.85044*eV 5.05100 3.87451*eV 5.03500 3.92479*eV 5.03200 3.93010*eV 5.03900 3.94980*eV 5.03400 3.97513*eV 5.02900 3.99949*eV 5.02400 4.02546*eV 5.02500 4.05045*eV 5.00900 4.07441*eV 4.98500 4.12456*eV 4.98600 4.13001*eV 4.92800 4.14940*eV 4.88500 4.17455*eV 4.79100 4.20001*eV 4.65900 4.22433*eV 4.45400 4.25040*eV 4.20500 4.27532*eV 3.66800 4.32453*eV 3.92600 4.33053*eV 3.40600 4.35032*eV 3.23200 4.37488*eV 3.03700 4.39972*eV 2.87700 4.42485*eV 2.72300 4.45026*eV 2.57400 4.47435*eV 2.29300 4.52497*eV 2.42600 4.53033*eV 2.18800 4.54988*eV 2.09900 4.57506*eV 2.01400 4.60053*eV 1.95400 4.62455*eV 1.89900 4.65057*eV 1.85400 4.67512*eV 1.82500"/>
    <matrix coldim="2" name="SIRINDEX_IMAG" values="1.49993*eV 0.00500 1.52502*eV 0.00460 1.55000*eV 0.00470 1.57500*eV 0.00290 1.60000*eV 0.00120 1.62496*eV 0.00440 1.65004*eV 0.00400 1.67501*eV 0.00260 1.72512*eV 0.00240 1.73004*eV 0.00290 1.74995*eV 0.00240 1.77501*eV 0.00260 1.80000*eV 0.00290 1.82491*eV 0.00240 1.84996*eV 0.00170 1.87514*eV 0.00210 1.92492*eV 0.00130 1.93014*eV 0.00170 1.95005*eV 0.00080 1.97490*eV 0.00130 2.00007*eV 0.00170 2.02489*eV 0.00240 2.05000*eV 0.00200 2.07505*eV 0.00260 2.12484*eV 0.00380 2.13000*eV 0.00350 2.14989*eV 0.00450 2.17516*eV 0.00470 2.19986*eV 0.00520 2.22513*eV 0.00640 2.25017*eV 0.00600 2.27494*eV 0.00750 2.32485*eV 0.01000 2.33984*eV 0.00800 2.34997*eV 0.01090 2.37518*eV 0.01220 2.40000*eV 0.01440 2.42488*eV 0.01890 2.44980*eV 0.02280 2.47523*eV 0.02400 2.52514*eV 0.03290 2.53019*eV 0.02800 2.55007*eV 0.03620 2.57496*eV 0.03930 2.59979*eV 0.04270 2.62512*eV 0.04820 2.64980*eV 0.05680 2.67496*eV 0.06260 2.72493*eV 0.08000 2.73000*eV 0.06900 2.74970*eV 0.08600 2.77494*eV 0.09500 2.80000*eV 0.10100 2.82488*eV 0.10800 2.85021*eV 0.12100 2.87533*eV 0.13000 2.92485*eV 0.15400 2.93022*eV 0.14200 2.94990*eV 0.17100 2.97467*eV 0.18700 2.99986*eV 0.20300 3.02474*eV 0.23200 3.05004*eV 0.25900 3.07500*eV 0.29700 3.12539*eV 0.38500 3.13038*eV 0.32600 3.15001*eV 0.44000 3.17501*eV 0.48600 3.19959*eV 0.58700 3.22540*eV 0.69500 3.24991*eV 0.87100 3.27481*eV 1.06800 3.32486*eV 1.75000 3.33009*eV 1.40400 3.35002*eV 2.16300 3.37464*eV 2.56200 3.39962*eV 2.86900 3.42498*eV 3.03700 3.44976*eV 3.10500 3.47489*eV 3.09200 3.52528*eV 3.02800 3.53040*eV 3.05600 3.54950*eV 3.01800 3.57509*eV 3.00800 3.60001*eV 3.00500 3.62527*eV 3.00900 3.64981*eV 3.03200 3.67469*eV 3.05000 3.72549*eV 3.11200 3.73992*eV 3.08300 3.75028*eV 3.14600 3.77540*eV 3.17400 3.79970*eV 3.21300 3.82549*eV 3.25800 3.85044*eV 3.28600 3.87451*eV 3.34700 3.92479*eV 3.44400 3.93010*eV 3.39200 3.94980*eV 3.49200 3.97513*eV 3.57500 3.99949*eV 3.64500 4.02546*eV 3.74400 4.05045*eV 3.82700 4.07441*eV 3.94100 4.12456*eV 4.20600 4.13001*eV 4.06700 4.14940*eV 4.36400 4.17455*eV 4.54800 4.20001*eV 4.74000 4.22433*eV 4.94900 4.25040*eV 5.14200 4.27532*eV 5.27200 4.32453*eV 5.34700 4.33053*eV 5.35300 4.35032*eV 5.33200 4.37488*eV 5.28000 4.39972*eV 5.23300 4.42485*eV 5.15800 4.45026*eV 5.11100 4.47435*eV 5.03100 4.52497*eV 4.85500 4.53033*eV 4.94100 4.54988*eV 4.73500 4.57506*eV 4.65900 4.60053*eV 4.54300 4.62455*eV 4.43900 4.65057*eV 4.34100 4.67512*eV 4.26200 4.69993*eV 4.17500"/> 
    <matrix coldim="2" name="SITRANSMITTANCE" values="1.38094*eV 0.00000 1.43193*eV 0.00000 1.44292*eV 0.00000 1.47103*eV 0.00000 1.51233*eV 0.00000 1.54610*eV 0.00000 1.59179*eV 0.00000 1.64583*eV 0.00000 1.68883*eV 0.00000 1.74523*eV 0.00000 1.78349*eV 0.00000 1.82213*eV 0.00000 1.87862*eV 0.00000 1.92716*eV 0.00000 1.97024*eV 0.00000 2.01111*eV 0.00000 2.04937*eV 0.00000 2.15889*eV 0.00000 2.18815*eV 0.00000 2.20805*eV 0.00000 2.27009*eV 0.00000 2.31343*eV 0.00000 2.35844*eV 0.00000 2.42329*eV 0.00000 2.47273*eV 0.00000 2.55079*eV 0.00000 2.57767*eV 0.00000 2.59170*eV 0.00000 2.63395*eV 0.00000 2.68501*eV 0.00000 2.71508*eV 0.00000 2.75364*eV 0.00000 2.78528*eV 0.00000 2.86766*eV 0.00000 2.88587*eV 0.00000 2.92829*eV 0.00000 2.97319*eV 0.00000 3.01011*eV 0.00000 3.05757*eV 0.00000 3.10656*eV 0.00000 3.13671*eV 0.00000 3.19880*eV 0.00000 3.21714*eV 0.00000 3.25245*eV 0.00000 3.29669*eV 0.00000 3.33066*eV 0.00000 3.36535*eV 0.00000 3.40076*eV 0.00000 3.42478*eV 0.00000 3.51161*eV 0.00000 3.53915*eV 0.00000 3.57638*eV 0.00000 3.64358*eV 0.00000 3.71335*eV 0.00000 3.78585*eV 0.00000 3.86124*eV 0.00000 3.90793*eV 0.00000 3.98830*eV 0.00000"/>
    <matrix coldim="2" name="SIREFLECTIVITY" values="1.38094*eV 0.00000 1.43193*eV 0.00000 1.44292*eV 0.00000 1.47103*eV 0.00000 1.51233*eV 0.00000 1.54610*eV 0.00000 1.59179*eV 0.00000 1.64583*eV 0.00000 1.68883*eV 0.00000 1.74523*eV 0.00000 1.78349*eV 0.00000 1.82213*eV 0.00000 1.87862*eV 0.00000 1.92716*eV 0.00000 1.97024*eV 0.00000 2.01111*eV 0.00000 2.04937*eV 0.00000 2.15889*eV 0.00000 2.18815*eV 0.00000 2.20805*eV 0.00000 2.27009*eV 0.00000 2.31343*eV 0.00000 2.35844*eV 0.00000 2.42329*eV 0.00000 2.47273*eV 0.00000 2.55079*eV 0.00000 2.57767*eV 0.00000 2.59170*eV 0.00000 2.63395*eV 0.00000 2.68501*eV 0.00000 2.71508*eV 0.00000 2.75364*eV 0.00000 2.78528*eV 0.00000 2.86766*eV 0.00000 2.88587*eV 0.00000 2.92829*eV 0.00000 2.97319*eV 0.00000 3.01011*eV 0.00000 3.05757*eV 0.00000 3.10656*eV 0.00000 3.13671*eV 0.00000 3.19880*eV 0.00000 3.21714*eV 0.00000 3.25245*eV 0.00000 3.29669*eV 0.00000 3.33066*eV 0.00000 3.36535*eV 0.00000 3.40076*eV 0.00000 3.42478*eV 0.00000 3.51161*eV 0.00000 3.53915*eV 0.00000 3.57638*eV 0.00000 3.64358*eV 0.00000 3.71335*eV 0.00000 3.78585*eV 0.00000 3.86124*eV 0.00000 3.90793*eV 0.00000 3.98830*eV 0.00000"/>
    <matrix coldim="2" name="SIEFFICIENCY" values="0.1*eV 1.00000 1.38094*eV 1.00000 1.43193*eV 1.00000 1.44292*eV 1.00000 1.47103*eV 1.00000 1.51233*eV 1.00000 1.54610*eV 1.00000 1.59179*eV 1.00000 1.64583*eV 1.00000 1.68883*eV 1.00000 1.74523*eV 1.00000 1.78349*eV 1.00000 1.82213*eV 1.00000 1.87862*eV 1.00000 1.92716*eV 1.00000 1.97024*eV 1.00000 2.01111*eV 1.00000 2.04937*eV 1.00000 2.15889*eV 1.00000 2.18815*eV 1.00000 2.20805*eV 1.00000 2.27009*eV 1.00000 2.31343*eV 1.00000 2.35844*eV 1.00000 2.42329*eV 1.00000 2.47273*eV 1.00000 2.55079*eV 1.00000 2.57767*eV 1.00000 2.59170*eV 1.00000 2.63395*eV 1.00000 2.68501*eV 1.00000 2.71508*eV 1.00000 2.75364*eV 1.00000 2.78528*eV 1.00000 2.86766*eV 1.00000 2.88587*eV 1.00000 2.92829*eV 1.00000 2.97319*eV 1.00000 3.01011*eV 1.00000 3.05757*eV 1.00000 3.10656*eV 1.00000 3.13671*eV 1.00000 3.19880*eV 1.00000 3.21714*eV 1.00000 3.25245*eV 1.00000 3.29669*eV 1.00000 3.33066*eV 1.00000 3.36535*eV 1.00000 3.40076*eV 1.00000 3.42478*eV 1.00000 3.51161*eV 1.00000 3.53915*eV 1.00000 3.57638*eV 1.00000 3.64358*eV 1.00000 3.71335*eV 1.00000 3.78585*eV 1.00000 3.86124*eV 1.00000 3.90793*eV 1.00000 3.98830*eV 1.00000 1000*eV 1.00000"/>  
    
    <matrix coldim="2" name="ALRINDEX" values="1.9997*eV 0.798 2.5200*eV 0.465 3.0020*eV 0.333 3.5024*eV 0.255 4.0255*eV 0.202"/>

"""


header_string2= r"""</define>

<materials>
        <isotope N="14" Z="7" name="N14">
            <atom unit="g/mole" value="14.0031"/>
        </isotope>
        <isotope N="15" Z="7" name="N15">
            <atom unit="g/mole" value="15.0001"/>
        </isotope>
        <element name="Nitrogen_El">
            <fraction n="0.99632" ref="N14"/>
            <fraction n="0.00368" ref="N15"/>
        </element>
        <isotope N="16" Z="8" name="O16">
            <atom unit="g/mole" value="15.9949"/>
        </isotope>
        <isotope N="17" Z="8" name="O17">
            <atom unit="g/mole" value="16.9991"/>
        </isotope>
        <isotope N="18" Z="8" name="O18">
            <atom unit="g/mole" value="17.9992"/>
        </isotope>
        <element name="Oxygen_El">
            <fraction n="0.99757" ref="O16"/>
            <fraction n="0.00038" ref="O17"/>
            <fraction n="0.00205" ref="O18"/>
        </element>

        <material name="Air" state="gas">
            <property name="RINDEX" ref="AIRRINDEX"/>
            <T unit="K" value="293.15"/>
            <MEE unit="eV" value="85.7030667332998"/>
            <D unit="g/cm3" value="0.00129"/>
            <fraction n="0.7" ref="Nitrogen_El"/>
            <fraction n="0.3" ref="Oxygen_El"/>
        </material>

        <isotope N="1" Z="1" name="H1">
            <atom unit="g/mole" value="1.00782503081372"/>
        </isotope>
        <isotope N="2" Z="1" name="H2">
            <atom unit="g/mole" value="2.01410199966617"/>
        </isotope>
        <element name="Hydrogen_El">
            <fraction n="0.999885" ref="H1"/>
            <fraction n="0.000115" ref="H2"/>
        </element>

        <isotope N="44" Z="35" name="Br79">
            <atom unit="g/mole" value="78.918"/>
        </isotope>
        <isotope N="46" Z="35" name="Br81">
            <atom unit="g/mole" value="80.916"/>
        </isotope>
        <element name="Bromine_El">
            <fraction n="0.505" ref="Br79"/>
            <fraction n="0.495" ref="Br81"/>
        </element>

        <isotope N="81" Z="57" name="La138">
            <atom unit="g/mole" value="137.907"/>
        </isotope>
        <isotope N="82" Z="57" name="La139">
            <atom unit="g/mole" value="138.905"/>
        </isotope>
        <element name="Lanthanum_El">
            <fraction n="0.0001" ref="La138"/>
            <fraction n="0.99" ref="La139"/>
        </element>

        <material name="LaBr3" state="solid">
            <property name="RINDEX" ref="LABR3INDEX"/>
            <property name="MIEHG" ref="LABR3MIEHG"/>
            <property name="ABSLENGTH" ref="LABR3ABSLENGTH"/>
            <property name="SCINTILLATIONCOMPONENT1" ref="LABR3SCINTILLATIONCOMPONENT1"/>
            <property name="SCINTILLATIONCOMPONENT2" ref="LABR3SCINTILLATIONCOMPONENT2"/>
            <property name="MIEHG_FORWARD" ref="LABR3MIEHG_FORWARD"/>
            <property name="MIEHG_BACKWARD" ref="LABR3MIEHG_BACKWARD"/>
            <property name="MIEHG_FORWARD_RATIO" ref="LABR3MIEHG_FORWARD_RATIO"/>
            <property name="SCINTILLATIONYIELD" ref="LABR3SCINTILLATIONYIELD"/>
            <property name="RESOLUTIONSCALE" ref="LABR3RESOLUTIONSCALE"/>
            <property name="SCINTILLATIONTIMECONSTANT1" ref="LABR3SCINTILLATIONTIMECONSTANT1"/>
            <property name="SCINTILLATIONTIMECONSTANT2" ref="LABR3SCINTILLATIONTIMECONSTANT2"/>
            <property name="SCINTILLATIONYIELD1" ref="LABR3SCINTILLATIONYIELD1"/>
            <property name="SCINTILLATIONYIELD2" ref="LABR3SCINTILLATIONYIELD2"/>
            <T unit="K" value="293.15"/>
            <MEE unit="eV" value="68.9984174679527"/>
            <D unit="g/cm3" value="5.2"/>
            <fraction n="0.366" ref="Lanthanum_El"/>
            <fraction n="0.634" ref="Bromine_El"/>
        </material>

        <isotope N="6" Z="6" name="C12">
            <atom unit="g/mole" value="12.000"/>
        </isotope>
        <isotope N="7" Z="6" name="C13">
            <atom unit="g/mole" value="13.004"/>
        </isotope>
        <isotope N="8" Z="6" name="C14">
            <atom unit="g/mole" value="14.003"/>
        </isotope>
        <element name="Carbon_El">
            <fraction n="0.990" ref="C12"/>
            <fraction n="0.012" ref="C13"/>
            <fraction n="0.00" ref="C14"/>
        </element>

        <isotope N="10" Z="9" name="F19">
            <atom unit="g/mole" value="18.998"/>
        </isotope>
        <element name="Fluorine_El">
            <fraction n="1" ref="F19"/>
        </element>

        <material name="PTFE" state="solid">
            <property name="RINDEX" ref="PTFERINDEX"/>
            <property name="REFLECTIVITY" ref="PTFEREFLECTIVITY"/>
            <property name="TRANSMITTANCE" ref="PTFETRANSMITTANCE"/>
            <T unit="K" value="293.15"/>
            <MEE unit="eV" value="85.7030667332998"/>
            <D unit="g/cm3" value="2.2"/>
            <fraction n="0.388" ref="Carbon_El"/>
            <fraction n="0.612" ref="Fluorine_El"/>
        </material>

        <isotope N="14" Z="14" name="Si28">
            <atom unit="g/mole" value="27.977"/>
        </isotope>
        <isotope N="15" Z="14" name="Si29">
            <atom unit="g/mole" value="28.977"/>
        </isotope>
        <isotope N="16" Z="14" name="Si30">
            <atom unit="g/mole" value="29.974"/>
        </isotope>
        <element name="Silicon_El">
            <fraction n="0.923" ref="Si28"/>
            <fraction n="0.047" ref="Si29"/>
            <fraction n="0.031" ref="Si30"/>
        </element>

        <material name="Silicon" state="solid">
            <property name="RINDEX" ref="SIRINDEX"/>
            <property name="REFLECTIVITY" ref="SIREFLECTIVITY"/>
            <property name="TRANSMITTANCE" ref="SITRANSMITTANCE"/>
            <property name="OP_DET_EFF" ref="SIEFFICIENCY"/>
            <property name="EFFICIENCY" ref="SIEFFICIENCY"/>
            <T unit="K" value="293.15"/>
            <MEE unit="eV" value="85.7030667332998"/>
            <D unit="g/cm3" value="2.33"/>
            <fraction n="1" ref="Silicon_El"/>

        </material>

        <isotope N="14" Z="13" name="Al27">
            <atom unit="g/mole" value="26.982"/>
        </isotope>
        <element name="Aluminium_El">
            <fraction n="1" ref="Al27"/>
        </element>

        <material name="Aluminium" state="solid">
            <property name="RINDEX" ref="ALRINDEX"/>
            <T unit="K" value="293.15"/>
            <MEE unit="eV" value="85.7030667332998"/>
            <D unit="g/cm3" value="2.71"/>
            <fraction n="1" ref="Aluminium_El"/>
        </material>

        <material name="Water" state="solid">
            <property name="RINDEX" ref="WATERRINDEX"/>
            <property name="MIEHG" ref="WATERMIEHG"/>
            <property name="ABSLENGTH" ref="WATERABSLENGTH"/>
            <property name="SCINTILLATIONCOMPONENT1" ref="WATERSCINTILLATIONCOMPONENT1"/>
            <property name="SCINTILLATIONCOMPONENT2" ref="WATERSCINTILLATIONCOMPONENT2"/>
            <property name="MIEHG_FORWARD" ref="WATERMIEHG_FORWARD"/>
            <property name="MIEHG_BACKWARD" ref="WATERMIEHG_BACKWARD"/>
            <property name="MIEHG_FORWARD_RATIO" ref="WATERMIEHG_FORWARD_RATIO"/>
            <property name="SCINTILLATIONYIELD" ref="WATERSCINTILLATIONYIELD"/>
            <property name="RESOLUTIONSCALE" ref="WATERRESOLUTIONSCALE"/>
            <property name="SCINTILLATIONTIMECONSTANT1" ref="WATERSCINTILLATIONTIMECONSTANT1"/>
            <property name="SCINTILLATIONTIMECONSTANT2" ref="WATERSCINTILLATIONTIMECONSTANT2"/>
	        <property name="SCINTILLATIONYIELD1" ref="WATERSCINTILLATIONYIELD1"/>
	        <property name="SCINTILLATIONYIELD2" ref="WATERSCINTILLATIONYIELD2"/>
            <T unit="K" value="293.15"/>
            <MEE unit="eV" value="68.9984174679527"/>
            <D unit="g/cm3" value="1"/>
            <fraction n="0.112097669256382" ref="Hydrogen_El"/>
            <fraction n="0.887902330743618" ref="Oxygen_El"/>
        </material>
        


    </materials>
"""

header_string3= r"""<solids>
    <box lunit="cm" name="World_solid" x="20" y="20" z="20"/>
"""


header_string4= r"""
</solids>
<structure>
"""


header_string5 = r"""

   	<volume name="World_volume">
		<materialref ref="Air"/>
		<solidref ref="World_solid"/>
"""


header_string6 = r"""
	</volume>
</structure>

<setup name="Default" version="1.0">
	<world ref="World_volume"/>
</setup>

</gdml>

"""

def read_csv(filename): 

    data = np.loadtxt(filename, delimiter=',')

    #print(data.shape)

    x = data[:,0]
    y = data[:,1]

    e = nm_to_ev(x)

    #print(e, x)

    return e, y



def nm_to_ev(x):


    c = np.asarray(299792458)
    h = 4.1357 / np.power(10, 15)

    e =  h * c / ( x / 1000000000) 

    return e


def ev_to_nm(e):

    c = np.asarray(299792458)
    h = 4.1357 / np.power(10, 15)

    x=((h*c)/e)*1000000000

    print("the converted wavelengths (in nm) are: ", x)

    return x


def interlace_values(string_1, string_2, energy_string='*eV', reverse=False):

    interlaced_string = str()

    if len(string_2) == 1:
        print('singular value for string 2, repeating %i times' % len(string_1))
        string_2 = string_2 * len(string_1) 

    for s1, s2 in zip(string_1, string_2):

        out_string = '%.5f%s %.5f ' % (s1, energy_string, s2)

        if reverse:
            interlaced_string = out_string + interlaced_string
        else:
            interlaced_string = interlaced_string + out_string

    print("this is the interlaced string",interlaced_string)

def deinterlace_values(string_1, ignore='*eV', convert_to_floats=True):

    v1 = list()
    v2 = list()

    split_string = string_1.split(' ')

    for i, s in enumerate(split_string):
        if ignore is not None:
            s = s.replace(ignore, '')
        if convert_to_floats:
            s = float(s)
        if i % 2: 
            v2.append(s)
        else:
            v1.append(s)

    v1 = np.asarray(v1)
    v2 = np.asarray(v2)

    return v1, v2



def gaussian_fit(edata, A=0.40, sigma_1=0.10, sigma_2=0.09, mean_1=3.23, mean_2=3.48):

    #edata  array of energy data points

    #calculating constant for first gaussian 
    constant_1= A/(np.sqrt(2*np.pi)*sigma_1)
    # constant_1= 1/(np.sqrt(2*np.pi)*sigma_1)

    #gaussian 1 
    gaussian_1=constant_1*np.exp(-((edata-mean_1)**2/(2*sigma_1**2)))
    
    #calculating constant for second gaussian 
    constant_2= (1-A)/(np.sqrt(2*np.pi)*sigma_2)
    # constant_2= (1)/(np.sqrt(2*np.pi)*sigma_2)

    #gaussian 2
    gaussian_2=constant_2*np.exp(-((edata-mean_2)**2/(2*sigma_2**2)))

    return(gaussian_1, gaussian_2)


    
    
def plot_emission(string_1, string_2, string_3=None):

    x_vals = np.asarray(string_1)
    y_vals = np.asarray(string_2)
    if string_3 is not None:
        y_vals_2 = np.asarray(string_3)

    plt.figure()
    plt.plot(x_vals, y_vals)
    if string_3 is not None:
        plt.plot(x_vals, y_vals_2)
    # plt.plot(y_vals)
    plt.show()


if __name__ == '__main__':

    main()
    # make_vertex_string(1,2,3,1,'v')

    eV =1 

# #these are the optical energies of CeBr3 
#     string_1 = [2.58558e+00*eV, 2.60375e+00*eV, 2.62735e+00*eV, 2.65348e+00*eV, 2.68122e+00*eV, 2.71175e+00*eV, 2.74185e+00*eV, 2.77033e+00*eV,
#         2.79940e+00*eV, 2.83029e+00*eV, 2.86188e+00*eV, 2.88540e+00*eV, 2.90805e+00*eV, 2.93235e+00*eV, 2.94140e+00*eV, 2.95443e+00*eV,
#         2.96758e+00*eV, 2.98485e+00*eV, 2.99962e+00*eV, 3.01317e+00*eV, 3.03098e+00*eV, 3.04899e+00*eV, 3.06159e+00*eV, 3.07005e+00*eV,
#         3.08139e+00*eV, 3.09426e+00*eV, 3.10724e+00*eV, 3.12032e+00*eV, 3.12911e+00*eV, 3.13942e+00*eV, 3.14683e+00*eV, 3.15726e+00*eV,
#         3.16475e+00*eV, 3.17228e+00*eV, 3.17984e+00*eV, 3.19049e+00*eV, 3.20429e+00*eV, 3.21976e+00*eV, 3.23224e+00*eV, 3.24482e+00*eV,
#         3.25274e+00*eV, 3.25910e+00*eV, 3.27189e+00*eV, 3.28155e+00*eV, 3.28802e+00*eV, 3.29941e+00*eV, 3.31417e+00*eV, 3.32574e+00*eV,
#         3.33572e+00*eV, 3.34576e+00*eV, 3.35249e+00*eV, 3.36094e+00*eV, 3.36943e+00*eV, 3.37967e+00*eV, 3.38998e+00*eV, 3.40035e+00*eV,
#         3.41079e+00*eV, 3.42129e+00*eV, 3.43185e+00*eV, 3.43893e+00*eV, 3.44782e+00*eV, 3.45676e+00*eV, 3.46574e+00*eV, 3.47477e+00*eV,
#         3.48385e+00*eV, 3.49480e+00*eV, 3.50767e+00*eV, 3.52063e+00*eV, 3.53556e+00*eV, 3.55820e+00*eV, 3.57729e+00*eV, 3.59658e+00*eV,
#         3.62001e+00*eV, 3.64375e+00*eV, 3.67588e+00*eV, 3.70036e+00*eV, 3.75876e+00*eV, 3.81466e+00*eV, 3.86776e+00*eV]
    
#     #these are the optical intensities of CeBr3 
#     string_2 = [3.95471e-04, 4.54059e-04, 4.54059e-04, 4.54059e-04, 4.54059e-04, 5.71236e-04, 6.88413e-04, 7.47001e-04,
#         8.64178e-04, 9.81354e-04, 1.15712e-03, 1.39147e-03, 1.74300e-03, 2.09453e-03, 2.32889e-03, 2.79759e-03,
#         3.26630e-03, 4.02795e-03, 4.84818e-03, 5.66842e-03, 7.13313e-03, 8.77360e-03, 1.00625e-02, 1.11757e-02,
#         1.24647e-02, 1.40465e-02, 1.55113e-02, 1.68002e-02, 1.77376e-02, 1.86750e-02, 1.93781e-02, 2.01397e-02,
#         2.06670e-02, 2.11357e-02, 2.15459e-02, 2.17802e-02, 2.20731e-02, 2.23661e-02, 2.27176e-02, 2.31277e-02,
#         2.34207e-02, 2.35964e-02, 2.38894e-02, 2.40652e-02, 2.43581e-02, 2.50026e-02, 2.59400e-02, 2.67602e-02,
#         2.74633e-02, 2.78734e-02, 2.81663e-02, 2.83421e-02, 2.82835e-02, 2.81663e-02, 2.76390e-02, 2.67016e-02,
#         2.54127e-02, 2.40066e-02, 2.18974e-02, 2.03155e-02, 1.83235e-02, 1.63315e-02, 1.43981e-02, 1.25233e-02,
#         1.08242e-02, 9.06654e-03, 7.19172e-03, 5.66842e-03, 4.32089e-03, 2.97336e-03, 1.86018e-03, 1.15712e-03,
#         6.88413e-04, 3.36883e-04, 1.61118e-04, 4.39412e-05, 4.39412e-05, 4.39412e-05, 4.39412e-05]


#these are the refractive index energies for silicon 
    # string_1 = [1.49993e+00*eV,1.52502e+00*eV, 1.55000e+00*eV, 1.57500e+00*eV, 1.60000e+00*eV, 1.62496e+00*eV, 1.65004e+00*eV, 1.67501e+00*eV, 1.72512e+00*eV,
    #     1.73004e+00*eV, 1.74995e+00*eV, 1.77501e+00*eV, 1.80000e+00*eV, 1.82491e+00*eV, 1.84996e+00*eV, 1.87514e+00*eV, 1.92492e+00*eV,
    #     1.93014e+00*eV, 1.95005e+00*eV, 1.97490e+00*eV, 2.00007e+00*eV, 2.02489e+00*eV, 2.05000e+00*eV, 2.07505e+00*eV, 2.12484e+00*eV,
    #     2.13000e+00*eV, 2.14989e+00*eV, 2.17516e+00*eV, 2.19986e+00*eV, 2.22513e+00*eV, 2.25017e+00*eV, 2.27494e+00*eV, 2.32485e+00*eV,
    #     2.33984e+00*eV, 2.34997e+00*eV, 2.37518e+00*eV, 2.40000e+00*eV, 2.42488e+00*eV, 2.44980e+00*eV, 2.47523e+00*eV, 2.52514e+00*eV,
    #     2.53019e+00*eV, 2.55007e+00*eV, 2.57496e+00*eV, 2.59979e+00*eV, 2.62512e+00*eV, 2.64980e+00*eV, 2.67496e+00*eV, 2.72493e+00*eV,
    #     2.73000e+00*eV, 2.74970e+00*eV, 2.77494e+00*eV, 2.80000e+00*eV, 2.82488e+00*eV, 2.85021e+00*eV, 2.87533e+00*eV, 2.92485e+00*eV,
    #     2.93022e+00*eV, 2.94990e+00*eV, 2.97467e+00*eV, 2.99986e+00*eV, 3.02474e+00*eV, 3.05004e+00*eV, 3.07500e+00*eV, 3.12539e+00*eV,
    #     3.13038e+00*eV, 3.15001e+00*eV, 3.17501e+00*eV, 3.19959e+00*eV, 3.22540e+00*eV, 3.24991e+00*eV, 3.27481e+00*eV, 3.32486e+00*eV,
    #     3.33009e+00*eV, 3.35002e+00*eV, 3.37464e+00*eV, 3.39962e+00*eV, 3.42498e+00*eV, 3.44976e+00*eV, 3.47489e+00*eV, 3.52528e+00*eV,
    #     3.53040e+00*eV, 3.54950e+00*eV, 3.57509e+00*eV, 3.60001e+00*eV, 3.62527e+00*eV, 3.64981e+00*eV, 3.67469e+00*eV, 3.72549e+00*eV,
    #     3.73992e+00*eV, 3.75028e+00*eV, 3.77540e+00*eV, 3.79970e+00*eV, 3.82549e+00*eV, 3.85044e+00*eV, 3.87451e+00*eV, 3.92479e+00*eV,
    #     3.93010e+00*eV, 3.94980e+00*eV, 3.97513e+00*eV, 3.99949e+00*eV, 4.02546e+00*eV, 4.05045e+00*eV, 4.07441e+00*eV, 4.12456e+00*eV,
    #     4.13001e+00*eV, 4.14940e+00*eV, 4.17455e+00*eV, 4.20001e+00*eV, 4.22433e+00*eV, 4.25040e+00*eV, 4.27532e+00*eV, 4.32453e+00*eV,
    #     4.33053e+00*eV, 4.35032e+00*eV, 4.37488e+00*eV, 4.39972e+00*eV, 4.42485e+00*eV, 4.45026e+00*eV, 4.47435e+00*eV, 4.52497e+00*eV,
    #     4.53033e+00*eV, 4.54988e+00*eV, 4.57506e+00*eV, 4.60053e+00*eV, 4.62455e+00*eV, 4.65057e+00*eV, 4.67512e+00*eV, 4.69993e+00*eV]
    
    # #these are the real refractive indexs for silicon 

    string_1 = [ 1.49993e+00*eV,
        1.52502e+00*eV, 1.55000e+00*eV, 1.57500e+00*eV, 1.60000e+00*eV, 1.62496e+00*eV, 1.65004e+00*eV, 1.67501e+00*eV, 1.72512e+00*eV,
        1.73004e+00*eV, 1.74995e+00*eV, 1.77501e+00*eV, 1.80000e+00*eV, 1.82491e+00*eV, 1.84996e+00*eV, 1.87514e+00*eV, 1.92492e+00*eV,
        1.93014e+00*eV, 1.95005e+00*eV, 1.97490e+00*eV, 2.00007e+00*eV, 2.02489e+00*eV, 2.05000e+00*eV, 2.07505e+00*eV, 2.12484e+00*eV,
        2.13000e+00*eV, 2.14989e+00*eV, 2.17516e+00*eV, 2.19986e+00*eV, 2.22513e+00*eV, 2.25017e+00*eV, 2.27494e+00*eV, 2.32485e+00*eV,
        2.33984e+00*eV, 2.34997e+00*eV, 2.37518e+00*eV, 2.40000e+00*eV, 2.42488e+00*eV, 2.44980e+00*eV, 2.47523e+00*eV, 2.52514e+00*eV,
        2.53019e+00*eV, 2.55007e+00*eV, 2.57496e+00*eV, 2.59979e+00*eV, 2.62512e+00*eV, 2.64980e+00*eV, 2.67496e+00*eV, 2.72493e+00*eV,
        2.73000e+00*eV, 2.74970e+00*eV, 2.77494e+00*eV, 2.80000e+00*eV, 2.82488e+00*eV, 2.85021e+00*eV, 2.87533e+00*eV, 2.92485e+00*eV,
        2.93022e+00*eV, 2.94990e+00*eV, 2.97467e+00*eV, 2.99986e+00*eV, 3.02474e+00*eV, 3.05004e+00*eV, 3.07500e+00*eV, 3.12539e+00*eV,
        3.13038e+00*eV, 3.15001e+00*eV, 3.17501e+00*eV, 3.19959e+00*eV, 3.22540e+00*eV, 3.24991e+00*eV, 3.27481e+00*eV, 3.32486e+00*eV,
        3.33009e+00*eV, 3.35002e+00*eV, 3.37464e+00*eV, 3.39962e+00*eV, 3.42498e+00*eV, 3.44976e+00*eV, 3.47489e+00*eV, 3.52528e+00*eV,
        3.53040e+00*eV, 3.54950e+00*eV, 3.57509e+00*eV, 3.60001e+00*eV, 3.62527e+00*eV, 3.64981e+00*eV, 3.67469e+00*eV, 3.72549e+00*eV,
        3.73992e+00*eV, 3.75028e+00*eV, 3.77540e+00*eV, 3.79970e+00*eV, 3.82549e+00*eV, 3.85044e+00*eV, 3.87451e+00*eV, 3.92479e+00*eV,
        3.93010e+00*eV, 3.94980e+00*eV, 3.97513e+00*eV, 3.99949e+00*eV, 4.02546e+00*eV, 4.05045e+00*eV, 4.07441e+00*eV, 4.12456e+00*eV,
        4.13001e+00*eV, 4.14940e+00*eV, 4.17455e+00*eV, 4.20001e+00*eV, 4.22433e+00*eV, 4.25040e+00*eV, 4.27532e+00*eV, 4.32453e+00*eV,
        4.33053e+00*eV, 4.35032e+00*eV, 4.37488e+00*eV, 4.39972e+00*eV, 4.42485e+00*eV, 4.45026e+00*eV, 4.47435e+00*eV, 4.52497e+00*eV,
        4.53033e+00*eV, 4.54988e+00*eV, 4.57506e+00*eV, 4.60053e+00*eV, 4.62455e+00*eV, 4.65057e+00*eV, 4.67512e+00*eV, 4.69993e+00*eV
    ]



    string_2 = [5.00000e-03,
        4.60000e-03, 4.70000e-03, 2.90000e-03, 1.20000e-03, 4.40000e-03, 4.00000e-03, 2.60000e-03, 2.40000e-03,
        2.90000e-03, 2.40000e-03, 2.60000e-03, 2.90000e-03, 2.40000e-03, 1.70000e-03, 2.10000e-03, 1.30000e-03,
        1.70000e-03, 8.00000e-04, 1.30000e-03, 1.70000e-03, 2.40000e-03, 2.00000e-03, 2.60000e-03, 3.80000e-03,
        3.50000e-03, 4.50000e-03, 4.70000e-03, 5.20000e-03, 6.40000e-03, 6.00000e-03, 7.50000e-03, 1.00000e-02,
        8.00000e-03, 1.09000e-02, 1.22000e-02, 1.44000e-02, 1.89000e-02, 2.28000e-02, 2.40000e-02, 3.29000e-02,
        2.80000e-02, 3.62000e-02, 3.93000e-02, 4.27000e-02, 4.82000e-02, 5.68000e-02, 6.26000e-02, 8.00000e-02,
        6.90000e-02, 8.60000e-02, 9.50000e-02, 1.01000e-01, 1.08000e-01, 1.21000e-01, 1.30000e-01, 1.54000e-01,
        1.42000e-01, 1.71000e-01, 1.87000e-01, 2.03000e-01, 2.32000e-01, 2.59000e-01, 2.97000e-01, 3.85000e-01,
        3.26000e-01, 4.40000e-01, 4.86000e-01, 5.87000e-01, 6.95000e-01, 8.71000e-01, 1.06800e+00, 1.75000e+00,
        1.40400e+00, 2.16300e+00, 2.56200e+00, 2.86900e+00, 3.03700e+00, 3.10500e+00, 3.09200e+00, 3.02800e+00,
        3.05600e+00, 3.01800e+00, 3.00800e+00, 3.00500e+00, 3.00900e+00, 3.03200e+00, 3.05000e+00, 3.11200e+00,
        3.08300e+00, 3.14600e+00, 3.17400e+00, 3.21300e+00, 3.25800e+00, 3.28600e+00, 3.34700e+00, 3.44400e+00,
        3.39200e+00, 3.49200e+00, 3.57500e+00, 3.64500e+00, 3.74400e+00, 3.82700e+00, 3.94100e+00, 4.20600e+00,
        4.06700e+00, 4.36400e+00, 4.54800e+00, 4.74000e+00, 4.94900e+00, 5.14200e+00, 5.27200e+00, 5.34700e+00,
        5.35300e+00, 5.33200e+00, 5.28000e+00, 5.23300e+00, 5.15800e+00, 5.11100e+00, 5.03100e+00, 4.85500e+00,
        4.94100e+00, 4.73500e+00, 4.65900e+00, 4.54300e+00, 4.43900e+00, 4.34100e+00, 4.26200e+00, 4.17500e+00
    ]
    # string_1 = [
    #     1.38094e+00*eV, 1.43193e+00*eV,
    #     1.44292e+00*eV, 1.47103e+00*eV, 1.51233e+00*eV, 1.54610e+00*eV, 1.59179e+00*eV, 1.64583e+00*eV, 1.68883e+00*eV, 1.74523e+00*eV,
    #     1.78349e+00*eV, 1.82213e+00*eV, 1.87862e+00*eV, 1.92716e+00*eV, 1.97024e+00*eV, 2.01111e+00*eV, 2.04937e+00*eV, 2.15889e+00*eV,
    #     2.18815e+00*eV, 2.20805e+00*eV, 2.27009e+00*eV, 2.31343e+00*eV, 2.35844e+00*eV, 2.42329e+00*eV, 2.47273e+00*eV, 2.55079e+00*eV,
    #     2.57767e+00*eV, 2.59170e+00*eV, 2.63395e+00*eV, 2.68501e+00*eV, 2.71508e+00*eV, 2.75364e+00*eV, 2.78528e+00*eV, 2.86766e+00*eV,
    #     2.88587e+00*eV, 2.92829e+00*eV, 2.97319e+00*eV, 3.01011e+00*eV, 3.05757e+00*eV, 3.10656e+00*eV, 3.13671e+00*eV, 3.19880e+00*eV,
    #     3.21714e+00*eV, 3.25245e+00*eV, 3.29669e+00*eV, 3.33066e+00*eV, 3.36535e+00*eV, 3.40076e+00*eV, 3.42478e+00*eV, 3.51161e+00*eV,
    #     3.53915e+00*eV, 3.57638e+00*eV, 3.64358e+00*eV, 3.71335e+00*eV, 3.78585e+00*eV, 3.86124e+00*eV, 3.90793e+00*eV, 3.98830e+00*eV
    # ]

    # string_2 = [0]


    interlace_values(string_1,string_2)


    # interlace_values(string_1,string_2)

    # plot_emission(string_1, string_2)

    # string_3 = '2.034*eV 1 2.068*eV 1 2.103*eV 1 2.139*eV 1 2.177*eV 1 2.216*eV 1 2.256*eV 1 2.298*eV 1 2.341*eV 1 2.386*eV 1 2.433*eV 1 2.481*eV 1 2.532*eV 1 2.585*eV 1 2.64*eV 1 2.697*eV 1 2.757*eV 1 2.82*eV 1 2.885*eV 1 2.954*eV 1 3.026*eV 1 3.102*eV 1 3.181*eV 1 3.265*eV 1 3.353*eV 1 3.446*eV 1 3.545*eV 1 3.649*eV 1 3.76*eV 1 3.877*eV 1 4.002*eV 1 4.136*eV 1'
    # string_4 = '2.034*eV 0.01 2.068*eV 1 2.103*eV 2 2.139*eV 3 2.177*eV 4 2.216*eV 5 2.256*eV 6 2.298*eV 7 2.341*eV 8 2.386*eV 9 2.433*eV 8 2.481*eV 7 2.532*eV 6 2.585*eV 4 2.64*eV 3 2.697*eV 2 2.757*eV 1 2.82*eV 0.01 2.885*eV 1 2.954*eV 2 3.026*eV 3 3.102*eV 4 3.181*eV 5 3.265*eV 6 3.353*eV 7 3.446*eV 8 3.545*eV 9 3.649*eV 8 3.76*eV 7 3.877*eV 6 4.002*eV 5 4.136*eV 4'
    # string_5 = '1.56962*eV 1.67024e+08 1.58974*eV 1.58727e+08 1.61039*eV 1.50742e+08 1.63157*eV 1.43062e+08 1.65333*eV 1.3568e+08 1.67567*eV 1.28587e+08 1.69863*eV 1.21776e+08 1.72222*eV 1.1524e+08 1.74647*eV 1.0897e+08 1.77142*eV 1.02959e+08 1.7971*eV 9.72004e+07 1.82352*eV 9.16869e+07 1.85074*eV 8.64113e+07 1.87878*eV 8.13668e+07 1.90769*eV 7.65464e+07 1.93749*eV 7.19435e+07 1.96825*eV 6.75513e+07 1.99999*eV 6.33634e+07 2.03278*eV 5.93732e+07 2.06666*eV 5.55746e+07 2.10169*eV 5.19612e+07 2.13793*eV 4.8527e+07 2.17543*eV 4.52659e+07 2.21428*eV 4.21719e+07 2.25454*eV 3.92394e+07 2.29629*eV 3.64625e+07 2.33962*eV 3.38357e+07 2.38461*eV 3.13534e+07 2.43137*eV 2.90103e+07 2.47999*eV 2.6801e+07 2.53061*eV 2.47204e+07 2.58333*eV 2.27634e+07 2.63829*eV 2.09249e+07 2.69565*eV 1.92001e+07 2.75555*eV 1.75842e+07 2.81817*eV 1.60724e+07 2.88371*eV 1.46604e+07 2.95237*eV 1.33435e+07 3.02438*eV 1.21173e+07 3.09999*eV 1.09777e+07 3.17948*eV 9.92042e+06 3.26315*eV 8.94141e+06 3.35134*eV 8.03671e+06 3.44444*eV 7.20247e+06 3.54285*eV 6.43493e+06 3.64705*eV 5.73043e+06 3.75757*eV 5.08542e+06 3.87499*eV 4.49647e+06 3.99999*eV 3.96021e+06 4.13332*eV 3.47341e+06 4.27585*eV 3.03294e+06 4.42856*eV 2.63575e+06 4.59258*eV 2.27891e+06 4.76922*eV 1.95959e+06 4.95999*eV 1.67506e+06 5.16665*eV 1.42271e+06 5.39129*eV 1.2e+06 5.63635*eV 1.00453e+06 5.90475*eV 833967 6.19998*eV 686106'
    # string_6 = '2.034*eV 3448 2.068*eV 4082 2.103*eV 6329 2.139*eV 9174 2.177*eV 12346 2.216*eV 13889 2.256*eV 15152 2.298*eV 17241 2.341*eV 18868 2.386*eV 20000 2.433*eV 26316 2.481*eV 35714 2.532*eV 45455 2.585*eV 47619 2.64*eV 52632 2.697*eV 52632 2.757*eV 55556 2.82*eV 52632 2.885*eV 52632 2.954*eV 47619 3.026*eV 45455 3.102*eV 41667 3.181*eV 37037 3.265*eV 33333 3.353*eV 30000 3.446*eV 28500 3.545*eV 27000 3.649*eV 24500 3.76*eV 22000 3.877*eV 19500 4.002*eV 17500 4.136*eV 14500'

    # a, b  = deinterlace_values(string_5)
    # w=ev_to_nm(a)
    # plot_emission(w,b)





    # x, y = read_csv('labr3_emission.csv')

    # #calling function to perform gaussian fits 
    # gfit=gaussian_fit(x)
    # print("These are the Gaussian fits",gfit)
    # #tuple 
    
    # gaussian_1,gaussian_2=gfit
    # print("this is gaussian fit 1", gaussian_1)
    # #numpy array 

    # print("this is gaussian fit 2", gaussian_2)

    # sum_of_gaussian= gaussian_2+gaussian_1 

    # # plot_emission(x, y)
    # # plot_emission(x, gaussian_1)
    # # plot_emission(x, gaussian_2)
    # plot_emission(x, gaussian_1, gaussian_2)
    # plot_emission(x, sum_of_gaussian)

    # print(np.sum(gaussian_1)/np.sum(sum_of_gaussian), np.sum(gaussian_2)/np.sum(sum_of_gaussian))

    # interlace_values(x, gaussian_1)
    # interlace_values(x, gaussian_2)

    # plot_emission(x, gaussian_1)
    # plot_emission(x, gaussian_2)
    # plot_emission(ev_to_nm(x), sum_of_gaussian)
    
    # interlace_values(x, y)


    # x1,y1= read_csv('scattering_lengths.csv')
    # print("this is x1", x1)
    # print("this is y1", y1)
    # interlace_values(x1, y1)


    # x1,y1= read_csv('n_mean.csv')
    # # x1 = np.linspace(350, 700, num=x1.size)
    # # x1 = ev_to_nm(x1)
    # print("this is x1", x1)
    # print("this is y1", y1)
    # interlace_values(x1, y1)
    # plot_emission(x1,y1)

