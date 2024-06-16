Интерфейс программы:

![image](https://github.com/IgorMonchD/installed_programs/assets/113885516/d9676b59-adca-49ca-b208-4b9260fcd212)

![image](https://github.com/IgorMonchD/installed_programs/assets/113885516/9f5ce07c-d870-4ccd-9445-24805f8ddae2)

![image](https://github.com/IgorMonchD/installed_programs/assets/113885516/b49f74e3-79cc-4aec-9048-3ec7a2fb5ed1)

![image](https://github.com/IgorMonchD/installed_programs/assets/113885516/c40e583b-9666-4dc1-ac55-c1a24caee933)

Архитектура рабочего окружения в Docker:

![image](https://github.com/IgorMonchD/installed_programs/assets/113885516/34d89215-3333-4066-8b8f-8faf21f215bb)

Для установки пакетов из файла requirements.txt с помощью pip, выполните следующую команду в терминале или командной строке:
`pip install -r ./app/requirements.txt`

Для сборки приложений используются две команды:
1.	`docker-compose up -d –build.`
2.	`docker-compose -f docker-compose.prod.yml up -d –build.`

Команды запускают контейнеры из описания контейнеров, определенного в файле docker-compose.yml и docker-compose.prod.yml, в фоновом режиме (-d) и перед запуском выполняет сборку образов контейнеров (--build).


Логическая модель базы данных, представлена в виде диаграммы ER (Entity-Relationship), которая отображает сущности, их атрибуты и связи между ними.
![image](https://github.com/IgorMonchD/installed_programs/assets/113885516/64e55372-c609-4d16-bac2-13baca6c61ca)



