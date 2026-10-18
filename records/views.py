from django.shortcuts import render
from models.records import find_record_by_id
from storage import load_records

def records(request):
    """Страница со списком всех пластинок."""
    records_list = load_records()
    context = {
        "records": records_list,
    }
    return render(request, "records/record_list.html", context)

def record_detail(request, record_id):
    """Страница конкретной пластинки."""
    records_list = load_records()
    record = find_record_by_id(records_list, record_id)

    context = {
        "record": record,
    }
    return render(
        request, 
        "records/record_detail.html", 
        context, 
        status=404 if record is None else 200
    )