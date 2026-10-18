from django.shortcuts import render
from models.collections import find_collection_by_id
from storage import load_collections, load_records

def collections(request):
    """Страница со списком коллекций."""
    all_records = load_records()
    collections_list = load_collections(all_records)
    
    context = {
        "collections": collections_list,
    }
    return render(request, "collections_app/collection_list.html", context)

def collection_detail(request, collection_id):
    """Страница конкретной коллекции."""
    all_records = load_records()
    collections_list = load_collections(all_records)
    collection = find_collection_by_id(collections_list, collection_id)

    context = {
        "collection": collection,
    }
    return render(
        request, 
        "collections_app/collection_detail.html", 
        context, 
        status=404 if collection is None else 200
    )