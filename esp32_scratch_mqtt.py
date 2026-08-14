from rfid import *
import math
from MQ2 import *
from ssd1306 import *
from pins import *
from yolo_uno import *
from mqtt_as import MQTTClient, config
from dht20 import *

# --- THÊM THƯ VIỆN CHO HÀM WIFI ---
import network
import time
try:
    import usocket as socket
except ImportError:
    import socket

WIFI_SSID = 'MEKONG STEM 5G'
WIFI_PASSWORD = 'Mekong2025'
INTERNET_TEST_HOST = 'example.com'
INTERNET_TEST_PORT = 80
INTERNET_TEST_TIMEOUT_S = 3
WIFI_CONNECT_TIMEOUT_S = 20
MQTT_WATCHDOG_INTERVAL_MS = 15000

wlan = network.WLAN(network.STA_IF)

# --- HÀM KẾT NỐI WIFI CỦA BẠN ĐÃ ĐƯỢC ĐÓNG GÓI ---
def connect_custom_wifi():
    wlan.active(True)
    if wlan.isconnected():
        print('WiFi already connected. IP:', wlan.ifconfig()[0])
        return True

    print("Connecting...")
    try:
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    except Exception as e:
        print('WiFi connect request failed:', e)
        return False

    for i in range(WIFI_CONNECT_TIMEOUT_S):
        print(i, "status =", wlan.status())
        if wlan.isconnected():
            print("CONNECTED!")
            print("IP:", wlan.ifconfig())
            return True
        time.sleep(1)
    print("Final:", wlan.status())
    print("Config:", wlan.ifconfig())
    return wlan.isconnected()

async def ensure_wifi_connection(force_reconnect=False):
    wlan.active(True)
    if wlan.isconnected() and not force_reconnect:
        return True

    if force_reconnect:
        print('WiFi connected but internet is unavailable. Reconnecting WiFi...')
        try:
            wlan.disconnect()
        except Exception as e:
            print('WiFi disconnect error:', e)
        await asleep_ms(500)

    try:
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    except Exception as e:
        print('WiFi connect request failed:', e)
        return False

    for i in range(WIFI_CONNECT_TIMEOUT_S):
        if wlan.isconnected():
            print('Wifi connected. IP:', wlan.ifconfig()[0])
            return True
        await asleep_ms(1000)

    print('WiFi reconnect timeout. Status:', wlan.status())
    return wlan.isconnected()

def check_internet():
    if not wlan.isconnected():
        print('Checking WiFi integrity: WiFi is disconnected.')
        return False

    print('Checking WiFi integrity.')
    test_socket = None
    try:
        test_socket = socket.socket()
        test_socket.settimeout(INTERNET_TEST_TIMEOUT_S)
        address = socket.getaddrinfo(INTERNET_TEST_HOST, INTERNET_TEST_PORT)[0][-1]
        test_socket.connect(address)
        print('Internet available.')
        return True
    except Exception as e:
        print('Internet check failed:', e)
        return False
    finally:
        if test_socket is not None:
            try:
                test_socket.close()
            except Exception:
                pass
# --------------------------------------------------

async def Hi_E1_BB_87u_ch_E1_BB_89nh_c_E1_BA_A3m_bi_E1_BA_BFn_gas():
    global card_ok, khi_gas, pir_motion_active, last_fan_state, Nhi_E1_BB_87t__C4_91_E1_BB_99, speed, light, AUTO_LIGHT, buzzer_when_detect, C_E1_BB_ADa, RFID, last_LED_state, color, gas_alarm_active, _C4_90_E1_BB_99__E1_BA_A9m, _C3_81nh_s_C3_A1ng
    oled.fill(0); oled.show()
    oled.text(str('Hieu chinh'), 1-1, 1-1, 1); oled.show()
    oled.text(str('cam bien...'), 1-1, 10-1, 1); oled.show()
    await mq_A2.calibrate(-1)
    mq_A2.mode(MQ2.STRATEGY_FAST)
    khi_gas = await mq_A2.readLPG()
    neopix.show(0, hex_to_rgb('#800080'))
    oled.fill(0); oled.show()
    oled.text(str('Xong'), 1-1, 10-1, 1); oled.show()
    await asleep_ms(1000)
    oled.fill(0); oled.show()

async def on_mqtt_msg_f_k_q_l(topic, msg):
    global khi_gas, RFID, Nhi_E1_BB_87t__C4_91_E1_BB_99, last_fan_state, speed, light, AUTO_LIGHT, auto_light_when_detect, C_E1_BB_ADa, last_LED_state, color, _C4_90_E1_BB_99__E1_BA_A9m, _C3_81nh_s_C3_A1ng
    msg = log_mqtt_message(topic, msg)
    if consume_local_state_echo(topic, msg):
        return
    last_LED_state = msg
    if msg == '1':
        rgb_led_D9.show(0, hex_to_rgb(color))
    else:
        rgb_led_D9.show(0, hex_to_rgb('#000000'))

async def on_mqtt_msg_J_V_x_E(topic, msg):
    global khi_gas, RFID, Nhi_E1_BB_87t__C4_91_E1_BB_99, last_fan_state, speed, light, AUTO_LIGHT, auto_light_when_detect, C_E1_BB_ADa, last_LED_state, color, _C4_90_E1_BB_99__E1_BA_A9m, _C3_81nh_s_C3_A1ng
    msg = log_mqtt_message(topic, msg)
    color = msg
    if last_LED_state == '1':
        rgb_led_D9.show(0, hex_to_rgb(color))

cfg = config.copy()
cfg['topics'] = list(cfg.get('topics', []))
MQTT_USER = 'luong873004'
# The OhStem MQTT adapter accepts channel names (V1...V20) and maps them to
# MQTT_USER + '/feeds/' + channel on the broker. Keep the short channel names
# below for the adapter, while logging the canonical wire topic explicitly.
MQTT_TOPIC_ROOT = MQTT_USER + '/feeds'
TOPIC_LIGHT_STATE = 'V1'
TOPIC_RGB_COLOR = 'V2'
TOPIC_RGB_STATE = 'V3'
TOPIC_TEMPERATURE = 'V4'
TOPIC_HUMIDITY = 'V5'
TOPIC_LIGHT_SENSOR = 'V6'
TOPIC_GAS = 'V7'
TOPIC_MOTION = 'V8'
TOPIC_FAN_STATE = 'V9'
TOPIC_FAN_SPEED = 'V10'
TOPIC_AUTO_LIGHT = 'V12'
TOPIC_MOTION_LIGHT = 'V13'
TOPIC_MAIN_DOOR = 'V14'
TOPIC_RFID_DOOR = 'V15'
TOPIC_BUZZER = 'V16'
TOPIC_DEVICE = 'V20'
RFID_SCAN_INTERVAL_MS = 75
RFID_ERROR_RETRY_MS = 500
RFID_OPEN_HOLD_MS = 4000
RFID_BEEP_MS = 100
GAS_READ_INTERVAL_MS = 1000
LOCAL_STATE_ECHO_WINDOW_MS = 1500
DOOR_COMMAND_DEDUP_WINDOW_MS = 500
BUZZER_EVENT_DEDUP_WINDOW_MS = 500

MQTT_COMMAND_CHANNELS = (
    'V1', 'V3', 'V9', 'V10', 'V12', 'V13', 'V14', 'V15', 'V16'
)

def mqtt_text(value):
    """Normalize mqtt_as values for comparisons and hardware callbacks."""
    if isinstance(value, bytes):
        try:
            value = value.decode('utf-8')
        except Exception:
            value = str(value)
    return str(value).strip()

def mqtt_wire_topic(channel):
    channel_text = mqtt_text(channel)
    if channel_text == MQTT_TOPIC_ROOT or channel_text.startswith(MQTT_TOPIC_ROOT + '/'):
        return channel_text
    return MQTT_TOPIC_ROOT + '/' + channel_text

def mqtt_channel(topic):
    topic_text = mqtt_text(topic)
    prefix = MQTT_TOPIC_ROOT + '/'
    if topic_text.startswith(prefix):
        return topic_text[len(prefix):]
    return topic_text

local_state_echoes = {}

def remember_local_state_echo(topic, payload):
    channel = mqtt_channel(topic)
    if channel in MQTT_COMMAND_CHANNELS:
        local_state_echoes[(channel, mqtt_text(payload))] = time.ticks_ms()

def consume_local_state_echo(topic, payload):
    channel = mqtt_channel(topic)
    key = (channel, mqtt_text(payload))
    sent_at = local_state_echoes.get(key)
    if sent_at is None:
        return False

    if time.ticks_diff(time.ticks_ms(), sent_at) > LOCAL_STATE_ECHO_WINDOW_MS:
        local_state_echoes.pop(key, None)
        return False

    local_state_echoes.pop(key, None)
    print('MQTT local state echo ignored:', channel, repr(key[1]))
    return True

def log_mqtt_message(topic, msg):
    topic_text = mqtt_text(topic)
    message_text = mqtt_text(msg)
    print('MQTT RX channel=', repr(topic_text),
          'wire=', repr(mqtt_wire_topic(topic_text)),
          'payload=', repr(message_text),
          'payload_type=', type(msg).__name__)
    return message_text

async def publish_device_state(topic, value, retain=False):
    if value is None:
        print('MQTT state skipped: None payload for', mqtt_wire_topic(topic))
        return False

    payload = mqtt_text(value)
    if payload.lower() == 'none' or payload == '':
        print('MQTT state skipped: invalid payload for', mqtt_wire_topic(topic))
        return False

    echo_key = (mqtt_channel(topic), payload)
    previous_echo_time = local_state_echoes.get(echo_key)
    # Mark before awaiting the network operation so a fast broker echo cannot
    # enter the command callback before the local-state filter is armed.
    remember_local_state_echo(topic, payload)
    published = await safe_publish(topic, payload, retain=retain)
    if not published:
        if previous_echo_time is None:
            local_state_echoes.pop(echo_key, None)
        else:
            local_state_echoes[echo_key] = previous_echo_time
    return published

def register_mqtt_topic(channel, callback):
    channel_text = mqtt_channel(channel)
    registered = [mqtt_channel(item[0]) for item in cfg['topics']]
    if channel_text in registered:
        raise ValueError('Duplicate MQTT channel registration: ' + channel_text)
    cfg['topics'].append((channel_text, callback))
    print('MQTT topic registered:', channel_text)

# --- CẤU HÌNH LWT ĐỂ XỬ LÝ HEARTBEAT TỰ ĐỘNG ---
cfg['will'] = (TOPIC_DEVICE, 'OFFLINE', True, 0)

async def read_dht20_safe():
    global Nhi_E1_BB_87t__C4_91_E1_BB_99, _C4_90_E1_BB_99__E1_BA_A9m
    for retry in range(5):
        try:
            temperature = await dht20.atemperature()
            humidity = await dht20.ahumidity()
            Nhi_E1_BB_87t__C4_91_E1_BB_99 = temperature
            _C4_90_E1_BB_99__E1_BA_A9m = humidity
            return True
        except OSError as e:
            print('DHT20 error:', e)
            if retry < 4:
                await asleep_ms(700)
    return False

def update_gas_oled():
    if gas_alarm_active:
        oled.fill(0); oled.show()
        oled.text(str('Phat hien'), 1-1, 1-1, 1); oled.show()
        oled.text(str('ro ri gas!!!!'), 1-1, 12-1, 1); oled.show()
        oled.text(str((''.join([str(x) for x in ['Khi gas:', khi_gas, 'ppm']]))), 1-1, 45-1, 1); oled.show()
    else:
        oled.fill_rect(0, 44, 128, 10, 0)
        oled.text(str((''.join([str(x) for x in ['Khi gas:', khi_gas, 'ppm']]))), 1-1, 45-1, 1); oled.show()

async def publish_gas_safe():
    await safe_publish(TOPIC_GAS, khi_gas)

async def K_E1_BA_BFt_n_E1_BB_91i_Wifi():
    global khi_gas, RFID, Nhi_E1_BB_87t__C4_91_E1_BB_99, last_fan_state, speed, light, AUTO_LIGHT, auto_light_when_detect, C_E1_BB_ADa, last_LED_state, color, _C4_90_E1_BB_99__E1_BA_A9m, _C3_81nh_s_C3_A1ng
    oled.text(str('Wifi connecting...'), 1-1, 1-1, 1); oled.show()
    while not await ensure_mqtt_connection():
        print('Reconnect: broker fail. Retrying...')
        await asleep_ms(3000)
    # GỬI TRẠNG THÁI ONLINE NGAY KHI KẾT NỐI THÀNH CÔNG VỚI RETAIN=TRUE
    oled.fill(0); oled.show()
    oled.text(str('Wifi connected'), 1-1, 1-1, 1); oled.show()
    neopix.show(0, hex_to_rgb('#00ff00'))
    await asleep_ms(1000)

async def Kh_E1_BB_9Fi__C4_91_E1_BB_99ng():
    global khi_gas, RFID, Nhi_E1_BB_87t__C4_91_E1_BB_99, last_fan_state, speed, light, AUTO_LIGHT, auto_light_when_detect, C_E1_BB_ADa, last_LED_state, color, _C4_90_E1_BB_99__E1_BA_A9m, _C3_81nh_s_C3_A1ng, buzzer_manual_on, buzzer_alarm_tone_on, buzzer_beep_active, gas_alarm_active, gas_alarm_task, last_door_command, last_door_command_ms
    RFID = '1'
    AUTO_LIGHT = '0'
    last_fan_state = '0'
    light = '0'
    C_E1_BB_ADa = '0'
    last_LED_state = '0'
    auto_light_when_detect = '0'
    speed = '20'
    color = '#ff0000'
    buzzer_manual_on = False
    buzzer_alarm_tone_on = False
    buzzer_beep_active = False
    gas_alarm_active = False
    gas_alarm_task = None
    last_door_command = None
    last_door_command_ms = 0
    servo_D2.servo_write(0)
    usb_switch_D3.write_analog(round(translate(0, 0, 100, 0, 1023)))
    minifan_D4.write_analog(round(translate(0, 0, 100, 0, 1023)))
    set_buzzer_output(False)
    rgb_led_D9.show(0, hex_to_rgb('#000000'))
    neopix.show(0, hex_to_rgb('#ff0000'))
    await asleep_ms(1000)
    neopix.show(0, hex_to_rgb('#00ff00'))
    await asleep_ms(1000)
    neopix.show(0, hex_to_rgb('#000000'))

async def on_mqtt_msg_c_A_i_o(topic, msg):
    global khi_gas, RFID, Nhi_E1_BB_87t__C4_91_E1_BB_99, last_fan_state, speed, light, AUTO_LIGHT, auto_light_when_detect, C_E1_BB_ADa, last_LED_state, color, _C4_90_E1_BB_99__E1_BA_A9m, _C3_81nh_s_C3_A1ng
    msg = log_mqtt_message(topic, msg)
    if consume_local_state_echo(topic, msg):
        return
    last_fan_state = msg
    if msg == '1':
        minifan_D4.write_analog(round(translate(speed, 0, 100, 0, 1023)))
    else:
        minifan_D4.write_analog(round(translate(0, 0, 100, 0, 1023)))

async def on_mqtt_msg_y_z_p_e(topic, msg):
    global khi_gas, RFID, Nhi_E1_BB_87t__C4_91_E1_BB_99, last_fan_state, speed, light, AUTO_LIGHT, auto_light_when_detect, C_E1_BB_ADa, last_LED_state, color, _C4_90_E1_BB_99__E1_BA_A9m, _C3_81nh_s_C3_A1ng
    msg = log_mqtt_message(topic, msg)
    if consume_local_state_echo(topic, msg):
        return
    try:
        speed = max(0, min(100, int(msg)))
    except (TypeError, ValueError):
        print('MQTT invalid fan speed:', repr(msg))
        return
    if last_fan_state == '1':
        minifan_D4.write_analog(round(translate(speed, 0, 100, 0, 1023)))

async def on_mqtt_msg_O_N_P_T(topic, msg):
    global khi_gas, RFID, Nhi_E1_BB_87t__C4_91_E1_BB_99, last_fan_state, speed, light, AUTO_LIGHT, auto_light_when_detect, C_E1_BB_ADa, last_LED_state, color, _C4_90_E1_BB_99__E1_BA_A9m, _C3_81nh_s_C3_A1ng
    msg = log_mqtt_message(topic, msg)
    if consume_local_state_echo(topic, msg):
        return
    light = msg
    if light == '1':
        usb_switch_D3.write_analog(round(translate(100, 0, 100, 0, 1023)))
    else:
        usb_switch_D3.write_analog(round(translate(0, 0, 100, 0, 1023)))

async def Hi_E1_BB_83n_th_E1_BB_8B_ban__C4_91_E1_BA_A7u():
    global khi_gas, RFID, Nhi_E1_BB_87t__C4_91_E1_BB_99, last_fan_state, speed, light, AUTO_LIGHT, auto_light_when_detect, C_E1_BB_ADa, last_LED_state, color, _C4_90_E1_BB_99__E1_BA_A9m, _C3_81nh_s_C3_A1ng
    _C3_81nh_s_C3_A1ng = light_A0.read_analog_percent()
    dht20_ok = await read_dht20_safe()
    oled.fill(0); oled.show()
    if Nhi_E1_BB_87t__C4_91_E1_BB_99 is None or _C4_90_E1_BB_99__E1_BA_A9m is None:
        oled.text(str('DHT20 loi'), 1-1, 1-1, 1); oled.show()
        oled.text(str('Thu lai sau'), 1-1, 15-1, 1); oled.show()
    else:
        oled.text(str((''.join([str(x5) for x5 in ['Nhiet do: ', Nhi_E1_BB_87t__C4_91_E1_BB_99, '*C']]))), 1-1, 1-1, 1); oled.show()
        oled.text(str((''.join([str(x6) for x6 in ['Do am: ', _C4_90_E1_BB_99__E1_BA_A9m, '%']]))), 1-1, 15-1, 1); oled.show()
    oled.text(str((''.join([str(x7) for x7 in ['Anh sang:', _C3_81nh_s_C3_A1ng, '%']]))), 1-1, 30-1, 1); oled.show()
    oled.text(str((''.join([str(x8) for x8 in ['Khi gas:', khi_gas, 'ppm']]))), 1-1, 45-1, 1); oled.show()
    await safe_publish(TOPIC_LIGHT_SENSOR, _C3_81nh_s_C3_A1ng)
    if dht20_ok:
        await safe_publish(TOPIC_TEMPERATURE, Nhi_E1_BB_87t__C4_91_E1_BB_99)
        await safe_publish(TOPIC_HUMIDITY, _C4_90_E1_BB_99__E1_BA_A9m)
    await safe_publish(TOPIC_GAS, khi_gas)
    await publish_device_state(TOPIC_RGB_STATE, last_LED_state)
    await publish_device_state(TOPIC_FAN_STATE, last_fan_state)
    await publish_device_state(TOPIC_LIGHT_STATE, light)
    await publish_device_state(TOPIC_MOTION_LIGHT, auto_light_when_detect)
    await publish_device_state(TOPIC_MAIN_DOOR, C_E1_BB_ADa)
    await publish_device_state(TOPIC_RFID_DOOR, RFID)
    await publish_device_state(TOPIC_AUTO_LIGHT, AUTO_LIGHT)

async def on_mqtt_msg_V_d_z_u(topic, msg):
    global khi_gas, RFID, Nhi_E1_BB_87t__C4_91_E1_BB_99, last_fan_state, speed, light, AUTO_LIGHT, auto_light_when_detect, C_E1_BB_ADa, last_LED_state, color, _C4_90_E1_BB_99__E1_BA_A9m, _C3_81nh_s_C3_A1ng
    msg = log_mqtt_message(topic, msg)
    if consume_local_state_echo(topic, msg):
        return
    AUTO_LIGHT = msg

async def on_mqtt_msg_motion_light(topic, msg):
    global khi_gas, RFID, Nhi_E1_BB_87t__C4_91_E1_BB_99, last_fan_state, speed, light, AUTO_LIGHT, auto_light_when_detect, C_E1_BB_ADa, last_LED_state, color, _C4_90_E1_BB_99__E1_BA_A9m, _C3_81nh_s_C3_A1ng
    msg = log_mqtt_message(topic, msg)
    if consume_local_state_echo(topic, msg):
        return
    if msg == '1':
        auto_light_when_detect = '1'
    else:
        auto_light_when_detect = '0'

async def on_mqtt_msg_buzzer_manual(topic, msg):
    global khi_gas, RFID, Nhi_E1_BB_87t__C4_91_E1_BB_99, last_fan_state, speed, light, AUTO_LIGHT, auto_light_when_detect, C_E1_BB_ADa, last_LED_state, color, _C4_90_E1_BB_99__E1_BA_A9m, _C3_81nh_s_C3_A1ng, buzzer_manual_on
    msg = log_mqtt_message(topic, msg)
    if msg not in ('0', '1'):
        print('MQTT invalid buzzer state:', repr(msg))
        return
    buzzer_manual_on = msg == '1'
    update_buzzer_output()

async def on_mqtt_msg_X_v_h_D(topic, msg):
    global khi_gas, RFID, Nhi_E1_BB_87t__C4_91_E1_BB_99, last_fan_state, speed, light, AUTO_LIGHT, auto_light_when_detect, C_E1_BB_ADa, last_LED_state, color, _C4_90_E1_BB_99__E1_BA_A9m, _C3_81nh_s_C3_A1ng, last_door_command, last_door_command_ms
    msg = log_mqtt_message(topic, msg)
    if consume_local_state_echo(topic, msg):
        return
    C_E1_BB_ADa = msg
    if C_E1_BB_ADa not in ('0', '1'):
        print('MQTT invalid door state:', repr(C_E1_BB_ADa))
        return
    if (C_E1_BB_ADa == last_door_command and
            time.ticks_diff(time.ticks_ms(), last_door_command_ms) <= DOOR_COMMAND_DEDUP_WINDOW_MS):
        print('MQTT duplicate door command ignored:', repr(C_E1_BB_ADa))
        return
    last_door_command = C_E1_BB_ADa
    last_door_command_ms = time.ticks_ms()
    if C_E1_BB_ADa == '1':
        servo_D2.servo_write(100)
    else:
        servo_D2.servo_write(0)
    await beep_once('dashboard-door-' + C_E1_BB_ADa, RFID_BEEP_MS)

async def on_mqtt_msg_r_E_x_W(topic, msg):
    global khi_gas, RFID, Nhi_E1_BB_87t__C4_91_E1_BB_99, last_fan_state, speed, light, AUTO_LIGHT, auto_light_when_detect, C_E1_BB_ADa, last_LED_state, color, _C4_90_E1_BB_99__E1_BA_A9m, _C3_81nh_s_C3_A1ng
    msg = log_mqtt_message(topic, msg)
    if consume_local_state_echo(topic, msg):
        return
    if msg not in ('0', '1'):
        print('MQTT invalid RFID mode:', repr(msg))
        return
    RFID = msg
    print(RFID)

khi_gas = None
RFID = None
Nhi_E1_BB_87t__C4_91_E1_BB_99 = None
last_fan_state = None
speed = None
light = None
AUTO_LIGHT = None
auto_light_when_detect = None
C_E1_BB_ADa = None
last_LED_state = None
color = None
_C4_90_E1_BB_99__E1_BA_A9m = None
_C3_81nh_s_C3_A1ng = None
gas_alarm_active = False
pir_motion_active = False
rfid_card_active = False
buzzer_manual_on = False
buzzer_output_state = None
buzzer_beep_active = False
buzzer_alarm_tone_on = False
buzzer_last_event_key = None
buzzer_last_event_ms = 0
gas_alarm_task = None
last_door_command = None
last_door_command_ms = 0
mq_A2 = MQ2(pinData=A2_PIN)
oled = SSD1306_I2C()
servo_D2 = Pins(D2_PIN)
buzzer_D7 = Pins(D7_PIN)
rgb_led_D9 = RGBLed(D9_PIN, 4)

def set_buzzer_output(is_on):
    global buzzer_output_state
    desired = bool(is_on)
    if buzzer_output_state == desired:
        return
    buzzer_output_state = desired
    buzzer_D7.write_analog(round(translate(70 if desired else 0, 0, 100, 0, 1023)))
    print('BUZZER output:', 'ON' if desired else 'OFF')

def update_buzzer_output():
    set_buzzer_output(buzzer_manual_on or buzzer_alarm_tone_on or buzzer_beep_active)

async def beep_once(event_key, duration_ms=RFID_BEEP_MS):
    global buzzer_beep_active, buzzer_last_event_key, buzzer_last_event_ms
    now = time.ticks_ms()
    if (event_key == buzzer_last_event_key and
            time.ticks_diff(now, buzzer_last_event_ms) <= BUZZER_EVENT_DEDUP_WINDOW_MS):
        print('BUZZER duplicate event ignored:', event_key)
        return
    if buzzer_beep_active:
        print('BUZZER overlapping event ignored:', event_key)
        return

    buzzer_last_event_key = event_key
    buzzer_last_event_ms = now
    buzzer_beep_active = True
    update_buzzer_output()
    await asleep_ms(duration_ms)
    buzzer_beep_active = False
    update_buzzer_output()

set_buzzer_output(False)

register_mqtt_topic(TOPIC_RGB_STATE, on_mqtt_msg_f_k_q_l)
register_mqtt_topic(TOPIC_RGB_COLOR, on_mqtt_msg_J_V_x_E)

cfg['ssid'] = WIFI_SSID
cfg['wifi_pw'] = WIFI_PASSWORD
cfg['server'] = 'mqtt.ohstem.vn'
cfg['port'] = 1883
cfg['user'] = MQTT_USER
cfg['password'] = 'mekongstem@2025'

dht20 = DHT20()
minifan_D4 = Pins(D4_PIN)
pir_D5 = Pins(D5_PIN)
register_mqtt_topic(TOPIC_FAN_STATE, on_mqtt_msg_c_A_i_o)
register_mqtt_topic(TOPIC_FAN_SPEED, on_mqtt_msg_y_z_p_e)
usb_switch_D3 = Pins(D3_PIN)
register_mqtt_topic(TOPIC_LIGHT_STATE, on_mqtt_msg_O_N_P_T)
light_A0 = Pins(A0_PIN)
register_mqtt_topic(TOPIC_AUTO_LIGHT, on_mqtt_msg_V_d_z_u)
register_mqtt_topic(TOPIC_MOTION_LIGHT, on_mqtt_msg_motion_light)
register_mqtt_topic(TOPIC_MAIN_DOOR, on_mqtt_msg_X_v_h_D)
register_mqtt_topic(TOPIC_RFID_DOOR, on_mqtt_msg_r_E_x_W)
register_mqtt_topic(TOPIC_BUZZER, on_mqtt_msg_buzzer_manual)

def deinit():
    mqtt_client.close()

import yolo_uno
yolo_uno.deinit = deinit

async def task_on_event_u_F_P_I():
    global khi_gas, RFID, Nhi_E1_BB_87t__C4_91_E1_BB_99, last_fan_state, speed, light, AUTO_LIGHT, auto_light_when_detect, C_E1_BB_ADa, last_LED_state, color, _C4_90_E1_BB_99__E1_BA_A9m, _C3_81nh_s_C3_A1ng, rfid_card_active
    while True:
        try:
            card_ok = rfid.scan_and_check("rfids_1")
        except OSError as e:
            print('RFID error:', e)
            await asleep_ms(RFID_ERROR_RETRY_MS)
            continue

        if not card_ok:
            rfid_card_active = False
            neopix.show(0, hex_to_rgb('#000000'))
            await asleep_ms(RFID_SCAN_INTERVAL_MS)
            continue

        if RFID == '1' and not rfid_card_active:
            rfid_card_active = True
            neopix.show(0, hex_to_rgb('#00ff00'))
            servo_D2.servo_write(100)
            C_E1_BB_ADa = '1'
            await beep_once('rfid-valid-card', RFID_BEEP_MS)
            await publish_device_state(TOPIC_MAIN_DOOR, C_E1_BB_ADa)
            await asleep_ms(RFID_OPEN_HOLD_MS)
            servo_D2.servo_write(0)
            C_E1_BB_ADa = '0'
            await publish_device_state(TOPIC_MAIN_DOOR, C_E1_BB_ADa)
            neopix.show(0, hex_to_rgb('#000000'))

        await asleep_ms(RFID_SCAN_INTERVAL_MS)

async def task_I_j_x_t():
    global khi_gas, RFID, Nhi_E1_BB_87t__C4_91_E1_BB_99, last_fan_state, speed, light, AUTO_LIGHT, auto_light_when_detect, C_E1_BB_ADa, last_LED_state, color, _C4_90_E1_BB_99__E1_BA_A9m, _C3_81nh_s_C3_A1ng, gas_alarm_active, gas_alarm_task, buzzer_alarm_tone_on
    while True:
        await asleep_ms(GAS_READ_INTERVAL_MS)
        khi_gas = round(await mq_A2.readLPG())
        if khi_gas > 200 and not gas_alarm_active and gas_alarm_task is None:
            gas_alarm_active = True
            gas_alarm_task = create_task(task_on_message_1())
        elif khi_gas <= 200:
            gas_alarm_active = False
            buzzer_alarm_tone_on = False
            update_buzzer_output()
        update_gas_oled()
        await publish_gas_safe()

async def task_on_message_1():
    global khi_gas, RFID, Nhi_E1_BB_87t__C4_91_E1_BB_99, last_fan_state, speed, light, AUTO_LIGHT, auto_light_when_detect, C_E1_BB_ADa, last_LED_state, color, _C4_90_E1_BB_99__E1_BA_A9m, _C3_81nh_s_C3_A1ng, gas_alarm_active, gas_alarm_task, buzzer_alarm_tone_on
    while gas_alarm_active:
        buzzer_alarm_tone_on = True
        update_buzzer_output()
        await asleep_ms(300)
        buzzer_alarm_tone_on = False
        update_buzzer_output()
        await asleep_ms(300)
    buzzer_alarm_tone_on = False
    gas_alarm_task = None
    update_buzzer_output()
    if not gas_alarm_active:
        oled.fill(0); oled.show()
        await Hi_E1_BB_83n_th_E1_BB_8B_ban__C4_91_E1_BA_A7u()
        neopix.show(0, hex_to_rgb('#000000'))

mqtt_client = MQTTClient(cfg); MQTTClient.DEBUG = True

mqtt_connected = False
mqtt_reconnect_in_progress = False

async def ensure_mqtt_connection():
    global mqtt_connected, mqtt_reconnect_in_progress

    if mqtt_connected:
        return True

    # Chỉ cho phép một task thực hiện reconnect; các task khác chờ kết quả.
    if mqtt_reconnect_in_progress:
        for i in range(60):
            if mqtt_connected:
                return True
            if not mqtt_reconnect_in_progress:
                break
            await asleep_ms(200)
        return mqtt_connected

    mqtt_reconnect_in_progress = True
    try:
        if not await ensure_wifi_connection():
            print('Reconnect: WiFi fail.')
            return False

        # WiFi có IP chưa chắc đã có đường ra internet.
        if not check_internet():
            if not await ensure_wifi_connection(force_reconnect=True):
                print('Reconnect: WiFi fail after internet check.')
                return False
            if not check_internet():
                print('Reconnect: internet still unavailable.')
                return False

        print('Internet OK. Connecting broker...')
        try:
            await mqtt_client.connect()
            await mqtt_client.publish(TOPIC_DEVICE, 'ONLINE', retain=True)
            mqtt_connected = True
            print('Broker connected.')
            return True
        except Exception as e:
            mqtt_connected = False
            print('Reconnect: broker fail.', e)
            try:
                mqtt_client.close()
            except Exception:
                pass
            return False
    finally:
        mqtt_reconnect_in_progress = False

async def safe_publish(topic, value, retain=False):
    print('MQTT TX channel=', repr(mqtt_channel(topic)),
          'wire=', repr(mqtt_wire_topic(topic)),
          'payload=', repr(mqtt_text(value)),
          'retain=', retain)
    if not await ensure_mqtt_connection():
        print('MQTT publish skipped:', mqtt_wire_topic(topic))
        return False

    try:
        await mqtt_client.publish(topic, value, retain=retain)
        return True
    except Exception as e:
        global mqtt_connected
        mqtt_connected = False
        print('MQTT publish failed:', mqtt_wire_topic(topic), e)

        # Thử reconnect một lần ngay tại lần publish bị lỗi.
        if await ensure_mqtt_connection():
            try:
                await mqtt_client.publish(topic, value, retain=retain)
                return True
            except Exception as retry_error:
                mqtt_connected = False
                print('MQTT publish retry failed:', mqtt_wire_topic(topic), retry_error)
        return False

async def task_mqtt_watchdog():
    while True:
        # Heartbeat cũng là phép kiểm tra broker. Nếu broker chết, safe_publish
        # sẽ thực hiện lại chuỗi: WiFi -> internet -> broker.
        await safe_publish(TOPIC_DEVICE, 'ONLINE', retain=True)
        await asleep_ms(MQTT_WATCHDOG_INTERVAL_MS)

async def task_N_h_S_S():
    global khi_gas, RFID, Nhi_E1_BB_87t__C4_91_E1_BB_99, last_fan_state, speed, light, AUTO_LIGHT, auto_light_when_detect, C_E1_BB_ADa, last_LED_state, color, _C4_90_E1_BB_99__E1_BA_A9m, _C3_81nh_s_C3_A1ng
    while True:
        await asleep_ms(30000)
        dht20_ok = await read_dht20_safe()
        oled.fill(0); oled.show()
        if Nhi_E1_BB_87t__C4_91_E1_BB_99 is None or _C4_90_E1_BB_99__E1_BA_A9m is None:
            oled.text(str('DHT20 loi'), 1-1, 1-1, 1); oled.show()
            oled.text(str('Thu lai sau'), 1-1, 15-1, 1); oled.show()
        else:
            oled.text(str((''.join([str(x) for x in ['Nhiet do: ', Nhi_E1_BB_87t__C4_91_E1_BB_99, '*C']]))), 1-1, 1-1, 1); oled.show()
            oled.text(str((''.join([str(x2) for x2 in ['Do am: ', _C4_90_E1_BB_99__E1_BA_A9m, '%']]))), 1-1, 15-1, 1); oled.show()
        oled.text(str((''.join([str(x3) for x3 in ['Anh sang:', _C3_81nh_s_C3_A1ng, '%']]))), 1-1, 30-1, 1); oled.show()
        oled.text(str((''.join([str(x4) for x4 in ['Khi gas:', khi_gas, 'ppm']]))), 1-1, 45-1, 1); oled.show()
        await safe_publish(TOPIC_LIGHT_SENSOR, _C3_81nh_s_C3_A1ng)
        if dht20_ok:
            await asleep_ms(500)
            await safe_publish(TOPIC_TEMPERATURE, Nhi_E1_BB_87t__C4_91_E1_BB_99)
            await asleep_ms(500)
            await safe_publish(TOPIC_HUMIDITY, _C4_90_E1_BB_99__E1_BA_A9m)

async def task_on_event_R_g_c_l():
    global khi_gas, RFID, Nhi_E1_BB_87t__C4_91_E1_BB_99, last_fan_state, speed, light, AUTO_LIGHT, auto_light_when_detect, C_E1_BB_ADa, last_LED_state, color, _C4_90_E1_BB_99__E1_BA_A9m, _C3_81nh_s_C3_A1ng, pir_motion_active
    while True:
        await asleep_ms(100)
        if (pir_D5.read_digital() == 1):
            if not pir_motion_active:
                pir_motion_active = True
                await safe_publish(TOPIC_MOTION, 'DETECTED')
            if auto_light_when_detect == '1' and light != '1':
                light = '1'
                usb_switch_D3.write_analog(round(translate(100, 0, 100, 0, 1023)))
                await publish_device_state(TOPIC_LIGHT_STATE, light)
        else:
            pir_motion_active = False

async def task_F_y_v_l():
    global khi_gas, RFID, Nhi_E1_BB_87t__C4_91_E1_BB_99, last_fan_state, speed, light, AUTO_LIGHT, auto_light_when_detect, C_E1_BB_ADa, last_LED_state, color, _C4_90_E1_BB_99__E1_BA_A9m, _C3_81nh_s_C3_A1ng
    while True:
        await asleep_ms(5000)
        if AUTO_LIGHT == '1':
            _C3_81nh_s_C3_A1ng = light_A0.read_analog_percent()
            if _C3_81nh_s_C3_A1ng < 50:
                usb_switch_D3.write_analog(round(translate(100, 0, 100, 0, 1023)))
            elif _C3_81nh_s_C3_A1ng > 70:
                usb_switch_D3.write_analog(round(translate(0, 0, 100, 0, 1023)))
        else:
            AUTO_LIGHT = '0'

async def setup():
    global khi_gas, RFID, Nhi_E1_BB_87t__C4_91_E1_BB_99, last_fan_state, speed, light, AUTO_LIGHT, auto_light_when_detect, C_E1_BB_ADa, last_LED_state, color, _C4_90_E1_BB_99__E1_BA_A9m, _C3_81nh_s_C3_A1ng
    print('App started')
    print('MQTT topic mapping:', 'V1 ->', mqtt_wire_topic(TOPIC_LIGHT_STATE),
          '| V20 ->', mqtt_wire_topic(TOPIC_DEVICE))
    print('MQTT subscriptions:', len(cfg['topics']),
          [mqtt_channel(item[0]) for item in cfg['topics']])
    print('Bắt đầu khởi động')
    await Kh_E1_BB_9Fi__C4_91_E1_BB_99ng()
    print('Đã khởi động xong')
    print('Bắt đầu kết nối wifi và Broker')
    await K_E1_BA_BFt_n_E1_BB_91i_Wifi()
    print('Đã kết nối wifi và Broker')
    print('Bắt đều hiệu chỉnh cảm biến khí Gas')
    await Hi_E1_BB_87u_ch_E1_BB_89nh_c_E1_BA_A3m_bi_E1_BA_BFn_gas()
    await asleep_ms(2000)
    print('Đã hiệu chỉnh cảm biến Gas')
    await Hi_E1_BB_83n_th_E1_BB_8B_ban__C4_91_E1_BA_A7u()
    print('Đã hiển thị dữ liệu ban đầu')

    create_task(task_on_event_u_F_P_I())
    create_task(task_I_j_x_t())
    create_task(task_N_h_S_S())
    create_task(task_on_event_R_g_c_l())
    create_task(task_F_y_v_l())
    create_task(task_mqtt_watchdog())

async def main():
    await setup()
    while True:
        await asleep_ms(100)

# --- CHẠY HÀM KẾT NỐI WIFI TRƯỚC TẤT CẢ MỌI THỨ Ở ĐÂY ---
connect_custom_wifi()

run_loop(main())
