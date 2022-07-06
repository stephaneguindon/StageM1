#!/usr/bin/env python
#-*- coding : utf-8 -*-


#__author__ = ("Kélian PEREZ")
#__contact__ = ("keperez.klp@gmail.com")
#__version__ = "1.0"
#__date__ = "05/13/2022"
#__licence__ ="This program is free software: you can redistribute it and/or modify
        #it under the terms of the GNU General Public License as published by
        #the Free Software Foundation, either version 3 of the License, or
        #(at your option) any later version.
        #This program is distributed in the hope that it will be useful,
        #but WITHOUT ANY WARRANTY; without even the implied warranty of
        #MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
        #GNU General Public License for more details.
        #You should have received a copy of the GNU General Public License
       # along with this program. If not, see <https://www.gnu.org/licenses/>."


     
    ### OPTION LIST:
        ##-h or --help: help information
        ##-i or --input: input file (.sam)
        ##-o or --output: output name files (.txt)
        ##-pol or --polygon_label: polygon_label (default = location) => locationX_80%HPD_XX

    #Synopsis:
        ##Discretize_MCC.py -h or --help # launch the help.
        ##Discretize_MCC.py -i or --input <file> # Launch Discretize_MCC
        ##Discretize_MCC.py -i or --input <file> -o or --output <name> # Launch Discretize_MCC to discretize your MCC BEAST nodes output and print the result in the file called <name>
  

############### IMPORT MODULES ###############

import os, sys, json, ast, numpy
from copy import deepcopy
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

def get_dict_leaves(treejson, pol_lab): #return dict_node a dictionary of node that contains related dictionaries with latitude and longitudes estimated for each leaves | params(nodes_output)
    with open(treejson, 'r') as file:
        dict = json.load(file) #open the json node_output from augur import beast as a dictionary and turn it into dictionary
        dict_node={}
        dict_locations={} 
        for n in dict["nodes"]: #iterate in JSON over the keys "nodes"
            if "NODE" not in n: #to apply the following lines to leaves only
                dict_node[n]={}
                for e in dict["nodes"][n]:
                    if pol_lab+"1" in e:
                        dict_locations[e]={}
                        for location in dict_locations: #link latitude to each leaf
                            dict_locations_l={}
                            if location==e:
                                dict_locations_l[location]= dict["nodes"][n][location]
                                dict_node[n].update(dict_locations_l)
                    elif pol_lab+"2" in e:
                        dict_locations[e]={}
                        for location in dict_locations: #link longitude to each leaf
                            dict_locations_l={}
                            if location==e:
                                dict_locations_l[location]= dict["nodes"][n][location]
                                dict_node[n].update(dict_locations_l)

                    ### if pol_lab not in e: #Throw exception error if location is not the polygons label
                        #raise ValueError("Your polygon's labels are not matching the default : location -> locationX_80%HPD_XX","\n","Please enter the polygon label using the option : -pol LABEL","\n")
        return(dict_node)

def get_points_leaves(dict, pol_lab): #return a dictionnary with each leaves and its relatives coordinates ('lat;long') 
    dict_points=deepcopy(dict)
    for node in dict:
        dict_points[node]={}
        coords=[]
        for hpds in dict[node]: #for each positions lat or long
            if pol_lab+'1' in hpds: #if list of latitudes
                hpd=hpds
                hpd2=hpd.replace(pol_lab+'1',pol_lab+'2') # the following lines are here to keep the structure of the previous dict
                coords=(str(dict[node][hpd])+';'+str(dict[node][hpd2]))
                dict_points[node]=coords #for each leaf, we get coordinates ('lat;long')
    return(dict_points)

def get_dict_HPD(treejson,pol_lab): #return dict_node a dictionary of node that contains related dictionaries with positions of polygons vertex | params(nodes_output)
    with open(treejson, 'r') as file:
        dict = json.load(file) #open the json node_output from augur import beast as a dictionary and turn it into dictionary
    dict_HPD={} 
    dict_node={} 
    for n in dict["nodes"]: #iterate in JSON over the keys "nodes"
        if "NODE" in n: #to apply the following lines to intern nodes only
            dict_node[n]={} #initialise dict_node with nodes labels as key
            for e in dict["nodes"][n]:  #for each attributes of intern nodes : NODE_XXXXXXX
                if "location1_80%HPD_" in e: #if node attribute is a list of latitudes
                    dict_HPD[e]={}  #initialize dict_HPD keys with each name of the lists of latitudes : location1_80%HPD_XX
                    for hpd in dict_HPD:#for each existing hpd location1_80%HPD_XX
                        dict_HPD_n={}
                        if hpd==e: #if hpd exists, then create a dict of node hpds
                            dict_HPD_n[hpd]=dict["nodes"][n][hpd]                         
                            dict_node[n].update(dict_HPD_n) #insert hpd dict in node dict
                elif "location2_80%HPD_" in e: #if node attribute is a list of longitudes
                    dict_HPD[e]={}
                    for hpd in dict_HPD:
                        dict_HPD_n={}
                        if hpd==e:
                            dict_HPD_n[hpd]=dict["nodes"][n][hpd]                       
                            dict_node[n].update(dict_HPD_n)
    return dict_node

def get_points_HPD(dict, pol_lab): #return a dictionnary with each nodes and its relatives coordinates ('lat;long') 
    dict_points=deepcopy(dict)
    for node in dict:
        coords=[]
        for hpds in dict[node]:
            if pol_lab+'1' in hpds:
                hpd=hpds
                hpd2=hpd.replace(pol_lab+'1',pol_lab+'2')
                dict_points[node]={}
#                del dict_points[node][hpd2]
#                del dict_points[node][hpd]
                for i in range(len(dict[node][hpd])):
                    coords.append(str(dict[node][hpd][i])+';'+str(dict[node][hpd2][i]))
                    if dict[node][hpd]==dict[node][hpds]:
                        dict_points[node]=coords
    return(dict_points)

def concatenate_dicts(dict1,dict2): #to concatenate positions in nodes and in leaves
    dict=dict2.update(dict1)
    return(dict2)

def translate_coord_to_countries(dict):
    dict_country=deepcopy(dict)
# Initialize Nominatim API
    geolocator = Nominatim(user_agent="MyScript")

    for node in dict:
        if "NODE" in node:
            dict_country[node]=[]
            for coordinates in dict[node]:
                location = geolocator.reverse(coordinates, language='en', timeout=10) #get all address from coordinates
                address = location.raw['address']  #to get address
                country = address.get('country')  #extract country from the address
                if "Côte d'Ivoire" in country:
                    country = "Ivory Coast"
                    dict_country[node].append(country)
                elif "The Gambia" in country:
                    country = "Gambia"
                    dict_country[node].append(country)
                else:    
                    dict_country[node].append(country)
        else:         
            coord=dict[node]
            location = geolocator.reverse(coord, language='en', timeout=10) #get all address from coordinates
            address = location.raw['address']  #to get address
            country = address.get('country')  #extract country from the address
            if "Côte d'Ivoire" in country:
                country = "Ivory Coast"
                dict_country[node]=country
            elif "The Gambia" in country:
                country = "Gambia"
                dict_country[node]=country
            else:    
                dict_country[node]=country
    with open ('translated_country.txt', 'w') as file:
        file.write(str(dict_country))

def get_weight(pol_lab): #get weight per country (weight = iteration of a country / total number number of vertex)
    with open('translated_country.txt','r') as file:
        contents=file.read() 
        dict= ast.literal_eval(contents) #str to dict
        file.close()
    weights= deepcopy(dict)

    for node in dict:
        if "NODE" in node:
            countries={}
            weights[node]={}
            for country in dict[node]:
                if country not in countries:
                    countries[country]=1
                    weights[node][country]=countries[country]/len(dict[node])
                else:
                    countries[country]+=1
                    weights[node][country]=countries[country]/len(dict[node])           
        else:
            weights[node]={}
            country=dict[node]
            weights[node][country]=1      
    return(weights)

def del_not_wanted(treejson, pol_lab): #return dict_node a dictionary of node that contains related dictionaries with positions of polygons vertex | params(nodes_output)
    with open(treejson, 'r') as file:
        dict = json.load(file) #open the json node_output from augur import beast as a dictionary and turn it into dictionary
        dict2 = deepcopy(dict)
    
    for n in dict["nodes"]: #iterate in JSON over the keys "nodes"
        for e in dict["nodes"][n]:  #for each attributes of nodes and leaves
            if 'location' in e or pol_lab in e or "rate_" in e:
                del dict2["nodes"][n][e]
    return(dict2)

def add_length_attribute(dict, pol_lab):
    dict_loc = get_weight(pol_lab)
    dict2 = deepcopy(dict)
    
    for node in dict["nodes"]:
        for node_l in dict_loc:
            if node == node_l:
                for e in dict["nodes"][node]:
                    if 'rate' in e:
                        dict2["nodes"][node]["branch_length"]=(dict["nodes"][node]["clock_length"]*dict["nodes"][node]["rate"])
                        dict2["nodes"][node]["mutation_length"]=(dict["nodes"][node]["clock_length"]*dict["nodes"][node]["rate"])
                    else:
                        dict2["nodes"][node]["branch_length"]= 0 
                        dict2["nodes"][node]["mutation_length"]= 0

    with open("branch_length.json", 'w') as file:
        json_str = json.dumps(dict2, skipkeys = True, indent = 6)
        file.write(json_str)

def add_location_attribute(dict, pol_lab):
    dict_loc = get_weight(pol_lab)
    dict2 = deepcopy(dict)
    
    for node in dict["nodes"]:
        weights=[]
        for node_l in dict_loc:
            if node == node_l:
                dict2["nodes"][node]["location_confidence"]=dict_loc[node_l]
                for countries in dict2["nodes"][node]["location_confidence"]:
                    if len(weights)==0:
                        max = dict2["nodes"][node]["location_confidence"][countries]
                        location = countries
                        weights=[dict2["nodes"][node]["location_confidence"][countries]]
                    else:
                        weights.append(dict2["nodes"][node]["location_confidence"][countries])
                        if (dict2["nodes"][node]["location_confidence"][countries]) > max:
                            location = countries
                    dict2["nodes"][node]["location"]=location
                entropy = 0
                for n in weights:
                    entropy += numpy.absolute(n * numpy.log(n))
                dict2["nodes"][node]["location_entropy"]=entropy

    with open("output_node_data.json", 'w') as file:
        json_str = json.dumps(dict2, skipkeys = True, indent = 6)
        file.write(json_str)

def help():
    print("\nAUTHOR: Kélian PEREZ\n\n"+
          "USAGE:\tDiscretize_MCC.py [options] <file_in.json>|<file_out.json>\n\n"+
          "OPTIONS:\n -h|--help\t  \t Display AUTHOR, USAGE and OPTIONS for Discretize_MCC.py\n"+
          " -i|--input\tFILE\t Input file path\n"+
          " -o|--output\tFILE\t Output file name [file_out.json]\n"+
          " -pol|--polygon-label\tLABEL\t Polygons label where label is labelX_80%HPD_XX\n\n")

def main(argv):
        
## Arguments gestion
    pol_lab="location"
    print("\n"+"Default polygon label has been chosen :\"location\""+"\n")
    dico_files={
       "file_in":"file_in",
       "file_out":"./file_out.json"
       }

    for i in range(0,len(sys.argv),1):
       
        liste_arg=["-i","--input","-o","--output","-pol","--polygon_label","-h","--help"]
        
        if ( sys.argv[i] in liste_arg[0:2] ):
        
            # Check if a file name/path is given after the option -i|--input and different from an option
            if i+1<len(sys.argv) and sys.argv[i+1] not in liste_arg:
                dico_files["file_in"]=sys.argv[i+1]
            else:
                print("\n"+"Please insert a file name/path after the -i|--input option"+"\n")
                exit()

        elif ( sys.argv[i] in liste_arg[2:4] ):
        
            # Check if a file name or path is given after the option -o|--output and different from an option
            if i+1<len(sys.argv) and sys.argv[i+1] not in liste_arg :
                dico_files["file_out"]=sys.argv[i+1]
            else:
                print("\n"+"Please insert a file name/path after the -o|--output option"+"\n")
                exit()

        elif ( sys.argv[i] in liste_arg[4:6] ):

            # Check if a label is given after the option -pol|--polygon_label and different from an option
            if i+1<len(sys.argv) and sys.argv[i+1] not in liste_arg :
                pol_lab=[sys.argv[i+1]]
                print("\n"+str(pol_lab)+"is now defined as polygon label") 
            else:
                print("\n"+"Please insert a polygon label after the -pol|--polygon_label option"+"\n")
                exit()

        elif ( sys.argv[i] in liste_arg[6:8] ) or ( len(sys.argv) == 1 ):
                help()
                exit()
        elif ((sys.argv[i] not in liste_arg) and i!=0 and (sys.argv[i-1] not in liste_arg)):
            print("\n"+"Please enter correct arguments (for more information, use the --help|-h option)."+"\n")
            exit()
    if ( sys.argv[i] in liste_arg[4:6] ):
        pol_lab=str(pol_lab).replace("[","")
        pol_lab=str(pol_lab).replace("]","")
        pol_lab=str(pol_lab).replace("'","")

    t=str(dico_files["file_in"])
    translate_coord_to_countries(concatenate_dicts(get_points_HPD(get_dict_HPD(t,pol_lab),pol_lab),get_points_leaves(get_dict_leaves(t,pol_lab),pol_lab)))
    get_weight(pol_lab)
    add_length_attribute(del_not_wanted(t,pol_lab),pol_lab)
    add_location_attribute(del_not_wanted(t,pol_lab),pol_lab)

if __name__=="__main__":
    main(sys.argv[1:])