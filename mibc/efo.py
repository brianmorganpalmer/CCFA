
import re
import Queue
import urllib
import urllib2
import threading

EFO_BASE_URL="http://www.ebi.ac.uk/efo"
rx_efo = r'EFO_\d{7}$'
rx_suggest = r'<a.*href\s*=\s*"(\S+_\d\S+)">\s*(\S+)\s*</a>'

IGNORED_TERMS = set([
    'SampleID', 'BarcodeSequence', 
    'LinkerPrimerSequence', 'Run_accession',
    'Description'
])

def head(url):
    request = urllib2.Request(url)
    request.get_method = lambda : 'HEAD'
    response = urllib2.urlopen(request)
    return response


def guess(*efo_ids):
    return dict([
        (efo_id, bool(re.match(rx_efo, efo_id)))
         for efo_id in efo_ids
        ])

def validate(*efo_ids):
    ret = dict()
    for efo_id in efo_ids:
        try:
            response = head(EFO_BASE_URL+"/"+efo_id)
            ret[efo_id] = bool(response.code == 200)
        except urllib2.HTTPError as e:
            if e.code == 404:
                ret[efo_id] = False
            else:
                raise
    return ret


def parallel_validate(*efo_ids, **kwargs):
    threads = kwargs.get('threads', 5)
    timeout = kwargs.get('timeout', 0.2)

    in_queue, out_queue = Queue.Queue(), Queue.Queue()

    for efo_id in efo_ids:
        in_queue.put(efo_id)

    def _consume():
        while True:
            try:
                val = in_queue.get(timeout=timeout)
                if val:
                    out_queue.put( (val, validate(val)), 
                                   timeout=timeout )
            except Queue.Empty:
                return

    for _ in range(threads):
        threading.Thread(target=_consume).start()
        
    ret = dict()
    while len(ret) < len(efo_ids):
        try:
            _, status = out_queue.get(timeout=timeout)
            ret.update(status)
        except Queue.Empty:
            continue

    return ret
        

def suggest(*terms):

    guesses = guess(*terms)

    ret = dict()
    for term in terms:
        if guesses[term] is True:
            ret[term] = [(term, term)]
            continue

        if term in IGNORED_TERMS:
            ret[term] = []
            continue

        url = "%s/search?%s" %( 
            EFO_BASE_URL, 
            urllib.urlencode({"query": term, "submitSearch": "Search" }) 
        )
        try:
            matches = iter( re.search(rx_suggest, line) 
                            for line in urllib2.urlopen(url) )
        except urllib2.HTTPError as e:
            pass
        
        ret[term] = [ (match.group(1).split('/')[-1], match.group(2))
                      for match in matches 
                      if match and "EFO" in match.group(0) ]

    return ret


def parallel_suggest(*terms, **kwargs):
    threads = kwargs.pop('threads', 5)
    timeout = kwargs.pop('timeout', 0.2)

    in_queue, out_queue = Queue.Queue(), Queue.Queue()

    for term in terms:
        in_queue.put(term)

    def _consume():
        while True:
            try:
                val = in_queue.get(timeout=timeout)
                if val:
                    out_queue.put( (val, suggest(val)), 
                                   timeout=timeout )
            except Queue.Empty:
                return

    for _ in range(threads):
        threading.Thread(target=_consume).start()
        
    ret = dict()
    while len(ret) < len(terms):
        try:
            _, status = out_queue.get(timeout=timeout)
            ret.update(status)
        except Queue.Empty:
            continue

    return ret

    
###
# Tests

def validate_test():
    good_efos = ['EFO_0000761','EFO_0000762','EFO_0000763',
                 'EFO_0000764','EFO_0000765','EFO_0000766']
    bad_efos  = ['EFO_0000767','EFO_00007610']
    assert all([ v for _, v in validate(*good_efos).iteritems()])
    assert not any([ v for _, v in validate(*bad_efos).iteritems()])

def parallel_validate_test():
    good_efos = ['EFO_0000761','EFO_0000762','EFO_0000763',
                 'EFO_0000764','EFO_0000765','EFO_0000766']
    bad_efos  = ['EFO_0000767','EFO_00007610']
    assert all([ v for _, v in parallel_validate(*good_efos).iteritems()])
    assert not any([ v for _, v in parallel_validate(*bad_efos).iteritems()])

def guess_test():
    good_efos = ['EFO_0000761','EFO_0000762','EFO_0000763',
                 'EFO_0000764','EFO_0000765','EFO_0000766']
    bad_efos  = ['EFO_00767','EFO_00007610', '_0000761', 'EFO_001kj33']
    assert all([ v for _, v in guess(*good_efos).iteritems()])
    assert not any([ v for _, v in guess(*bad_efos).iteritems()])
