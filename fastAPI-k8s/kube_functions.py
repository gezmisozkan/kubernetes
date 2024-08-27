from datetime import datetime, timezone
from kubernetes import client, config
import yaml

config.load_kube_config()
v1 = client.CoreV1Api()
apps_v1 = client.AppsV1Api()

def format_age(age):
    total_seconds = int(age.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}h {minutes}m {seconds}s"


# create a pod with name, label, and image
def create_pod(name:str, label: dict, image:str="nginx"):
    # check if pod already exists
    try:
        v1.read_namespaced_pod(name=name, namespace="default")
        print("Pod already exists")
        return
    except client.rest.ApiException:
        pass
    pod = client.V1Pod(
        metadata=client.V1ObjectMeta(
            name=name,
            labels=label
        ),
        spec=client.V1PodSpec(
            containers=[
                client.V1Container(
                    name="my-container",
                    image=image
                )
            ]
        )
    )
    v1.create_namespaced_pod(namespace="default", body=pod)
    print(f"Pod {name} created!")

# create a deployment from ../yaml_files/all-deployment.yaml
def create_deployment_from_yaml():
    with open("../yaml_files/all-deployments.yaml") as f:
        docs = yaml.safe_load_all(f)
        for dep in docs:
            if dep['kind'] == 'Deployment':
                resp = apps_v1.create_namespaced_deployment(body=dep, namespace="default")
                print("Deployment created. status='%s'" % str(resp.status))

# create a service from ../yaml_files/all-services.yaml
def create_service_from_yaml():
    with open("../yaml_files/all-services.yaml") as f:
        docs = yaml.safe_load_all(f)
        for svc in docs:
            if svc['kind'] == 'Service':
                resp = v1.create_namespaced_service(body=svc, namespace="default")
                print("Service created. status='%s'" % str(resp.status))

def create_deployment(name: str, image: str, replicas: int=1, label: dict[str, str]={"app": "nginx", "tier": "backend"}):
    # Define the deployment specification
    try: 
        apps_v1.read_namespaced_deployment(name=name, namespace="default")
        print(f"Deployment {name} already exists")
        return
    except client.rest.ApiException:
        pass
    deployment = client.V1Deployment(
        metadata=client.V1ObjectMeta(name=name),
        spec=client.V1DeploymentSpec(
            replicas=replicas,
            selector=client.V1LabelSelector(
                match_labels=label
            ),
            template=client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(labels=label),
                spec=client.V1PodSpec(
                    containers=[
                        client.V1Container(
                            name="my-container",
                            image=image
                        )
                    ]
                )
            )
        )
    )

    # Create the deployment
    apps_v1.create_namespaced_deployment(namespace="default", body=deployment)
    print(f"Deployment {name} created!")

#create nodeport service
def create_nodeport_service(name: str, port: int, target_port: int, node_port: int, selector: dict[str, str]={"app": "nginx"}):
    try:
        v1.read_namespaced_service(name=name, namespace="default")
        print(f"Service {name} already exists")
        return
    except client.rest.ApiException:
        pass
    service = client.V1Service(
        metadata=client.V1ObjectMeta(name=name),
        spec=client.V1ServiceSpec(
            ports=[
                client.V1ServicePort(
                    port=port,
                    target_port=target_port,
                    node_port=node_port
                )
            ],
            selector=selector,
            type="NodePort"
        )
    )

    v1.create_namespaced_service(namespace="default", body=service)
    print(f"Service {name} created!")


# list all pods
def list_pods():
    ret = v1.list_pod_for_all_namespaces(watch=False)
    for i in ret.items:
        creation_timestamp = i.metadata.creation_timestamp
        age = datetime.now(timezone.utc) - creation_timestamp
        formatted_age = format_age(age)
        print("%s\t%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name, formatted_age))

# return all pods as a list
def return_pods():
    ret = v1.list_pod_for_all_namespaces(watch=False)
    pods = []
    for i in ret.items:
        creation_timestamp = i.metadata.creation_timestamp
        age = datetime.now(timezone.utc) - creation_timestamp
        formatted_age = format_age(age)
        pods.append({"status": i.status, "name": i.metadata.name, "namespace": i.metadata.namespace, "age": formatted_age})
    return pods

# list all services
def list_services():
    ret = v1.list_service_for_all_namespaces(watch=False)
    for i in ret.items:
        creation_timestamp = i.metadata.creation_timestamp
        age = datetime.now(timezone.utc) - creation_timestamp
        formatted_age = format_age(age)
        print("%s\t%s\t%s\t%s" % (i.spec.cluster_ip, i.metadata.namespace, i.metadata.name, formatted_age))

# list all deployments
def list_deployments():
    ret = v1.list_deployment_for_all_namespaces(watch=False)
    for i in ret.items:
        creation_timestamp = i.metadata.creation_timestamp
        age = datetime.now(timezone.utc) - creation_timestamp
        formatted_age = format_age(age)
        print("%s\t%s\t%s\t%s" % (i.metadata.namespace, i.metadata.name, i.status.replicas, formatted_age))

# return all deployments as a list
def return_deployments():
    ret = apps_v1.list_deployment_for_all_namespaces(watch=False)
    deployments = []
    for i in ret.items:
        creation_timestamp = i.metadata.creation_timestamp
        age = datetime.now(timezone.utc) - creation_timestamp
        formatted_age = format_age(age)
        deployments.append({"name": i.metadata.name, "replicas": i.status.replicas, "namespace": i.metadata.namespace, "age": formatted_age})
    return deployments

# return all services as a list
def return_services():
    ret = v1.list_service_for_all_namespaces(watch=False)
    services = []
    for i in ret.items:
        creation_timestamp = i.metadata.creation_timestamp
        age = datetime.now(timezone.utc) - creation_timestamp
        formatted_age = format_age(age)
        services.append({"cluster_ip": i.spec.cluster_ip, "name": i.metadata.name, "namespace": i.metadata.namespace, "age": formatted_age})
    return services

# delete a pod
def delete_pod(name):
    try:
        v1.read_namespaced_pod(name=name, namespace="default")
    except client.rest.ApiException:
        print(f"Pod {name} does not exist")
        return
    v1.delete_namespaced_pod(name=name, namespace="default")
    print(f"Pod {name} deleted")

# delete a service
def delete_service(name):
    v1.delete_namespaced_service(name=name, namespace="default")
    print("Service deleted")

# delete a deployment
def delete_deployment(name):
    apps_v1.delete_namespaced_deployment(name=name, namespace="default")
    print("Deployment deleted")

# delete all pods
def delete_all_pods():
    try:
        ret = v1.list_namespaced_pod(namespace="default")
        for i in ret.items:
            v1.delete_namespaced_pod(name=i.metadata.name, namespace="default")
        print("All pods in the default namespace deleted")
    except client.rest.ApiException as e:
        print(f"Exception when deleting pods: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

        
# delete all services
def delete_all_services():
    try:
        ret = v1.list_namespaced_service(namespace="default")
        ret.items = [i for i in ret.items if i.metadata.name != "kubernetes"]
        for i in ret.items:
            v1.delete_namespaced_service(name=i.metadata.name, namespace="default")
        print("All services in the default namespace deleted")
    except client.rest.ApiException as e:
        print(f"Exception when deleting services: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

# delete all deployments 
def delete_all_deployments():
    try:
        ret = apps_v1.list_namespaced_deployment(namespace="default")
        for i in ret.items:
            apps_v1.delete_namespaced_deployment(name=i.metadata.name, namespace="default")
        print("All deployments in the default namespace deleted")
    except client.rest.ApiException as e:
        print(f"Exception when deleting deployments: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")