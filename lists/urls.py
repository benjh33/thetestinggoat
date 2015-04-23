from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    url(r"^(\d+)/$", "lists.views.view_list", name="view_list"),
    url(r"^users/(.+)/$", "lists.views.my_lists", name="my_lists"),
    ## we are saying no trailing slash means we're manipulating db
    ## so we're adding an item to existing list
    ## and adding a new list
    url(r"^new$", "lists.views.new_list", name="new_list"),
)
