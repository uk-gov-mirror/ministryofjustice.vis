from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404, render
from django.http import Http404
from django.contrib.auth.decorators import permission_required

from wagtail.wagtailadmin.modal_workflow import render_modal_workflow
# from wagtail.wagtailadmin.views.chooser import get_querystring
from wagtail.wagtailadmin.forms import SearchForm

from wagtail.wagtailcore.models import Page



@permission_required('wagtailadmin.access_admin')
def chooser(request, parent_page_id=None):
    page_type = request.GET.get('page_type') or 'wagtailcore.page'
    content_type_app_name, content_type_model_name = page_type.split('.')

    is_searching = False
    page_types_restricted = page_type != 'wagtailcore.page'

    try:
        content_type = ContentType.objects.get_by_natural_key(content_type_app_name, content_type_model_name)
    except ContentType.DoesNotExist:
        raise Http404
    desired_class = content_type.model_class()

    if 'q' in request.GET:
        search_form = SearchForm(request.GET)
        if search_form.is_valid() and search_form.cleaned_data['q']:
            pages = desired_class.objects.exclude(
                depth=1  # never include root
            ).filter(title__icontains=search_form.cleaned_data['q'])[:10]
            is_searching = True

    if not is_searching:
        if parent_page_id:
            parent_page = get_object_or_404(Page, id=parent_page_id)
        else:
            parent_page = Page.get_first_root_node()

        parent_page.can_choose = issubclass(parent_page.specific_class, desired_class)
        search_form = SearchForm()
        pages = parent_page.get_children()

    # restrict the page listing to just those pages that:
    # - are of the given content type (taking into account class inheritance)
    # - or can be navigated into (i.e. have children)

    shown_pages = []
    for page in pages:
        page.can_choose = issubclass(page.specific_class, desired_class)
        page.can_descend = page.get_children_count()

        if page.can_choose or page.can_descend:
            shown_pages.append(page)

    if is_searching:
        return render(request, 'wagtailextra/anchoredchooser/_search_results.html', {
            'querystring': request.GET,
            'searchform': search_form,
            'pages': shown_pages,
            'is_searching': is_searching,
            'page_type_string': page_type,
            'page_type': desired_class,
            'page_types_restricted': page_types_restricted
        })

    return render_modal_workflow(request, 'wagtailextra/anchoredchooser/browse.html', 'wagtailextra/anchoredchooser/browse.js', {
        'allow_external_link': request.GET.get('allow_external_link'),
        'allow_email_link': request.GET.get('allow_email_link'),
        'querystring': request.GET,
        'parent_page': parent_page,
        'pages': shown_pages,
        'search_form': search_form,
        'is_searching': False,
        'page_type_string': page_type,
        'page_type': desired_class,
        'page_types_restricted': page_types_restricted
    })
