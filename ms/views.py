from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from .models import ArtPiece, Artist, Create, Event, Museum
from django.template import RequestContext, loader, Context, Template
from django.core.urlresolvers import reverse
from django.db import connection

from .forms.VeggieForms import SearchForm, SelectRegionForm, SelectTypeForm, SelectStyleForm

region_list = ["Asian", "African", "North American", "Central & South American", "Ocenanian", "European"]
type_list = ["Applied & Decorative Arts","Drawing","Painting","Photograph","Print", "Sculpture","Watercolor"]
style_list = ["Realist","Abstract","Expressionist","Conceptual"]

def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]


def search_piece(query):
       cursor = connection.cursor()
       cursor.execute(
               ''' SELECT *
               FROM art_piece JOIN artist JOIN `create` ON art_piece.art_id = `create`.art_id AND `create`.artist_id=artist.artist_id
               WHERE art_name LIKE '%%' %s '%%'
               OR region LIKE '%%' %s '%%'
               OR style LIKE '%%' %s '%%'
               OR art_type LIKE '%%' %s '%%'
               OR description LIKE '%%' %s '%%'
               OR artist_name LIKE '%%' %s '%%'
               ''', [query, query, query, query, query, query])
       res = dictfetchall(cursor)

       cursor.execute(
               '''SELECT COUNT(*)
               FROM art_piece JOIN artist JOIN `create` ON art_piece.art_id = `create`.art_id AND `create`.artist_id=artist.artist_id
               WHERE art_name LIKE '%%' %s '%%'
               OR artist_name LIKE '%%' %s '%%'
               OR region LIKE '%%' %s '%%'
               OR style LIKE '%%' %s '%%'
               OR art_type LIKE '%%' %s '%%'
               OR description LIKE '%%' %s '%%' ''', [query, query, query, query, query, query])
       row = cursor.fetchone()

       return res, row[0]

def search_event(query):
        res = Event.objects.raw("SELECT * FROM event WHERE event_name LIKE '%%' %s '%%'", [query])

        cursor = connection.cursor()
        cursor.execute(
                '''
                SELECT COUNT(*)
                FROM event
                WHERE event_name LIKE '%%' %s '%%'
                ''', [query])

        row = cursor.fetchone()
        return res, row[0]

def index(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)

        # # dropdown queries
        # art_region = request.POST.get('region')
        # art_type = request.POST.get('type')
        # art_style = request.POST.get('style')

        # c = RequestContext(request, {
        #     'r': art_region,
        #     't': art_type,
        #     's': art_style,})

        # return render(request, 'ms/drop.html', c)

        if form.is_valid():
            # Processing the data, i.e. query them from the database
            search_query = form.cleaned_data['content']
            # return render(request, 'ms/results_artpieces.html', context)
            return HttpResponseRedirect('/ms/results/search_artpieces_%s' % search_query)

    else:
        form = SearchForm()

    return render(request, 'ms/index.html', {'form': form,
                                               'region_list': region_list,
                                               'type_list':type_list,
                                               'style_list':style_list})


def results(request):
    return render(request, 'ms/results.html', {})

def results_artpieces(request, search_query):
    # if request.method == 'POST':
    #     form = SearchForm(request.POST)
    #     if form.is_valid():
    #         # do a new search
    #         search_query = form.cleaned_data['content']
    #         art_piece_list, piece_num= search_piece(search_query)
    #         if len(list(art_piece_list)) <= 0:
    #             art_piece_list = None

    #         context = RequestContext(request, {
    #             'art_piece_list': art_piece_list,
    #             'piece_num': piece_num,
    #             'query':search_query,
    #             'form': form,
    #         })
    #         return render(request, 'ms/results_artpieces.html', context)
    #     else:
    #         return HttpResponseRedirect('/ms/')
    # else:
        form = SearchForm()
        art_piece_list, piece_num= search_piece(search_query)
        if len(list(art_piece_list)) <= 0:
            art_piece_list = None

        context = RequestContext(request, {
            'art_piece_list': art_piece_list,
            'piece_num': piece_num,
            'query':search_query,
            'form': form,
        })

        return render(request, 'ms/results_artpieces.html', context)


def results_events(request, search_query):
    form = SearchForm()

    event_list, event_num= search_event(search_query)
    if len(list(event_list)) <= 0:
        event_list = None

    context = RequestContext(request, {
        'event_list': event_list,
        'event_num': event_num,
        'query':search_query,
        'form':form,
    })
    return render(request, 'ms/results_events.html', context)

def thanks(request):
    return render(request, 'ms/thanks.html', {})
