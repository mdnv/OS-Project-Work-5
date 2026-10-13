# Пошаговая инструкция: MacBook → SSH → Ubuntu → GitHub

Все файлы и готовый краткий README уже входят в проект. Программа проверена:
10 тестов проходят; SRTF и RR совпадают с эталоном задания.

**В условии ошибка FCFS:** для заданного set1 правильные средние — 8,75 и
15,25, а не 9,25 и 15,75. Подробный расчет приведен в REPORT.md.
Приоритеты set1 выбраны самостоятельно, потому что в условии их нет.
set2 и set3 — демонстрационные наборы; если преподаватель выдал свои файлы,
замени соответствующие файлы перед экспериментами. generate_data.py
перезаписывает входные файлы, поэтому не запускай его после такой замены.

## 1. Скачать проект на Mac

Скачай OS-Project-Work-5.zip в Downloads. Открой Finder → Загрузки и дважды
нажми архив. Появится папка OS-Project-Work-5.

Открой новое окно Terminal через Command+N. Это окно должно быть локальным,
не SSH. Выполни:

```bash
cd ~/Downloads/OS-Project-Work-5
ls
```

Ожидаются sched.py, experiments.py, generate_data.py, test_sched.py,
set1.txt, set2.txt, set3.txt, starvation.txt, requirements.txt, README.md,
REPORT.md, INSTRUCTION.md, results.

Если папка не найдена, проверь имя и место загрузки в Finder. Не вводи
команды Mac в окне SSH: у Ubuntu другая папка Downloads.

## 2. Скопировать проект в Ubuntu

Используй имя, адрес и порт из своей рабочей команды SSH.
Если подключение выглядит как `ssh user@192.168.1.50`, выполни на Mac:

```bash
scp -r ~/Downloads/OS-Project-Work-5 user@192.168.1.50:~/
```

Это только пример: замени user и IP своими значениями.
Если подключаешься через `ssh -p 2222 user@127.0.0.1`, копирование такое:

```bash
scp -P 2222 -r ~/Downloads/OS-Project-Work-5 user@127.0.0.1:~/
```

Для scp порт задается большой `-P`, для ssh — маленькой `-p`.
Выбери один вариант. Пароль — пароль пользователя Ubuntu; символы при
вводе не отображаются. Повторное копирование обновляет одноименные файлы:
если уже работал в этой папке, сначала сохрани свою копию.

В уже открытом SSH-окне выполни:

```bash
whoami
uname -s
cd ~/OS-Project-Work-5
pwd
ls -a
```

Должны быть Linux и путь `/home/ТВОЙ_ПОЛЬЗОВАТЕЛЬ/OS-Project-Work-5`.
В списке должна быть .gitignore. Дальнейшие команды до копирования графиков
выполняются в Ubuntu через SSH.

## 3. Подготовить Python

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git nano
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

Для штатного Python Ubuntu 24.04 ожидается версия 3.12.x. После активации
перед приглашением обычно появляется (.venv). Проверь:

```bash
which python3
```

Путь должен заканчиваться `OS-Project-Work-5/.venv/bin/python3`.
Matplotlib используется только для графиков. sched.py и тесты работают
без сторонних пакетов. Графики сохраняются в PNG: рабочий стол Ubuntu не нужен.

Если `ensurepip is not available`:

```bash
sudo apt install -y python3-venv
python3 -m venv .venv
source .venv/bin/activate
```

Если `externally-managed-environment`, активируй .venv и повтори установку.
Если `No module named matplotlib`, выполни установку requirements внутри .venv.

## 4. Проверить данные и посмотреть код

```bash
cat set1.txt
wc -l set1.txt set2.txt set3.txt
```

set1:

```text
# PID arrival burst priority
P1 0 8 3
P2 1 4 1
P3 2 9 4
P4 3 5 2
```

Числа означают время прибытия, CPU-бёрст и приоритет.
Меньший приоритет — более важный процесс. Ожидаемые количества строк:
5, 21, 21, включая одну строку комментария в каждом файле.

Открой код:

```bash
nano sched.py
```

Для поиска функции нажми Control+W, введи `def simulate`, Enter.
Чтобы выйти, нажми Control+X. Чтобы сохранить изменение: Control+O, Enter.
Здесь используется Control, а не Command.

Основные части кода:

- read_processes читает четыре поля, пропуская комментарии и пустые строки.
- simulate возвращает список интервалов (начало, конец, PID).
- FCFS выбирает самый ранний прибывший процесс и выполняет до конца.
- SJF при освобождении CPU выбирает кратчайший из готовых процессов.
- SRTF каждый такт выбирает наименьшее оставшееся CPU-время.
- Priority каждый такт сравнивает эффективные приоритеты.
- RR использует deque; admit(t) добавляет новые процессы раньше
  queue.append(i), который возвращает вытесненный процесс в хвост.
- calculate_metrics вычисляет ожидание, оборот, отклик, CPU и переключения.
- main разбирает --algo, --quantum, --aging и имя входного файла.

Время здесь условное: не нужно измерять секунды через time или смотреть top.

## 5. Запустить контрольный набор

```bash
python3 sched.py --algo rr --quantum 3 set1.txt
```

Ожидается:

```text
Algorithm             AvgWait   AvgTurn   AvgResp     CPU%  Switches
RR q=3                  13.50     20.00      3.00   100.00         9
```

```bash
python3 sched.py --algo srtf set1.txt
python3 sched.py --algo all set1.txt
```

Ожидаемая полная таблица:

| Алгоритм | AvgWait | AvgTurn | AvgResp | CPU% | Switches |
|---|---:|---:|---:|---:|---:|
| FCFS | 8.75 | 15.25 | 8.75 | 100 | 3 |
| SJF | 7.75 | 14.25 | 7.75 | 100 | 3 |
| SRTF | 6.50 | 13.00 | 4.25 | 100 | 4 |
| PRIORITY | 6.50 | 13.00 | 4.25 | 100 | 4 |
| RR q=3 | 13.50 | 20.00 | 3.00 | 100 | 9 |

Это правильные результаты для приложенного set1. Одинаковые результаты
SRTF и Priority обусловлены выбранными приоритетами, а не равенством алгоритмов.

Подробный RR:

```bash
python3 sched.py --algo rr --quantum 3 --timeline --per-process set1.txt
```

Интервалы:

```text
0-3:P1 | 3-6:P2 | 6-9:P3 | 9-12:P4 | 12-15:P1 |
15-16:P2 | 16-19:P3 | 19-21:P4 | 21-23:P1 | 23-26:P3
```

Пример P2: прибытие=1, первый запуск=3, завершение=16, burst=4.
Оборот=16−1=15; ожидание=15−4=11; отклик=3−1=2.

Переключения считаются между соседними разными PID. Первый запуск,
переходы через IDLE и очередной квант того же единственного процесса
не считаются. Стоимость переключений — ноль.

## 6. Запустить проверки

```bash
python3 -m unittest -v
```

Ожидается `Ran 10 tests ... OK`. Время может отличаться.
При FAIL проверь, что sched.py не изменен случайно и что запущен из папки проекта.
При расхождении SRTF/RR также проверь содержимое set1 и quantum=3.

## 7. Сравнить set2 и set3, построить графики

```bash
python3 sched.py --algo all set2.txt
python3 sched.py --algo all set3.txt
python3 experiments.py
ls results
cat results/rr_quantum.csv
```

Создаются comparison.csv, rr_quantum.csv, aging.csv, rr_quantum.png, aging.png.
PNG из архива уже есть, а запуск experiments.py пересчитывает их на текущих данных.

На приложенном set2 для q=1 ожидание=411.40, переключения=531;
для q=3 — 404.55 и 183; для q=10 — 365.80 и 58.
Отклик для q=1 — 8.55, для q=10 — 89.50.

На set3 SRTF дает ожидание=11.60 против 88.05 у FCFS: короткие процессы
вытесняют длинный и быстро завершаются.

Текст вывода: малый квант улучшает отклик, но повышает число переключений.
Большой квант уменьшает потенциальные накладные расходы, но ухудшает отклик.
Среднее ожидание зависит от конкретных бёрстов и прибытий и не обязано
меняться монотонно. В симуляторе переключения не занимают время, поэтому
на этих наборах CPU=100% при любом q.

## 8. Проверить aging

```bash
python3 sched.py --algo priority --per-process starvation.txt > results/priority_no_aging.txt
python3 sched.py --algo priority --aging 5 --per-process starvation.txt > results/priority_aging.txt
grep '^LOW' results/priority_no_aging.txt results/priority_aging.txt
```

LOW без aging: первый запуск=1600, завершение=1608, ожидание=1600.
LOW с aging=5: первый запуск=96, завершение=118, ожидание=110.

Важная формула:

```text
waiting = t - arrival - (burst - remaining)
effective_priority = priority - waiting // 5
```

Приоритет улучшается только за ожидание, а не за выполнение.
Aging применяется ко всем ожидающим процессам; бонус не сбрасывается.

Текст вывода: на конечном наборе без aging LOW все же запускается после
завершения высокоприоритетных процессов. Если непрерывно продолжать поступление
того же потока, LOW вообще не получит CPU — это голодание. Aging дает LOW
возможность выполняться еще до окончания высокоприоритетного потока.

## 9. Открыть графики на Mac

В новом локальном окне Terminal на Mac (не в SSH) выполни:

```bash
mkdir -p ~/Downloads/CPU-Lab5-results
scp -r user@192.168.1.50:~/OS-Project-Work-5/results/. ~/Downloads/CPU-Lab5-results/
open ~/Downloads/CPU-Lab5-results/rr_quantum.png
open ~/Downloads/CPU-Lab5-results/aging.png
```

Для проброшенного порта:

```bash
scp -P 2222 -r user@127.0.0.1:~/OS-Project-Work-5/results/. ~/Downloads/CPU-Lab5-results/
```

Подставь рабочие данные подключения. `open: command not found` означает,
что команда выполняется в Ubuntu, а нужна локальная вкладка Terminal на Mac.

## 10. README и сдача

```bash
cat README.md
cat REPORT.md
```

README уже готов и описывает реализацию, запуск, метрики и результаты.
REPORT содержит таблицы, выводы и расчет ошибки FCFS.
Для демонстрации приготовь запуск RR/SRTF, таблицу всех алгоритмов,
график RR, сравнение aging и результат тестов.

Ответы:

1. Точный SJF требует заранее знать длину следующего CPU-бёрста, а реальная
   ОС ее не знает. Она может лишь оценивать будущий бёрст по предыдущим.
2. При кванте больше всех бёрстов RR работает как FCFS.

## 11. Загрузить на GitHub

На Mac в браузере открой https://github.com/new. Название:
OS-Project-Work-5. Выбери доступность Public/Private по требованиям преподавателя.
Оставь README, .gitignore и license при создании выключенными: они уже есть
в локальном проекте. Нажми Create repository.

Вернись в Ubuntu через SSH:

```bash
cd ~/OS-Project-Work-5
git init
git branch -M main
git config user.name "ТВОЕ ИМЯ"
git config user.email "ТВОЙ EMAIL GITHUB"
git add .
git status
git commit -m "Add CPU scheduling simulator and experiments"
```

Подставь имя и email. В git status должны быть код, данные и results;
.venv не должна попадать в коммит благодаря .gitignore.

Скопируй HTTPS-адрес нового репозитория и используй:

```bash
git remote add origin https://github.com/ТВОЙ_ЛОГИН/OS-Project-Work-5.git
git remote -v
git push -u origin main
```

Если Git просит Username — введи логин GitHub. В Password нужен personal
access token, а не обычный пароль и не шестизначный одноразовый код.

Если токена еще нет, в браузере GitHub:
аватар → Settings → Developer settings → Personal access tokens →
Fine-grained tokens → Generate new token. Назови CPU-Lab5, выбери срок,
Resource owner — свой аккаунт, Repository access — Only select repositories,
выбери OS-Project-Work-5. Repository permissions: Contents — Read and write.
Создай токен и вставь его в скрытый запрос Password терминала. Не вставляй
токен в sched.py, README или команду remote: это учетные данные.

Успех: в выводе есть `main -> main`, а после обновления страницы GitHub видны
файлы и README. Открой results/rr_quantum.png и REPORT.md, проверь загрузку.

Если `remote origin already exists`, исправь адрес:

```bash
git remote set-url origin https://github.com/ТВОЙ_ЛОГИН/OS-Project-Work-5.git
```

Если `Author identity unknown`, задай user.name и user.email как выше,
затем повтори commit.

Если `Invalid username or token`, проверь срок токена, выбранный репозиторий
и разрешение Contents: Read and write; затем повтори push.

Если `non-fast-forward`, вероятно в GitHub уже создан README. Для этого
нового учебного репозитория сначала сохрани локальную работу коммитом, затем:

```bash
git fetch origin
git merge origin/main --allow-unrelated-histories
```

Если конфликта нет, сделай push. Если конфликт в README.md:
`nano README.md`, оставь нужный текст и убери маркеры <<<<<<<, =======, >>>>>>>;
затем `git add README.md`, `git commit`, `git push -u origin main`.
Для отмены незавершенного merge: `git merge --abort`.

Последующие обновления:

```bash
git add .
git commit -m "Update CPU scheduling results"
git push
```

Если `nothing to commit`, новых изменений нет.

## Дополнительные ошибки

| Сообщение | Что сделать |
|---|---|
| scp: Connection refused / timed out | Использовать тот же адрес и порт, с которыми работает SSH; проверить, запущена ли VM |
| Permission denied при SSH/scp | Проверить имя пользователя и пароль Ubuntu |
| can't open file sched.py | `cd ~/OS-Project-Work-5`, затем `ls` |
| expected PID arrival burst priority | Удалить заголовок без #; оставить четыре поля на каждой строке |
| arrival >= 0 and burst > 0 | Исправить отрицательное прибытие или нулевой/отрицательный burst |
| quantum must be a positive integer | Указать `--quantum 3` или другой положительный целый квант |
| CPU всегда 100% | Ожидаемо для данных без простоя при нулевой стоимости переключений |
| No module named matplotlib | `source .venv/bin/activate`, затем `python3 -m pip install -r requirements.txt` |
| Temporary failure resolving / network unreachable | Проверить интернет в Ubuntu; повторить apt/pip после восстановления сети |

После нового SSH-подключения возвращайся в проект и активируй окружение:

```bash
cd ~/OS-Project-Work-5
source .venv/bin/activate
```

Официальные справки:
- https://ubuntu.com/developers/docs/tutorials/python-use/
- https://research.cs.wisc.edu/wind/OSTEP/cpu-sched.pdf
- https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github
- https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens
