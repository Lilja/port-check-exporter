# Port check tool

Env: 
 - CONF_PATH. a place to read `config.toml`
 - FREQUENCY. How often to check ports. defaults to 12 hours.

```toml
# config.toml
[servers]
    [servers.test-server]
    domain = "google.com"
    port = 443
```


```yml
# Prometheus config

scrape_configs

  - job_name: port-check-exporter
    scrape_interval: 12h
    static_configs:
      - targets: ['localhost']

```
