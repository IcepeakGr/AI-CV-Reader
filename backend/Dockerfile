FROM python:3.9.13-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . . 
ENV BACKEND_FASTAPI_PORT=8000
EXPOSE ${BACKEND_FASTAPI_PORT}
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "${BACKEND_FASTAPI_PORT}"]