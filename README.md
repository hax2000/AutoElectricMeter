# AutoElectricMeter
GUI-Приложение, созданное для считывания и визуализации на экране ПК данных, полученных с специального счётчика, подключенному через Serial.
## Порядок установки и запуска
1. Для начала необходимо установить необходимые библиотеки для Python:
```
pip install -r requirements.txt
```
2. Теперь заходим в обёртку mysql на <b>локальном</b> компьютере (Можно воспользоваться Workbench`ем) и скармливаем ему database.sql:
```
source database.sql
```
### 3. Подключаем датчик в usb-порт, ждём пару секунд инициализацию
4. Запускаем программу
5. Выбираем порт и ждём несколько секунд пока программа начнёт считывать данные.
