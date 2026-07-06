# 🏛️ Shekinah AI Portal — Цитадель Духа
> **Мультипровайдерный ИИ-Чат на Streamlit & Python**

[![Deploy to Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/)
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/)
[![Deploy to Netlify](https://www.netlify.com/img/deploy/button.svg)](https://www.netlify.com/)

Интеллектуальная Обитель Цитадели Духа — это локальный и облачный веб-интерфейс для ведения глубоких, академических диалогов с передовыми языковыми моделями семейств **Google Gemini**, **Anthropic Claude** и **Mistral AI**. Портал оформлен в строгом темном минимализме, оптимизирован для Arch Linux и готов к развертыванию.

---

## 🚀 1. Локальный запуск и настройка

### Клонирование репозитория
Склонируйте проект из удаленной обители в локальный каталог:
```bash
git clone https://gitlab.com/webarystan/ai-chat-app.git
cd ai-chat-app
```

### Настройка окружения
Проект поддерживает автоматическую активацию виртуальной среды с помощью `direnv`. 

1. **Метод через Direnv (Рекомендуемый для Arch Linux + Fish)**:
   * Убедитесь, что `direnv` установлен и хук добавлен в `~/.config/fish/config.fish` (`direnv hook fish | source`).
   * В корне проекта файл `.envrc` должен содержать `layout python`.
   * Разрешите выполнение:
     ```bash
     direnv allow
     ```
   * Окружение активируется автоматически при переходе в папку проекта.

2. **Классический метод (Ручной)**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate.fish  # Для Fish shell
   # или source .venv/bin/activate для Bash/Zsh
   ```

### Установка зависимостей
```bash
pip install -r requirements.txt
```

### Настройка ключей доступа
Создайте в корне файл `.env` (он находится в `.gitignore` и защищен от утечек) и добавьте ваши секретные ключи доступа к API:
```env
GEMINI_API_KEY=your_gemini_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
MISTRAL_API_KEY=your_mistral_key_here
```

### Запуск приложения
```bash
streamlit run app.py
```
*После запуска интерфейс будет доступен в браузере по адресу `http://localhost:8501`.*

---

## 💾 2. Синхронизация с GitLab & GitHub

Если вам необходимо сохранять проект в двух независимых обителях (GitLab и GitHub) одновременно, настройте удаленные репозитории.

### Настройка двух remotes
1. Убедитесь, что `origin` указывает на GitLab:
   ```bash
   git remote set-url origin https://gitlab.com/webarystan/ai-chat-app.git
   ```
2. Добавьте зеркало на GitHub (замените `your-username` на ваш аккаунт):
   ```bash
   git remote add github https://github.com/your-username/ai-chat-app.git
   ```

### Пуш в обе обители по отдельности
```bash
# Отправка на GitLab
git push origin main

# Отправка на GitHub
git push github main
```

### Лайфхак: Пуш в обе обители одной командой
Вы можете настроить Git так, чтобы при вызове `git push origin` коммиты автоматически уходили на оба сервера:
```bash
git remote set-url --add --push origin https://gitlab.com/webarystan/ai-chat-app.git
git remote set-url --add --push origin https://github.com/your-username/ai-chat-app.git
```
*Теперь простой вызов `git push origin main` отправит изменения и на GitLab, и на GitHub.*

---

## 🌐 3. Развертывание в облаке (Deploy)

### 3.1. Streamlit Community Cloud (Нативно и бесплатно)
Это самый надежный способ развернуть Streamlit-приложение, так как платформа предоставляет постоянный серверный процесс.

1. Загрузите проект в публичный или приватный репозиторий на **GitHub** (Streamlit Cloud тесно интегрирован именно с GitHub).
2. Авторизуйтесь на [share.streamlit.io](https://share.streamlit.io/).
3. Нажмите кнопку **New app**, выберите ваш репозиторий, ветку `main` и укажите главный файл: `app.py`.
4. Нажмите на иконку шестеренки (Advanced settings), перейдите в раздел **Secrets** и скопируйте туда содержимое вашего `.env`:
   ```toml
   GEMINI_API_KEY = "your_key"
   ANTHROPIC_API_KEY = "your_key"
   MISTRAL_API_KEY = "your_key"
   ```
5. Нажмите **Deploy**. Через 1–2 минуты ваша Цитадель будет доступна в сети.

### 3.2. Vercel и Netlify (Особенности Serverless)
> ⚠️ **Важное техническое предупреждение:**
> Платформы Vercel и Netlify спроектированы под **Serverless-архитектуру** (бессерверные функции) и хостинг статических сайтов. Streamlit требует постоянного двустороннего WebSocket-соединения с работающим в фоне процессом Python. Поэтому запустить Streamlit на Vercel или Netlify «из коробки» напрямую невозможно — сессия будет обрываться по таймауту.

Если вам критически необходимо развернуть приложение именно там:
* **Способ для Vercel**: Используйте специальный шаблон с конфигурацией `vercel.json`, перенаправляющий запросы через бессерверный runtime Python (например, `@vercel/python`). Однако это может повлечь ограничения по времени выполнения функций (обычно 10-60 секунд на генерацию).
* **Альтернатива через Docker**: Рекомендуется развернуть Docker-контейнер на хостинг-платформах типа **Render**, **Railway** или **Fly.io**, которые предоставляют полноценный VPS-процесс для Python-приложений.

---

***

# AI Oracle

## Getting started

To make it easy for you to get started with GitLab, here's a list of recommended next steps.

Already a pro? Just edit this README.md and make it your own. Want to make it easy? [Use the template at the bottom](#editing-this-readme)!

## Add your files

* [Create](https://docs.gitlab.com/user/project/repository/web_editor/#create-a-file) or [upload](https://docs.gitlab.com/user/project/repository/web_editor/#upload-a-file) files
* [Add files using the command line](https://docs.gitlab.com/topics/git/add_files/#add-files-to-a-git-repository) or push an existing Git repository with the following command:

```
cd existing_repo
git remote add origin https://gitlab.com/webarystan/ai-chat-app.git
git branch -M main
git push -uf origin main
```

## Integrate with your tools

* [Set up project integrations](https://gitlab.com/webarystan/ai-chat-app/-/settings/integrations)

## Collaborate with your team

* [Invite team members and collaborators](https://docs.gitlab.com/user/project/members/)
* [Create a new merge request](https://docs.gitlab.com/user/project/merge_requests/creating_merge_requests/)
* [Automatically close issues from merge requests](https://docs.gitlab.com/user/project/issues/managing_issues/#closing-issues-automatically)
* [Enable merge request approvals](https://docs.gitlab.com/user/project/merge_requests/approvals/)
* [Set auto-merge](https://docs.gitlab.com/user/project/merge_requests/auto_merge/)

## Test and Deploy

Use the built-in continuous integration in GitLab.

* [Get started with GitLab CI/CD](https://docs.gitlab.com/ci/quick_start/)
* [Analyze your code for known vulnerabilities with Static Application Security Testing (SAST)](https://docs.gitlab.com/user/application_security/sast/)
* [Deploy to Kubernetes, Amazon EC2, or Amazon ECS using Auto Deploy](https://docs.gitlab.com/topics/autodevops/requirements/)
* [Use pull-based deployments for improved Kubernetes management](https://docs.gitlab.com/user/clusters/agent/)
* [Set up protected environments](https://docs.gitlab.com/ci/environments/protected_environments/)

***

# Editing this README

When you're ready to make this README your own, just edit this file and use the handy template below (or feel free to structure it however you want - this is just a starting point!). Thanks to [makeareadme.com](https://www.makeareadme.com/) for this template.

## Suggestions for a good README

Every project is different, so consider which of these sections apply to yours. The sections used in the template are suggestions for most open source projects. Also keep in mind that while a README can be too long and detailed, too long is better than too short. If you think your README is too long, consider utilizing another form of documentation rather than cutting out information.

## Name
Choose a self-explaining name for your project.

## Description
Let people know what your project can do specifically. Provide context and add a link to any reference visitors might be unfamiliar with. A list of Features or a Background subsection can also be added here. If there are alternatives to your project, this is a good place to list differentiating factors.

## Badges
On some READMEs, you may see small images that convey metadata, such as whether or not all the tests are passing for the project. You can use Shields to add some to your README. Many services also have instructions for adding a badge.

## Visuals
Depending on what you are making, it can be a good idea to include screenshots or even a video (you'll frequently see GIFs rather than actual videos). Tools like ttygif can help, but check out Asciinema for a more sophisticated method.

## Installation
Within a particular ecosystem, there may be a common way of installing things, such as using Yarn, NuGet, or Homebrew. However, consider the possibility that whoever is reading your README is a novice and would like more guidance. Listing specific steps helps remove ambiguity and gets people to using your project as quickly as possible. If it only runs in a specific context like a particular programming language version or operating system or has dependencies that have to be installed manually, also add a Requirements subsection.

## Usage
Use examples liberally, and show the expected output if you can. It's helpful to have inline the smallest example of usage that you can demonstrate, while providing links to more sophisticated examples if they are too long to reasonably include in the README.

## Support
Tell people where they can go to for help. It can be any combination of an issue tracker, a chat room, an email address, etc.

## Roadmap
If you have ideas for releases in the future, it is a good idea to list them in the README.

## Contributing
State if you are open to contributions and what your requirements are for accepting them.

For people who want to make changes to your project, it's helpful to have some documentation on how to get started. Perhaps there is a script that they should run or some environment variables that they need to set. Make these steps explicit. These instructions could also be useful to your future self.

You can also document commands to lint the code or run tests. These steps help to ensure high code quality and reduce the likelihood that the changes inadvertently break something. Having instructions for running tests is especially helpful if it requires external setup, such as starting a Selenium server for testing in a browser.

## Authors and acknowledgment
Show your appreciation to those who have contributed to the project.

## License
For open source projects, say how it is licensed.

## Project status
If you have run out of energy or time for your project, put a note at the top of the README saying that development has slowed down or stopped completely. Someone may choose to fork your project or volunteer to step in as a maintainer or owner, allowing your project to keep going. You can also make an explicit request for maintainers.
