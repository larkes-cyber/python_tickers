From python:3.9

WORKDIR /app

COPY requirements.txt ./requirements.txt
COPY front.py ./front.py

RUN pip install -r requirements.txt

EXPOSE 8501

ENTRYPOINT ["streamlit","run"]
CMD ["front.py"]
