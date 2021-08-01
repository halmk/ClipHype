from django.contrib import admin
from .models import Digest, Contact, SocialAppToken


admin.site.register(Digest)
admin.site.register(Contact)
admin.site.register(SocialAppToken)
