# -*- coding: utf-8 -*-
'''
This file offer api to fetch url's content.

'''

import sys
reload(sys)
sys.setdefaultencoding('utf8')

from settings import READABILITY as RS

import requests
import urlparse
import re
import math
import urlparse
from uuid import uuid4 as genid
from BeautifulSoup import  BeautifulSoup as bs, Tag
import numpy as np

ATTR_SCORE = '_xscore'
ATTR_XUUID = '_xuuid'

    
def get(url):

    try :
        get = requests.get(url)
        get.raise_for_status()
            
        candidates = []
        html = bs(get.content)
        
        title = html.find('title').text

        # remove useless
        # we cannot delete this together with evaluating score, becasue findAll does not delete its tag in its loop
        # following will be removed:
        # 1. useless name
        # 2. useless id and not include a useful value
        # 3. uselesss class and not include a useful value
        # 4. empty a/img/p
        [tag.extract() for tag in html.findAll() if re.search(RS['useless']['name'], tag.name, re.I) or \
                                                    (tag.get('id')
                                                     and re.search(RS['useless']['id'], tag['id'], re.I)
                                                     and not re.search(RS['useful']['id'], tag['id'], re.I)) or \
                                                    (tag.get('class')
                                                     and re.search(RS['useless']['class'], tag['class'], re.I)
                                                     and not re.search(RS['useful']['class'], tag['class'], re.I)) or \
                                                    (tag.name == 'img' and not tag.get('src')) or \
                                                    (tag.name == 'a' and not tag.get('href')) or \
                                                    (tag.name == 'p' and not tag.text)
        ]
            
        for tag in html.findAll():
                
            # calculate basic score
            s = 0
            s += len(re.findall(ur'[,.;，。；]', ''.join(filter(lambda x: type(x)!=Tag, tag.contents))))
            s += min(math.floor(len(tag.text) / 100.0), 3.0)

            for item in RS['score']['init']:
                s += item['score'] if re.search(item['name'], tag.name, re.I) else 0

            for key,value in tag.attrMap.iteritems() :
                for item in RS['score']['addition']:
                    s += item['score'] if re.search(item['key'], key, re.I) and re.search(item['value'], value, re.I) else 0

            # multiple the links ratio
            links =  [item for item in tag.contents if type(item)==Tag and item.name in ['a', 'img']]
            s *= (1 - len(links) * 1.0 / max(len(tag.text), 1.0))

            uuid = str(genid())
            tag[ATTR_SCORE] = s
            tag[ATTR_XUUID] = uuid
            candidates.append({ATTR_XUUID: uuid, ATTR_SCORE: s})
            
        with open('test.basic.html', 'w') as f:
            f.write(html.prettify())

        # find top n candicates & filter <= scores
        topn = filter(
            lambda _x : _x[ATTR_SCORE] > 0.0,
            sorted(candidates, key=lambda item : item[ATTR_SCORE], reverse=True))[0:RS['candidates']['topn']]
        print topn
        
        # recusive to top, find for the ancestor with bigger score
        while True:
            tmp = []
            newadd = False
         
            for item in topn:
         
                tag = html.find(attrs={ATTR_XUUID: item[ATTR_XUUID]})

                # we won't use whole html
                if tag.name == 'html':
                    continue

                # if this is directly child of html tag, we won't search for its ancestor
                if tag.parent.name == 'html':
                    tmp.append(item)
                    continue

                # if current tags's parent have already exist, we will add score
                same = [_i for _i, _v in enumerate(tmp) if _v[ATTR_XUUID]==item[ATTR_XUUID]]
                if same:
                    tmp[same[0]][ATTR_SCORE] += item[ATTR_SCORE]
                    continue

                # if the std is bigger than config, just keep current tag
                siblings = tag.parent.findChildren()
                scores = [_i[ATTR_SCORE] for _i in siblings]
                if np.array(scores).std() > RS['candidates']['std']:
                    tmp.append(item)
                    continue

                # everything seems good, add its parent instead of itself
                newadd = True
                tmp.append({ATTR_XUUID: tag.parent[ATTR_XUUID], ATTR_SCORE: tag.parent[ATTR_SCORE] + item[ATTR_SCORE]})

            if not newadd:
                break

            topn = tmp
            print topn
            
        # update scores of the tree
        for item in topn:
            tag = html.find(attrs={ATTR_XUUID: item[ATTR_XUUID]})
            if tag:
                tag[ATTR_SCORE] = item[ATTR_SCORE]

        with open('test.final.html', 'w') as f:
            f.write(html.prettify())

        best = reduce(lambda x, y : x if x[ATTR_SCORE] > y[ATTR_SCORE] else y, topn)
        content = html.find(attrs={ATTR_XUUID: best[ATTR_XUUID]})

        print best
            
        # pretty best
        for tag in content.findAll():
            del (tag['class'], tag['id'], tag['style'])

            if tag.name.lower() in ['iframe', 'form']:
                tag.extract()
            elif tag.name == 'img':
                tag['src'] = urlparse.urljoin(url, tag['src'])

            elif tag.name.lower() == 'object' or tag.name.lower() == 'embed':
                if not filter(lambda x : re.search(settings.READABILITY['vedio'], x[1], re.I), tag.attrs):
                    tag.extract()

        with open('test.html', 'w') as f:
            f.write(content.prettify())
                    
        return {'title': title,
                'content': {
                    'html': content.prettify(),
                    'pure': clean(content.prettify()),
                    'len': len(clean(content.prettify()).decode('utf-8'))
                }
        }

    finally:
        get.close()

        
def clean(htmls):
    non_tags = re.sub(r'</?[^>]*/?>', '', htmls)
    non_space = re.sub(r'\s+', '', non_tags)

    return non_space
