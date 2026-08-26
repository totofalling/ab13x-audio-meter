from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from . import DOMAIN, API

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator, session = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        MuteSwitch(coordinator, session, "input", "Input Mute"),
        MuteSwitch(coordinator, session, "output", "Output Mute"),
    ])

class MuteSwitch(CoordinatorEntity, SwitchEntity):
    def __init__(self, coordinator, session, target, name):
        super().__init__(coordinator)
        self.session = session
        self.target = target
        self._attr_name = name
        self._attr_unique_id = f"ab13x_{target}_mute"
    @property
    def is_on(self):
        return bool(self.coordinator.data.get(f"{self.target}_mute", False))
    async def _set(self, value):
        async with self.session.post(f"{API}/control", json={"target": self.target, "mute": value}, timeout=2) as r:
            if r.status != 200:
                raise ValueError(await r.text())
        await self.coordinator.async_request_refresh()
    async def async_turn_on(self, **kwargs):
        await self._set(True)
    async def async_turn_off(self, **kwargs):
        await self._set(False)
