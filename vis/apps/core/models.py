from django.db import models
from wagtail.wagtailadmin.edit_handlers import FieldPanel, InlinePanel, \
    PageChooserPanel
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailcore.models import Page, Orderable
from modelcluster.fields import ParentalKey


class JadePageMixin(object):

    def get_template(self, request, *args, **kwargs):
        template_path = super(JadePageMixin, self).get_template(request, *args, **kwargs)
        return template_path.replace('.html', '.jade')


class HomePage(JadePageMixin, Page):
    pass


class SimplePage(JadePageMixin, Page):
    content = RichTextField()


class Panel(models.Model):
    title = models.CharField(max_length=255, help_text="Panel Title")
    content = models.TextField(help_text="Panel Body")
    link_page = models.ForeignKey(
        'core.SimplePage',
        null=True,
        blank=True,
        related_name='+'
    )
    link_text = models.CharField(max_length=255, help_text="Link Text", blank=True)

    panels = [
        FieldPanel('title'),
        FieldPanel('content', classname="full"),
        PageChooserPanel('link_page'),
        FieldPanel('link_text'),
    ]

    class Meta:
        abstract = True


class PromoPanel(Panel):
    icon_classname = models.CharField(max_length=255, help_text="Icon class name")

    panels = [
        FieldPanel('icon_classname'),
    ] + Panel.panels

    class Meta:
        abstract = True


class HomePagePromoPanels(Orderable, PromoPanel):
    page = ParentalKey('core.HomePage', related_name='promo_panels')


class HomePagePanels(Orderable, Panel):
    page = ParentalKey('core.HomePage', related_name='panels')


SimplePage.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('content', classname="full"),
]


HomePage.content_panels = [
    FieldPanel('title', classname="full title"),
    InlinePanel(HomePage, 'promo_panels', label="Promo Panels"),
    InlinePanel(HomePage, 'panels', label="Panels"),
]
