FROM python:3.14

WORKDIR /app

COPY requirements .
RUN pip install --no-cache-dir -r requirements

COPY . .

EXPOSE 8001

CMD ["uvicorn", "app/main:app", "--host", "0.0.0.0", "--port", "8001"]