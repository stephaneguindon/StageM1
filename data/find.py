#!/usr/bin/env python
#First of all you need to install geopy with : pip install geopy or conda install -c conda-forge geopy 

# Import the required library
from geopy.geocoders import Nominatim
import re

# Initialize Nominatim API
geolocator = Nominatim(user_agent="MyScript")

def get_city_country(coord):
    location = geolocator.reverse(coord, language='en') #get all address from coordinates
    address = location.raw['address']  #to get address
    #state = address.get('state', '')
    #province = address.get('province', '')
    country = address.get('country', '')  #extract country from the address
    if "Côte d'Ivoire" in country:
        country = "Ivory Coast"
    if "The Gambia" in country:
        country = "Gambia"
    #conc = country+'\t'+country+'/'+state
    #if state =='':
    #    conc = country+'\t'+country
    #elif province !='':
    #    conc = country+'/'+province
    #else:
    #    region = address.get('region', '')
    #    conc = country+'/'+region

    return country


with open('metadata_WA261.tsv', 'r') as f, open('metadata_updated_country.tsv','w') as file:
    raw = f.read().splitlines()
    header = raw[0].split("\t")

    header.append('location\tdate')
    #updated_header = str(header).replace('[','')
    #updated_header = str(header).replace(']','')
    #updated_header = str(header).replace(',','')
    #updated_header = str(header).replace("'",'')
    file.write('\t'.join(header)+'\n')
    #column_nb = 0
    #for i in header:
        #column_nb+=1
        #if i == 'state':
    for line in raw[1:]:
        col = line.split("\t")
        date = re.search('^\d{4}', col[0]).group(0)
        line +='\t'+str(get_city_country(col[1:3]))+'\t'+date+'\n'
        file.write(line)
#print(get_city_country("14.4,1.2"))
