## v0.10.1 (2023-10-26)

### Fix

- **incoming**: typo in System model - type_ -> type

## v0.10.0 (2023-10-24)

### Feat

- **incoming**: Add incoming system messages

## v0.9.0 (2023-07-26)

### Feat

- **client**: Add pair_with_code method
- Add upload_file method
- Add status privacy method

### Fix

- pass *args, **kwargs in delete_message method
- don't log data when is too long (1000)
- better error handling

## v0.8.2 (2023-05-01)

### Fix

- **deps**: upgrade loguru dependency from version 0.6.0 to 0.7.0

## v0.8.1 (2023-02-23)

### Fix

- typo in client send_list & send_buttons typing

## v0.8.0 (2023-02-23)

### Feat

- Add header & footer for send_list & send_buttons

### Fix

- support whatsapp v2.45 api

## v0.7.3 (2022-12-25)

### Fix

- fix reactions - emoji key typo

## v0.7.2 (2022-12-25)

### Feat

- Add support for replying to user message

## v0.7.1 (2022-12-25)

## v0.7.0 (2022-12-25)

### Feat

- support reaction messages

## v0.6.0 (2022-12-25)

### Feat

- allow passing Thumbnail to media
- Add delete message and contacts method
- support official WhatsApp CloudAPI

### Fix

- **responses**: client.send return AnyResponse
- support for python ^3.7

## v0.5.1 (2022-05-29)

### Fix

- update Group, Account and Text models
- **deps**: Bump driconfig 0.1.1 -> 0.2.0
- **deps**: bump loguru 0.5.3 -> 0.6.0

## v0.5.0 (2022-04-11)

### Feat

- Add location message

## v0.4.3 (2022-04-10)

### Fix

- typo in Client.send

## v0.4.2 (2022-04-10)

### Fix

- config typos

## v0.4.1 (2022-04-10)

### Fix

- Parse config defaults in Client.send method

## v0.4.0 (2022-04-10)

### Feat

- Add preview_url default config

## v0.3.2 (2022-04-07)

### Fix

- Add LogoutResponse

## v0.3.1 (2022-04-02)

### Fix

- typo in PrivateMessage

## v0.3.0 (2022-04-02)

### Feat

- **messages**: Add Group & Private messages

## v0.2.1 (2022-04-01)

### Fix

- fix Interactive text
- some fix's

## v0.2.0 (2022-03-27)

### Feat

- **media**: Support Uploading and Sending media

## v0.1.3 (2022-03-27)

### Feat

- **client**: Add image response on login

## v0.1.2 (2022-01-26)

### Fix

- **interactive**: fix Interactive List sections rows

## v0.1.1 (2022-01-26)

### Fix

- **interactive**: fi'x interactive list button type
