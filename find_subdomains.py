# THIS SCRIPT EXTRACT SUBDOMAINS FROM GOOGLE DORK SEARCHS
# example : python3 find_subdomains.py google.com

import requests
import os
import time
import argparse
import sys

parser = argparse.ArgumentParser()
parser.add_argument("domain", help="Domain to scan")
args = parser.parse_args()

DIR_PATH = os.getcwd()
print("Actual directory : "+DIR_PATH)
SUBDOMAINS = []
SUBDOMAINS_MINUS = []
DOMAIN = args.domain
COMPTEUR = 0

def main():
	global SUBDOMAINS, DOMAIN
	search = "site:*."+DOMAIN
	url = "https://www.google.com/search?q="+search
	
	page_content = get_content_page(url)
	page_content = page_content.replace("*."+DOMAIN,"")
	print(page_content.encode("utf-8"))
	add_subdomains_from_content_page(page_content)
	write_result()
	
	while page_content.find("Aucun document ne correspond aux termes") == -1 and page_content.find("et les mots qui le suivent") == -1 :
		search_updated = ""
		for result in SUBDOMAINS :
			search_updated = search_updated + "+-" +result
		url = "https://www.google.com/search?q=site:*."+DOMAIN+search_updated+"&filter=0"
		page_content = get_content_page(url)
		page_content = page_content.replace("*."+DOMAIN,"")
		page_content = page_content.replace(url,"")
		add_subdomains_from_content_page(page_content)
		write_result()
		if page_content.find("Aucun document ne correspond aux termes") != -1 :
			print("CASE 1")
			write_result()
			print("File written : "+DIR_PATH+"/"+DOMAIN+"_subdomains.txt")
			print("*** END ***")
			sys.exit()
		elif page_content.find("et les mots qui le suivent") != -1 :
			page = 2
			while page_content.find("Page "+str(page)) != - 1 :
				url = get_URL_from_page_number(page_content, page)
				page_content = get_content_page(url)
				page_content = page_content.replace("*."+DOMAIN,"")
				page_content = page_content.replace(url,"")
				add_subdomains_from_content_page(page_content)
				write_result()
				page = page + 1
			print("CASE 2")
			write_result()
			print("File written : "+DIR_PATH+"/"+DOMAIN+"_subdomains.txt")
			print("*** END ***")
			sys.exit()
	print("CASE 3")


def get_URL_from_page_number(page_content, page_number) :
	i = page_content.find('"Page '+str(page_number)+'"')
	i = i + 25 + len(str(page_number))
	url = "https://www.google.com"
	while page_content[i] != '"' :
		url = url + page_content[i]
		i = i + 1
	url = url + "&filter=0"
	url = url.replace("amp;","")
	return url


# Write the subdomains found into the result file
def write_result():
	global SUBDOMAINS, DIR_PATH, DOMAIN
	file = open(DIR_PATH+"/"+DOMAIN+"_subdomains.txt","w",encoding="utf-8")
	for subdomain in SUBDOMAINS :
		file.write(subdomain+"\n")
	file.close()

# Extract the subdomains from the content page
def add_subdomains_from_content_page(content_page):
	global DOMAIN
	while content_page.find(DOMAIN) != -1 :
		i = content_page.find(DOMAIN)
		j = i
		if content_page[i-1] == "." :
			i = i - 2
			while is_domain_name_character(content_page[i]) :
				i = i - 1
			subdomain = content_page[i+1:j]
			subdomain = subdomain.lower()
			if subdomain+DOMAIN in SUBDOMAINS :
				pass
			elif subdomain[0] == "-" or subdomain[0] == "." :
				pass
			else:
				print("subdomain found : "+subdomain+DOMAIN)
				SUBDOMAINS.append(subdomain+DOMAIN)
			content_page = content_page.replace(subdomain+DOMAIN,"")
		else:
			content_page = content_page.replace(content_page[i:i+len(DOMAIN)],"",1)

# Check if the input is an expected caractere for a domain name (no specials except - and .)
def is_domain_name_character(caractere):
	if is_lowcase(caractere) or is_uppercase(caractere) or is_number(caractere) or ord(caractere) == 46 or ord(caractere) == 45:
		return True
	else :
		return False

def is_lowcase(caractere):
	return (ord(caractere) > 96 and ord(caractere) < 123)

def is_uppercase(caractere):
	return (ord(caractere) > 64 and ord(caractere) < 91)

def is_number(caractere):
	return (ord(caractere) > 47 and ord(caractere) < 58)

# Return the content of a webpage
def get_content_page(url):
	global COMPTEUR
	if COMPTEUR == 0 :
		COMPTEUR = 1
	else:
		time.sleep(10)
	headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'}
	response = requests.get(url,headers=headers)
	print("Request to : "+url)
	content = response.text
	return content

if __name__ == "__main__":
	main()