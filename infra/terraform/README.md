# Розгортання в Azure через Terraform + cloud-init

## Передумови

- Обліковий запис Azure.
- Доступ до Azure Portal через браузер.

## Швидкий старт

### 1. Відкрити Azure Cloud Shell

Зайти на [portal.azure.com](https://portal.azure.com), 
натиснути іконку `>_` у верхній панелі, обрати **Bash**.

### 2. Склонувати репозиторій

\`\`\`bash
git clone https://github.com/YOUR_USERNAME/open-data-ai-analytics.git
cd open-data-ai-analytics/infra/terraform
\`\`\`

### 3. Розгорнути інфраструктуру

\`\`\`bash
terraform init
terraform plan
terraform apply
\`\`\`

Ввести `yes` для підтвердження. Створення займає ~3-5 хвилин.

### 4. Дочекатися cloud-init

Після `terraform apply` ще ~5 хвилин виконується автоматичне 
налаштування VM (встановлення Docker, клонування проєкту, 
запуск контейнерів).

### 5. Відкрити веб-інтерфейс

\`\`\`bash

Outputs:

public_ip = PUBLIC_IP
ssh_private_key = ssh
web_url = PUBLIC_IP

\`\`\`

Скопіювати URL у браузер. Має відкритися інтерфейс застосунку.

### 6. Видалення інфраструктури

\`\`\`bash
terraform destroy
\`\`\`

## Структура файлів

- `main.tf` — описує всі ресурси Azure (VM, мережа, NSG, IP).
- `variables.tf` — налаштовувані параметри (URL репозиторію, 
  розмір VM, локація).
- `outputs.tf` — вивід публічної IP і SSH-ключа після apply.
- `cloud-init.yaml` — сценарій налаштування VM при першому 
  запуску (встановлення Docker, клонування, docker compose up).

## Налаштування VM

Використовується розмір `Standard_B2s` (2 vCPU, 4 GB RAM). 
Менший `Standard_B1s` (1 GB RAM) виявився недостатнім для 
білду контейнерів.
