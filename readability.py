# -*- coding: utf-8 -*-
'''
This file offer api to fetch url's content.

'''

from settings import READABILITY as RS

import requests
import urlparse
import re
import math
import urlparse
from uuid import uuid4 as genid

from BeautifulSoup import BeautifulSoup as bs


ATTR_SCORE = '_xscore'
ATTR_XUUID = '_xuuid'

    
def grabArticle(url):

    try :
        get = requests.get(url)
        get.raise_for_status()
            
        candidates = {}
        html = bs(get.content)
        
        title = html.find('title').text

        # remove useless
        # we cannot delete this together with evaluating score, becasue findAll does not delete its tag in its loop
        [tag.extract() for tag in html.findAll() if re.search(RS['useless']['name'], tag.name, re.I) or \
                                                    (tag.get('id')
                                                     and re.search(RS['useless']['id'], tag['id'], re.I)
                                                     and not re.search(RS['useful']['id'], tag['id'], re.I)) or \
                                                    (tag.get('class')
                                                     and re.search(RS['useless']['class'], tag['class'], re.I)
                                                     and not re.search(RS['useful']['class'], tag['class'], re.I))]
            
        for tag in html.findAll():
            
            # simplify tag names
            for item in RS['simplify']:
                tag.name = item['to'] if re.search(item['from'], tag.name, re.I) else tag.name

            # add uuid to tag
            uuid = str(genid())
            
            # calculate basic score
            s = 0
            s += len(re.findall(ur'[,.，。]', tag.text)) if tag.name == 'p' else 0
            s += min(math.floor(len(tag.text) / 100.0), 3.0) if tag.name == 'p' else 0

            for item in RS['score']['init']:
                s += item['score'] if re.search(item['name'], tag.name, re.I) else 0

            for key,value in tag.attrMap.iteritems() :
                for item in RS['score']['addition']:
                    s += item['score'] if re.search(item['key'], key, re.I) and re.search(item['value'], value, re.I) else 0
            
            tag[ATTR_SCORE] = s

            if tag.name == 'p':
                tag[ATTR_XUUID] = uuid
                candidates[uuid] = s
                

                    
        # add more score to every candicate
        for uuid, score in candidates.iteritems():
            tag = html.find(attrs={ATTR_XUUID: uuid})
            if tag.parent and tag.parent.get(ATTR_XUUID):
                candidates[tag.parent[ATTR_XUUID]] += score
                if tag.parent.parent and tag.parent.parent.get(ATTR_XUUID):
                    candidates[tag.parent.parent[ATTR_XUUID]] += (score / 2.0)
            
        # add weight of link density
        for uuid, score in candidates.iteritems():
            tag = html.find(attrs={ATTR_XUUID: uuid})
            candidates[uuid] = score * (1 - len(tag.findAll('a')) * 1.0 / max(len(tag.text), 1))
                    
        # update scores of the tree
        for uuid, score in candidates.iteritems():
            tag = html.find(attrs={ATTR_XUUID: uuid})
            if tag:
                tag[ATTR_SCORE] = score

        best = reduce(lambda x, y : x if x[1] > y[1] else y, candidates.iteritems())

        print 'best:' + str(best)
        content = html.find(attrs={ATTR_XUUID: best[0]})

            
        # pretty best
        for tag in content.findAll():
            del (tag['class'], tag['id'], tag['style'])

            if tag.name.lower() in ['iframe', 'form']:
                tag.extract()
            elif tag.name == 'img':
                if not img['src']:
                    img.extract()
                else:
                    img['src'] = urlparse.urljoin(url, img['src'])

            elif tag.name.lower() == 'object' or tag.name.lower() == 'embed':
                if not filter(lambda x : re.search(settings.READABILITY['vedio'], x[1], re.I), tag.attrs):
                    tag.extract()

             
        return {'title': title, 'content': content.prettify()}

    finally:
        get.close()

        
