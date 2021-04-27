# -*- coding: utf-8 -*-
from cornice.service import Service
from pyramid.response import Response
from urllib.parse import urlparse

health = Service(name="health", path="/health", renderer="json")
HEALTH_THRESHOLD_FUNCTIONS = {"any": any, "all": all}


def is_replication_task(task):
    if task.get("type", "") == "replication":
        target = urlparse(task["target"])
        source = urlparse(task["source"])
        return source.path == target.path and source.netloc != target.netloc


@health.get()
def get_spore(request):
    replication_tasks = [
        t for t in getattr(request.registry, "admin_couchdb_server", request.registry.couchdb_server).tasks()
        if is_replication_task(t)
    ]
    output = {
        task["replication_id"]: task["progress"]
        for task in replication_tasks
    }
    try:
        health_threshold = float(request.params.get("health_threshold", request.registry.health_threshold))
    except ValueError as e:
        health_threshold = request.registry.health_threshold
    health_threshold_func_name = request.params.get("health_threshold_func", request.registry.health_threshold_func)
    health_threshold_func = HEALTH_THRESHOLD_FUNCTIONS.get(health_threshold_func_name, all)
    if not (
        output
        and health_threshold_func(
            [
                (task["source_seq"] - task["checkpointed_source_seq"]) <= health_threshold
                for task in replication_tasks
            ]
        )
    ):
        return Response(json_body=output, status=503)
    return output
