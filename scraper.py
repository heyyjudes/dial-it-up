from gensim.summarization import summarize

from bs4 import BeautifulSoup

import requests


def extractText(url):
	response = requests.get(url)
	html = response.content

	result = {}

	soup = BeautifulSoup(html, "html.parser")

	# print soup.encode("utf-8")

	header = soup.find_all("h1")[0]
	result["header"] = header.text
	print(header.text)

	result["text"] = ""

	tag = soup.find_all("main")

	for p_tag in soup.find_all('p'):
		p = p_tag.text.encode("utf-8")
		if len(str(p).split(" ")) > 3:
			result["text"] += p.decode("utf-8")


	return result

def findSummary(text, ratio):
	print('Summary:')
	print(summarize(text, ratio))

if __name__ == "__main__": 
	url = 'https://www.nytimes.com/2018/06/09/science/fish-decompression-chamber.html?action=click&contentCollection=science&region=rank&module=package&version=highlights&contentPlacement=2&pgtype=sectionfront'
	result = extractText(url)["text"]
	print(result)
	findSummary(result, 0.1)

# # body = soup.find(id="site content")
# print tag

# print soup.prettify()