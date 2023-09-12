FROM python:3.8-slim
WORKDIR /app
COPY . /app
RUN pip install --trusted-host pypi.python.org -r requirements.txt
EXPOSE 8000
CMD ["gunicorn", "app:app", "-b", "0.0.0.0:8000", "--workers", "3", "--log-level", "info"]