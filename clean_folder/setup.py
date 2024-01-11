from setuptools import setup


setup(name = "clean_folder",
      version = "0.0.1",
      packages = ["clean_folder"],
      author = "Andrii Hrytsenko",
      description= "clean folder",
      entry_points = {
          'console_scripts': ['clean-folder = clean_folder.clean:main'] 
      }         
)