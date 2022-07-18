import os, sys, json, ast, numpy
from copy import deepcopy


def ignore_jitter():
    with open("output_node_data.json", 'r') as file, open("metadata_updated_country.tsv", 'r') as metadata_tsv:
        dict = json.load(file) #open the json node_output from augur import beast as a dictionary and turn it into dictionary
        dict2 = deepcopy(dict)
        dict_leaves={}

        raw = metadata_tsv.read().splitlines() #read metadata file as a tabulated separated format
        header = raw[0].split("\t")
        for line in raw[1:]:
            col = line.split("\t")

            country = col[3] #extract country from metadata (4th column)
            isolate = col[0] #extract isolate name from metadata (1st column)
            dict_leaves[isolate]= country #dictionnary that attribute real country to each leaf

        for node in dict["nodes"]: #iterate in JSON over the keys "nodes"
            if "NODE" not in node: #to apply the following lines to leaves only
                    location = dict["nodes"][node]["location"] #extract attributed location
                    if dict_leaves[node] != location: #compare real location to attributed location
                        print("BEAST's Jitter has introduced a bias for : "+node+" ...")
                        dict2["nodes"][node]["location"]=dict_leaves[node]
                        dict2["nodes"][node]["location_confidence"]={}
                        dict2["nodes"][node]["location_confidence"][dict_leaves[node]]=1
                        print("Previous location was : " +location+" , resolved location is : "+dict_leaves[node]+"\n")

    with open("output_node_data_without_jitter.json", 'w') as output:
        json_str = json.dumps(dict2, skipkeys = True, indent = 6)
        output.write(json_str)
                    

def main():
    ignore_jitter()

if __name__ == '__main__':
    main()