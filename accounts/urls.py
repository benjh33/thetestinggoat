from django.conf.urls import url, patterns

urlpatterns = patterns("",
        url(r"^login$", "accounts.views.login", name='login'),
        url(r"^logout$", "accounts.views.logout", name='logout'),
        )
