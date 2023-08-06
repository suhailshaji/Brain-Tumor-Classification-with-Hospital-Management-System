
# Importing the `create_app` function from the `app` module.
from hms import create_app

# Checking if the name of the current module (`__name__`) is `__main__`. 
if __name__ =='__main__':
      
      # Calling the `create_app` function to create a new application instance and then running it using the `run()` method.
      create_app().run(port=5000)
