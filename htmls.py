'''
A simple extractor for fetching html file features
'''

from BeautifulSoup import BeautifulSoup as bs
import jieba.analyse


class HtmlFeatures :

    def _is_mobile_adapted(self):
        viewport = self.html_bs.head.find(name='meta', attrs={'name':'viewport'})
        if viewport:
            self.mobile_friendly = True
        else:
            self.mobile_friendly = False
    
    def _include_video(self) :

        video_suffix = ['.SWF', '.FLV', '.MP4', '.3GP', '.OGG', '.MPEG4', '.WEBM']
        if [True for item in video_suffix if item in str(self.body_bs)]:
            self.video = True
        elif self.html_bs.find('vedio'):
            self.video = True
        else :
            self.video = False
            
    def _extract_words_cnt(self):
        bs = self.body_bs
     
        #remove useless content
        [s.extract() for s in bs('script')]
        [a.extract() for a in bs('a')]

        #remove tags
        self.body = '\n'.join(i.string for i in bs.fetch() if i.string)

        self.words_count = len(self.body)


    def _extract_n_keywords(self):

        self.keywords = jieba.analyse.extract_tags(self.body, topK=self.kw_cnt, allowPOS=('n'))
        
    
    def __init__(self, html, keyword_count):
        self.html_bs = bs(html)
        self.body_bs = self.html_bs.body
        self.kw_cnt = keyword_count

        self._is_mobile_adapted()
        self._include_video()
        self._extract_words_cnt()
        self._extract_n_keywords()

    def get_features(self) :
        return {
            'include_video': self.video,
            'is_mobile_friendly': self.mobile_friendly,
            'words_count': self.words_count,
            'topn_key_words': self.keywords
        }
