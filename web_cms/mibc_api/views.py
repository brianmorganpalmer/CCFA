import re
import os
import sys
import hashlib
from functools import wraps
from itertools import izip, chain

from django.http import HttpResponse
from django.http import Http404

from mibc import (
    settings,
    validate,
    models,
    util,
    efo
)

from . import (
    upload
)

repo = models.Repository()
URLENCODED = 'application/x-www-form-urlencoded'

def send_json(data):
    return HttpResponse( util.serialize(data), 
                         content_type="application/json" )

def project_or_404(username, projectname):
    project = repo.users[username].projects[projectname]
    if not project.exists():
        raise Http404("Project not found")
    else:
        return project

def users_all(request):
    return send_json(repo.users.all())

def user(request, name):
    user = repo.users[name]
    if user.exists():
        return send_json(user)
    else:
        raise Http404('User not found')

def project(request, username, projectname):
    project = project_or_404(username, projectname)
    return send_json(project)

def validate_project(request, username, projectname):
    project = project_or_404(username, projectname)
    validation_results = validate.validate(project)
    return send_json(validation_results)

def mapvalidate_project(request, username, projectname):
    project = project_or_404(username, projectname)
    
    to_validate = list()
    for line_idx, line in enumerate(chain(
            (project.map_headers,), project.map)):
        guesses = enumerate(efo.guess(*line).items())
        to_validate.extend(
            [ ((line_idx, col_idx), efo_id)
              for col_idx, (efo_id, guess) in guesses 
              if guess is True]
        )

    coords, efo_ids = izip(*to_validate)
    validation_results = zip(coords,efo.parallel_validate(*efo_ids).items())

    return send_json(validation_results)
        

def efovalidate(request):

    if request.method != "POST":
        return HttpResponse("post only, please", status=400)

    data = util.deserialize(request.body.read())["data"]

    ret = zip(*[ 
        (idx, val) 
        for idx, val in data
        if efo.guess(val)[val]
    ])

    if not ret:
        return util.serialize([])
    else:
        coords, efo_ids = ret

    validation_results = zip(coords,efo.parallel_validate(*efo_ids).items())

    return send_json(validation_results)


def efosuggest(request):

    if request.method != "POST":
        return HttpResponse("post only, please", status=400)

    data = util.deserialize(request.body.read())["data"]

    terms = [ ( idx, re.sub(r'\W+', ' ', term ) )
              for idx, term in data
              if not re.match(r'.*\d.*', term) ]

    idxs, terms = zip(*[ 
        term for term in terms 
        if term[1] 
    ])

    results = efo.parallel_suggest(*terms)

    return send_json(zip(idxs, results.iteritems()))


def upload_file(request, path):
    if request.method != "POST":
        return upload.probe(request)

    filename = upload.clean_filename(request.POST['name'])
    dst = os.path.join(settings.c_repository_root,
                       path,
                       filename)

    md5chunk = request.POST.get('md5chunk', False)
    md5total = request.POST.get('md5total', False)

    chunk = int(request.POST.get('chunk', 0))
    chunks = int(request.POST.get('chunks', 0))

    if md5chunk and md5total:
        upload.upload_with_checksum(
            request, dst, md5chunk, md5total, chunk, chunks)
    else:
        upload.upload_simple(request, dst, chunk)

    return HttpResponse('uploaded')


def probe(request):
    filename = clean_filename(request.GET['name'])

    dst = os.path.join(settings.c_repository_root, filename)
    if(os.path.exists(dst)):
        f_meta_dst = dst + '.meta'
        if(os.path.exists(f_meta_dst)):
            f_meta = file(f_meta_dst, 'r')
            try:
                data = f_meta.read()
                return HttpResponse(data, content_type=URLENCODED)
            finally:
                f_meta.close()
        else:
            # meta file deleted
            return HttpResponse("status=finished", content_type=URLENCODED)
    else:
        return HttpResponse("status=unknown", content_type=URLENCODED)
    

