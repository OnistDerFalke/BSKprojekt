## Short API application description

---

Application was build using python Flask framework. 
That app is mainly used for maneging Users which could communicate with each other
using a graphic application created especially for this purpose.

---

### How to run the application

#### Window
To run this application on Windows OS go in the console to the main *api_users* application folder is needed.
Then enter in console command
```shell
./run.bat
```
is needed. Application should lunch in a few seconds showing information about URL address on which is reachable.

#### Linux
To run this application on Linux OS go in the console to the main *api_users* application folder is needed.
Then enter in console command
```shell
./run.sh
```
is needed. Application should lunch in a few seconds showing information about URL address on which is reachable.

---

### Available endpoints
| Request methods   |      /api/users      |  /api/users/\<int:user_id\> |
|-------------------|:--------------------:|:---------------------------:|
| GET               | `:white_check_mark:` | `:white_check_mark:`        |
| POTS              | `:white_check_mark:` | `:x:`                       |
| PUT               | `:x:`                | `:white_check_mark:`        |
| DELETE            | `:x:`                | `:white_check_mark:`        |

### Swagger

After launching of the application and going to an url /api/swagger **swagger UI** is available 
for checking API endpoints and for sending testing requests. 