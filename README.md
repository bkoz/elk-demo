# elk-demo

## Platforms 

### Container approach using podman on RHEL 9.2
[Local testing with podman](https://www.elastic.co/guide/en/elasticsearch/reference/current/run-elasticsearch-locally.html)

Create a container network bridge.
```
podman network create elastic
```

Start the elastic container.
```
podman run -it --name elasticsearch --network=elastic -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" -t docker.elastic.co/elasticsearch/elasticsearch:8.8.2
```
Copy and save the elastic password and enrollment token (expires in 30 minutes). It will be used when you visit the
Kibana UI.

A few health checks.
```
curl -k -u elastic:<password> https://127.0.0.1:9200/_cat/health
```

Example output.
```
1689710442 20:00:42 docker-cluster green 1 1 1 1 0 0 0 0 - 100.0%
```
```
curl -k -u elastic:<password> https://127.0.0.1:9200
```

Example output.
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
curl -k -u elastic:password -X GET https://10.0.14.228:9200/customer/_doc/1
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
podman run -it --name kibana --network=elastic -p 5601:5601 docker.elastic.co/kibana/kibana:8.8.2

```
Copy the code and visit the URL presented. You will need the elastic enrollent token.
After kibana initializes login with the `elastic` user and password from above.

Integrations -> upload

Upload the [Linux log example](https://github.com/logpai/loghub/blob/master/Linux/Linux_2k.log)

Name the index and choose *import*.

View the index in *discover*.

### Kubernetes approach using Openshift 4.12

- Create a namespace
- Install the Elastic Operator
- Create an instance of Elastic
  - Choose the yaml view and add the `- ingest` member to the `node.roles`.

```
  - config:
      node.attr.attr_name: attr_value
      node.roles:
      - master
      - data
      - ingest
```

- Create an instance of Kibana

When creating the Kibana instance check *Disabled indicates that the provisioning of the 
self-signed certifcate should be disabled.

http -> certificate -> selfSignedCertificate -> disabled

oc explain kibanas.kibana.k8s.elastic.co.spec.http.tls.selfSignedCertificate.disabled

- Create a route for Kibana

```
oc create route edge my-kibana-route --service=kibana-sample-no-self-signed-kb-http
```

- Obtain the password for elastic


```
PASSWD=$(oc get secrets elasticsearch-sample-es-elastic-user -o=jsonpath="{.data.elastic}" | base64 --decode)
```

### Openshift Testing
#### POST data using curl

- Obtain the elastic service name that supports port 9200.
```
oc get svc
```

- Connect to the kibana pod
```
oc rsh <kibana-pod> bash
```

- POST some example data
```
curl -k -u elastic:passwd -X POST "https://elasticsearch-sample-es-http:9200/customer/_doc/3?pretty" -H 'Content-Type: application/json' -d'{"firstname": "Bob", "lastname": "K"}'
```
- GET the previous POST.
```
curl -k -u elastic:passwd https://elasticsearch-sample-es-http:9200/customer/_doc/3
```

##### [Elastic Client](https://www.elastic.co/guide/en/elasticsearch/client/python-api/current/overview.html)

##### Kibana UI
- Visit the Kibana route and login as `elastic/$PASSWD`

```
oc get route --selector=common.k8s.elastic.co/type=kibana --output=custom-columns=NAME:.spec.host --no-headers
```

- Un-zip and upload the sample log data (`./data/Linux_2k.log.gz`)

##### LogStash (not tested with Openshift 4)

To upload data into ElasticSearch, use the LogStash client for your operating system of choice. This
example should work for Linux or MacOS systems.

```
wget https://artifacts.elastic.co/downloads/logstash/logstash-8.8.2-linux-x86_64.tar.gz
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
