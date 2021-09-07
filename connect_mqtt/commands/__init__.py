import click
import frappe
import asyncio
import os
import signal
import time

from gmqtt import Client as MQTTClient

STOP = asyncio.Event()


def on_connect(client, flags, rc, properties):
	print('Connected')
	client.subscribe('$share/frappe/MessageEmitted', qos=0)


def on_message(client, topic, payload, qos, properties):
	print('RECV MSG:', payload)


def on_disconnect(client, packet, exc=None):
	print('Disconnected')


def on_subscribe(client, mid, qos, properties):
	print('SUBSCRIBED')


def ask_exit(*args):
	STOP.set()


async def subscribe_client():
	client = MQTTClient(frappe.generate_hash())
	client.on_connect = on_connect
	client.on_message = on_message
	client.on_disconnect = on_disconnect
	client.on_subscribe = on_subscribe
	host = os.environ.get('EVENTS_HOST', 'localhost')
	port = int(os.environ.get('EVENTS_PORT', '1883'))
	token = os.environ.get('TOKEN', 'fake token')
	client.set_auth_credentials(token, None)
	await client.connect(host, port)
	await STOP.wait()


async def publish_client():
	client = MQTTClient(frappe.generate_hash())
	host = os.environ.get('EVENTS_HOST', 'localhost')
	port = int(os.environ.get('EVENTS_PORT', '1883'))
	token = os.environ.get('TOKEN', 'fake token')
	client.set_auth_credentials(token, None)
	await client.connect(host, port)
	client.publish('MessageEmitted', str(time.time()), qos=1, retain=True, message_expiry_interval=60, content_type='json')


@click.command('subscribe-mqtt')
def subscribe_mqtt():
	loop = asyncio.get_event_loop()
	loop.add_signal_handler(signal.SIGINT, ask_exit)
	loop.add_signal_handler(signal.SIGTERM, ask_exit)
	loop.run_until_complete(subscribe_client())


@click.command('publish-mqtt')
def publish_mqtt():
	loop = asyncio.get_event_loop()
	loop.add_signal_handler(signal.SIGINT, ask_exit)
	loop.add_signal_handler(signal.SIGTERM, ask_exit)
	loop.run_until_complete(publish_client())


commands = [
	subscribe_mqtt,
	publish_mqtt,
]
