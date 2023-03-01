# import firebase_admin
# from firebase_admin import auth, credentials

# cred = credentials.Certificate(
#     "/Users/hd/Desktop/kin-pay/pay-telebirr/serviceAccountKey.json")
# firebase_admin.initialize_app(cred)

# # id_token comes from the client app (shown above)


# def find_user(id_token):
#     decoded_token = auth.verify_id_token(id_token)
#     uid = decoded_token['uid']
#     return uid

# # if we have uid its easier


# def user_info(uid):
#     user = auth.get_user(uid)
#     print('Successfully fetched user data: {0}'.format(user.uid))
#     return user


# def create_user():
#     user = auth.create_user(
#         email='user@example.com',
#         email_verified=False,
#         phone_number='+15555550100',
#         password='secretPassword',
#         display_name='John Doe',
#         photo_url='http://www.example.com/12345678/photo.png',
#         disabled=False)
#     print('Sucessfully created new user: {0}'.format(user.uid))


# def update_user(uid):
#     user = auth.update_user(
#         uid,
#         email='user@example.com',
#         phone_number='+15555550100',
#         email_verified=True,
#         password='newPassword',
#         display_name='John Doe',
#         photo_url='http://www.example.com/12345678/photo.png',
#         disabled=True)
#     print('Sucessfully updated user: {0}'.format(user.uid))


# def delete_user(uid):
#     auth.delete_user(uid)
#     print('Successfully deleted user')


# def delete_multiple_users(uid1, uid2, uid3):
#     result = auth.delete_users(["uid1", "uid2", "uid3"])
#     print('Successfully deleted {0} users'.format(result.success_count))
#     print('Failed to delete {0} users'.format(result.failure_count))

#     for err in result.errors:
#         print('error #{0}, reason: {1}'.format(result.index, result.reason))


# def list_all_users():
#     # Start listing users from the beginning, 1000 at a time.
#     page = auth.list_users()
#     while page:
#         for user in page.users:
#             print('User: ' + user.uid)
#             # Get next batch of users.
#             page = page.get_next_page()

# # Iterate through all users. This will still retrieve users in batches,
# # buffering no more than 1000 users in memory at a time.
#     for user in auth.list_users().iterate_all():
#         print('User: ' + user.uid)


# # cred = credentials.Certificate("./serviceAccountKey.json")
# # firebase_admin.initialize_app(cred)

# # id_token comes from the client app (shown above)


# # if we have uid its easier


# def user_info(uid):
#     user = auth.get_user(uid)
#     print('Successfully fetched user data: {0}'.format(user.uid))
#     return user


# uid = 'rZ44TdX7fBQ8hUZZDy2bRkTIcns1'
# test = user_info(uid)
