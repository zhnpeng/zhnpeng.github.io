#!python
import sys, getopt, os
from datetime import datetime

t_format = '%Y-%m-%d-%H-%M-%S'

template = '<p>[{datetime}]{content}</p>'

tweet_template = '''---
layout: page
title: tweet
permalink: /tweet/
---

{content}
'''

suffix = '.md'


def main(argv):
    message = ''
    try:
        opts, args = getopt.getopt(argv, "hm:", ["message="])
    except getopt.GetoptError:
        print 'tweet.py -m <message>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'tweet.py -m <message>'
            sys.exit()
        elif opt in ("-m", "--message"):
            message = arg
    now = datetime.now()
    with open(os.path.join('_includes', 'tweet', now.strftime(t_format)+suffix), 'w') as fp:
        content = template.format(datetime=now.strftime(t_format), content=message)
        fp.write(content)

    files = os.listdir(os.path.join('_includes', 'tweet'))
    files.sort(reverse=True)

    content = '\n'.join(['{% include tweet/'+f+' %}' for f in files])

    with open('tweet.md', 'w') as fp:
        fp.write(tweet_template.format(content=content))


if __name__ == '__main__':
    main(sys.argv[1:])
