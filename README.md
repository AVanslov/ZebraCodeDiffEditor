# Zebra - Code Diff Editor Widget

По заданию виджет, который предполагается для использования в программе для отображения изменений в коде внесенных ИИ. Позволяет увидеть, какие изменения внесены и отредактировать код.

В данном случай разработано как десктопное приложение на Python + PySide6 для редактирования кода и симуляцией обработки код через ИИ - изменение, удаление, добавление пустых и новых строк.

В файле [ROADMAP.md](/ROADMAP.md) вы можете найти рабочие записи, планы, задачи.

[![GitHub](https://img.shields.io/badge/-GitHub_репозиторий_проекта-black?style=for-the-badge&logo=GitHub)](https://github.com/AVanslov/ZebraCodeDiffEditor)
[![GoogleDrive](https://img.shields.io/badge/-google_диск_с_архивом_проекта-black?style=for-the-badge&logo=GoogleDrive)](https://drive.google.com/drive/folders/1cPUx0n--lFTD2nSzK6GYpuNtPBHfINSX?usp=sharing)

## Реализованы возможности:
- Ввести промпт и нажать run для активации манипуляций с исходным кодом
- Подсветка синтаксиса для python
- Подсветка удаленных строк
- Подстветка новых строк
- Подстветка измененных строк
- Возможность отредактировать и в режиме реального времени увидеть изменения и подсветку изменений относительно исходного кода
- Сворачивание немодифицированных строк кода (есть баги)
- Функции undo / redo
- Возможность сохранить исправленный код в виде текстового файла с пользовательским расширением
- Возможность переключаться с помощью тогла между режимами отображения кода (2 / 1 колонка)
- Возможность сворачивать левый сайдбар, предусмотренный для ввода промпта, а также для потенциального маштабирования функций приложения
- Возможность переключаться между светлой и темной темами
- Созданая заставка загрузки приложения

**В будущем планируется:**
- Исправить баги в разворачивании немодифицированных блоков
- Настроить стиль кнопки разворачивании немодифицированных блоков
- Более детально подобрать цветовые сочетания
- Добавить анимации в нажатия тогл кнопок
- Добавить тени в тогл, кнопки и интерфейс для большей глубины интерфейса
- Улучшить алгоритм отслеживания изменений между версиями кода - сравнивать строки отслеживая их перемещения из-за добавления или удаления строк
- Улучшить поведение при загрузке больших файлов
- Добавить кнопки для возможности копировать код из полей
- Добавить линии в редакторе для отображения отступов и пробелов
- Добавить подсветку синтаксиса для большего числа языков
- Добавить раздел настроек для настройки стилей интерфейса

## Технологический стек проекта

![Python3](https://img.shields.io/badge/-Python3-black?style=for-the-badge&logo=python)
![PySide6](https://img.shields.io/badge/-PySide6-black?style=for-the-badge)

## Установка и запуск:

1. Установите Python 3.10+ (если ещё не установлен).

2. Клонируйте репозиторий или распакуйте архив проекта:

```
git clone git@github.com:AVanslov/ZebraCodeDiffEditor.git
cd ZebraCodeDiffEditor
```

3. (Рекомендуется) Создайте виртуальное окружение:
```
python3 -m venv venv
```
*Для Linux/Mac*
```
source venv/bin/activate
```
*Для Windows*
```
venv\Scripts\activate
```

4. Установите проект:

```
pip install .
```

5. Запустите приложение:
```
zebra-diff
```

## Удаление проекта

Чтобы удалить проект выполните команду:

```
pip uninstall zebra-code-diff-editor
```

## Разработчик

[![GitHub](https://img.shields.io/badge/-Бучельников_Александр-black?style=for-the-badge&logo=GitHub)](https://github.com/AVanslov)
[![Telegram](https://img.shields.io/badge/-Telegram-black?style=for-the-badge&logo=Telegram)](https://t.me/aleksandr_buchelnikov)
[![LinkedIn](https://img.shields.io/badge/-LinkedIn-black?style=for-the-badge&logo=LinkedIn)](https://www.linkedin.com/in/aleksandr-buchelnikov/)
[![Upwork](https://img.shields.io/badge/-Upwork-black?style=for-the-badge&logo=Upwork)](https://www.upwork.com/freelancers/~01f4ee846d7823ab17?mp_source=share)
[![E-mail](https://img.shields.io/badge/-E_mail-black?style=for-the-badge&logo=Gmail)](mailto:al.buchelnikov@gmail.com)