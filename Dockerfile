FROM python:3.10

# Install Entrez Direct
# https://www.ncbi.nlm.nih.gov/books/NBK179288/
RUN yes | sh -c "$(curl -fsSL https://ftp.ncbi.nlm.nih.gov/entrez/entrezdirect/install-edirect.sh)"

# Install Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

WORKDIR /workspaces/pmc-open-access-subset-utils
