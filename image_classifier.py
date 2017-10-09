import shutil
import os
import re
import pandas as pd
from ast import literal_eval
global unique_pt_dict
global unique_num
global unique_convention
unique_pt_dict = {}
unique_convention = {}
unique_num     = 0

image_mapping  = pd.read_csv("image_mapping.csv")

def PTcategorize(src_path,category,destn_name):
    cwd      = os.getcwd()
    source   = str(cwd)+'/images/'+str(src_path)
    destn_folder    = str(cwd)+'/PT_kroger_amazon/'+str(category) 
    destn_name      = destn_folder+"/"+destn_name
    if not os.path.exists(destn_folder):
        os.makedirs(destn_folder)
    try: shutil.move(source, destn_name)
    except: print("Error : "+str(source))
    return

def check_for_global_unique_pt(product_name,category):
    global unique_num
    
    if(category not in list(unique_pt_dict.keys())):
        unique_num+=1
        unique_string = "CAX"+str(unique_num)
        unique_pt_dict[category] = {}
        unique_pt_dict[category][product_name] = unique_string
    else:
        if(len(list(unique_pt_dict[category].keys()))==500):
            print("\n > Finished Category: "+str(category))
            return None
        unique_num+=1
        unique_string = "CAX"+str(unique_num)
        if(product_name not in list(unique_pt_dict[category].keys())):
            unique_pt_dict[category][product_name] = unique_string

    return unique_pt_dict[category][product_name]

def return_convention_for_destinaton_path(unique_pt_id,image_name):
    extension  = image_name.split(".")[-1]
    if(unique_pt_id not in list(unique_convention.keys())):
        unique_convention[unique_pt_id]= [image_name]
    else:
        unique_convention[unique_pt_id].append(image_name)
    destn_image_unq_name = unique_pt_id+"_"+str(len(unique_convention[unique_pt_id]))+"."+extension
    return destn_image_unq_name


for index,single_row in image_mapping.iterrows():
   
    if((index+1)%10000==0):
        this_lakh = re.findall(r"[1-9]+",str(index))[0]
        print(" >> "+str(this_lakh)+" thousand Moved.")
    try: 
        detail_dict = literal_eval(single_row["images"])
        source      = str(detail_dict[0]['path'])
        category    = literal_eval(single_row["image_names"])[0]
        product_name = single_row["product_name"]
    except: continue 
    unique_pt_id = check_for_global_unique_pt(product_name,category)
    if(unique_pt_id==None): continue
    destination = return_convention_for_destinaton_path(unique_pt_id,source)
    print(destination)
    PTcategorize(source,category,destination)