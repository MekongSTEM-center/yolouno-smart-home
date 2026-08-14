# MQTT protocol for Yolo UNO Smart Home

The dashboard uses the canonical OhStem topic root:

```text
luong873004/feeds/<channel>
```

The MicroPython OhStem MQTT adapter receives the short channel name (`V1`,
`V2`, ...). The firmware now logs both forms so the actual broker topic can be
verified with MQTT Explorer.

| Channel | Meaning | Dashboard publishes | Firmware publishes | Payload |
| --- | --- | --- | --- | --- |
| V1 | Main light | Yes | Yes | `1` / `0` |
| V2 | RGB color | Yes | No | `#rrggbb` |
| V3 | RGB state | Yes | Yes | `1` / `0` |
| V4 | Temperature | No | Yes | Number |
| V5 | Humidity | No | Yes | Number |
| V6 | Light sensor | No | Yes | Percentage |
| V7 | Gas sensor | No | Yes | ppm |
| V8 | Motion | No | Yes | `DETECTED` |
| V9 | Fan state | Yes | Yes | `1` / `0` |
| V10 | Fan speed | Yes | Yes | `0`–`100` |
| V12 | Automatic light by sensor | Yes | Yes | `1` / `0` |
| V13 | Automatic light by motion | Yes | Yes | `1` / `0` |
| V14 | Main door | Yes | Yes | `1` / `0` |
| V15 | RFID mode | Yes | Yes | `1` / `0` |
| V16 | Buzzer | Yes | Yes | `1` / `0` |
| V20 | Device presence | No | Yes | `ONLINE` / `OFFLINE` |

## Verification checklist

1. Subscribe to `luong873004/feeds/#` in MQTT Explorer.
2. Open the dashboard Console and keep the `MQTT publish`, `MQTT receive`, and
   acknowledgement messages visible.
3. Toggle each control and compare topic, payload, firmware `MQTT RX` log, and
   physical output.
4. Confirm that reconnect publishes `V20=ONLINE` and a lost connection results
   in `V20=OFFLINE`.
5. Repeat after refreshing the dashboard and after clearing its saved MQTT
   configuration.

The firmware callback log has this form:

```text
MQTT RX channel= 'V1' wire= 'luong873004/feeds/V1' payload= '1' payload_type= str
```

If the dashboard publishes a full topic but this log never appears, compare
the adapter's topic expansion with the broker capture before changing GPIO or
device code.
