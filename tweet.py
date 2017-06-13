#!python
import sys, getopt, os
from datetime import datetime

tf_format = '%Y-%m-%d-%H-%M-%S'
t_format = '%Y-%m-%d %H:%M:%S'

template = '<p><strong>[{datetime}]</strong>: {content}</p>'

tweet_template = '''---
layout: page
title: tweet
permalink: /tweet/
---

{content}
'''

suffix = '.md'

def tweet(msg):
    now = datetime.now()
    with open(os.path.join('_includes', 'tweet', now.strftime(tf_format)+suffix), 'w') as fp:
        content = template.format(datetime=now.strftime(t_format), content=msg)
        fp.write(content)

    files = os.listdir(os.path.join('_includes', 'tweet'))
    files.sort(reverse=True)

    content = '\n'.join(['{% include tweet/'+f+' %}' for f in files])

    with open('tweet.md', 'w') as fp:
        fp.write(tweet_template.format(content=content))


def main(argv):
    message = ''
    try:
        opts, args = getopt.getopt(argv[1:], "hm:", ["message="])
    except getopt.GetoptError as e:
        print str(e)
        print 'tweet.py -m <message>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'tweet.py -m <message>'
            sys.exit()
        elif opt in ("-m", "--message"):
            message = arg
            tweet(message)
            print "success tweet: %s" % message
            sys.exit()
    print "%s -m <message>" % argv[0]

if __name__ == '__main__':
    main(sys.argv)
