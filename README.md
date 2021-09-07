## Connect Mqtt

Connect MQTT

Subscribe messages. This command will start the listener process.

```shell
EVENTS_HOST=172.17.0.1 bench --site mysite.localhost subscribe-mqtt
```

Publish messages. This command will publish message and disconnect.

```shell
EVENTS_HOST=172.17.0.1 bench --site mysite.localhost publish-mqtt
```

Note: replace `mysite.localhost` with site name.

#### License

MIT
