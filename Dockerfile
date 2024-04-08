FROM python:3.10

# Install Entrez Direct
# https://www.ncbi.nlm.nih.gov/books/NBK179288/
RUN sh -c "$(curl -fsSL https://ftp.ncbi.nlm.nih.gov/entrez/entrezdirect/install-edirect.sh)"
RUN sh -c "$(wget -q https://ftp.ncbi.nlm.nih.gov/entrez/entrezdirect/install-edirect.sh -O -)"
RUN echo "export PATH=\$HOME/edirect:\$PATH" >> $HOME/.bash_profile

# Install Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# mkdir -p $EDIRECT_LOCAL_ARCHIVE
# archive-pubmed
# ?archive-pubmed -index
