from .model import Joke
import sys
import traceback
import json


json_file = sys.argv[1]

j = Joke()
i = 0
with open(json_file) as f:
    for line in f.readlines():
        item = json.loads(line)
        cont = item['cont'].encode('utf-8')
        if len(cont) >= 1024:
            continue
        #__import__('pdb').set_trace()
        print i
        try:
            j.add(md5_check=True, cont=cont)
        except:
            traceback.print_exc()

        # if i >= 1:
        #	break
        i = i + 1
