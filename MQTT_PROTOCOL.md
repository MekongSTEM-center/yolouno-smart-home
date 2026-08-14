# MQTT protocol for Yolo UNO Smart Home

The dashboard uses the canonical OhStem topic root:

```text
luong873004/feeds/<channel>
```

The MicroPython OhStem MQTT adapter receives the short channel name (`V1`,
`V2`, ...). The firmware now logs both forms so the actual broker topic can be
verified with MQTT Explorer.

| Channel | Meaning | Direction | Payload | Expected side effect |
| --- | --- | --- | --- | --- |
| V1 | Main light | Dashboard → firmware; firmware → dashboard state | `1` / `0` | One output change |
| V2 | RGB color | Dashboard → firmware | `#rrggbb` | One color update |
| V3 | RGB state | Dashboard → firmware; firmware → dashboard state | `1` / `0` | One output change |
| V4 | Temperature | Firmware → dashboard | Number | No actuator |
| V5 | Humidity | Firmware → dashboard | Number | No actuator |
| V6 | Light sensor | Firmware → dashboard | Percentage | No actuator |
| V7 | Gas sensor | Firmware → dashboard | ppm | May start one gas alarm task |
| V8 | Motion | Firmware → dashboard | `DETECTED` | No duplicate alert event |
| V9 | Fan state | Dashboard → firmware; firmware → dashboard state | `1` / `0` | One output change |
| V10 | Fan speed | Dashboard → firmware | `0`–`100` | One PWM update |
| V12 | Automatic light by sensor | Dashboard → firmware; firmware → dashboard state | `1` / `0` | One mode change |
| V13 | Automatic light by motion | Dashboard → firmware; firmware → dashboard state | `1` / `0` | One mode change |
| V14 | Main door | Dashboard → firmware; firmware → dashboard state | `1` / `0` | One servo action and one beep |
| V15 | RFID mode | Dashboard → firmware; firmware → dashboard state | `1` / `0` | One mode change |
| V16 | Buzzer | Dashboard → firmware | `1` / `0` | One manual output change |
| V20 | Device presence | Firmware → dashboard | `ONLINE` / `OFFLINE` | No actuator |

## Command/state separation

Channels such as V1, V3, V9, V12, V13, V14 and V15 carry both commands and
device state because this is the OhStem dashboard contract. Firmware-originated
state publishes are marked locally and their matching MQTT echo is ignored by
the command callback. A command callback never republishes the same topic.

The buzzer is owned by one firmware manager. Normal startup is silent, door and
RFID events request one-shot beeps, gas owns the repeating alarm pattern, and
V16 controls the manual buzzer state without creating another alarm task.

## Verification checklist

1. Subscribe to `luong873004/feeds/#` in MQTT Explorer.
2. Open the dashboard Console and keep the `MQTT client created`, `MQTT publish`,
   and `MQTT receive` messages visible. Each record includes client ID,
   sequence number, timestamp, topic, and payload.
3. Toggle each control and compare topic, payload, firmware `MQTT RX` log, and
   physical output.
4. Confirm that reconnect publishes `V20=ONLINE` and a lost connection results
   in `V20=OFFLINE`.
5. Repeat after refreshing the dashboard and after clearing its saved MQTT
   configuration.

For V14 and V15, count separately: dashboard command, firmware command callback,
firmware state publish, and ignored local state echo. The local echo must never
cause a second servo action or buzzer event.

The firmware callback log has this form:

```text
MQTT RX channel= 'V1' wire= 'luong873004/feeds/V1' payload= '1' payload_type= str
```

If the dashboard publishes a full topic but this log never appears, compare
the adapter's topic expansion with the broker capture before changing GPIO or
device code.
