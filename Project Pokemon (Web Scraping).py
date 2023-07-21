#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 15 09:46:03 2023

@author: vivekchowdary
"""

############################################################################################
################################## Import Libraries ########################################
############################################################################################

# Import the necessary libraries to scrap data from pokemondb.net
from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import re

############################################################################################
############################# Extract Stats & Types ########################################
############################################################################################

# Provide the URL and ready the library to import data
national_dex_pokemondb = requests.get("https://pokemondb.net/pokedex/all", timeout = (100, 200)) # give it 10 seconds to connect to the server, and timeout if server does not send any data back for 200+ seconds)
national_dex_text = BeautifulSoup(national_dex_pokemondb.text, "html.parser")

pokemon_names = national_dex_text.findAll("td", attrs={"class":"cell-name"}) # Extract pokemon names
pokemon_types = national_dex_text.findAll("td", attrs={"class":"cell-icon"}) # Extract pokemon types
pokedex_entries_and_stats = national_dex_text.findAll("td", attrs={"class":"cell-num"}) # Extract pokedex entry numbers and stats

# Convert element.ResultSet to a list
pokemon_names_ls = []
pokemon_types_ls = []
pokedex_entries_and_stats_ls = []

# Store all the pokemon names inside a list
for pokemon_name in pokemon_names:
    pokemon_names_ls.append(pokemon_name.text)
    
# Store all the pokemon types inside a list
for pokemon_type in pokemon_types:
    pokemon_types_ls.append(pokemon_type.text)
    
# Store all the pokedex entries and stats inside a list
for entry_and_stats in pokedex_entries_and_stats:
    pokedex_entries_and_stats_ls.append(entry_and_stats.text)

# Create a temporary dataframe for splitting the records   
df = pd.DataFrame(pokedex_entries_and_stats_ls) # Convert list to a dataframe
df = df.rename(columns={0: "Records"}) # Rename the column 0 to Records
#df.index = np.arange(1, len(df) + 1) # Convert the starting index from 0 to 1
df = df.reset_index() # Reset the index
df["Record_Split"] = df["index"] % 8 # Split the records

# Create another temporary dataframe for splitting the types into 2 separate columns
df1 = pd.DataFrame(pokemon_types_ls) # Convert list to a dataframe
df1 = df1.rename(columns={0: "Types"}) # Rename the column 0 to Records
df1["Type1"] = np.nan # Create a dummy column

# Split the records
for i in range(0, len(df1)):
    df1["Type1"][i] = df1["Types"][i].split()

# This step is explained better at: https://stackoverflow.com/questions/35491274/split-a-pandas-column-of-lists-into-multiple-columns
df2 = pd.DataFrame(df1)
df2[["Type_1", "Type_2"]] = pd.DataFrame(df1.Type1.tolist(), index = df2.index)

# Create the pokedex dataframe and add columns to it
pokedex = pd.DataFrame()
pokedex['Name'] = pokemon_names_ls
pokedex['Type_1'] = df2['Type_1']
pokedex['Type_2'] = df2['Type_2']

# This method of populating the dataframe is extremely fast and effective compared to using the for loops
pokedex['Pokedex_Entry'] = df[df['Record_Split']==0]['Records'].reset_index(drop = True) # Extract pokedex entries from df
pokedex['Total'] = df[df['Record_Split']==1]['Records'].reset_index(drop = True) # Extract total from df
pokedex['HP'] = df[df['Record_Split']==2]['Records'].reset_index(drop = True) # Extract HP from df
pokedex['Attack'] = df[df['Record_Split']==3]['Records'].reset_index(drop = True) # Extract Attack from df
pokedex['Defense'] = df[df['Record_Split']==4]['Records'].reset_index(drop = True) # Extract Defense from df
pokedex['Sp_Atk'] = df[df['Record_Split']==5]['Records'].reset_index(drop = True) # Extract Sp.Atk from df
pokedex['Sp_Def'] = df[df['Record_Split']==6]['Records'].reset_index(drop = True) # Extract Sp.Def from df
pokedex['Speed'] = df[df['Record_Split']==7]['Records'].reset_index(drop = True) # Extract Speed from df

# Delete all unwanted variables from memory
del [[df, df1, df2, i, pokedex_entries_and_stats, pokedex_entries_and_stats_ls,
      pokemon_names, pokemon_names_ls, pokemon_types, pokemon_types_ls, national_dex_pokemondb]]

############################################################################################
################################## Extract Abilities #######################################
############################################################################################

# Scraping abilities from serebii.net
national_dex_serebii = requests.get("https://www.serebii.net/pokemon/nationalpokedex.shtml", timeout = (100, 200)) # give it 10 seconds to connect to the server, and timeout if server does not send any data back for 200+ seconds)
national_dex_text = BeautifulSoup(national_dex_serebii.text, "html.parser")
national_dex_data = national_dex_text.findAll("td", attrs={"class":"fooinfo"}) # Extract all data from the page where class = fooinfo

bcd = []

for xay in national_dex_data:
    #if('(hidden ability)' in xay.text):
    bcd.append(xay.text)

for i in range(0, len(bcd)):
    bcd[i] = bcd[i].strip()

bcd = pd.DataFrame(bcd)
bcd = bcd.replace('', np.NaN).dropna()

bcd = bcd.rename(columns={0: "Records"})
bcd = bcd.reset_index(drop = True).reset_index()
bcd["Record_Split"] = bcd["index"] % 9 # Split the records

df1 = pd.DataFrame()
df1['Names_for_Abilities'] = bcd[bcd['Record_Split']==1]['Records'].reset_index(drop = True)
df1['Abilities'] = bcd[bcd['Record_Split']==2]['Records'].reset_index(drop = True)

df1['Names_for_Abilities'] = df1['Names_for_Abilities'].str.lower()

# Extract abilities from serebii.net
serebii_abilities = []

# Extract pure raw data along with the html tags
national_dex_raw_data = str(national_dex_data)
national_dex_raw_data = national_dex_raw_data.replace('</a> </td>', '</a></td>') # Pokemon with just single ability (such as metapod) has some weird space between </a> and </td>. So removed it.

# Extract all text between the start (.shtml">) and end (</a></td>) characters
serebii_abilities_with_html_tags = re.findall(r'.shtml">(.*?)</a></td>', national_dex_raw_data)

insert_comma = ","
substr = "</a>"

# Insert a comma to separate all the abilities from one another
for i in range(0, len(serebii_abilities_with_html_tags)):
    
    if (substr in serebii_abilities_with_html_tags[i]):
    
        k = 0
        idx = [m.start() for m in re.finditer(substr, serebii_abilities_with_html_tags[i])] # Finding all occurrences of a substring inside a string: https://stackoverflow.com/questions/4664850/how-to-find-all-occurrences-of-a-substring
        
        for j in idx:
            
            serebii_abilities_with_html_tags[i] = serebii_abilities_with_html_tags[i][:j+k] + insert_comma + serebii_abilities_with_html_tags[i][j+k:] # Inserting a substring into a string at a given index: https://stackoverflow.com/questions/4022827/insert-some-string-into-given-string-at-given-index
            k = k + len(insert_comma)

# Append the abilities to a list
for i in range(0, len(serebii_abilities_with_html_tags)):
    
    substr = '</a>'
    
    if(substr in serebii_abilities_with_html_tags[i]):
    
        idx = serebii_abilities_with_html_tags[i].index(substr)
        
        soup = BeautifulSoup(serebii_abilities_with_html_tags[i], 'html.parser')
        serebii_abilities.append(soup.get_text())
        
    else:
        
        serebii_abilities.append(serebii_abilities_with_html_tags[i])
 
# Convert to a dataframe and add the pokemon names       
serebii_abilities = pd.DataFrame(serebii_abilities)
serebii_abilities = serebii_abilities.rename(columns={0: "Abilities"}) 
serebii_abilities['Name'] = df1['Names_for_Abilities'].str.capitalize()

# Split the abilities by comma
serebii_abilities['Abilities_Split'] = serebii_abilities['Abilities'].str.split(', ')
serebii_abilities['Ability_1'] = serebii_abilities['Abilities_Split'].str[0] # https://stackoverflow.com/questions/37125174/accessing-every-1st-element-of-pandas-dataframe-column-containing-lists

serebii_abilities['Ability_2'] = np.NaN
serebii_abilities['Hidden_Ability'] = np.NaN

# Populating the 2nd and hidden abilities
for i in range(0, len(serebii_abilities)):
    
    if (len(serebii_abilities['Abilities_Split'][i]) == 2):
        serebii_abilities['Ability_2'][i] = np.NaN
        serebii_abilities['Hidden_Ability'][i] = serebii_abilities['Abilities_Split'][i][1]
        
    elif(len(serebii_abilities['Abilities_Split'][i]) == 3):
        serebii_abilities['Ability_2'][i] = serebii_abilities['Abilities_Split'][i][1]
        serebii_abilities['Hidden_Ability'][i] = serebii_abilities['Abilities_Split'][i][2]


# Listing all pokemon with different forms but have the same abilities
different_forms_same_abilities = ['Castform', 'Deoxys', 'Burmy', 'Wormadam', 'Rotom', 'Keldeo', 'Meloetta', 
           'Aegislash', 'Pumpkaboo', 'Gourgeist', 'Hoopa', 'Oricorio', 'Wishiwashi',
           'Minior', 'Eiscue', 'Morpeko', 'Zacian', 'Zamazenta', 'Urshifu', 'Basculegion',
           'Maushold', 'Palafin', 'Tatsugiri', 'Dudunsparce']

# Create a new column and list all the names of the Pokemon excluding any mega evolutions, and regional forms as they are all a part of the same page in pokemondb.net
pokedex['Names_for_Abilities'] = ''
            
for i in range(0, len(pokedex)):
    if(('Mega' not in pokedex['Name'][i]) & ('Alolan' not in pokedex['Name'][i]) & ('Partner' not in pokedex['Name'][i]) & ('Galarian' not in pokedex['Name'][i]) & ('Hisuian' not in pokedex['Name'][i]) & ('Paldean' not in pokedex['Name'][i])):
            pokedex['Names_for_Abilities'][i] = pokedex['Name'][i]

# If the record consists of a pokemon with a different form but have the same abilities as the base form, then replace the field 'Names_for_Abilities' with that of the base form
for i in range(0, len(pokedex)):
    for outlier in different_forms_same_abilities:
        if(outlier in pokedex['Name'][i]):
            pokedex['Names_for_Abilities'][i] = outlier 

# Convert all the alphabets to lowercase as the website uses only lowercase letters
pokedex['Names_for_Abilities'] = pokedex['Names_for_Abilities'].str.lower()

# Create a new temporary dataframe and join both the previous dataframes (pokedex, df1) together on name of the pokemon
df2 = pd.merge(pokedex, df1, on = 'Names_for_Abilities', how = 'left')
#df2['Abilities'] = df2['Abilities'].fillna('') # Replace null values with a blank string

# Listing all pokemon with different forms and having different abilities
different_forms_different_abilities = ['Giratina Altered Forme', 'Shaymin Land Forme', 'Basculin Red-Striped Form', 
                                       'Darmanitan Standard Mode', 'Tornadus Incarnate Forme', 'Thundurus Incarnate Forme', 
                                       'Landorus Incarnate Forme', 'Meowstic Male', 'Zygarde 50% Forme', 'Lycanroc Midday Form', 
                                       'Toxtricity Amped Form', 'Indeedee Male', 'Enamorus Incarnate Forme', 'Oinkologne Male', 
                                       'Squawkabilly Green Plumage', 'Gimmighoul Chest Form']

# Discarding the names of pokemon with different forms that have different abilities as their abilities will be extracted later
#for i in range(0, len(df2)):
#    if(df2['Names_for_Abilities'][i] != '') & (df2['Abilities'][i] == ''):
#        df2['Names_for_Abilities'][i] = ''

# Assign temporary dataframe to pokedex        
pokedex = df2

# Create a temporary dataframe and count the records with repeating pokedex entry
df1 = pokedex.groupby('Pokedex_Entry')['Pokedex_Entry'].count()
df1 = pd.DataFrame(df1)

# Rename the column and drop the index
df1 = df1.rename(columns={"Pokedex_Entry": "Count"})
df1 = df1.reset_index(drop = False)

# Merge pokedex and df1 again this time on 'Pokedex_Entry'
df2 = pd.merge(pokedex, df1, on = 'Pokedex_Entry', how = 'left')

# Only extract records where count > 1 (These are all the records belonging to mega-evolutions and regional variants)
df2 = df2[df2['Count'] > 1]
df2 = df2.reset_index(drop = True)
df2['Names_for_Abilities'] = df2['Names_for_Abilities'].str.capitalize()
df2['different_forms_same_abilities'] = False

# Deleting records of pokemon with different forms but same abilities as we have already extracted their abilities in the earlier step
for i in range(0, len(df2)):
    for outlier in different_forms_same_abilities:
        if(outlier in df2['Names_for_Abilities'][i]):
            df2['different_forms_same_abilities'][i] = True

# Only mega-evolutions, regional variants, and same pokemon with different abilities are left now
# Delete records from a pandas dataframe based on a condition
df2 = df2.drop(df2[df2['different_forms_same_abilities'] == True].index) # https://stackoverflow.com/questions/13851535/how-to-delete-rows-from-a-pandas-dataframe-based-on-a-conditional-expression
df2 = df2.reset_index(drop = True)  

# Create 2 new columns that will be used in the next step
df2['New_Names_for_Abilities'] = ''
df2['Abilities_isna'] = df2['Abilities'].isna()

for i in range(0, len(df2)):
    if("'" in df2['Names_for_Abilities'][i]): # Farfetch'd
        df2['Names_for_Abilities'][i] = df2['Names_for_Abilities'][i].replace("'", '')
        
    elif("Mr. " in df2['Names_for_Abilities'][i]): # Mr. Mime
        df2['Names_for_Abilities'][i] = df2['Names_for_Abilities'][i].replace(". ", '-')

for i in range(0, len(df2)):
    for weirdo in different_forms_different_abilities:
        if(weirdo in df2['Name'][i]): # different_forms_different_abilities
            df2['New_Names_for_Abilities'][i] = df2['Names_for_Abilities'][i].split()
            
        elif((weirdo not in df2['Name'][i]) & (df2['Abilities_isna'][i] == False)): # all other pokemon with records belonging to their base forms
            df2['New_Names_for_Abilities'][i] = df2['Names_for_Abilities'][i].split()
 
# Extract only the names of the pokemon leaving all the text related to their forms (Ex: only extract giratina when name is giratina altered forme and so on)
# Extracting first element of a list inside a pandas dataframe column        
df2['New_Names_for_Abilities'] = df2['New_Names_for_Abilities'].str[0] # https://stackoverflow.com/questions/37125174/accessing-every-1st-element-of-pandas-dataframe-column-containing-lists
            
# Convert pokemon names to lower-case and fill null values
df2['New_Names_for_Abilities'] = df2['New_Names_for_Abilities'].str.lower()
df2['New_Names_for_Abilities'] = df2['New_Names_for_Abilities'].fillna('')

############################################################################################
################################### Split Abilities ########################################
############################################################################################
 
# Works but computationally expensive (Keep an eye-out for updates in the future)
# Extract hidden abilities of regional variants from pokemondb.net as serebii.net do not have them unfortunately :( 
# Convert element.ResultSet to a list
hidden_abilities = []

for i in range(0, len(df2)):
    
    if(df2['New_Names_for_Abilities'][i] != ''):
        
        hidden_abilities_scrape_page = requests.get("https://pokemondb.net/pokedex/"+df2['New_Names_for_Abilities'][i], timeout = (100, 200)) # give it 10 seconds to connect to the server, and timeout if server does not send any data back for 200+ seconds
        hidden_abilities_page = BeautifulSoup(hidden_abilities_scrape_page.text, "html.parser")
        hidden_abilities_text = hidden_abilities_page.findAll("small", attrs={"class":"text-muted"})
        
        occurance = str(hidden_abilities_text).count('(hidden ability)')
        
        if((df2['Count'][i] != occurance) & (occurance == 0)):
            for j in range(occurance, df2['Count'][i]):
                hidden_abilities.append('')
        
        elif((df2['Count'][i] > 1) & (occurance == 1)):
            hidden_abilities.append(hidden_abilities_text[0].text)
            
            for j in range(1, df2['Count'][i]):
                hidden_abilities.append('')
            
        elif((occurance > 1) & (df2['Count'][i] == occurance)):
        
            for j in range(0, occurance):
                start = 'ability/'
                end = '" title'
                
                hidden_abilities.append((str(hidden_abilities_text).split(start))[j+1].split(end)[0])
                
        elif((occurance > 1) & (df2['Count'][i] > occurance)):
        
            for j in range(0, occurance):
                start = 'ability/'
                end = '" title'
                
                hidden_abilities.append((str(hidden_abilities_text).split(start))[j+1].split(end)[0])
                
            for k in range(occurance, df2['Count'][i]):
                hidden_abilities.append('')

# Extract regular abilities of mega-evolutions and regional variants from pokemondb.net as serebii.net do not have them unfortunately :(
regular_abilities = []

for i in range(0, len(df2)):
    
    if(i in (16, 88, 255)): # Exclude partner pikachu & eevee and eternatus gigantamax form as they do not have in-game abilities
        regular_abilities.append(str(i) + ';' + '')
    
    elif(df2['New_Names_for_Abilities'][i] != ''):
        
        regular_abilities_scrape_page = requests.get("https://pokemondb.net/pokedex/"+df2['New_Names_for_Abilities'][i], timeout = (1000, 2000)) # give it 10 seconds to connect to the server, and timeout if server does not send any data back for 200+ seconds
        regular_abilities_page = BeautifulSoup(regular_abilities_scrape_page.text, "html.parser")
        regular_abilities_text = regular_abilities_page.findAll("span", attrs={"class":"text-muted"})
        
        # Store all the pokemon abilities inside a list
        for pokemon_name in regular_abilities_text:
            if(('1. ' in pokemon_name) | ('2. ' in pokemon_name)):
                regular_abilities.append(str(i) + ';' + pokemon_name.text)

# Splitting the records by abilities (remember some pokemon have a second ability as well!)              
df1 = pd.DataFrame(regular_abilities)
df1 = df1.rename(columns={0: "df2_Entry_&_Ability"})
df1["df2_Entry_&_Ability_ls"] = df1["df2_Entry_&_Ability"].str.split('.')
    
df1['df2_Entry_&_Ability_Num'] = df1['df2_Entry_&_Ability_ls'].str[0]
df1['df2_Ability'] = df1['df2_Entry_&_Ability_ls'].str[1]


df1["df2_Entry_&_Ability_ls_2"] = df1["df2_Entry_&_Ability"].str.split(';')
df1['df2_Entry'] = df1['df2_Entry_&_Ability_ls_2'].str[0]

df1['df2_Ability'] = df1['df2_Ability'].str.strip()

abc = []
df1['Count'] = 0

for i in range(0, len(df1)):
    
    abc.append(df1['df2_Entry_&_Ability_Num'][i])
    df1['Count'][i] = abc.count(df1['df2_Entry_&_Ability_Num'][i])
    
df1['Entry_Count'] = df1['df2_Entry'] + ' ' + df1['Count'].astype(str)

df1['df2_Ability2'] = df1['df2_Ability'].fillna('')
    
df3 = df1.groupby('Entry_Count', as_index=False).agg({'Entry_Count' : 'first', 'df2_Ability2' : ', '.join})

df3["Split_Entry_Count"] = df3["Entry_Count"].str.split(' ')
df3['Entry'] = df3['Split_Entry_Count'].str[0].astype(int)
df3['Count'] = df3['Split_Entry_Count'].str[1].astype(int)
df3 = df3.sort_values(['Entry', 'Count'], ascending=[True, True])
df3 = df3.reset_index(drop = True)

df3 = df3.rename(columns={'df2_Ability2': 'df2_Ability'})

# Add regular abilities to df2
df2['Abilities'] = df3['df2_Ability']

df2['Hidden_Ability'] = ''

for i in range(0, len(hidden_abilities)):
    df2['Hidden_Ability'][i] = hidden_abilities[i]

# Add hidden abilities to df2
for i in range(0, len(df2)):    
    df2['Hidden_Ability'][i] = df2['Hidden_Ability'][i].replace(' (hidden ability)', '').replace('-', ' ').title()
    
# Readying df2 to merge to pokedex
for i in range(0, len(df2)):
    if (df2['Hidden_Ability'][i] != ''):
        df2['Abilities'][i] = df2['Abilities'][i] + ', ' + df2['Hidden_Ability'][i]  
        
df2 = df2.drop(['Type_1', 'Type_2', 'Pokedex_Entry', 'Total', 'HP', 'Attack', 'Defense', 
                'Sp_Atk', 'Sp_Def', 'Speed', 'Names_for_Abilities', 'Count', 
                'different_forms_same_abilities', 'New_Names_for_Abilities', 'Abilities_isna', 
                'Hidden_Ability'], axis = 1)

df2['Abilities_Split'] = df2['Abilities'].str.split(', ')
df2['Ability_1'] = np.NaN
df2['Ability_2'] = np.NaN
df2['Hidden_Ability'] = np.NaN

# Populating the 1st, 2nd, and hidden abilities
for i in range(0, len(df2)):
    
    if (df2['Abilities'][i] == ''):
        df2['Ability_1'][i] = np.NaN
        
    elif (len(df2['Abilities_Split'][i]) == 1):
        df2['Ability_1'][i] = df2['Abilities_Split'][i][0]
        df2['Ability_2'][i] = np.NaN
        df2['Hidden_Ability'][i] = np.NaN
    
    elif (len(df2['Abilities_Split'][i]) == 2):
        df2['Ability_1'][i] = df2['Abilities_Split'][i][0]
        df2['Ability_2'][i] = np.NaN
        df2['Hidden_Ability'][i] = df2['Abilities_Split'][i][1]
        
    elif(len(df2['Abilities_Split'][i]) == 3):
        df2['Ability_1'][i] = df2['Abilities_Split'][i][0]
        df2['Ability_2'][i] = df2['Abilities_Split'][i][1]
        df2['Hidden_Ability'][i] = df2['Abilities_Split'][i][2]
        
df2 = df2.drop(['Abilities_Split'], axis = 1)

############################################################################################
################################## Merge Dataframes ########################################
############################################################################################

# Readying serebii_abilities to merge to pokedex
serebii_abilities = serebii_abilities.drop(['Abilities_Split'], axis = 1)

# Drop the record belonging to gallade from serebii as the abilities have updated in pokemondb.net but not in serebii.net for some weird reason
serebii_abilities = serebii_abilities.drop(serebii_abilities[serebii_abilities['Name'] == 'Gallade'].index) # https://stackoverflow.com/questions/13851535/how-to-delete-rows-from-a-pandas-dataframe-based-on-a-conditional-expression


for i in range(0, len(pokedex)):
    if(pokedex['Names_for_Abilities'][i] == ''):
       pokedex['Names_for_Abilities'][i] = pokedex['Name'][i] 
       
pokedex['Names_for_Abilities'] = pokedex['Names_for_Abilities'].str.title()

# Concat df2 and serebii_abilities after dropping duplicates
data = pd.concat([df2, serebii_abilities]).drop_duplicates()
data = data.reset_index(drop = True)

# Merge
data = pd.merge(pokedex, data, on = 'Name', how = 'left')

data['Abilities_y'] = data['Abilities_y'].fillna('')

for i in range(0, len(data)):
    if(data['Abilities_y'][i] == ''):
        data['Abilities_y'][i] = data['Abilities_x'][i]
        
# Rename Abilities_y to Abilities
data = data.rename(columns={"Abilities_y": "Abilities"})
        
# Discarde unwanted columns from pokedex
data = data.drop(['Names_for_Abilities', 'Abilities_x', 'Ability_1', 'Ability_2', 'Hidden_Ability'], axis = 1)

data['Abilities'] = data['Abilities'].fillna('')
data['Abilities_Split'] = data['Abilities'].str.split(', ')
data['Ability_1'] = np.NaN
data['Ability_2'] = np.NaN
data['Hidden_Ability'] = np.NaN

# Populating the 1st, 2nd, and hidden abilities
for i in range(0, len(data)):
    
    if (data['Abilities'][i] == ''):
        data['Ability_1'][i] = np.NaN
        
    elif (len(data['Abilities_Split'][i]) == 1):
        data['Ability_1'][i] = data['Abilities_Split'][i][0]
        data['Ability_2'][i] = np.NaN
        data['Hidden_Ability'][i] = np.NaN
    
    elif (len(data['Abilities_Split'][i]) == 2):
        data['Ability_1'][i] = data['Abilities_Split'][i][0]
        data['Ability_2'][i] = np.NaN
        data['Hidden_Ability'][i] = data['Abilities_Split'][i][1]
        
    elif(len(data['Abilities_Split'][i]) == 3):
        data['Ability_1'][i] = data['Abilities_Split'][i][0]
        data['Ability_2'][i] = data['Abilities_Split'][i][1]
        data['Hidden_Ability'][i] = data['Abilities_Split'][i][2]
        
data = data.drop(['Abilities_Split'], axis = 1)

# Final pokedex
pokedex = data

############################################################################################
################################# Create Pokedex.csv #######################################
############################################################################################

# Store the pokedex dataframe as a csv
pokedex.to_csv('Pokedex.csv', index = False, encoding = 'utf-8')

############################################################################################
######################### Perform NLP on Ability Descriptions ##############################
############################################################################################

# Provide the URL and ready the library to import data
abilities_scrape_page = requests.get("https://pokemondb.net/ability", timeout = (100, 200)) # give it 10 seconds to connect to the server, and timeout if server does not send any data back for 200+ seconds)
abilities_page = BeautifulSoup(abilities_scrape_page.text, "html.parser")

pokemon_abilities = abilities_page.findAll("a", attrs={"class":"ent-name"}) # Extract all pokemon abilities
pokemon_ability_descriptions = abilities_page.findAll("td", attrs={"class":"cell-med-text"}) # Extract all pokemon ability descriptions

# Convert element.ResultSet to a list
pokemon_abilities_ls = []

# Store all the pokemon names inside a list
for ability in pokemon_abilities:
    pokemon_abilities_ls.append(ability.text)

# Convert element.ResultSet to a list
pokemon_ability_descriptions_ls = []

# Store all the pokemon names inside a list
for ability_description in pokemon_ability_descriptions:
    pokemon_ability_descriptions_ls.append(ability_description.text)
 
# Extracted the descriptions of abilities for performing some NLP tasks in the future
abilities_with_descriptions = pd.DataFrame()
abilities_with_descriptions['Ability'] = pokemon_abilities_ls
abilities_with_descriptions['Description'] = pokemon_ability_descriptions_ls
