# elk-demo

## Platform 

### RHEL 9.2
[Local testing with podman](https://www.elastic.co/guide/en/elasticsearch/reference/current/run-elasticsearch-locally.html)

Create a container network.
```
podman network create elastic
```

Start the elastic container.
```
podman run -it --name elasticsearch -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" -t docker.elastic.co/elasticsearch/elasticsearch:8.8.2
```
Copy and save the elastic password and enrollment token (expires in 30 minutes). It will be used when you visit the
Kibana UI.

A few health checks.
```
curl -k -u elastic:<password> https://127.0.0.1:9200/_cat/health
```
```
1689710442 20:00:42 docker-cluster green 1 1 1 1 0 0 0 0 - 100.0%
```
```
curl -k -u elastic:<password> https://127.0.0.1:9200
```
```
{
  "name" : "77e542c3f7fb",
  "cluster_name" : "docker-cluster",
  "cluster_uuid" : "918SKMvaQ5ysi7ngAfC2_Q",
  "version" : {
    "number" : "8.8.2",
    "build_flavor" : "default",
    "build_type" : "docker",
    "build_hash" : "98e1271edf932a480e4262a471281f1ee295ce6b",
    "build_date" : "2023-06-26T05:16:16.196344851Z",
    "build_snapshot" : false,
    "lucene_version" : "9.6.0",
    "minimum_wire_compatibility_version" : "7.17.0",
    "minimum_index_compatibility_version" : "7.0.0"
  },
  "tagline" : "You Know, for Search"
}
```

POST some data.
```
$ curl -k -u elastic:password -X POST "https://10.0.14.228:9200/customer/_doc/1?pretty" -H 'Content-Type: application/json' -d'
{
  "firstname": "Jennifer",
  "lastname": "Walters"
}
'
```

GET the data.
```
curl -k -u elastic:jPHCvK0m_hG_xHD5o--f -X GET https://10.0.14.228:9200/customer/_doc/1
```
```
{"_index":"customer","_id":"1","_version":2,"_seq_no":1,"_primary_term":1,"found":true,"_source":
{
  "firstname": "Jennifer",
  "lastname": "Walters"
}
```
Kibana
```
podman run -it --name kibana -p 5601:5601 docker.elastic.co/kibana/kibana:8.8.2

```
Copy the code and visit the URL presented. You will need the elastic enrollent token.

### Openshift (4 years ago probably on Openshift 3.x)
How I deployed a single node ElasticSearch, Logstash, Kibana (ELK) stack on OpenShift. This is for demonstration purposes and is not a supported document. To deploy ELK at scale, you'll want to follow the [Elastic Cloud on Kubernetes](https://operatorhub.io/operator/elastic-cloud-eck) operator. 

### Node configuration

The Elastic Search container requires a kernel parameter to be tuned on the OpenShift
worker nodes.

```
sudo sysctl vm.max_map_count=262144
```

Login to the OpenShift API server and create a new project.

```
oc login https://api.example.com 
PROJ=elk
oc new-project ${PROJ}
```

### ElasticSearch 

Use the OpenShift client to deploy the container from ElasticSearch's registry.

```
oc new-app docker.elastic.co/elasticsearch/elasticsearch:6.8.0
```

Add persistent storage (5GB minimum).

```
oc set volume dc/elasticsearch --add --mount-path=/usr/share/elasticsearch/data --claim-size=10G --claim-class=glusterfs-storage-block
```

Create a route.

```
oc expose svc elasticsearch
```

Save the ElasticSearch route.

```
ES_ROUTE=$(oc get route --selector=app=elasticsearch --output=custom-columns=NAME:.spec.host --no-headers)
```

Confirm the ElasticSearch pod is running and ready.

```
oc get pods
```

Example Output.

```
NAME                    READY     STATUS    RESTARTS   AGE
elasticsearch-2-jn49t   1/1       Running   9          19d
```

Test the ElasticSearch endpoint.

```
curl ${ES_ROUTE}
```

Example output.

```
{
  "name" : "-X-G1Wk",
  "cluster_name" : "docker-cluster",
  "cluster_uuid" : "1mX4vApHQY-wKmPUBv9U4g",
  "version" : {
    "number" : "6.0.1",
    "build_hash" : "601be4a",
    "build_date" : "2017-12-04T09:29:09.525Z",
    "build_snapshot" : false,
    "lucene_version" : "7.0.1",
    "minimum_wire_compatibility_version" : "5.6.0",
    "minimum_index_compatibility_version" : "5.0.0"
  },
  "tagline" : "You Know, for Search"
}
```

### Kibana

Use the OpenShift client to deploy the Kibana container. The ```ELASTICSEARCH_URL``` variable gets set to
the ElasticSearch Kubernetes service hostname. This allows the Kibana pod to **discover** the 
ElasticSearch service.

```
oc new-app docker.elastic.co/kibana/kibana:6.8.0 -e ELASTICSEARCH_URL=http://elasticsearch.elk.svc.cluster.local:9200
```

Add persistent storage.

```
oc set volume dc/kibana --add --mount-path=/usr/share/kibana/data --claim-size=1G
```

Expose the Kibana service as an OpenShift route.

```
oc expose svc kibana
```

Save the Kibana route.

```
KIBANA_ROUTE=$(oc get route --selector=app=kibana --output=custom-columns=NAME:.spec.host --no-headers)
```

Confirm the Kibana pod is running and ready.

```
oc get pods
```

Example Output.

```
NAME                    READY     STATUS    RESTARTS   AGE
elasticsearch-2-jn49t   1/1       Running   9          19d
kibana-3-vwxxj          1/1       Running   0          18d
```

### LogStash

To upload data into ElasticSearch, use the LogStash client for your operating system of choice. This
example should work for Linux or MacOS systems.

```
wget https://artifacts.elastic.co/downloads/logstash/logstash-6.6.2.tar.gz

tar zxf logstash-6.6.2.tar.gz
```

Download the sample data from https://www.kaggle.com/mirosval/personal-cars-classifieds 

```
unzip classified-ads-for-cars.zip
```

Edit ```logstash-load-csv.conf``` (provided in this repo) as follows. 

Input Section

-> The ```path``` variable should point to the CSV file.

Output Section

-> The ```hosts``` variable should be set to the external ElasticSearch route defined in OpenShift.

Now run LogStash to upload the cars data into ElasticSearch. This could take several minutes.

```
bin/logstash -f logstash-load-csv.conf > /dev/null 2>&1 &
```

Watch the progress.

```
curl -XPOST "http://${ES_ROUTE}:80/cars/_count?pretty"
```

Expected output.

```
{
  "count" : 3552913,
  "_shards" : {
    "total" : 5,
    "successful" : 5,
    "skipped" : 0,
    "failed" : 0
  }
}
```

#### Kibana visualization.

* Visit the Kibana console (${KIBANA_ROUTE})
* -> Discover
* Change the index pattern from ```logstash-*``` to ```cars*```
* Set the time filter field to ```@timestamp```
* -> Create Index Pattern

![Kibana](images/index.png)

* Visualize -> Create visualization -> Pie
* Choose the ```cars*``` index
* Split Slices -> Aggregation -> ```Terms```
* Field -> ```maker.keyword```
* Descend -> Size = ```30```
* Choose the "Play/Apply changes" button

![Kibana](images/top30.png)
