class Queue:
    project  = "kgavengers"
    location = "asia-northeast2"
    queue    = "test"
    audience = "https://asia-northeast2-kgavengers.cloudfunctions.net/test1"
    service_account_email = "task-queue-cloud-function@kgavengers.iam.gserviceaccount.com"
    
worker_urls = {
    "test":"https://asia-northeast2-kgavengers.cloudfunctions.net/test1",
    "test_with_IAM":"https://asia-northeast2-kgavengers.cloudfunctions.net/function"
}