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
    
# Run the application
echo "Running the application"
python doc-gen.py $1 $2

# Copy generated .md files to the pub directory
echo "Copying generated .md files to the pub directory"
cp -f ./doc/*.md ./doc_pub/

# Run sphinx, `make html` in the doc_pub directory
cd ./doc_pub
make html
cd ..

# Deactivate the virtual environment
echo "Deactivating the virtual environment"
deactivate
