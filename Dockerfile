# Используем официальный образ Python
FROM python:3.10-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальные файлы проекта
COPY . .

# Пробрасываем порт (если Flask сервер, по умолчанию 5000)
EXPOSE 5000

# Команда для запуска Flask-приложения
CMD ["python", "app.py"]
