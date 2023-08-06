FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10-2022-11-25

ENV OPENAI_API_KEY="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"
ENV ENVIRONMENT="TEST"

WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
EXPOSE 3500
CMD ["uvicorn", "server:load_app", "--host", "0.0.0.0", "--port", "3500"]
