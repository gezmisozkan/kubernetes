from fastapi import FastAPI
import kube_functions as kf
from fastapi.templating import Jinja2Templates
from fastapi import Request

templates = Jinja2Templates(directory="templates")

app = FastAPI()


@app.get("/")
async def read_root(request: Request):
    pods = kf.return_pods()
    deployments = kf.return_deployments()
    services = kf.return_services()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "pods": pods,
        "deployments": deployments,
        "services": services
    })

@app.post("/create-pod")
def create_pod_endpoint(name: str,label: dict[str,str]={"app": "nginx"}, image: str="nginx"):
    kf.create_pod(name, label, image)
    return {"message": "Pod created"}

@app.post("/create-deployment-from-yaml")
def create_deployment_from_yaml():
    try:
        kf.create_deployment()
        return {"message": "Deployment created successfully"}
    except FileNotFoundError as e:
        return {"error": str(e)}

@app.post("/create-service-from-yaml")
def create_service_from_yaml():
    try:
        kf.create_service()
        return {"message": "Service created successfully"}
    except FileNotFoundError as e:
        return {"error": str(e)}

@app.post("/create-deployment")
def create_deployment(name: str, image: str, replicas: int=1, label: dict[str, str]={"app": "nginx", "tier": "backend"}):
    kf.create_deployment(name, image, replicas, label)
    return {"message": "Deployment created"}

@app.post("/create-nodeport-service")
def create_nodeport_service(name: str, port: int, target_port: int, node_port: int, selector: dict[str, str]={"app": "nginx"}):
    kf.create_nodeport_service(name, port, target_port, node_port, selector)
    return {"message": "NodePort service created"}

@app.get("/list-pods")
def get_pods():
    pods = kf.list_pods()
    return {"pods": pods}

@app.get("/k8s/pods")
def list_pods_website(request: Request):
    return templates.TemplateResponse("pods.html", {"request": request, "pods": kf.return_pods()})

@app.post("/delete-pod")
def delete_pod_endpoint(name: str):
    kf.delete_pod(name)
    return {"message": f"Pod {name} deleted"}

@app.post("/delete-pods")
def delete_all_pods_endpoint():
    kf.delete_all_pods()
    return {"message": "All pods deleted"}

@app.post("/delete-services")
def delete_all_services_endpoint():
    kf.delete_all_services()
    return {"message": "All services deleted"}

@app.post("/delete-deployments")
def delete_all_deployments_endpoint():
    kf.delete_all_deployments()
    return {"message": "All deployments deleted"}