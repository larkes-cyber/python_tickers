From python:3.7


WORKDIR /app

COPY requirements.txt ./requirements.txt
COPY data_ticker_history.sqlite ./data_ticker_history.sqlite
COPY data_ticker_summary.py ./data_ticker_summary.py
COPY front.py ./front.py

RUN pip install -r requirements.txt

EXPOSE 8501

ENTRYPOINT ["streamlit","run"]
CMD ["front.py"]
