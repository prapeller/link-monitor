from database.models.user import User, UserModel

head_dict = {
    'id': 1,
    'email': 'head@mail.com',
    'first_name': 'head',
    'last_name': 'headov',
    'is_head': True,
    'is_teamlead': True,
    'is_accepting_emails': True,
    'is_accepting_telegram': True,
    'telegram_id': '1',
    'is_active': True,
    'teamlead_id': None,
    'is_seo': True
}

teamlead_dict = {
    'id': 2,
    'email': 'teamlead@mail.com',
    'first_name': 'team',
    'last_name': 'leadov',
    'is_head': False,
    'is_teamlead': True,
    'is_accepting_emails': True,
    'is_accepting_telegram': True,
    'telegram_id': '2',
    'is_active': True,
    'teamlead_id': None,
    'is_seo': False
}

linkbuilder1_dict = {
    'id': 3,
    'email': 'linkbuilder1@mail.com',
    'first_name': 'linkbuilder1',
    'last_name': 'linkbuilderov1',
    'is_head': False,
    'is_teamlead': False,
    'is_accepting_emails': True,
    'is_accepting_telegram': True,
    'telegram_id': '3',
    'is_active': True,
    'teamlead_id': 2,
    'is_seo': False
}

linkbuilder2_dict = {
    'id': 4,
    'email': 'linkbuilder2@mail.com',
    'first_name': 'linkbuilder2',
    'last_name': 'linkbuilderov2',
    'is_head': False,
    'is_teamlead': False,
    'is_accepting_emails': True,
    'is_accepting_telegram': True,
    'telegram_id': '4',
    'is_active': True,
    'teamlead_id': 2,
    'is_seo': False
}

seo_dict = {
    'id': 5,
    'email': 'seo@mail.com',
    'first_name': 'seo',
    'last_name': 'seodov',
    'is_head': False,
    'is_teamlead': False,
    'is_accepting_emails': True,
    'is_accepting_telegram': True,
    'telegram_id': '5',
    'is_active': True,
    'teamlead_id': None,
    'is_seo': True
}


def create_user(session, user_dict):
    session.execute(
        f"""INSERT INTO user (
        id,
        email,
        first_name,
        last_name,
        is_head,
        is_teamlead,
        is_accepting_emails,
        is_accepting_telegram,
        telegram_id,
        is_active,
        teamlead_id,
        is_seo
        )
        VALUES (
        :id,
        :email,
        :first_name,
        :last_name,
        :is_head,
        :is_teamlead,
        :is_accepting_emails,
        :is_accepting_telegram,
        :telegram_id,
        :is_active,
        :teamlead_id,
        :is_seo
        )""", user_dict)


# def test_create_and_retrieve_user(repo):
#     repo.create(head_dict)
#     repo.create(teamlead_dict)
#     repo.create(linkbuilder1_dict)
#     repo.create(linkbuilder2_dict)
#     repo.create(seo_dict)
#     expected_users = [
#         UserModel(**head_dict),
#         UserModel(**teamlead_dict),
#         UserModel(**linkbuilder1_dict),
#         UserModel(**linkbuilder2_dict),
#         UserModel(**seo_dict),
#     ]
#     users = repo.get_all(UserModel)
#     assert users == expected_users
#
#
# def test_create_and_retrieve_user2(repo):
#     create_user(session, head_dict)
#     create_user(session, teamlead_dict)
#     create_user(session, linkbuilder1_dict)
#     create_user(session, linkbuilder2_dict)
#     create_user(session, seo_dict)
#     expected_users = [User(**head_dict),
#                       User(**teamlead_dict),
#                       User(**linkbuilder1_dict),
#                       User(**linkbuilder2_dict),
#                       User(**seo_dict),
#                       ]
#     assert session.query(User).all() == expected_users
