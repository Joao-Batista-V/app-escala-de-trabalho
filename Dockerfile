FROM python:3.10.5-alpine
ADD requirements.txt requirements.txt
RUN pip install Flask && pip install Flask-SQLAlchemy && pip install Flask-Login && pip install pandas
COPY app.py /app.py
CMD ["python","app.py"]