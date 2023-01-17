"""Support for Melissa Climate A/C."""
from __future__ import annotations

import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Iterate through and add all Melissa devices."""
    api = hass.data[DOMAIN][entry.entry_id]
    devices = (await api.async_fetch_devices()).values()

    all_devices = []

    for device in devices:
        if device["type"] == "melissa":
            all_devices.append(MelissaClimate(api, device))

    async_add_entities(all_devices)


class MelissaClimate(SwitchEntity):
    """Representation of a Melissa Climate device."""

    def __init__(self, api, device):
        """Initialize the climate device."""
        self.device = device
        self._attr_unique_id = f"{device['serial_number']}_led"
        self._attr_entity_id = f"{device['serial_number']}_led"
        self._name = f"{device['name']} LED"
        self._api = api
        self._serial_number = device["serial_number"]
        self._attr_icon = "mdi:led-outline"

    @property
    def name(self):
        """Return the name of the thermostat, if any."""
        return self._name

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.device["serial_number"])},
            name=self.name,
            manufacturer=self.device["device_group"],
            model=self.device["type"],
            sw_version=self.device["controller_log"]["version"],
        )

    async def async_turn_on(self, **kwargs) -> None:
        """Set fan mode."""
        await self._api.async_send(
            self._serial_number, "led", {self._api.COMMAND: self._api.LED_ON}
        )

    async def async_turn_off(self, **kwargs) -> None:
        """Set operation mode."""
        await self._api.async_send(
            self._serial_number, "led", {self._api.COMMAND: self._api.LED_OFF}
        )
