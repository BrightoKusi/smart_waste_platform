FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY simulate_bin_data.py .

CMD ["python", "simulate_bin_data.py"]
