from homeassistant.components.number import NumberEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from . import DOMAIN, API
import aiohttp

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator, session = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        VolumeNumber(coordinator, session, "input", "Input Volume"),
        VolumeNumber(coordinator, session, "output", "Output Volume"),
    ])

class VolumeNumber(CoordinatorEntity, NumberEntity):
    _attr_native_min_value = 0
    _attr_native_max_value = 100
    _attr_native_step = 1
    def __init__(self, coordinator, session, target, name):
        super().__init__(coordinator)
        self.session = session
        self.target = target
        self._attr_name = name
        self._attr_unique_id = f"ab13x_{target}_volume"
        self._attr_native_unit_of_measurement = "%"
    @property
    def native_value(self):
        return self.coordinator.data.get(f"{self.target}_volume", 0)
    async def async_set_native_value(self, value):
        async with self.session.post(f"{API}/control", json={"target": self.target, "volume": value}, timeout=2) as r:
            if r.status != 200:
                raise ValueError(await r.text())
        await self.coordinator.async_request_refresh()
