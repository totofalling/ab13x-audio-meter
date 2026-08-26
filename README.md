# AB13X Audio Meter for Home Assistant

Real-time PulseAudio input/output monitoring and volume control for the Generic AB13X USB Audio device.

## Features

- Live Input RMS and Peak meter
- Live Output RMS and Peak meter
- Input volume 0-100%
- Output volume 0-100%
- Input mute/unmute
- Output mute/unmute
- Lovelace dashboard card
- No MQTT required
- Does not modify linux_voice_assistant

## Installation

Add this repository to Home Assistant Apps/Add-ons:

https://github.com/totofalling/ab13x-audio-meter

Install the AB13X Audio Meter app and start it.

Then install the custom integration from the custom_components directory.

Add the Lovelace resource:

/local/ab13x-audio-meter.js

Resource type: JavaScript Module

## Lovelace Card

```yaml
type: custom:ab13x-audio-meter
input_rms: sensor.input_rms
input_peak: sensor.input_peak
output_rms: sensor.output_rms
output_peak: sensor.output_peak
input_volume: number.input_volume
output_volume: number.output_volume
input_mute: switch.input_mute
output_mute: switch.output_mute
```

## License

MIT License
