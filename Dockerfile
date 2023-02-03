FROM python:3.11.1-alpine
RUN pip install flask
RUN pip install flask_sqlalchemy
RUN pip install flask_login
RUN pip install pandas
COPY app.py /app.py
CMD ["python","app.py"]