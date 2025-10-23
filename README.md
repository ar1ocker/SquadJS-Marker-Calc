# SquadJS-Marker-Calc

Консольное приложение для Windows которое считывает ваше текущее местоположение на карте и отправляет его в сервис [https://github.com/ar1ocker/SquadJS-Mortar-Calc](https://github.com/ar1ocker/SquadJS-Mortar-Calc) который расчитывает расстояние и выдаёт вам варн на сервере с этим расстоянием и углами для миномёта

На сервере должен быть установлен плагин-сервис [https://github.com/ar1ocker/SquadJS-Mortar-Calc](https://github.com/ar1ocker/SquadJS-Mortar-Calc)

## Подготовка

Для работы приложения - нужен Tesseract-OCR [https://tesseract-ocr.github.io/tessdoc/Downloads](https://tesseract-ocr.github.io/tessdoc/Downloads)

И к нему по хорошему модельку best_end.traineddata [https://github.com/tesseract-ocr/tessdata_best](https://github.com/tesseract-ocr/tessdata_best) которую нужно положить в папку tessdata

## Как билдить в бинарь

```
pyinstaller --paths=ВАШ_SITE_PACHAGES_В_VENV --add-data Tesseract-OCR:Tesseract-OCR --add-data config.toml:. .\squad_marker_calc.py
```

## Настройки

В файле config.toml можно изменить место которое скриншотит приложение

Скриншот и обработка производится при нажатии левой кнопки мыши при открытой большой карте и при нажатии пкм

Скриншот нужен левой верхней части экрана над картой, где написаны текущие координаты и где появляются координаты при наведении на карту

```
[resolutions.1920x1080]
top = 0
left = 518
width = 466
height = 76
```
