from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from . import DOMAIN

SENSORS = [
    ("input_rms", "Input RMS", "dBFS"),
    ("input_peak", "Input Peak", "dBFS"),
    ("output_rms", "Output RMS", "dBFS"),
    ("output_peak", "Output Peak", "dBFS"),
]

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator, _ = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([MeterSensor(coordinator, key, name, unit) for key, name, unit in SENSORS])

class MeterSensor(CoordinatorEntity, SensorEntity):
    _attr_should_poll = False
    def __init__(self, coordinator, key, name, unit):
        super().__init__(coordinator)
        self.key = key
        self._attr_name = name
        self._attr_unique_id = f"ab13x_{key}"
        self._attr_native_unit_of_measurement = unit
    @property
    def native_value(self):
        return self.coordinator.data.get(self.key)
