FROM nvcr.io/nvidia/pytorch:23.11-py3

# Install Entrez Direct
# https://www.ncbi.nlm.nih.gov/books/NBK179288/
RUN sh -c "$(curl -fsSL https://ftp.ncbi.nlm.nih.gov/entrez/entrezdirect/install-edirect.sh)"
RUN sh -c "$(wget -q https://ftp.ncbi.nlm.nih.gov/entrez/entrezdirect/install-edirect.sh -O -)"
RUN echo "export PATH=\$HOME/edirect:\$PATH" >> $HOME/.bash_profile
