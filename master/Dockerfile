FROM python:3.11-slim

ENV FLASK_APP run.py

COPY run.py gunicorn-cfg.py requirements.txt .env create_db.py ./
COPY qcheckserv qcheckserv

RUN pip install -r requirements.txt

EXPOSE 7010
CMD ["gunicorn", "--config", "gunicorn-cfg.py", "run:app"]