FROM python:latest
COPY . .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
EXPOSE 5001
ENTRYPOINT [ "python3" ]
CMD ["main.py" ]
