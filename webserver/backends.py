"""
@author: Sebastian Paripsa
@email: paripsa@uni-wuppertal.de
(or: sebastian.paripsa@gmail.com)
@linkedin: https://www.linkedin.com/in/sebastian-paripsa/
@git: https://github.com/San-WierPa
@orcid: https://orcid.org/0009-0000-3487-5399

SEO Tags:
#SciCat #DatasetAutomation #Python #DataScience

Requirements:
- Python 3.10
- SciCat API access
- AWS-S3 access
"""

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from storages.backends.s3boto3 import S3Boto3Storage


if getattr(settings, "LOCAL_STORAGE", False):

    class PublicMediaStorage(FileSystemStorage):
        """
        Local filesystem storage for public media files.
        Used when LOCAL_STORAGE=True.
        """

        def __init__(self, *args, **kwargs):
            kwargs.setdefault("location", settings.MEDIA_ROOT)
            kwargs.setdefault("base_url", settings.MEDIA_URL)
            super().__init__(*args, **kwargs)


    class PrivateMediaStorage(FileSystemStorage):
        """
        Local filesystem storage for private/uploaded files.
        Used when LOCAL_STORAGE=True.
        """

        def __init__(self, *args, **kwargs):
            kwargs.setdefault("location", settings.MEDIA_ROOT)
            kwargs.setdefault("base_url", settings.MEDIA_URL)
            super().__init__(*args, **kwargs)


    class StaticsMediaStorage(FileSystemStorage):
        """
        Local filesystem storage for static files.
        Used when LOCAL_STORAGE=True.
        """

        def __init__(self, *args, **kwargs):
            kwargs.setdefault("location", settings.STATIC_ROOT)
            kwargs.setdefault("base_url", settings.STATIC_URL)
            super().__init__(*args, **kwargs)


else:

    class PublicMediaStorage(S3Boto3Storage):
        """
        S3 storage for publicly accessible media files.
        Used in the existing production configuration.
        """

        location = settings.MEDIA_LOCATION
        default_acl = "public-read"
        querystring_auth = False


    class PrivateMediaStorage(S3Boto3Storage):
        """
        S3 storage for private files.
        Signed/query-string URLs remain enabled.
        """

        location = settings.MEDIA_LOCATION
        default_acl = "private"
        querystring_auth = True


    class StaticsMediaStorage(S3Boto3Storage):
        """
        S3 storage for Django static files.
        """

        location = settings.AWS_LOCATION
        default_acl = "public-read"
        querystring_auth = False