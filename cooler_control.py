#!/usr/bin/python3
import RPi.GPIO as GPIO  # Импортируем библиотеку по работе с GPIO
import sys
import traceback  # Импортируем библиотеки для обработки исключений

from time import sleep  # Импортируем библиотеку для работы со временем
from re import findall  # Импортируем библиотеку по работе с регулярными выражениями
from subprocess import check_output  # Импортируем библиотеку по работе с внешними процессами


class Pi:
    @staticmethod
    def get_temperature():
        temperature = check_output(["vcgencmd", "measure_temp"]).decode()  # Выполняем запрос температуры
        temperature = float(findall('\d+\.\d+', temperature)[
                                0])  # Извлекаем при помощи регулярного выражения
        # значение температуры из строки "temp=47.8'C"
        return temperature  # Возвращаем результат

    @staticmethod
    def gpio_init():
        GPIO.setmode(GPIO.BCM)  # Режим нумерации в BCM

    @staticmethod
    def gpio_setup(pin, initial=0):
        GPIO.setup(pin, GPIO.OUT, initial=initial)  # Управление

    @staticmethod
    def gpio_set_state(pin, state):
        GPIO.output(pin, state)

    # Возвращаем пины в исходное состояние
    @staticmethod
    def gpio_cleanup():
        GPIO.cleanup()


class Cooler:
    temperature_for_turn_on = None
    temperature_for_turn_off = None
    state = None
    T_MAX = 60
    T_MIN = 50
    DEFAULT_PIN = 14

    def __init__(self,
                 temperature_for_turn_on=None,
                 temperature_for_turn_off=None,
                 init_state=None,
                 control_pin=None):
        self.temperature_for_turn_on = Cooler.T_MAX if temperature_for_turn_on is None else temperature_for_turn_on
        self.temperature_for_turn_off = Cooler.T_MIN if temperature_for_turn_off is None else temperature_for_turn_off

        self.state = False if not init_state else True
        self.control_pin = Cooler.DEFAULT_PIN if control_pin is None else control_pin

        # Сброс пинов
        Pi.gpio_cleanup()
        # Инициализация пинов
        Pi.gpio_init()
        Pi.gpio_setup(self.control_pin)

        # При первом включении прогонит вентилятор
        if self.state:
            self.turn_on()
            sleep(5)
            self.turn_off()
            sleep(1)

    def __del__(self):
        Pi.gpio_cleanup()

    def run(self):
        try:
            while True:  # Бесконечный цикл запроса температуры
                temperature = Pi.get_temperature()  # Получаем значение температуры

                if temperature >= self.temperature_for_turn_on:
                    self.turn_on()
                    sleep(7)

                if temperature <= self.temperature_for_turn_off:
                    self.turn_off()

                print(str(temperature) + " - " + str(self.get_state()))  # Выводим температуру в консоль
                sleep(3)  # Пауза

        except KeyboardInterrupt:
            # ...
            print("Exit pressed Ctrl+C")  # Выход из программы по нажатию Ctrl+C
        except:
            # ...
            print("Other Exception")  # Прочие исключения
            print("--- Start Exception Data:")
            traceback.print_exc(limit=2, file=sys.stdout)  # Подробности исключения через traceback
            print("--- End Exception Data:")
        finally:
            print("CleanUp")  # Информируем о сбросе пинов
            Pi.gpio_cleanup()  # Возвращаем пины в исходное состояние
            print("End of program")  # Информируем о завершении работы программы

    def __invert_state(self):
        self.state = not self.state

    def is_turn_on(self):
        return True if self.state else False

    def is_turn_off(self):
        return not self.is_turn_on()

    def turn_on(self):
        self.__set_state(True)

    def turn_off(self):
        self.__set_state(False)

    def __set_state(self, state):
        self.state = True if state else False
        Pi.gpio_set_state(self.control_pin, self.state)

    def get_state(self):
        return 'On' if self.state else 'Off'


if __name__ == "__main__":
    cooler = Cooler(init_state=True)
    cooler.run()
    # cooler.cleanup_controller()
