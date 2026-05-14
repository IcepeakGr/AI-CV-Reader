FROM python:3.9.13-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . .
ENV FRONTEND_STREAMLIT_PORT=8501
EXPOSE ${FRONTEND_STREAMLIT_PORT}
CMD ["streamlit", "run", "app.py", "--server.port=${FRONTEND_STREAMLIT_PORT}", "--server.address=0.0.0.0"]