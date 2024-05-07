# Create a virtual environment if it doesn't alreay exist
echo "Creating a virtual environment if it doesn't already exist"
python3 -m venv dgv

# Activate the virtual environment
echo "Activating the virtual environment"
source dgv/bin/activate

# Install the required packages
echo "Installing the required packages"
pip install -r requirements.txt

# Check for doc and doc_pub directories
echo "Checking for doc and doc_pub directories"
if [ ! -d "./build/doc" ]; then
    echo "Creating the doc directory"
    mkdir -p build/doc
fi
if [ ! -d "./build/doc/pub" ]; then
    echo "Creating the pub directory"
    mkdir -p build/doc/pub
    echo "Creating sphinx template which will be used to publish documentation..."
    cd build/doc/pub
    cp ../../../pub_template/* ./
    mkdir _static
    mkdir _templates
    cd -
fi

# Run the application
echo "Running the doc-gen application"
python ./src/docgen.py $1 $2 $3 $4 $5 $6 $7 $8 $9

# Clear .md files from the doc_pub directory
echo "Clearing .md files from the doc_pub directory"
rm ./build/doc/pub/*.md

# Copy generated .md files to the pub directory
echo "Copying generated .md files to the pub directory"
cp ./build/doc/*.md ./build/doc/pub/

# Create index.rst file
echo "Creating ./build/doc/pub/index.rst file"
python ./src/docgen/create_index_rst.py

# Run sphinx, `make html` in the doc_pub directory
cd ./build/doc/pub
make html
cd -

echo "Documentation generation complete and can be viewed at ./build/doc/pub/_build/html/index.html"

# Deactivate the virtual environment
echo "Deactivating the virtual environment"
deactivate

# query the user if they would like to view the generated documentation
echo "Would you like to view the generated documentation? (y/n)"
read view_doc
if [ $view_doc == "y" ]; then
    xdg-open "./build/doc/pub/_build/html/index.html" &
fi