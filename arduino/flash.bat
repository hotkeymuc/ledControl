@ECHO OFF
SET AVRDUDE=Z:\Apps\_code\arduino-1.0-windows\hardware\tools\avr\bin\avrdude
SET CONFIG=Z:\Apps\_code\arduino-1.0-windows\hardware\tools\avr\etc\avrdude.conf
SET HEXFILE=ledControl.cpp.hex
echo Flashing %HEXFILE%...
REM ### %AVRDUDE%
REM ### %AVRDUDE% -p m128 -P COM3  -e -U flash:w:%HEXFILE%
REM ### %AVRDUDE% -C %CONFIG% -c arduino -p m168 -P COM3 -e -U flash:w:%HEXFILE%
REM ### %AVRDUDE% -C %CONFIG% -b 115200 -c arduino -p m168 -P COM3 -U flash:w:%HEXFILE%
REM ### %AVRDUDE% -C %CONFIG% -b 115200 -c arduino -p m168 -P COM3 -U flash:w:%HEXFILE%
REM ### %AVRDUDE% -C %CONFIG% -c usbtiny -p m168 -U flash:w:%HEXFILE%

REM -V = Do not verify
REM %AVRDUDE% -C %CONFIG% -c usbtiny -p m32 -V -U flash:w:%HEXFILE%

REM %AVRDUDE% -C %CONFIG% -c usbtiny -p m644 -U flash:w:%HEXFILE%

REM ### Set fuses
REM %AVRDUDE% -C %CONFIG% -c usbtiny -p m644 -U lfuse:r:-:b -U hfuse:r:-:b -U efuse:r:-:b
REM %AVRDUDE% -C %CONFIG% -c usbtiny -p m644 -U lfuse:r:-:i -U hfuse:r:-:i -U efuse:r:-:i
REM %AVRDUDE% -C %CONFIG% -c usbtiny -p m644 -U lfuse:w:0xff:m -U hfuse:w:0xde:m -U efuse:w:0xfd:m