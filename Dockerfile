# ---------- Base image ----------
FROM python:3.12

# ---------- System dependencies ----------
RUN apt-get update && apt-get install -y \
    wget xvfb fonts-liberation libnss3 libatk-bridge2.0-0 libxkbcommon0 \
    libgtk-3-0 libdrm2 libgbm1 libasound2 libxshmfence1 libxrandr2 \
    && rm -rf /var/lib/apt/lists/*

# ---------- Install Playwright and Chromium ----------
RUN pip install --no-cache-dir playwright
RUN playwright install --with-deps chromium

# ---------- Set working directory and copy project ----------
WORKDIR /app
COPY . /app

# ---------- Install Python dependencies ----------
RUN pip install --no-cache-dir -r requirements.txt

# ---------- Collect static files (for Django apps) ----------
RUN python manage.py collectstatic --noinput

# ---------- Set environment variables ----------
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=bet9ja_tracker.settings

# ---------- Start command ----------
CMD ["gunicorn", "bet9ja_tracker.wsgi:application", "--bind", "0.0.0.0:8000"]
