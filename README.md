# Лабораторные работы

# Требования
- IDE:
    - Jupyter Notebook
- ОС:
    - Linux
    - Windows + WSL (Windows Subsystem for Linux)
- Менеджер окружения:
    - uv
- Python == 3.11


# Предварительные шаги для Windows
В современной индустрии серверная и облачная разработка преимущественно ведётся в UNIX-подобных средах (Linux и macOS). Для разработчиков на Windows рекомендуется использование подсистемы Windows для Linux (WSL 2), которая обеспечивает нативную совместимость с Linux-инструментами без потери производительности.

## WSL
1. Нажмите `Win + X` и выберите Терминал (Администратор) или Windows PowerShell (Администратор)
2. Выполните команду установки `wsl --install` (установит в WSL дистрибутив Ubuntu по умолчанию)
3. Перезагрузите компьютер
4. Начните работу в WSL:
    - После перезагрузки
        - нажмите `Win + S` -> введите `cmd` ->  зайдите к командную строку и откройте новую вкладку Ubuntu
        - или нажмите `Win + S` -> введите `Ubuntu`
    - При первом запуске Вам потребуется придумать имя пользователя (login) и пароль для Linux-системы.

# Запуск

## Запустите терминал

Запустите терминал (для Windows сначала запустите WSL: нажмите `Win + S` -> введите `Ubuntu` -> зайдите и откройте командную строку)

## Установка uv

```bash
# 1. Скачивание установщика uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Скачать и установить Python 3.11
uv python install 3.11

# 3. Перезагрузите терминал. Проверьте, что uv установился
uv --version
```

## Создание директории (распаковка архива)

```bash
# Распакуйте лабораторные работы
unzip labs-autumn2026-master.zip -d ~/labs
cd ~/labs

# Переместить содержимое на уровень выше
mv labs-autumn2026-master/* ~/labs
rm -rf labs-autumn2026-master

# Проверить содержимое директории
ls
```

## Настройка uv для проекта

```bash
# Установка зависимостей для Jupyter notebook
uv add --dev ipykernel

# Добавляем Jupyter в проект
uv add --dev jupyter

# Добавляем ядро
uv run python -m ipykernel install --user --name=labs --display-name="Python 3.11 (labs)"
```

## Запуск Jupyter notebook

```bash
# Запуск
uv run jupyter notebook
```

Скопируйте ссылку и откройте в браузере на Windows
(или наведите курсор на адрес вида  `http://localhost:8888/tree?token=...` нажмите Ctrl + левая клавиша мыши)

### Открытие файлов jupyter notebook

- Откройте в файловом браузере файл с расширением `.ipynb`.
- Выберите ядро `Python 3.11 (labs)`.

### Если ссылка не открывается

Если ссылка вида http://localhost:8888/tree?token=a903cb... не открывается на Windows, замените на реальный IP.  
(Остановите Jupyter `Ctrl + C` в терминале, если он был запущен).
```bash
# Проверить IP
hostname -I

# Запуск 
uv run jupyter notebook --ip=0.0.0.0 --no-browser
```
Скопируйте ссылку, **замените IP** (первый в hostname) и откройте в браузере на Windows

Далее откройте в файловом браузере файл с расширением `.ipynb`.

# Полезные ссылки
1) Учебник по машинному обучению, https://education.yandex.ru/handbook/ml/article/mashinnoye-obucheniye
2) Курс "Машинное обучение" на ФКН ВШЭ, https://github.com/esokolov/ml-course-hse
http://wiki.cs.hse.ru/Машинное_обучение_1, 
http://wiki.cs.hse.ru/Машинное_обучение_2
3) Машинное обучение (курс лекций, К.В.Воронцов), http://www.machinelearning.ru/wiki/index.php?title=Машинное_обучение_(курс_лекций%2C_К.В.Воронцов)
4) Машинное и глубокое обучение, онлайн-учебник, В. В. Китов, https://deepmachinelearning.ru/





