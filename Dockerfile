FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10-2022-11-25
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["uvicorn", "server:load_app", "--host", "0.0.0.0", "--port", "3500"]
