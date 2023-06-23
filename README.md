# semantic-kernel-playground


# How to run this locally:
```
python -m venv .venv
.\.venv\Scripts\activate

python -m pip config set global.index-url https://pkgs.dev.azure.com/azure-sdk/public/_packaging/azure-sdk-for-python/pypi/simple/
pip install -r .\requirements.txt 

streamlit run .\app_chat.py
```