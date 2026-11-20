from django.core.paginator import Paginator


def paginate(objects_list, request, per_page=10):
    """Return the requested page and a compact range of navigation links."""
    paginator = Paginator(objects_list, per_page)
    page = paginator.get_page(request.GET.get('page', 1))
    page.navigation = paginator.get_elided_page_range(page.number, on_each_side=2)
    return page
