# Лабораторная работа № 5

## Краткое описание

В ходе работы необходимо настроить версионирование кода и данных.

## Подготовка

В инструкции при вводе команды sudo необходимо ввести пароль!

Для лабораторной работы нужно выполнить в терминале выполнить команды для установки, которые указаны ниже.

### Устанавливаем Docker
```bash
# Add Docker's official GPG key:
sudo apt update
sudo apt install ca-certificates curl tree
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
# Add the repository to Apt sources:
sudo tee /etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOF
sudo apt update
```

```bash
sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
# Ввести пароль и согласиться 'Y'
```

```bash
# Запускаем docker
sudo systemctl start docker
```

```bash
# Проверяем что всё успешно установлено 
sudo docker run hello-world
# Увидим "Hello from Docker! ..."
```
```bash
# Переходим в папку с лабой
cd ~/labs/lab_05
# Перезагрузим докер и развернём наш GitLab
sudo systemctl restart docker && docker compose up -d 
```

### Установка Git
```bash
sudo apt install git
```

### Запуск Jupyter
```bash
cd ~/labs
uv run jupyter notebook
```
После запуска переходим в jupyter notebook