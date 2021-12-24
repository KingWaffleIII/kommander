import django
django.setup()

from django.contrib.sites.models import Site
from django.conf import settings

try:
    site = Site.objects.get(pk=1)

    if settings.DEBUG:
        site.domain = 'dev.planetwaffle.net'
    else:
        site.domain = "kommander.planetwaffle.net"

    site.name = 'Planet Waffle: Kommander'
    site.save()
except Site.DoesNotExist:
    try:
        existing = Site.objects.get(domain='kommander.planetwaffle.net')
        existing.delete()
        existing = Site.objects.get(domain='dev.planetwaffle.net')
        existing.delete()
    except Site.DoesNotExist:
        pass

    site = Site()
    site.pk = 1
    site.name = 'Planet Waffle: Kommander'
    
    if settings.DEBUG:
        site.domain = 'dev.planetwaffle.net'
    else:
        site.domain = "kommander.planetwaffle.net"
    
    site.save()

print(f"Created site: {Site.objects.get(pk=1).domain}")
