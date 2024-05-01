# Create a virtual environment if it doesn't alreay exist
echo "Creating a virtual environment if it doesn't already exist"
python3 -m venv dgv

# Activate the virtual environment
echo "Activating the virtual environment"
source dgv/bin/activate

# Install the required packages
echo "Installing the required packages"
pip install -r requirements.txt

# set the environment variables
echo "Checking the environment variables"
if [ -z "$OPENAI_API_KEY" ]; then
    echo "OPENAI_API_KEY is not set, you will need this to communicate with the OpenAI Python API."
    echo "Please set the OPENAI_API_KEY environment variable to the OpenAI API key for your project"
    echo "It should be something like OPENAI_API_KEY=\'sk-proj-1234567890abcdef1234567890abcdef\'"
    echo "You can get your API key from the OpenAI dashboard at https://platform.openai.com/account/api-keys"
    echo "Exiting..."
    exit 1
else
    echo "Found OPENAI_API_KEY=$OPENAI_API_KEY"
fi  

# Check for doc and doc_pub directories
echo "Checking for doc and doc_pub directories"
if [ ! -d "./doc" ]; then
    echo "Creating the doc directory"
    mkdir doc
fi
if [ ! -d "./doc_pub" ]; then
    echo "Creating the doc_pub directory"
    mkdir doc_pub
    echo "Creating sphinx template which will be used to publish documentation..."
    cd doc_pub
    sphinx-quickstart
    cd ..
fi

# debug
# exit 0

# Run the application
echo "Running the application"
python ./src/docgen.py $1 $2 $3 $4 $5 $6 $7 $8 $9

# Clear .md files from the doc_pub directory
echo "Clearing .md files from the doc_pub directory"
rm -f ./doc_pub/*.md

# Copy generated .md files to the pub directory
echo "Copying generated .md files to the pub directory"
cp -f ./doc/*.md ./doc_pub/

# Create index.rst file
echo "Creating ./doc_pub/index.rst file"
python ./src/create_index_rst.py

# Run sphinx, `make html` in the doc_pub directory
cd ./doc_pub
make html
cd ..

# Deactivate the virtual environment
echo "Deactivating the virtual environment"
deactivate
