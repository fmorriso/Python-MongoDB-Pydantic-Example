# python MongoDB with Pydantic models example

Example of using Pymongo to access MongoDB Atlas databases and collections using Pydantic models.

## Developer notes

* Warning: as of August 1, 2024, dependency package Cryptography issues a warning message if you install a version
  greater than or equal to 43.
  See the requirements.txt file for more information.

## References

* [Pydantic Fields](https://docs.pydantic.dev/2.10/usage/fields)

## Tools Used

| Tool          |  Version |
|:--------------|---------:|
| Python        |   3.13.2 |
| MongoDB Atlas |    8.0.4 |
| Pydantic      |   2.10.6 |
| Pymongo       |   4.11.1 |
| Loguru        |    0.7.3 |
| VSCode        |   1.97.2 |
| PyCharm       | 2024.3.3 |

## Change History

| Date       | Description                                                                        |
|:-----------|:-----------------------------------------------------------------------------------|
| 2024-05-20 | Initial creation                                                                   |
| 2024-07-30 | verify execution against latest version of software tools                          |
| 2024-08-01 | add requirements.txt file and warning about cryptography package level restriction |
| 2024-09-17 | Verify program works with python 3.12.6 and other new levels of related packages   |
| 2024-10-01 | Verify program works with python 3.12.7                                            |
| 2025-01-16 | Verify program works with python 3.13.1 and latest package releases                |
| 2025-01-30 | Upgrade packages                                                                   |
| 2025-02-18 | Upgrade to python 3.13.2 and latest packages                                       |
| 2025-02-21 | Stop using PyODMongo and use Pydantic instead                                      | 
| 2025-02-22 | rename remote repo and switch from GitLab to GitHub                                |
| 2025-02-24 | add extract_customer_schema method                                                 |
| 2025-02-25 | add static find_by_unique_id method to base model class                            |
| 2025-02-27 | start moving MongoDb methods and logging setup to base class                       | 

## References

* [MongoDB Atlas](https://www.mongodb.com/atlas)
* [PyMongo](https://pymongo.readthedocs.io/en/stable/index.html)
* [Pydantic](https://docs.pydantic.dev/2.10/)
* [Pydantic dynamic model creation](https://docs.pydantic.dev/2.10/concepts/models/#dynamic-model-creation)

## Developer Notes

* Following information is expected to be available and accurate in a file named .env with values different than the
  ones shown:

```text
MONGODB_CONNECTION_TEMPLATE='fmorrison-learning.vemxm.mongodb.net/?retryWrites=true&w=majority&appName=FMORRISON-LEARNING&authSource=admin'
MONGODB_UID='' <--- fill in your super user ID
MONGODB_PWD='' <--- fill in your super user password
DB_USER=<db_password>@fmorrison-learning.vemxm.mongodb.net/?retryWrites=true&w=majority&appName=FMORRISON-LEARNING
MONGODB_DATABASE_NAME='sample_analytics' <--- This program expects you have pulled in the free MongoDB sample databases
MONGODB_COLLECTION_NAME='customers'      <--- This program expects you have pulled in the free MongoDB sample collections
```

* since many MongoDB collections have an _id field, I created a parent class named `MongoDbBaseModel` to make it easier
  to handle working with that field,
  especially when creating new records by copying existing ones that will need a different unique id from the one they
  were copied from.