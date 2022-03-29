.. _Output:

Output modules
==============

DevNull
-----------

Just discard messages send to this module.

Configuration template:

::

    - output.DevNull


ElasticSearch
-----------------

Store the data dictionary in an elasticsearch index.

The elasticsearch module takes care of discovering all nodes of the elasticsearch cluster.
Requests will the be loadbalanced via round robin.

| **action**:      Either index or update. If update be sure to provide the correct doc_id.
| **format**:      Which event fields to send on, e.g. '$(@timestamp) - $(url) - $(country_code)'.
| If not set the whole event dict is send.
| **nodes**:       Configures the elasticsearch nodes.
| **read_timeout**: Set number of seconds to wait until requests to elasticsearch will time out.
| **connection_type**:     One of: 'thrift', 'http'.
| **http_auth**:   'user:password'.
| **use_ssl**:     One of: True, False.
| **index_name**:  Sets the index name. Timepatterns like %Y.%m.%d and dynamic values like $(bar) are allowed here.
| **doc_id**:      Sets the es document id for the committed event data.
| routing:    Sets a routing value (@see: http://www.elasticsearch.org/blog/customizing-your-document-routing/)
| Timepatterns like %Y.%m.%d are allowed here.
| **ttl**:         When set, documents will be automatically deleted after ttl expired.
| Can either set time in milliseconds or elasticsearch date format, e.g.: 1d, 15m etc.
| This feature needs to be enabled for the index.
| @See: http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/mapping-ttl-field.html
| **sniff_on_start**:  The client can be configured to inspect the cluster state to get a list of nodes upon startup.
| Might cause problems on hosts with multiple interfaces. If connections fail, try to deactivate this.
| **sniff_on_connection_fail**:  The client can be configured to inspect the cluster state to get a list of nodes upon failure.
| Might cause problems on hosts with multiple interfaces. If connections fail, try to deactivate this.
| **store_interval_in_secs**:      Send data to es in x seconds intervals.
| **batch_size**:  Sending data to es if event count is above, even if store_interval_in_secs is not reached.
| **backlog_size**:    Maximum count of events waiting for transmission. If backlog size is exceeded no new events will be processed.

Configuration template:

::

    - output.ElasticSearch:
       action:                          # <default: 'index'; type: string; is: optional; values: ['index', 'update']>
       format:                          # <default: None; type: None||string; is: optional>
       nodes:                           # <type: string||list; is: required>
       read_timeout:                    # <default: 10; type: integer; is: optional>
       connection_type:                 # <default: 'urllib3'; type: string; values: ['urllib3', 'requests']; is: optional>
       http_auth:                       # <default: None; type: None||string; is: optional>
       use_ssl:                         # <default: False; type: boolean; is: optional>
       index_name:                      # <default: 'lumbermill-%Y.%m.%d'; type: string; is: optional>
       doc_id:                          # <default: '$(lumbermill.event_id)'; type: string; is: optional>
       routing:                         # <default: None; type: None||string; is: optional>
       ttl:                             # <default: None; type: None||integer||string; is: optional>
       sniff_on_start:                  # <default: False; type: boolean; is: optional>
       sniff_on_connection_fail:        # <default: False; type: boolean; is: optional>
       store_interval_in_secs:          # <default: 5; type: integer; is: optional>
       batch_size:                      # <default: 500; type: integer; is: optional>
       backlog_size:                    # <default: 500; type: integer; is: optional>


File
--------

Store all received events in a file.

| **file_name**:  absolute path to filen. String my contain pythons strtime directives and event fields, e.g. %Y-%m-%d.
| format: Which event fields to use in the logline, e.g. '$(@timestamp) - $(url) - $(country_code)'
| **store_interval_in_secs**:  sending data to es in x seconds intervals.
| **batch_size**:  sending data to es if event count is above, even if store_interval_in_secs is not reached.
| **backlog_size**:  maximum count of events waiting for transmission. Events above count will be dropped.
| **compress**:  Compress output as gzip or snappy file. For this to be effective, the chunk size should not be too small.

Configuration template:

::

    - output.File:
       file_name:                       # <type: string; is: required>
       format:                          # <default: '$(data)'; type: string; is: optional>
       store_interval_in_secs:          # <default: 10; type: integer; is: optional>
       batch_size:                      # <default: 500; type: integer; is: optional>
       backlog_size:                    # <default: 500; type: integer; is: optional>
       compress:                        # <default: None; type: None||string; values: [None,'gzip','snappy']; is: optional>


Graphite
--------

Send metrics to graphite server.

| **server**:  Graphite server to connect to.
| **port**:  Port carbon-cache is listening on.
| **formats**:  Format of messages to send to graphite, e.g.: ['lumbermill.stats.event_rate_$(interval)s $(event_rate)'].
| **store_interval_in_secs**:  Send data to graphite in x seconds intervals.
| **batch_size**:  Send data to graphite if event count is above, even if store_interval_in_secs is not reached.
| **backlog_size**:  Send count of events waiting for transmission. Events above count will be dropped.

Here a simple example to send http_status statistics to graphite:

::

    - output.Statistics:
        interval: 10
        fields: ['http_status']

    - output.Graphite:
        filter: if $(field_name) == "http_status"
        server: 127.0.0.1
        batch_size: 1
        formats: ['lumbermill.stats.http_200_$(interval)s $(field_counts.200)',
                  'lumbermill.stats.http_400_$(interval)s $(field_counts.400)',
                  'lumbermill.stats.http_total_$(interval)s $(total_count)']


Configuration template:

::

    - output.Graphite:
       server:                          # <default: 'localhost'; type: string; is: optional>
       port:                            # <default: 2003; type: integer; is: optional>
       formats:                         # <type: list; is: required>
       store_interval_in_secs:          # <default: 5; type: integer; is: optional>
       batch_size:                      # <default: 50; type: integer; is: optional>
       backlog_size:                    # <default: 50; type: integer; is: optional>


Kafka
-----


Publish incoming events to kafka topic.

| **topic**: Name of kafka topic to send data to.
| **brokers**: Kafka brokers to connect to.
| **key**: Key for compacted topics.
| **format**: Which event fields to send on, e.g. '$(@timestamp) - $(url) - $(country_code)'. If not set, the whole event dict is send.

Configuration template:

::

    - output.Kafka:
       topic:                           # <type: string; is: required>
       brokers:                         # <default: ['localhost:9092']; type: list; is: optional>
       key:                             # <default: None; type: None||string; is: optional>
       format:                          # <default: None; type: None||string; is: optional>

Logger
----------

Send data to lumbermill logger.

formats: Format of messages to send to logger, e.g.:
['############# Statistics #############',
'Received events in $(interval)s: $(total_count)',
'EventType: httpd_access_log - Hits: $(field_counts.httpd_access_log)',
'EventType: Unknown - Hits: $(field_counts.Unknown)']

Configuration template:

::

    - output.Logger:
       formats:                         # <type: list; is: required>


MongoDb
-----------

Store incoming events in a mongodb.

| **host**: Mongodb server.
| **database**:  Mongodb database name.
| **collection**:  Mongodb collection name. Timepatterns like %Y.%m.%d and dynamic values like $(bar) are allowed here.
| **optinonal_connection_params**: Other optional parameters as documented in https://api.mongodb.org/python/current/api/pymongo/mongo_client.html
| **format**:      Which event fields to send on, e.g. '$(@timestamp) - $(url) - $(country_code)'.
| If not set the whole event dict is send.
| **doc_id**:      Sets the document id for the committed event data.
| **store_interval_in_secs**:      Send data to es in x seconds intervals.
| **batch_size**:  Sending data to es if event count is above, even if store_interval_in_secs is not reached.
| **backlog_size**:    Maximum count of events waiting for transmission. If backlog size is exceeded no new events will be processed.

Configuration template:

::

    - output.MongoDb:
       host:                            # <default: 'localhost:27017'; type: string; is: optional>
       database:                        # <default: 'lumbermill'; type: string; is: optional>
       collection:                      # <default: 'lumbermill-%Y.%m.%d'; type: string; is: optional>
       optinonal_connection_params:     # <default: {'serverSelectionTimeoutMS': 5}; type: dictionary; is: optional>
       format:                          # <default: None; type: None||string; is: optional>
       doc_id:                          # <default: '$(lumbermill.event_id)'; type: string; is: optional>
       store_interval_in_secs:          # <default: 5; type: integer; is: optional>
       batch_size:                      # <default: 500; type: integer; is: optional>
       backlog_size:                    # <default: 5000; type: integer; is: optional>


RedisChannel
----------------

Publish incoming events to redis channel.

| **channel**:  Name of redis channel to send data to.
| **server**:  Redis server to connect to.
| **port**:  Port redis server is listening on.
| **db**:  Redis db.
| **password**:  Redis password.
| **format**:  Which event fields to send on, e.g. '$(@timestamp) - $(url) - $(country_code)'. If not set, the whole event dict is send.

Configuration template:

::

    - output.RedisChannel:
       channel:                         # <type: string; is: required>
       server:                          # <default: 'localhost'; type: string; is: optional>
       port:                            # <default: 6379; type: integer; is: optional>
       db:                              # <default: 0; type: integer; is: optional>
       password:                        # <default: None; type: None||string; is: optional>
       format:                          # <default: None; type: None||string; is: optional>


RedisList
-------------

Send events to a redis lists.

| **list**:  Name of redis list to send data to.
| **server**:  Redis server to connect to.
| **port**:  Port redis server is listening on.
| **db**:  Redis db.
| **password**:  Redis password.
| **format**:  Which event fields to send on, e.g. '$(@timestamp) - $(url) - $(country_code)'. If not set the whole event dict is send.
| **store_interval_in_secs**:  Send data to redis in x seconds intervals.
| **batch_size**:  Send data to redis if event count is above, even if store_interval_in_secs is not reached.
| **backlog_size**:  Maximum count of events waiting for transmission. Events above count will be dropped.

Configuration template:

::

    - output.RedisList:
       list:                            # <type: String; is: required>
       server:                          # <default: 'localhost'; type: string; is: optional>
       port:                            # <default: 6379; type: integer; is: optional>
       db:                              # <default: 0; type: integer; is: optional>
       password:                        # <default: None; type: None||string; is: optional>
       format:                          # <default: None; type: None||string; is: optional>
       store_interval_in_secs:          # <default: 5; type: integer; is: optional>
       batch_size:                      # <default: 500; type: integer; is: optional>
       backlog_size:                    # <default: 500; type: integer; is: optional>


SQS
-------

Send messages to amazon sqs service.

| **aws_access_key_id**:  Your AWS id.
| **aws_secret_access_key**:  Your AWS password.
| **region**:  The region in which to find your sqs service.
| **queue**:  Queue name.
| **format**:  Which event fields to send on, e.g. '$(@timestamp) - $(url) - $(country_code)'.
| If not set event.data will be send es MessageBody, all other fields will be send as MessageAttributes.
| **store_interval_in_secs**:  Send data to redis in x seconds intervals.
| batch_size: Number of messages to collect before starting to send messages to sqs. This refers to the internal
| receive buffer of this plugin. When the receive buffer is maxed out, this plugin will always send
| the maximum of 10 messages in one send_message_batch call.
| **backlog_size**:  Maximum count of events waiting for transmission. Events above count will be dropped.

values: ['us-east-1', 'us-west-1', 'us-west-2', 'eu-central-1', 'eu-west-1', 'ap-southeast-1', 'ap-southeast-2', 'ap-northeast-1', 'sa-east-1', 'us-gov-west-1', 'cn-north-1']

Configuration template:

::

    - output.SQS:
       aws_access_key_id:               # <type: string; is: required>
       aws_secret_access_key:           # <type: string; is: required>
       region:                          # <type: string; is: required>
       queue:                           # <type: string; is: required>
       format:                          # <default: None; type: None||string; is: optional>
       store_interval_in_secs:          # <default: 5; type: integer; is: optional>
       batch_size:                      # <default: 500; type: integer; is: optional>
       backlog_size:                    # <default: 500; type: integer; is: optional>
       receivers:
        - NextModule


StdOut
----------

Print the data dictionary to stdout.

| **pretty_print**:  Use pythons pprint function.
| **fields**: Set event fields to include in pretty print output.
| **format**:  Format of messages to send to graphite, e.g.: ['lumbermill.stats.event_rate_$(interval)s $(event_rate)'].

Configuration template:

::

    - output.StdOut:
       pretty_print:                    # <default: True; type: boolean; is: optional>
       fields:                          # <default: None; type: None||list; is: optional>
       format:                          # <default: None; type: None||string; is: optional>


Syslog
----------

Send events to syslog.

| **format**:  Which event fields to send on, e.g. '$(@timestamp) - $(url) - $(country_code)'. If not set the whole event dict is send.
| **address**:  Either a server:port pattern or a filepath to a unix socket, e.g. /dev/log.
| **proto**:  Protocol to use.
| facility: Syslog facility to use. List of possible values, @see: http://epydoc.sourceforge.net/stdlib/logging.handlers.SysLogHandler-class.html#facility_names

Configuration template:

::

    - output.Syslog:
       format:                          # <type: string; is: required>
       address:                         # <default: 'localhost:514'; type: string; is: required>
       proto:                           # <default: 'tcp'; type: string; values: ['tcp', 'udp']; is: optional>
       facility:                        # <default: 'user'; type: string; is: optional>

Udp
-----------

Send events to udp socket.

| **address**: address:port
| **format**: Which event fields to send on, e.g. '$(@timestamp) - $(url) - $(country_code)'. If not set the whole event dict is send.
| **store_interval_in_secs**: Send data to redis in x seconds intervals.
| **batch_size**: Send data to redis if event count is above, even if store_interval_in_secs is not reached.
| **backlog_size**: Maximum count of events waiting for transmission. Events above count will be dropped.

Configuration template:

::

    - output.Udp:
       address:                         # <default: 'localhost:514'; type: string; is: required>
       format:                          # <default: None; type: None||string; is: optional>
       store_interval_in_secs:          # <default: 5; type: integer; is: optional>
       batch_size:                      # <default: 500; type: integer; is: optional>
       backlog_size:                    # <default: 500; type: integer; is: optional>

WebHdfs
-----------

Store events in hdfs via webhdfs.

server: webhdfs/https node
| **user**:  Username for webhdfs.
| **path**:  Path to logfiles. String my contain any of pythons strtime directives.
| **name_pattern**:  Filename pattern. String my conatain pythons strtime directives and event fields.
| **format**:  Which event fields to send on, e.g. '$(@timestamp) - $(url) - $(country_code)'. If not set the whole event dict is send.
| **store_interval_in_secs**:  Send data to webhdfs in x seconds intervals.
| **batch_size**:  Send data to webhdfs if event count is above, even if store_interval_in_secs is not reached.
| **backlog_size**:  Maximum count of events waiting for transmission. Events above count will be dropped.
| **compress**:  Compress output as gzip file. For this to be effective, the chunk size should not be too small.

Configuration template:

::

    - output.WebHdfs:
       server:                          # <default: 'localhost:14000'; type: string; is: optional>
       user:                            # <type: string; is: required>
       path:                            # <type: string; is: required>
       name_pattern:                    # <type: string; is: required>
       format:                          # <type: string; is: required>
       store_interval_in_secs:          # <default: 10; type: integer; is: optional>
       batch_size:                      # <default: 1000; type: integer; is: optional>
       backlog_size:                    # <default: 5000; type: integer; is: optional>
       compress:                        # <default: None; type: None||string; values: [None,'gzip','snappy']; is: optional>


Zabbix
----------

Send events to zabbix.

hostname: Hostname for which the metrics should be stored.
fields: Event fields to send.
field_prefix: Prefix to prepend to field names. For e.g. cpu_count field with default lumbermill_ prefix, the Zabbix key is lumbermill_cpu_count.
timestamp_field: Field to provide timestamp. If not provided, current timestamp is used.
agent_conf: Path to zabbix_agent configuration file. If set to True defaults to /etc/zabbix/zabbix_agentd.conf.
server: Address of zabbix server. If port differs from default it can be set by appending it, e.g. 127.0.0.1:10052.
store_interval_in_secs: sending data to es in x seconds intervals.
batch_size: sending data to es if event count is above, even if store_interval_in_secs is not reached.
backlog_size: maximum count of events waiting for transmission. Events above count will be dropped.

Configuration template:

::

    - output.Zabbix:
       hostname:                        # <type: string; is: required>
       fields:                          # <type: list; is: required>
       field_prefix:                    # <default: "lumbermill_"; type: string; is: optional>
       timestamp_field:                 # <default: "timestamp"; type: string; is: optional>
       agent_conf:                      # <default: True; type: boolean||string; is: optional>
       server:                          # <default: False; type: boolean||string; is: required if agent_conf is False else optional>
       store_interval_in_secs:          # <default: 10; type: integer; is: optional>
       batch_size:                      # <default: 500; type: integer; is: optional>
       backlog_size:                    # <default: 500; type: integer; is: optional>


Zmq
-------

Sends events to zeromq.

| **server**:  Server to connect to. Pattern: hostname:port.
| **pattern**:  Either push or pub.
| **mode**:  Whether to run a server or client. If running as server, pool size is restricted to a single process.
| **topic**:  The channels topic.
| **hwm**:  Highwatermark for sending socket.
| **format**:  Which event fields to send on, e.g. '$(@timestamp) - $(url) - $(country_code)'. If not set the whole event dict is send msgpacked.
| **store_interval_in_secs**:  Send data to redis in x seconds intervals.
| **batch_size**:  Send data to redis if event count is above, even if store_interval_in_secs is not reached.
| **backlog_size**:  Maximum count of events waiting for transmission. Events above count will be dropped.

Configuration template:

::

    - output.Zmq:
       server:                          # <default: 'localhost:5570'; type: string; is: optional>
       pattern:                         # <default: 'push'; type: string; values: ['push', 'pub']; is: optional>
       mode:                            # <default: 'connect'; type: string; values: ['connect', 'bind']; is: optional>
       topic:                           # <default: None; type: None||string; is: optional>
       hwm:                             # <default: None; type: None||integer; is: optional>
       format:                          # <default: None; type: None||string; is: optional>
       store_interval_in_secs:          # <default: 5; type: integer; is: optional>
       batch_size:                      # <default: 500; type: integer; is: optional>
       backlog_size:                    # <default: 500; type: integer; is: optional>