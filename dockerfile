FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir
COPY . .
WORKDIR /app/project
CMD ["uvicorn", "settings:app", "--host", "0.0.0.0", "--port", "8000"]