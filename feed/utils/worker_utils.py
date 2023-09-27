import json
from google.cloud import tasks_v2
from worker_secret import Queue, worker_urls

def enqueue_task(
    url: str,
    task_data: dict,
    ) -> tasks_v2.Task:

    project  = Queue.project
    location = Queue.location
    queue    = Queue.queue
    audience = Queue.audience
    service_account_email = Queue.service_account_email
    
    # Create a client.
    client = tasks_v2.CloudTasksClient()

    payload = json.dumps(task_data).encode()
    # Construct the request body.
    task = tasks_v2.Task(
        http_request=tasks_v2.HttpRequest(
            http_method=tasks_v2.HttpMethod.POST,
            url=url,
            oidc_token=tasks_v2.OidcToken(
                service_account_email=service_account_email,
                audience=audience,
            ),
            body=payload,
        ),
    )

    # Use the client to build and send the task.
    return client.create_task(
        tasks_v2.CreateTaskRequest(
            parent=client.queue_path(project, location, queue),
            task=task,
        )
    )
task_data = {
    "data":"this is data"
}
response = enqueue_task(
    worker_urls["test"],
    task_data,
)
print(response)

