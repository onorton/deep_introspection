# Deep Introspection

This is a web application that allows the user to upload image classification models and test images so that they can help explain why their network makes particular predictions. There are two such tools currently:

1. **Occlusion**: Occlude features of an image to learn how the network deals with missing information.
2. **Synthesis**: Synthesise features of an image to get a better idea on how the network "sees" those features.

The application currently supports both Caffe and TensorFlow models.

A more detailed guide can be accessed in the appendix of the report.pdf file 

## Installation

### Front End Server
1. **Install node and npm**
2. **Open the 'frontend' directory in a terminal**
3. **Install dependencies**: Run `npm install` to install all of the dependencies for the front end.
4.  **Build frontend bundle**: Run `npm build`
### Django Server
1. **Install Python and pip**
2. **Install main dependencies**: This can be done by running in the root directory `pip install -r requirements` to install all of the Python dependencies other than Caffe
3. **Install Caffe**: For Windows, this can be done using the [Windows branch](https://github.com/BVLC/caffe/tree/windows). For Ubuntu, [this guide](https://github.com/dungba88/caffe-python3-install/blob/master/install-caffe.md) works well.
4. **Configure settings**: These can be accessed in deep_introspection/settings.py. The main thing that needs to  be done is to generate a secret key. Generate a random string of 50 characters and place it in a text file named 'secret.txt' in this root directory. Then add an environment variable name 'PROJECT_PATH' that points to this directory.
5. **Set up database**: This is done by running python manage.py migrate
6. Run the server on port 8000 by running `python manage.py runserver 0.0.0.0:8000 --settings=deep_introspection.production_settings`. This can be accessed from http://127.0.0.1:8000.
