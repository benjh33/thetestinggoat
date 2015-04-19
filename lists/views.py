from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.core.exceptions import ValidationError

from .models import Item, List
from .forms import ItemForm
# Create your views here.

def home_page(request):
    return render(request, 'home.html', {'form': ItemForm()})

def view_list(request, list_id):
    list_ = List.objects.get(id = list_id)
    error = None
    if request.method == "POST":
        try:
            item = Item.objects.create(text=request.POST['item_text'], list = list_)
            item.full_clean()
            item.save()
            return redirect(list_)
        except ValidationError:
            # the item is getting saved and failing an FT - different from book.
            item.delete()
            error = "You can't have an empty list item."
    return render(request, 'list.html', {'list': list_, 'error': error, 'form': ItemForm()}) 

def new_list(request):
    list_ = List.objects.create()
    item = Item.objects.create(text=request.POST['item_text'], list = list_)
    try:
        item.full_clean()
        item.save()
    except ValidationError:
        error = "You can't have an empty list item."
        list_.delete()
        return render(request, 'home.html', {'error': error, 'form': ItemForm()})
    return redirect(list_)


