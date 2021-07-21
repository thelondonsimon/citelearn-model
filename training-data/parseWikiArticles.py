##
## This script parses a given set of Wikipedia articles
## to split the content into sentences. In addition to 
## capturing the contextual heading structure of the 
## sentence, it detects if the sentence has a citation
## (or a citation needed flag)
##

import re
import csv
import requests
from bs4 import BeautifulSoup

# obtain a list of wikipedia article ids to parse
articleIds = []
with open('./fa-article-ids.txt','r') as faFile:
  for line in faFile:
    articleIds.append(line.strip())


# termination headings are a list of H2 level headings in a Wikipedia page that indicate the body of the article is finished
terminationHeadings = ["See also","Notes","References","Further reading","External links"]


with open('./fa-sentences.txt','w') as tsvFile:
  writer = csv.writer(tsvFile, delimiter = '\t')
  writer.writerow(['Article ID','H2 Heading','H3 Heading','H2 #','H3 #','Paragraph #','Sentence #','Sentence','Has Citation','Paragraph Has Citation','Previous Sentence Has Citation','Next Sentence Has Citation'])
  
  for articleId in articleIds:
    # use ?curid query parameter as URL for the page in wikipedia
    url = "https://en.wikipedia.org/wiki/?curid={}".format(articleId)
    html = requests.get(url)
    
    soup = BeautifulSoup(html.content, 'html.parser')
    pageContent = soup.find('div', {"id": "mw-content-text"}).div  # div containing page content
    
    h2Count = 0  # the sequential index of the current H2 heading in the current page
    h3Count = 0  # the sequential index of the current H3 heading in the current H2 section
    parCount = 0 # the sequential index of the current paragraph in the current H2/H3 section
    h2 = None    # the title of the current H2 heading
    h3 = None    # the title of the current H3 heading
    
    # loop through each child element of the <div>, looking for <h2>, <h3> and <p> elements
    for el in pageContent.contents:
      tagType = el.name
      if tagType == 'h2':
        h2Count += 1
        h3Count = 0
        parCount = 0
        h3 = None
        span = el.find('span', {"class": "mw-headline"})
        h2 = span.get_text()
        if h2 in terminationHeadings:
          break
      
      elif tagType == 'h3':
        h3Count += 1
        parCount = 0
        span = el.find('span', {"class": "mw-headline"})
        h3 = span.get_text()
      
      elif tagType == 'p':
        parContents = el.get_text().strip()
        if parContents == '':
          continue
        
        parCount += 1
        
        # to help better sentence splitting:
        # - remove trailing full stops from spaced single letters (e.g. A. B. C. ... => A B C ...)
        parContents = re.sub("([A-Z])\. ",r"\1 ",parContents)
        # - remove full stops from acronyms that are not the end of a sentence (e.g. "the C.I.A. was" => "the CIA was")
        parContents = re.sub(" ([A-Z]\.)+ [a-z]",lambda m: m.group(0).replace('.',''),parContents)
        
        # remove newlines for clean tsv output
        parContents = re.sub("\n"," ",parContents)
        
        # split the paragraph in to sentences by spliting on ". " or ".[\d] " or ".[citation needed] "
        # (the character after the delimeter must be a capital letter or integer to indicate new setence
        splitPar = re.split("([\.\?\!](?:\[\d+\])?(?:\[citation needed\])? )(?=[A-Z0-9])",parContents)
        
        # the output of each sentence will need to know if the paragraph it is in contains a citation,
        # together with whether the preceding and proceding sentences have citations
        parSentences = [] # the sentences which will ultimately be output to TSV
        parHasCitation = False
        
        for i,sp in enumerate(splitPar):
          # we need to re-assemble each sentence by re-concatenating the delimeter which each sentence was just split on 
          # - sentences will be at even list indexes of splitPar and delimeters are at odd indexes
          # - the final sentence in the index will already be properly assembled
          if (i+1) < len(splitPar):
            if (i % 2) == 0:
              sp = (sp + splitPar[i+1]).strip()
              
              # if the 'sentence' is less than 10 characters, suggests problems parsing
              if len(sp) < 10:
                continue
            else:
              continue
          
          # detect if there is a citation or if there is a 'citation needed' flag in the sentence
          if re.search("\[\d+\]",sp) or re.search("\[citation needed\]",sp):
            sp = re.sub("\[\d+\]","",sp)
            sp = re.sub("\[citation needed\]","",sp)
            hasCitation = True
            parHasCitation = True
          else:
            hasCitation = False
          
          parSentences.append((articleId,h2,h3,h2Count,h3Count,sp,hasCitation))
        
        # now that we have parsed all sentences in the paragraph, we can update
        # whether the paragraph and previous/next sentences have citations for the TSV output
        for i,s in enumerate(parSentences):
          (articleId,h2,h3,h2Count,h3Count,sp,hasCitation) = s
          
          if (i == 0):
            prevSentenceHasCitation = False
          else:
            prevSentenceHasCitation = parSentences[i-1][6]
          
          if ((i+1) == len(parSentences)):
            nextSentenceHasCitation = False
          else:
            nextSentenceHasCitation = parSentences[i+1][6]
          
          # output to TSV
          writer.writerow([articleId,h2,h3,h2Count,h3Count,parCount,(i+1),sp,hasCitation,parHasCitation,prevSentenceHasCitation,nextSentenceHasCitation])

