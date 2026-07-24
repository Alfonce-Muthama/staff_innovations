from django.core.paginator import Paginator, EmptyPage
from django.http import JsonResponse


def paginate_queryset(request, queryset, serializer, per_page=10):
    """
    Generic pagination helper.

    serializer -> function that converts one model object into a dictionary.
    """

    page = request.GET.get("page", 1)

    paginator = Paginator(queryset, per_page)

    try:
        current_page = paginator.page(page)
    except EmptyPage:
        current_page = paginator.page(paginator.num_pages)

    return JsonResponse({
        "page": current_page.number,
        "per_page": per_page,
        "total_pages": paginator.num_pages,
        "total_records": paginator.count,
        "has_next": current_page.has_next(),
        "has_previous": current_page.has_previous(),
        "results": [
            serializer(obj)
            for obj in current_page.object_list
        ]
    })