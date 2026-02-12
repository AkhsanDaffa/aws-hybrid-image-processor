FROM python:3.9-slim
WORKDIR /app
RUN pip install flask boto3
COPY app.py .
CMD ["python", "app.py"]