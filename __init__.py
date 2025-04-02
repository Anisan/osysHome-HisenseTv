import socket
import re
import datetime
import json
import paho.mqtt.client as mqtt
from flask import redirect
from sqlalchemy import delete
from app.database import session_scope
from app.core.main.BasePlugin import BasePlugin
from app.core.lib.object import updateProperty, removeLinkFromObject
from app.core.lib.common import addNotify, CategoryNotify
from plugins.HisenseTv.models.Device import HisenseDevice
from plugins.HisenseTv.models.Data import HisenseData
from plugins.HisenseTv.forms.DeviceForm import routeDevice
from plugins.HisenseTv.forms.DataForm import routeData

class HisenseTv(BasePlugin):

    def __init__(self, app):
        super().__init__(app, __name__)
        self.title = "HisenseTv"
        self.author = "Eraser"
        self.version = "0.2"
        self.description = """Control for Hisense TV"""
        self.category = "Devices"
        self.actions = ["cycle"]
        self._clients = {}
        self.cache_devices = {}

    def initialization(self):
        with session_scope() as session:
            devices = session.query(HisenseDevice).all()
            for device in devices:
                client = self.createClient("osysHome_dev" + str(device.id))
                if client:
                    self._clients[device.ip] = client

    def admin(self, request):
        device_id = request.args.get("device", None)
        data_id = request.args.get("data", None)
        op = request.args.get("op", None)
        if op == "delete":
            with session_scope() as session:
                if device_id:
                    data = session.query(HisenseData).where(HisenseData.device_id == device_id).all()
                    for item in data:
                        if item.linked_object:
                            removeLinkFromObject(
                                item.linked_object, item.linked_property, self.name
                            )
                    sql = delete(HisenseData).where(HisenseData.device_id == device_id)
                    session.execute(sql)
                    sql = delete(HisenseDevice).where(HisenseDevice.id == device_id)
                    session.execute(sql)
                    session.commit()
                elif data_id:
                    item = session.query(HisenseData).where(HisenseData.id == data_id).one_or_none
                    if item and item.linked_object:
                        removeLinkFromObject(
                            item.linked_object, item.linked_property, self.name
                        )
                    sql = delete(HisenseData).where(HisenseData.id == data_id)
                    session.execute(sql)
                    session.commit()
            return redirect(self.name)
        if op == "add" or op == "edit":
            return routeDevice(request)
        if op == "edit_link":
            return routeData(request)

        devices = HisenseDevice.query.all()
        return self.render("hisense_devices.html", {"devices": devices})

    def cyclic_task(self):
        if self.event.is_set():
            # Останавливаем цикл обработки сообщений
            for _, client in self._clients.items():
                client.loop_stop()
                # Отключаемся от брокера MQTT
                client.disconnect()
        else:
            for ip, client in self._clients.items():
                if not client.is_connected():
                    self.connectClient(client, ip)
            self.event.wait(1.0)

    def mqttPublish(self, host, topic, value, qos=0, retain=False):
        self.logger.info("Publish to %s: %s %s", host, topic, value)
        if host in self._clients:
            client = self._clients[host]
            client.publish(topic, str(value), qos=qos, retain=retain)

    def changeLinkedProperty(self, obj, prop, val):
        self.logger.debug("changeLinkedProperty: %s.%s=%s", obj, prop, val)
        with session_scope() as session:
            data = (
                session.query(HisenseData)
                .where(HisenseData.linked_object == obj, HisenseData.linked_property == prop)
                .all()
            )
            for item in data:
                if item.value != val:
                    device = (
                        session.query(HisenseDevice)
                        .where(HisenseDevice.id == item.device_id)
                        .one_or_none()
                    )
                    name = "osysHome_dev" + str(device.id)
                    if item.title == "state":
                        if val == 1:
                            self.wake_on_lan("192.168.0.255", device.mac)
                        else:
                            self.mqttPublish(
                                device.ip,
                                f"/remoteapp/tv/remote_service/{name}/actions/sendkey",
                                "KEY_POWER",
                            )
                    elif item.title == "channel_num":
                        ch = str(val)
                        a = list(ch)
                        for v in a:
                            if v == "0":
                                self.mqttPublish(
                                    device.ip,
                                    f"/remoteapp/tv/remote_service/{name}/actions/sendkey",
                                    "KEY_0",
                                )
                            elif v == "1":
                                self.mqttPublish(
                                    device.ip,
                                    f"/remoteapp/tv/remote_service/{name}/actions/sendkey",
                                    "KEY_1",
                                )
                            elif v == "2":
                                self.mqttPublish(
                                    device.ip,
                                    f"/remoteapp/tv/remote_service/{name}/actions/sendkey",
                                    "KEY_2",
                                )
                            elif v == "3":
                                self.mqttPublish(
                                    device.ip,
                                    f"/remoteapp/tv/remote_service/{name}/actions/sendkey",
                                    "KEY_3",
                                )
                            elif v == "4":
                                self.mqttPublish(
                                    device.ip,
                                    f"/remoteapp/tv/remote_service/{name}/actions/sendkey",
                                    "KEY_4",
                                )
                            elif v == "5":
                                self.mqttPublish(
                                    device.ip,
                                    f"/remoteapp/tv/remote_service/{name}/actions/sendkey",
                                    "KEY_5",
                                )
                            elif v == "6":
                                self.mqttPublish(
                                    device.ip,
                                    f"/remoteapp/tv/remote_service/{name}/actions/sendkey",
                                    "KEY_6",
                                )
                            elif v == "7":
                                self.mqttPublish(
                                    device.ip,
                                    f"/remoteapp/tv/remote_service/{name}/actions/sendkey",
                                    "KEY_7",
                                )
                            elif v == "8":
                                self.mqttPublish(
                                    device.ip,
                                    f"/remoteapp/tv/remote_service/{name}/actions/sendkey",
                                    "KEY_8",
                                )
                            elif v == "9":
                                self.mqttPublish(
                                    device.ip,
                                    f"/remoteapp/tv/remote_service/{name}/actions/sendkey",
                                    "KEY_9",
                                )
                        self.mqttPublish(
                            device.ip,
                            f"/remoteapp/tv/remote_service/{name}/actions/sendkey",
                            "KEY_OK",
                        )
                    elif item.title == "volume_value":
                        self.mqttPublish(
                            device.ip,
                            f"/remoteapp/tv/platform_service/{name}/actions/changevolume",
                            val,
                        )
                    elif item.title == "source":
                        # todo set source
                        pass

    def createClient(self, client_id):
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id=client_id)
        # Назначаем функции обратного вызова
        client.on_connect = self.on_connect
        client.on_disconnect = self.on_disconnect
        client.on_message = self.on_message
        return client

    def connectClient(self, client, host):
        username = "hisenseservice"
        password = "multimqttservice"
        port = 36669
        # Подключаемся к брокеру MQTT
        try:
            client.username_pw_set(username, password)
            client.connect(host, port, 0)
            client.loop_start()
        except Exception:
            data = {}
            data["state"] = 0
            self.updateData(host, data)

    # Функция обратного вызова для подключения к брокеру MQTT
    def on_connect(self, client, userdata, flags, rc):
        self.logger.info("Connected with result code %s", rc)
        # Подписываемся на топик
        client.subscribe("#")
        host = client.host
        self.updateData(host, {"state": 1})

    def on_disconnect(self, client, userdata, rc):
        host = client.host
        self.updateData(host, {"state": 0})
        addNotify("Disconnect MQTT", str(rc), CategoryNotify.Error, self.name)
        if rc == 0:
            self.logger.info("Disconnected gracefully.")
        elif rc == 1:
            self.logger.info("Client requested disconnection.")
        elif rc == 2:
            self.logger.info("Broker disconnected the client unexpectedly.")
        elif rc == 3:
            self.logger.info("Client exceeded timeout for inactivity.")
        elif rc == 4:
            self.logger.info("Broker closed the connection.")
        else:
            self.logger.warning("Unexpected disconnection with code: %s", rc)

    def updateData(self, host, data):
        with session_scope() as session:
            device = session.query(HisenseDevice).where(HisenseDevice.ip == host).one()
            values = session.query(HisenseData).where(HisenseData.device_id == device.id).all()
            for key, value in data.items():
                self.logger.debug("%s-%s", key, value)
                is_set = False
                for val in values:
                    if val.title == key:
                        if val.value != value:
                            val.value = value
                            if val.linked_object:
                                if val.linked_property:
                                    updateProperty(
                                        val.linked_object + "." + val.linked_property,
                                        value,
                                        self.name,
                                    )
                        val.updated = datetime.datetime.now()
                        is_set = True
                if not is_set:
                    data = HisenseData()
                    data.device_id = device.id
                    data.title = key
                    data.value = value
                    data.updated = datetime.datetime.now()
                    session.add(data)
            session.commit()

    # Функция обратного вызова для получения сообщений
    def on_message(self, client, userdata, msg):
        payload = msg.payload.decode("utf-8")
        self.logger.info("%s %s", msg.topic, payload)

        if "/set" in msg.topic:
            return

        host = client.host

        self.processMessage(host, msg.topic, payload)

    def processMessage(self, host, path, value):
        payload = {}

        if path == "/remoteapp/mobile/broadcast/ui_service/state":
            tmp = json.loads(value)
            if tmp["statetype"] == "livetv":
                payload["channel_num"] = tmp["channel_num"]
                payload["channel_name"] = tmp["channel_name"]
                payload["progname"] = tmp["progname"]
                payload["detail"] = tmp["detail"]
                payload["starttime"] = tmp["starttime"]
                payload["endtime"] = tmp["endtime"]
                payload["source"] = "tv"
            elif tmp["statetype"] == "app":
                payload["app_name"] = tmp["name"]
                payload["url"] = tmp["url"]
                payload["source"] = tmp["name"]
            elif tmp["statetype"] == "mediadmp":
                payload["media_name"] = tmp["name"]
                payload["mediatype"] = tmp["mediatype"]
                payload["playstate"] = tmp["playstate"]
                payload["starttime"] = tmp["starttime"]
                payload["curtime"] = tmp["curtime"]
                payload["totaltime"] = tmp["totaltime"]
                payload["source"] = "media"
            elif tmp["statetype"] == "sourceswitch":
                payload["source_name"] = tmp["displayname"]
                payload["sourceid"] = tmp["sourceid"]
                payload["source"] = tmp["sourcename"].lower()
            payload["statetype"] = tmp["statetype"]
            payload["state"] = 1

            self.updateData(host, payload)
        elif (
            path == "/remoteapp/mobile/broadcast/platform_service/actions/volumechange"
        ):
            tmp = json.loads(value)
            payload["volume_value"] = tmp["volume_value"]
            self.updateData(host, payload)
        elif path == "/remoteapp/mobile/broadcast/platform_service/actions/tvsleep":
            payload["state"] = 0
            self.updateData(host, payload)
        elif path == "/remoteapp/tv/ui_service/Majordomo/actions/changesource":
            tmp = json.loads(value)
            payload["sourceid"] = tmp["sourceid"]
            payload["source"] = tmp["sourcename"].lower()
            self.updateData(host, payload)

    def wake_on_lan(self, broadcast, mac):
        # Example usage
        # wake_on_lan('192.168.1.255', '00:11:22:33:44:55')
        self.logger.info(f"Wake on lan - {broadcast} {mac}")
        # Remove any non-hexadecimal characters from MAC address
        hwaddr = bytes.fromhex(re.sub(r"[^0-9a-fA-F]", "", mac))
        # Create Magic Packet
        packet = b"\xff" * 6 + hwaddr * 16
        # Create UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # Set socket option to broadcast
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            # Send the Magic Packet to the broadcast address on port 7
            sock.sendto(packet, (broadcast, 7))
        finally:
            # Close the socket
            sock.close()
