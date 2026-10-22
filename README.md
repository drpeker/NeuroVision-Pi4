# NeuroVision-Pi4

**Raspberry Pi 4 | Voice AI + Computer Vision + MCP**

Developed by Dr. Mustafa Kemal Peker

## Proje

NeuroVision-Pi4, Raspberry Pi 4 üzerinde sesli yapay zekâ ile yerel nesne algılamayı birleştiren robotik AI projesidir.

## Donanım

- Raspberry Pi 4 Model B (4 GB)
- Debian 13 Trixie
- Logitech C270 USB kamera ve mikrofon
- Analog ses çıkışı ve harici amplifikatör

## Özellikler

- SSD MobileNet v2 ile nesne algılama
- OpenCV ve LiteRT
- Canlı MJPEG kamera yayını
- XiaoZhi sesli yapay zekâ
- MCP get_visible_objects entegrasyonu
- Türkçe sesli yanıt
- SSH üzerinden tek komutla başlatma

## Başlatma

    ~/.local/bin/neuro-vision

Durdurmak için Ctrl+C.

## Önemli dosyalar

| Dosya | Görevi |
|---|---|
| vision/neurovision_live.py | Kamera ve nesne algılama |
| vision/models/ | Yapay zekâ modelleri |
| src/mcp/tools/neurovision/register.py | MCP görsel algılama |
| src/mcp/mcp_server.py | MCP araç kaydı |
| scripts/neuro-vision | Başlatma betiği |

## Kamera arayüzü

- http://neurobrain.local:8080/
- http://neurobrain.local:8080/stream
- http://neurobrain.local:8080/detections

## Açık kaynak altyapı

Sesli asistan altyapısı [py-xiaozhi](https://github.com/huangjunsen0406/py-xiaozhi) projesine dayanır.

[Orijinal XiaoZhi README](README-XIAOZHI.md)

Orijinal MIT lisansı korunmaktadır.
