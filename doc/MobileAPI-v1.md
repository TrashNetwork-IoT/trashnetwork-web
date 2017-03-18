# Mobile REST API Document 

## Introduction

Unified URL format: 

`http(s)://{HOST}/trashnetwork/{API_VERSION}/mobile/{API_PATH}` 

+ `{HOST}`: the server host address.
+ `{API_VERSION}`: API version. This doc is written for `v1` version.
+ `{API_PATH}`: relative path of the APIs described in this doc.

For example, if the `{API_PATH}` of signing in API is `account/login`, and the server is deployed on host `localhost` at port `23000`, the whole URL is:

```
http(s)://localhost:23000/trashnetwork/v1/mobile/account/login
```

## Format Requirement

1. If no specific instructions, the Content-Type of request body and response body of all APIs are both `application/json`, and all JSON responses will contain the following two fields at least:

   + result_code: result code, integer.
   + message: literal description of result, string.

2. All literal content must be encoded in `UTF-8` character set.

3. Date time format: UNIX timestamp, with second unit.

## Authentication

If an API need authentication to access, client must put token to **`Auth-Token`**  field in HTTP header when launching request.

If an API need authentication, it will be marked with * in this doc.

## Common Response

Possible responses of every given API:

| HTTP Status Code | result_code | message               |
| ---------------- | ----------- | --------------------- |
| 404              | 404         | API not found         |
| 400              | 400         | Bad request           |
| 401              | 401         | Invalid token         |
| 403              | 403         | Permission denied     |
| 500              | 500         | Server internal error |

## 1. API for cleaning job management client

### 1.1 Account API

#### 1.1.1 Sign in

```
PUT cleaning/account/login
```

##### Request field

+ `user_id`: user ID, long integer.

+ `password`: password, string.

##### Response

| HTTP Status Code | result_code | message             |
| ---------------- | ----------- | ------------------- |
| 401              | 100001      | User does not exist |
| 401              | 100002      | Incorrect password  |
| 201              | 0           | Login successfully  |

If login successfully, the response should contain new generated token. The token can be used for authentication later.

Successful response example:

```json
{
  "result_code": 0,
  "message": "Login successfully",
  "token": "7457052ea6f1f56eb5d830353f36bbcace59dac3"
}
```

#### 1.1.2 * Logout

```
DELETE cleaning/account/logout
```

##### Response

| HTTP Status Code | result_code | message |
| ---------------- | ----------- | ------- |
| 204              | -           | -       |

#### 1.1.3 * Check login status

Check if a token corresponding to the given user is valid.

```
GET cleaning/account/check_login/{user_id}
```

+ `{user_id}`: ID of the user to check, long integer.

##### Response

| HTTP Status Code | result_code | message                        |
| ---------------- | ----------- | ------------------------------ |
| 401              | 401         | Token does not match this user |
| 200              | 0           | -                              |


#### 1.1.4 * Query user info by ID

```
GET cleaning/account/user_info/by_id/{user_id}
```

+ `{user_id}`: ID of the user to query, long integer.

##### Response

| HTTP Status Code | result_code | message             |
| ---------------- | ----------- | ------------------- |
| 404              | 100003      | User does not exist |
| 200              | 0           | -                   |

If query successfully, the response should contain corresponding **complete** user info.

Complete user info should contain following fields:

+ Basic user info:

  + `user_id`: ID of the user, long integer.

  + `phone_number`: phone number of the user(may be blank), string.

  + `name`: full name of the user, string.

  + `gender`: gender of the user, single character. `M` represents male, `F` represents female.

  + `account_type`: job type of the user, single character. `C` represents cleaner, `M` represents manager.

  + `portrait`: portrait image data encoded by `base64`, string.

Successful response example:

```json
{
  "result_code": 0,
  "message": "",
  "user": {
    "user_id": 123456,
    "phone_number": "123456",
    "name": "San Zhang",
    "gender": "M",
    "account_type": "C",
    "portrait": "Tm90IEZvdW5kOiAvCg=="
  }
}
```

#### 1.1.5 * Query all user basic info

This API should return basic info of all users **except** requester self.

```
GET cleaning/account/all_group_users
```
##### Response

| HTTP Status Code | result_code | message |
| ---------------- | ----------- | ------- |
| 200              | 0           | -       |

Successful response should contain a list consisting of basic info of all users.

Successful response example:

```json
{
  "result_code": 0,
  "message": "",
  "user_list": [
    {
      "user_id": 123456,
      "phone_number": "123456",
      "name": "San Zhang",
      "gender": "M",
      "account_type": "C",
      "portrait": "Tm90IEZvdW5kOiAvCg=="
    }
  ]
}
```

### 1.2 Group API

#### 1.2.1 * Query all group info

This API should return info of all groups that the requester belongs to.

```
GET cleaning/group/all_groups
```

##### Response

| HTTP Status Code | result_code | message         |
| ---------------- | ----------- | --------------- |
| 404              | 100101      | Group not found |
| 200              | 0           | -               |

Successful response should contain a list consisting of info of all groups that the requester belongs to.

Group info should contain:

+ `group_id`: group ID, long integer.

+ `name`: name of the group, string.

+ `portrait`: portrait image data encoded by `base64`, string.

+ `member_list`: a list consist of user IDs(long integer) of all group members.

Successful response example:

```json
{
  "result_code": 0,
  "message": "",
  "group_list": [
    {
      "group_id": 233333,
      "name": "Work Group",
      "portrait": "Tm90IEZvdW5kOiAvCg==",
      "member_list": [
        123456
      ]
    }
  ]
}
```
#### 1.2.2 * Query bulletins of a group

1. Query at most N latest bulletins until now.

```
GET cleaning/group/bulletin/{group_id}/{limit_num}
```

2. Query at most N latest bulletins until a specific end time point.

```
GET cleaning/group/bulletin/{group_id}/{end_time}/{limit_num}
```

3. Query at most N latest bulletins during a specific time period.

```
GET cleaning/group/bulletin/{group_id}/{start_time}/{end_time}/{limit_num}
```

+ `{group_id}`: ID of the group to query, long integer.

+ `{start_time}`: start time point, UNIX timestamp format(second unit).

+ `{end_time}`: end time point, UNIX timestamp format(second unit).

+ `{limit_num}`: the maximum number of bulletins that this API can return, integer.


##### Response

| HTTP Status Code | result_code | message                            |
| ---------------- | ----------- | ---------------------------------- |
| 404              | 100101      | Group not found                    |
| 422              | 100102      | User does not belong to this group |
| 404              | 100111      | Bulletin not found                 |
| 200              | 0           | -                                  |

Successful response should contain a list consisting of info of bulletins, and bulletins should be sort by post time(newest to oldest).

Every bulletin should contain following fields:

+ `poster_id`: user ID of the poster, long integer.
+ `post_time`: post time, UNIX timestamp format(second unit).
+ `title`: title of the bulletin, string.
+ `text_content`: text content of the bulletin, string.

Successful response example:

```json
{
  "result_code": 0,
  "message": "",
  "bulletin_list": [
    {
      "poster_id": 123456,
      "post_time": 1489827858,
      "title": "Important Notice",
      "text_content": "Notice content..."
    }
  ]
}
```

#### 1.2.3 * Post new bulletin 

Only **managers** can post new bulletins.

```
POST cleaning/group/new_bulletin
```

##### Request field

+ `group_id`: ID of the group where requester post new bulletin, long integer.

- `title`: title of the new bulletin, string.

- `text_content`: text content of the new bulletin, string.

##### Response

| HTTP Status Code | result_code | message                            |
| ---------------- | ----------- | ---------------------------------- |
| 404              | 100101      | Group not found                    |
| 422              | 100102      | User does not belong to this group |
| 201              | 0           | Post new bulletin successfully     |

### 1.3 Work Record API

#### 1.3.1 * Query work record

1. Query latest records by time.

(1) Query at most N latest records until now.

```
GET cleaning/work/record/{limit_num}
```

(2) Query at most N latest records until a specific end time point.

```
GET cleaning/work/record/{end_time}/{limit_num}
```

(3) Query at most N latest records during a specific time period.

```
GET cleaning/work/record/{start_time}/{end_time}/{limit_num}
```

2. Query latest records by specific user.

```
GET cleaning/work/record/by_user/{user_id}/{limit_num}
GET cleaning/work/record/by_user/{user_id}/{end_time}/{limit_num}
GET cleaning/work/record/by_user/{user_id}/{start_time}/{end_time}/{limit_num}
```

3. Query latest records by specific trash.

```
GET cleaning/work/record/by_trash/{trash_id}/{limit_num}
GET cleaning/work/record/by_trash/{trash_id}/{end_time}/{limit_num}
GET cleaning/work/record/by_trash/{trash_id}/{start_time}/{end_time}/{limit_num}
```

+ `{user_id}`: ID of the user to query, long integer.

+ `{trash_id}`: ID of the trash to query, long integer.

+ `{start_time}`: start time point, UNIX timestamp format(second unit).

+ `{end_time}`: end time point, UNIX timestamp format(second unit).

+ `{limit_num}`: the maximum number of records that this API can return, integer.


##### Response

| HTTP Status Code | result_code | message               |
| ---------------- | ----------- | --------------------- |
| 404              | 100201      | Work record not found |
| 200              | 0           | -                     |

Successful response should contain a list consisting of info of work records, and records should be sort by post time(newest to oldest).

Every work record should contain following fields:

+ `user_id`: ID of the worker, long integer.
+ `trash_id`: ID of the corresponding trash, long integer.
+ `record_time`: record time, UNIX timestamp format(second unit).

Successful response example:

```json
{
  "result_code": 0,
  "message": "",
  "work_record_list": [
    {
      "user_id": 123456,
      "trash_id": 1,
      "record_time": 1489827858
    }
  ]
}
```

#### 1.3.2 * Post new work record

When posting new work record, the worker should not exceed **50 meters** distant from the given trash.

```
POST cleaning/work/new_record
```

##### Request field

+ `trash_id`: ID of the specific trash, long integer.

+ `longitude`: longitude of worker's current location, double.

+ `latitude`: latitude of worker's current location, double.


##### Response

| HTTP Status Code | result_code | message                           |
| ---------------- | ----------- | --------------------------------- |
| 404              | 100202      | Trash not found                   |
| 422              | 100203      | Illegal location                  |
| 422              | 100204      | Too far away from specific trash  |
| 201              | 0           | Post new work record successfully |

## 2. Public API

### 2.1 Query trashes

```
GET public/trash/all_trashes
```

##### Response

| HTTP Status Code | result_code | message |
| ---------------- | ----------- | ------- |
| 200              | 0           | -       |

Successful response should contain a list consisting of info of all trashes.

Every trash should contain following fields:

+ `trash_id`: trash ID, long integer.
+ `description`: literal description of the trash, string.
+ `longitude`: longitude of the trash's location.
+ `latitude`: latitude of the trash's location.

```json
{
  "result_code": 0,
  "message": "",
  "trash_list": [
    {
      "trash_id": 1,
      "description": "Trash on layer 2, No.9 student apartment",
      "longitude": 116.362249,
      "latitude": 39.970163
    }
  ]
}
```
