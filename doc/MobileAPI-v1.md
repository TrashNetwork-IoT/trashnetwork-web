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

If authentication of an API is optional, the API will be marked with (*) in this doc. **ATTENTION: optional authentication does NOT mean that requester can provide an invalid token.**

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

**By default, there is a fixed group named "Work Group" which includes all users.**

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

3. Query latest records by specific trash can.

```
GET cleaning/work/record/by_trash/{trash_id}/{limit_num}
GET cleaning/work/record/by_trash/{trash_id}/{end_time}/{limit_num}
GET cleaning/work/record/by_trash/{trash_id}/{start_time}/{end_time}/{limit_num}
```

+ `{user_id}`: ID of the user to query, long integer.

+ `{trash_id}`: ID of the trash can to query, long integer.

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
+ `trash_id`: ID of the corresponding trash can, long integer.
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

When posting new work record, the worker should not exceed **50 meters** distant from the given trash can.

```
POST cleaning/work/new_record
```

##### Request field

+ `trash_id`: ID of the specific trash can, long integer.

+ `longitude`: longitude of worker's current location, double.

+ `latitude`: latitude of worker's current location, double.


##### Response

| HTTP Status Code | result_code | message                              |
| ---------------- | ----------- | ------------------------------------ |
| 404              | 100202      | Trash can not found                  |
| 422              | 100203      | Illegal location                     |
| 422              | 100204      | Too far away from specific trash can |
| 201              | 0           | Post new work record successfully    |

## 2. API for recycle client

### 2.1 Account API

#### 2.1.1 Sign in

```
PUT recycle/account/login
```

##### Request field

- `user_name`: user name, string.
- `password`: password, string.

##### Response

| HTTP Status Code | result_code | message             |
| ---------------- | ----------- | ------------------- |
| 401              | 200001      | User does not exist |
| 401              | 200002      | Incorrect password  |
| 201              | 0           | Login successfully  |

If login successfully, the response should contain new generated token and basic user info. The token can be used for authentication later.

Basic user info should contain:

+ `user_id`: user ID, long integer.
+ `account_type`: user type, string. `N` represents normal user, `C` represents garbage collector.
+ `credit`: credit the user owns currently, integer.

Successful response example:

```json
{
  "result_code": 0,
  "message": "Login successfully",
  "token": "7457052ea6f1f56eb5d830353f36bbcace59dac3",
  "user": {
    "user_id": 123456,
    "account_type": "N",
    "credit": 0
  }
}
```

#### 2.1.2 Sign up

```
POST recycle/account/register
```

##### Request field

+ `user_name`: user name, string.
+ `password`: password, the password must not be fewer than 6 characters and not be more than 20 characters in length, string.
+ `email`: email address, string.
+ `account_type`: string, must be one of the following values:
  + `N`: normal user
  + `C`: garbage collector 

##### Response

| HTTP Status Code | result_code      | message                           |
| ---------------- | ---------------- | --------------------------------- |
| 422              | 200011           | User name has been used           |
| 422              | 200012           | Password is too short or too long |
| 422              | 200013(Reversed) | Illegal password format           |
| 422              | 200014           | Illegal email address             |
| 422              | 200015           | Illegal account type              |
| 201              | 0                | Sign up successfully              |

If register successfully, the response should contain new generated token and basic user info. In other word, the response is similar with that of login.

#### 2.1.3 * Logout

```
DELETE recycle/account/logout
```

##### Response

| HTTP Status Code | result_code | message |
| ---------------- | ----------- | ------- |
| 204              | -           | -       |

#### 2.1.4 * Check login status

Check if a token corresponding to the given user is valid.

```
GET cleaning/account/check_login/{user_id}
```

+ `user_id`: ID of the user to check, long integer.

##### Response

| HTTP Status Code | result_code | message                        |
| ---------------- | ----------- | ------------------------------ |
| 401              | 401         | Token does not match this user |
| 200              | 0           | -                              |

#### 2.1.5 * Query Self Info

```
GET recycle/account/self
```

##### Response

| HTTP Status Code | result_code | message |
| ---------------- | ----------- | ------- |
| 200              | 0           | -       |

Response should contain complete user info.

Complete user info should contain:

+ Basic user info

Successful response example:

```json
{
  "result_code": 0,
  "message": "",
  "user": {
    "user_id": 123456,
    "account_type": "N",
    "credit": 0
  }
}
```

### 2.2 Credit Record API

#### 2.2.1 * Query credit record

1. Query at most N latest records until now.

```
GET recycle/credit/record/{limit_num}
```

2. Query at most N latest records until a specific end time point.

```
GET recycle/credit/record/{end_time}/{limit_num}
```

3. Query at most N latest records during a specific time period.

```
GET recycle/credit/record/{start_time}/{end_time}/{limit_num}
```

- `{start_time}`: start time point, UNIX timestamp format(second unit).
- `{end_time}`: end time point, UNIX timestamp format(second unit).
- `{limit_num}`: the maximum number of records that this API can return, integer.

##### Response

| HTTP Status Code | result_code | message                 |
| ---------------- | ----------- | ----------------------- |
| 404              | 200101      | Credit record not found |
| 200              | 0           | -                       |

Successful response should contain a list consisting of info of credit records, and records should be sort by post time(newest to oldest).

Every work record should contain following fields:

- `good_description`: good description, string.
- `quantity`: quantity of good, integer.
- `credit`: credit number relate to this record, integer. If user gain credits in this record, it should be a positive number, otherwise negative.
- `record_time`: record time, UNIX timestamp format(second unit).

Successful response example:

```json
{
  "result_code": 0,
  "message": "",
  "credit_record_list": [
    {
      "good_description": "Bottle recycle",
      "quantity": 1,
      "credit": 1,
      "record_time": 1489827858
    }
  ]
}
```

#### 2.2.2 * Post new credit record(bottle recycle)

When recycling bottles, the user should not exceed **50 meters** distant from the specific recycle point.

```
POST recycle/credit/record/new/bottle_recycle
```

##### Request field

+ `recycle_point_id`: recycle point ID, long integer.
+ `quantity`: quantity of bottles, integer.
+ `longitude`: longitude of user's current location, double.
+ `latitude`: latitude of user's current location, double.

##### Response

| HTTP Status Code | result_code | message                                  |
| ---------------- | ----------- | ---------------------------------------- |
| 404              | 200111      | Recycle point not found                  |
| 422              | 200112      | This recycle point does not accept bottles |
| 422              | 200113      | Illegal location                         |
| 422              | 200114      | Too far away from specific recycle point |
| 201              | 0           | Recycle bottle successfully              |

Response should contain credits that the user gain by recycling bottles this time.

Successful response example:

```json
{
  "result_code": 0,
  "message": "Recycle bottle successfully",
  "credit": 3
}
```

### 2.3 Feedback API

#### 2.3.1 (*) Post new feedback

If requester does not provide token, the feedback will be post anonymously.

```
POST recycle/feedback/new_feekback
```

##### Request field

+ `title`: title of new feedback, string.
+ `text_content`: text content of new feedback, string.

##### Response

| HTTP Status Code | result_code | message                    |
| ---------------- | ----------- | -------------------------- |
| 201              | 0           | Post feedback successfully |

### 2.4 Recycle Point API

#### 2.4.1 (*) Query recycle points 

```
GET recycle/recycle_point/all_points
```

##### Response

| HTTP Status Code | result_code | message |
| ---------------- | ----------- | ------- |
| 200              | 0           | -       |

Successful response should contain a list consisting of info of all recycle points.

Every recycle point can should contain following fields at least:

- `recycle_point_id`: recycle point ID, long integer.
- `description`: literal description of the recycle point, string.
- `longitude`: longitude of the recycle point's location, double.
- `latitude`: latitude of the recycle point's location, double.
- `bottle_recycle`: if this recycle point is able to accept bottles, boolean.

If the requester is authenticated as a garbage collector and this recycle point is managed by him, it should contain following additional fields:

+ `bottle_num`: (if `bottle_recycle` is true)current quantity of bottles in this recycle point, integer.


+ `owner_id`: The user ID of the user who manages this recycle point.

Successful response example:

```json
{
  "result_code": 0,
  "message": "",
  "recycle_point_list": [
    {
      "point_id": 1,
      "description": "Trash on layer 2, No.9 student apartment",
      "longitude": 116.355769,
      "latitude": 39.96431,
      "bottle_num": 5,
      "owner_id": 100
    }
  ]
}
```

### 2.5 Recycle Record API

#### 2.5.1 * Query recycle records

Only **garbage collector** can query recycle records.

1. Query at most N latest records until now.

```
GET recycle/recycle_record/{limit_num}
```

2. Query at most N latest records until a specific end time point.

```
GET recycle/recycle_record/{end_time}/{limit_num}
```

3. Query at most N latest records during a specific time period.

```
GET recycle/recycle_record/{start_time}/{end_time}/{limit_num}
```

- `{start_time}`: start time point, UNIX timestamp format(second unit).
- `{end_time}`: end time point, UNIX timestamp format(second unit).
- `{limit_num}`: the maximum number of records that this API can return, integer.

##### Response

| HTTP Status Code | result_code | message   |
| ---------------- | ----------- | --------- |
| 404              | 200401      | No record |
| 200              | 0           | -         |

Successful response should contain a list consisting of info of recycle records.

Every record should contain following fields:

+ `recycle_point_id`: ID of the corresponding recycle point, long integer
+ `bottle_num`: (if the recycle point is able to accept bottles)recycled quantity of bottles in this record, integer.
+ `recycle_time`: time of this record, UNIX timestamp format(second unit).

Successful response example:

```json
{
  "result_code": 0,
  "message": "",
  "recycle_record_list": [
    {
      "recycle_point": 1,
      "bottle_num": 5,
      "recycle_time": 1489827858
    }
  ]
}
```

#### 2.5.2 * Post new recycle record

Only **garbage collector** can post recycle records.

```
POST recycle/recycle_record/new_record
```

##### Request filed

+ `recycle_point_id`: ID of the recycle point to recycle.

##### Response

| HTTP Status Code | result_code | message                                  |
| ---------------- | ----------- | ---------------------------------------- |
| 404              | 200402      | Recycle point not found                  |
| 422              | 200403      | The recycle point does not be managed by you |
| 422              | 200404      | The recycle point is empty               |
| 201              | 0           | Post recycle record successfully         |

## 3. Public API

### 3.1 Query trash cans

```
GET public/trash/all_trashes
```

##### Response

| HTTP Status Code | result_code | message |
| ---------------- | ----------- | ------- |
| 200              | 0           | -       |

Successful response should contain a list consisting of info of all trash cans.

Every trash can should contain following fields:

+ `trash_id`: trash can ID, long integer.
+ `description`: literal description of the trash can, string.
+ `longitude`: longitude of the trash can's location, double.
+ `latitude`: latitude of the trash can's location, double.

Successful response example:

```json
{
  "result_code": 0,
  "message": "",
  "trash_list": [
    {
      "trash_id": 1,
      "description": "Trash on layer 2, No.9 student apartment",
      "longitude": 116.355769,
      "latitude": 39.96431
    }
  ]
}
```

### 3.2 Query feedbacks

1. Query at most N latest feedbacks until now.

```
GET public/feedback/feedbacks/{limit_num}
```

2. Query at most N latest feedbacks until a specific end time point.

```
GET public/feedback/feedbacks/{end_time}/{limit_num}
```

3. Query at most N latest feedbacks during a specific time period.

```
GET public/feedback/feedbacks/{start_time}/{end_time}/{limit_num}
```

- `{start_time}`: start time point, UNIX timestamp format(second unit).
- `{end_time}`: end time point, UNIX timestamp format(second unit).
- `{limit_num}`: the maximum number of feedbacks that this API can return, integer.

##### Response

| HTTP Status Code | result_code | message     |
| ---------------- | ----------- | ----------- |
| 404              | 200201      | No feedback |
| 200              | 0           | -           |

Successful response should contain a list consisting of info of feedbacks and they should be sort by post time(newest to oldest).

Every feedback should contain following fields:

+ `user_name`: (if any) user name of poster, string.
+ `title`: title of feedback, string.
+ `text_content`: text content of feedback, string.

- `feedback_time`: time when the feedback was post, UNIX timestamp format(second unit).

Successful response example:

```json
{
  "result_code": 0,
  "message": "",
  "feedback_list": [
    {
      "user_name": "Test user",
      "title": "Feedback Title",
      "text_content": "Feedback content...",
      "feedback_time": 1489827858
    }
  ]
}
```

