# django-mpathy changelog

Breaking/important changes for all released versions of django-mpathy will be listed here.

# 0.2.0

* Dropped support for Django < 3.2
* Added support for django 3.2 and 4.0
* Removed the `mpathy.compat` module. If you are using it for `GistIndex` in your migrations, just replace with the `django.contrib.postgres.indexes` module instead.
