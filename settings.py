

READABILITY = {

    'vedio': r'(http(s)?://(www.)?(youku|youtube|vimeo).com|.swf|.mp4|.mpeg4|.ogg)',

    # score for evaluating tag
    'score': {
        'init': [
            {
                'name': r'(div)',
                'score': 5
            },
            {
                'name': r'(blockquote)',
                'score': 3
            },
            {
                'name': r'(form)',
                'score': -3
            },
            {
                'name': r'(th)',
                'score': -5
            }
        ],
        'addition': [
            {
                'key': r'(id|class)',
                'value': r'(combx|comment|com|contact|foot|footer|footnote|masthead|media|meta|outbrain|promo|related|scroll|shoutbox|sidebar|sponsor|shopping|tags|tool|widget)',
                'score': -25
            },
            {
                'key': r'(id|class)',
                'value': r'(article|body|content|entry|hentry|main|page|pagination|post|text|blog|story)',
                'score': 25
            }
        ]
    },

    # simplify all kinds of to common flag
    'simplify' : [
        {
            'from': r'(a|blockquote|dl|div|img|ol|p|pre|table|ul)',
            'to': 'p'
        }
    ],
    
    # useless name have one or more following flags
    'useless' : {
        'name': r'(script|style|link)',
        'id': r'(combx|comment|community|disqus|extra|foot|header|menu|remark|rss|shoutbox|sidebar|sponsor|ad-break|agegate|pagination|pager|popup|tweet|twitter)',
        'class': r'(combx|comment|community|disqus|extra|foot|header|menu|remark|rss|shoutbox|sidebar|sponsor|ad-break|agegate|pagination|pager|popup|tweet|twitter)',
    },

    # if a item satisfy useful & useless, we won't delete it
    'useful' : {
        'name': r'(body|article)',
        'id':  r'(article|body|content|entry|hentry|main|page|pagination|post|text|blog|story)',
        'class':  r'(article|body|content|entry|hentry|main|page|pagination|post|text|blog|story)'
    }

}

