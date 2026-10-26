
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("homepage.urls")),
    path("records/", include("records.urls")),
    path("collections/", include("collections_app.urls")),
]

handler404 = "homepage.views.custom_404"
