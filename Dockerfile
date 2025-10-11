# ---------- Base image ----------
FROM python:3.12-slim

# ---------- System deps ----------
RUN apt-get update && apt-get install -y \
    wget xvfb fonts-liberation libnss3 libatk-bridge2.0-0 libxkbcommon0 \
    libgtk-3-0 libdrm2 libgbm1 libasound2 libxshmfence1 libxrandr2 \
    && rm -rf /var/lib/apt/lists/*

# ---------- Install Playwright ----------
RUN pip install playwright
RUN playwright install --with-deps chromium

# ---------- Copy project ----------
WORKDIR /app
COPY . /app

# ---------- Install Python deps ----------
RUN pip install --no-cache-dir -r requirements.txt

# ---------- Set environment ----------
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=bet9ja_tracker.settings

# ---------- Start command ----------
# The "web" process will run Django
CMD ["gunicorn", "bet9ja_tracker.wsgi:application", "--bind", "0.0.0.0:8080"]
