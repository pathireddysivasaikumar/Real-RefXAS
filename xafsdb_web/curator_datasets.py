import logging

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods

from . import views


logger = logging.getLogger(__name__)
CURATOR_GROUP = "RefXAS Curators"


def review_status(dataset):
    if dataset.get("isPublished") is True:
        return "Approved"

    history = dataset.get("history")
    entries = history if isinstance(history, list) else [history]
    if any(
        isinstance(entry, dict)
        and "updatedscientificMetadata" in entry
        for entry in entries
    ):
        return "Disapproved"

    return None


@login_required
@require_http_methods(["GET", "POST"])
@csrf_protect
def reviewed_datasets(request):
    if not request.user.is_active or not request.user.groups.filter(
        name=CURATOR_GROUP
    ).exists():
        raise PermissionDenied

    notice = ""
    status_code = 200

    with views.scicat_py.ApiClient(configuration=views.CONFIGURATION) as client:
        client.configuration.access_token = views.get_access()
        datasets = views.scicat_py.DatasetsApi(client)
        reviewed = {}

        for dataset in datasets.datasets_controller_find_all(filter=None):
            dataset_id = dataset.get("id")
            status = review_status(dataset)
            if dataset_id and status:
                reviewed[str(dataset_id)] = {
                    "id": str(dataset_id),
                    "title": dataset.get("datasetName") or str(dataset_id),
                    "status": status,
                }

        if request.method == "POST":
            selected = list(dict.fromkeys(request.POST.getlist("dataset_id")))
            if request.POST.get("confirm") != "yes" or not selected:
                notice = "Select at least one dataset and confirm deletion."
                status_code = 400
            elif any(dataset_id not in reviewed for dataset_id in selected):
                notice = "The selection has changed. Reload the list and select again."
                status_code = 409
            else:
                deleted = 0
                failed = []
                for dataset_id in selected:
                    try:
                        datasets.datasets_controller_find_by_id_and_delete(
                            dataset_id, async_req=False, _preload_content=False
                        )
                    except views.scicat_py.exceptions.ApiException as exc:
                        logger.warning(
                            "SciCat curator delete failed with HTTP status %s",
                            exc.status,
                        )
                        failed.append(reviewed[dataset_id]["title"])
                    else:
                        deleted += 1
                        del reviewed[dataset_id]

                notice = f"Deleted {deleted} SciCat dataset record(s)."
                if failed:
                    notice += " Could not confirm deletion for: " + ", ".join(failed)
                    status_code = 502

    return render(
        request,
        "landing/reviewed_datasets.html",
        {"reviewed": reviewed.values(), "notice": notice},
        status=status_code,
    )
