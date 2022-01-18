"""Platform for Rademacher Bridge"""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_DEVICES
from .homepilot.device import HomePilotDevice
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .homepilot.sensor import HomePilotSensor
from .homepilot.hub import HomePilotHub
from .entity import HomePilotEntity
from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry: ConfigEntry, async_add_entities):
    entry = hass.data[DOMAIN][config_entry.entry_id]
    hub: HomePilotHub = entry[0]
    coordinator: DataUpdateCoordinator = entry[1]
    devices: dict = (
        entry[2][CONF_DEVICES] if CONF_DEVICES in entry[2] else list(hub.devices)
    )
    new_entities = []
    for did in hub.devices:
        if did in devices:
            device: HomePilotDevice = hub.devices[did]
            if isinstance(device, HomePilotSensor):
                if device.has_rain_detection:
                    _LOGGER.info(
                        "Found Rain Detection Sensor for Device ID: %s", device.did
                    )
                    new_entities.append(
                        HomePilotBinarySensorEntity(
                            coordinator,
                            device,
                            "rain_detect",
                            "Rain Detection",
                            "rain_detection_value",
                            BinarySensorDeviceClass.MOISTURE,
                            None,
                            None,
                        )
                    )
                if device.has_sun_detection:
                    _LOGGER.info(
                        "Found Sun Detection Sensor for Device ID: %s", device.did
                    )
                    new_entities.append(
                        HomePilotBinarySensorEntity(
                            coordinator,
                            device,
                            "sun_detect",
                            "Sun Detection",
                            "sun_detection_value",
                            BinarySensorDeviceClass.LIGHT,
                            None,
                            None,
                        )
                    )
                if device.has_contact_state:
                    _LOGGER.info("Found Contact Sensor for Device ID: %s", device.did)
                    new_entities.append(
                        HomePilotBinarySensorEntity(
                            coordinator,
                            device,
                            "contact_state",
                            "Contact State",
                            "contact_state_value",
                            BinarySensorDeviceClass.OPENING,
                            None,
                            None,
                        )
                    )
    # If we have any new devices, add them
    if new_entities:
        async_add_entities(new_entities)


class HomePilotBinarySensorEntity(HomePilotEntity, BinarySensorEntity):
    def __init__(
        self,
        hub,
        device: HomePilotSensor,
        id_suffix,
        name_suffix,
        value_attr,
        device_class,
        icon_on,
        icon_off,
    ):
        super().__init__(
            hub,
            device,
            unique_id=f"{device.uid}_f{id_suffix}",
            name=f"{device.name} {name_suffix}",
            device_class=device_class,
        )
        self._value_attr = value_attr
        self._icon_on = icon_on
        self._icon_off = icon_off

    @property
    def value_attr(self):
        return self._value_attr

    @property
    def is_on(self):
        value = getattr(self.coordinator.data[self.did], self.value_attr)
        return value if isinstance(value, bool) else value.value

    @property
    def icon(self):
        return self._icon_on if self.is_on else self._icon_off