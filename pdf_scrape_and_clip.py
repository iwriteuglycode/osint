'''
This is a very wonky Python script to extract text from a PDF and scrape for IOCs.

1- Asks user for download PDF URL
2- Converts the PDF to text
3- Extracts International and Domestic Phone Number, Email Address, Domain, IPv4 Address, 
4- Spits out the results onto the clipboard

This does NOT work with scanned pictures converted to PDF (weak pdf). It should work with .doc or .txt files converted to PDF (strong pdf).

Matthew Pahl - 2020
'''

#TODO: Perhaps incorporate glob to natively find PDFs in a directory?

import io
import requests
import PyPDF2      #PDF strong text module
import pyperclip   #Clipboard module
import re          #RegEx
import sys         #sys.exit in the event of a faulty url or pdf download

url = input("Please paste in the .pdf URL!")          #example is https://www.justice.gov/opa/press-release/file/1334551/download
r = requests.get(url)
f = io.BytesIO(r.content)                             #convert pdf found at URL to a stream

try:
    pdfReader = PyPDF2.PdfFileReader(f)               #Read the open files
except :                                              #If the PDF on the download URL is bad, then exit 
        print('Error: Unable to extract the PDF from the download URL.')
        sys.exit()
        
num_pages = pdfReader.numPages                    #Determine the page count of the document
count = 0
text = ""

while count < num_pages:                     #While loop for pagination
    pageObj = pdfReader.getPage(count) 
    count +=1                                #Increment the page
    text += pageObj.extractText()            #Get the text and append it into the 'text' variable
    
#print(text)                                 #testing 

text = text.replace('\n', ' ')               #eliminate new lines, which was causing formatting issues with the extracted text

#print(text)                                 #testing

#create phone regex

phoneRegex = re.compile(r'''( 

    (\+?\d{1,3}\s)?         #first group including "+" and " " if present
    (\d{2,3}|\(\d{3}\))?    #second group accounting for 2 or 3 digits and parentheses in US area code
    (\s|-|\.)?(\d{3,4})     #third group, 3 or 4 digits
    (\s|-|\.)(\d{4})        #fourth group
    )''', re.VERBOSE)


#Create Email Regex

emailRegex = re.compile(r'''(
    [a-zA-Z0-9._%+-]+				#username
    @								#@ symbol
    [a-zA-Z0-9.-]+					#domain name
    (\.[a-zA-Z]{2,5})				#tld
    )''', re.VERBOSE)
    

#Create Domain Regex

domainRegex = re.compile(r'((?=^.{4,253}$)(^((?!-)[a-zA-Z0-9-]{0,62}[a-zA-Z0-9]\.)+[a-zA-Z]{2,63}$))')

#Create IPv4 Regex

ipv4Regex = re.compile(r'((([01]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])[ (\[]?(\.|dot)[ )\]]?){3}([01]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5]))')

#Find result matches and add them into a set

matches = set()
for groups in phoneRegex.findall(text):
	phoneNum = ''.join([groups[0], groups[1], groups[3], groups[5]])
	matches.add(phoneNum)
    
for groups in emailRegex.findall(text):
	matches.add(groups[0])
    
for groups in domainRegex.findall(text):
    matches.add(groups[0])

for groups in ipv4Regex.findall(text):
    matches.add(groups[0])

#copy results to the clipboard
if len(matches) > 0:
    pyperclip.copy('\n' .join(matches))
    print('Copied to clipboard:')
    print(','.join(matches))		
else:
	print('No IoC\'s found.')
