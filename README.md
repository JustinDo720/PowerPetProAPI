# PowerPetProAPI

---

### This directory will hold the backend code for our [PowerPetPro Project](https://github.com/JustinDo720/PowerPetPro). This is written in Python using Django Framework.
NOTE: This is a PUBLIC directory which means our secret key for this Django project will be open, but we will be changing the secret key on live servers.

Google Cloud Storage: The json file that contains our credentials will **NOT** be pushed on github. Check GCP IAM to obtain the .json file

---

### Major Packages (all packages are all requirements.txt)

- API Packages & Settings
    - [Django Rest Framework](https://www.django-rest-framework.org/)
    - [Cors](https://pypi.org/project/django-cors-headers/)
- User Authentication
    - [Djoser](https://djoser.readthedocs.io/en/latest/getting_started.html)
    - [Simple JSON Web Token](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/)
- Images 
    - [Google Cloud Storages](https://django-storages.readthedocs.io/en/latest/backends/gcloud.html)
- Data
    - [Faker](https://pypi.org/project/Faker/)

### Key Features of This Project
1. User Authentication and Profiles using Djoser and Simple JWT to connect this backend with our frontend Vue page
1. Emails are sent to user's emails for order details
1. Connected Feedback system with questions and answers as well as user opinions and feedback 
1. Extra API views for admin control on front-end 
1. MYSQL database 
1. Stripe to handle payments 
1. RestAPI viewsets that showcases users, products, categories and user feedbacks 
1. Faker Package for random and easier fake data inputs 



