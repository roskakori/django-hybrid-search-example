from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from core.forms import SearchForm
from core.readers import documents_matching_full_text_search, documents_matching_plain_search


def home_view(request: HttpRequest) -> HttpResponse:
    form = SearchForm(request.GET or None)
    results = []

    if form.is_valid():
        term = form.cleaned_data["term"]
        kind = form.cleaned_data["kind"]
        iso_language = form.cleaned_data["iso_language"]
        match kind:
            case "plain":
                results = documents_matching_plain_search(iso_language, term)
            case "full-text":
                results = documents_matching_full_text_search(iso_language, term)
            case _:
                pass

    return render(
        request,
        "core/home.html",
        {
            "form": form,
            "results": results,
        },
    )
