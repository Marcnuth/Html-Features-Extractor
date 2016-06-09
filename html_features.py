# -*- coding: utf-8 -*-


'''
A simple extractor for fetching html file features
'''

import sys
reload(sys)
sys.setdefaultencoding('utf8')


from BeautifulSoup import BeautifulSoup as bs
import jieba, jieba.analyse
import re, requests

#constant features name string
FT_VEDIO_FLAG = 'is_vedio_included'
FT_WORD_COUNT = 'word_count'
FT_TOPN_KEY_WORDS = 'topn_keywords'
FT_TITLE_KEY_WORDS = 'title_keywords'
FT_ARTICLE_FLAG = 'is_article'
FT_ARTICLE_LIST_FLAG = 'is_article_list'


'''
only search the suffix of video in all attributes
'''
def is_vedio_included(hbs) :
    for tag in hbs.findAll():
        if re.search(r'\.(swf|flv|mp4|3gp|ogg|mpeg4|webm)', ','.join([_i[1] for _i in tag.attrs]), re.I):
            return True

    return False

'''
only calulate the text part, and calculate length using utf-8
'''
def count_word(hbs):
    _text = hbs.getText('\n')
    return len(_text.decode('utf-8'))

'''
only get top n Noun. key words. Default n is 10
'''
def get_topn_keywords(hbs, n=10):
    _text = hbs.getText('\n')
    return jieba.analyse.extract_tags(_text, topK=n, allowPOS=('n'))

'''
get title key words
'''
def get_title_keywords(hbs):
    _title = hbs.title
    if not _title or not _title.text.strip():
        return []

    return [_i for _i in jieba.cut(_title.text.strip(), cut_all=False)]
    

'''
we will see a passage as a non-article everytime we found the tile of html is not show in body
this rule will be a little strict, for general purpose, you can use is_article_list
'''
def is_article(url, hbs):
    if re.match(r'^https?://[^/]*/index[^/]*$', url, re.I) or \
       re.match(r'^https?://[^/]*(/\d*)?$', url, re.I):
        return False

    _title = hbs.title.text.strip()
    if not _title:
        return False
    elif hbs.h1 and (hbs.h1.text.strip() in _title or _title in hbs.h1.text.strip()):
        return True
    elif hbs.h2 and (hbs.h2.text.strip() in _title or _title in hbs.h2.text.strip()):
        return True
    elif hbs.h3 and (hbs.h3.text.strip() in _title or _title in hbs.h3.text.strip()):
        return True
    elif hbs.h4 and (hbs.h4.text.strip() in _title or _title in hbs.h4.text.strip()):
        return True

    return False

'''
following will be seen as a article list
1. the website's index page (this will be determined in is_article)
2. title tag's content cannot found in body, or quite less similar to any h1/h2/h3... text (this is determined in is_article)
3. page indicators' found
4. many h1 or h2 titles
'''
def is_article_list(url, hbs):

    if is_article(url, hbs):
        return False

    for tag in hbs.findAll():
        if re.match(r'^[\s\d]+$', tag.text):
            _prev = tag.previousSibling
            if _prev and re.match(r'^[\s\d]+$', _prev.text):
                return True

            _next = tag.netSibling
            if _next and re.match(r'^[\s\d]+$', _next.text):
                return True
    
    _h1s = a.findAll(name=['h1'])
    if _h1s and len(_h1s) > 2:
        return True

    _h2s = a.findAll(name=['h2'])
    if not _h1s and _h2s and len(_h2s) > 2:
        return True

    return False

def get_features(url, hbs, n=10):
    return {
        FT_VEDIO_FLAG: is_vedio_included(hbs),
        FT_WORD_COUNT: count_word(hbs),
        FT_TOPN_KEY_WORDS: get_topn_keywords(hbs, n),
        FT_TITLE_KEY_WORDS : get_title_keywords(hbs),
        FT_ARTICLE_FLAG: is_article(url, hbs),
        FT_ARTICLE_LIST_FLAG: is_article_list(url, hbs)
    }
