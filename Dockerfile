FROM python:3.11.1-alpine
RUN pip install -r requirements.txt
COPY app.py /app.py
CMD ["python","app.py"]