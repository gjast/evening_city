FROM python:3.14

WORKDIR /app

COPY requirements .
RUN pip install --no-cache-dir -r requirements

COPY . .

EXPOSE 8002

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]

