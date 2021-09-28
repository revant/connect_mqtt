import click
import frappe
import asyncio
import signal
import time

from frappe.commands import pass_context
from gmqtt import Client as MQTTClient

STOP = asyncio.Event()


def on_connect(client, flags, rc, properties):
	print("Connected")
	client.subscribe("$share/frappe/+", qos=0)


def on_message(client, topic, payload, qos, properties):
	print("RECV MSG:", payload)
	print("--- END MESSAGE ---")
	print("")


def on_disconnect(client, packet, exc=None):
	print("Disconnected")


def on_subscribe(client, mid, qos, properties):
	print("SUBSCRIBED")


def ask_exit(*args):
	STOP.set()


async def subscribe_client(context):
	site = None
	try:
		site = context.sites[0]
	except IndexError:
		print("Invalid Site")
		exit(1)

	frappe.init(site=site)
	frappe.connect()

	client = MQTTClient(frappe.generate_hash())
	client.on_connect = on_connect
	client.on_message = on_message
	client.on_disconnect = on_disconnect
	client.on_subscribe = on_subscribe
	host = frappe.get_conf().get("events_host", "localhost")
	port = int(frappe.get_conf().get("events_port", "1883"))
	username = frappe.get_conf().get("events_user", "admin")
	password = frappe.get_conf().get("events_password", "changeit")
	client.set_auth_credentials(username, password)
	await client.connect(host, port)
	await STOP.wait()


async def publish_client(context):
	site = None
	try:
		site = context.sites[0]
	except IndexError:
		print("Invalid Site")
		exit(1)

	frappe.init(site=site)
	frappe.connect()
	client = MQTTClient(frappe.generate_hash())
	host = frappe.get_conf().get("events_host", "localhost")
	port = int(frappe.get_conf().get("events_port", "1883"))
	username = frappe.get_conf().get("events_user", "admin")
	password = frappe.get_conf().get("events_password", "changeit")
	client.set_auth_credentials(username, password)
	await client.connect(host, port)
	client.publish("MessageEmitted", str(time.time()), qos=1, retain=True, message_expiry_interval=60, content_type="json")


@click.command("subscribe-mqtt")
@pass_context
def subscribe_mqtt(context):
	loop = asyncio.get_event_loop()
	loop.add_signal_handler(signal.SIGINT, ask_exit)
	loop.add_signal_handler(signal.SIGTERM, ask_exit)
	loop.run_until_complete(subscribe_client(context))


@click.command("publish-mqtt")
@pass_context
def publish_mqtt(context):
	loop = asyncio.get_event_loop()
	loop.add_signal_handler(signal.SIGINT, ask_exit)
	loop.add_signal_handler(signal.SIGTERM, ask_exit)
	loop.run_until_complete(publish_client(context))


commands = [
	subscribe_mqtt,
	publish_mqtt,
]
